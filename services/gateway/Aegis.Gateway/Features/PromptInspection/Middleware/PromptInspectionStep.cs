using System.Security.Cryptography;
using System.Text;
using Aegis.Gateway.Features.Policy;
using Aegis.Gateway.Features.Policy.Models;
using Aegis.Gateway.Features.Policy.Services;
using Aegis.Gateway.Features.PromptExtraction;
using Aegis.Gateway.Features.PromptInspection.Contracts;
using Aegis.Gateway.Features.PromptInspection.Infrastructure;
using Microsoft.AspNetCore.Mvc;
using Yarp.ReverseProxy.Configuration;
using Yarp.ReverseProxy.Model;

namespace Aegis.Gateway.Features.PromptInspection.Middleware;

public sealed class PromptInspectionStep(
    RequestDelegate next,
    IPromptInspectionClient promptInspectionClient,
    IPromptExtractorResolver promptExtractorResolver,
    IPolicyProvider policyProvider,
    IPolicyEvaluator policyEvaluator,
    IConfirmTokenService confirmTokenService,
    ILogger<PromptInspectionStep> logger)
{
    private const string ConfirmHeader = "X-Aegis-Confirm-Token";
    private const string DecisionHeader = "X-Aegis-Decision";

    public async Task InvokeAsync(HttpContext context)
    {
        CancellationToken ct = context.RequestAborted;

        var proxyFeature = context.Features.Get<IReverseProxyFeature>();
        RouteConfig? routeConfig = proxyFeature?.Route.Config;

        if (!ShouldInspectRoute(routeConfig))
        {
            await next(context);
            return;
        }

        PromptPolicy policy = policyProvider.GetPolicyForRoute(routeConfig);

        string body = await ReadRequestBodyAsync(context.Request, ct);
        PromptInspectionMeta meta = CreateMeta(context, routeConfig);

        if (!promptExtractorResolver.TryExtractPrompt(routeConfig, body, out var promptText))
        {
            await WriteMisconfiguredResponseAsync(context, ct);
            return;
        }

        PromptInspectionResponse piResponse = await promptInspectionClient.InspectAsync(promptText, meta, ct);

        // Always log findings (avoid logging snippets if you consider them sensitive)
        logger.LogInformation(
            "Prompt inspection: route={RouteId} policy={PolicyId} findings={FindingCount}",
            routeConfig?.RouteId, policy.Id, piResponse.Findings.Count);

        PolicyActionEnum action = policyEvaluator.Evaluate(policy, piResponse.Findings);

        if (action == PolicyActionEnum.Block)
        {
            await WriteBlockedResponseAsync(context, piResponse, policy, ct);
            return;
        }

        if (action == PolicyActionEnum.Confirm)
        {
            ConfirmTokenRequest confirmRequest = BuildConfirmRequest(policy.Id, routeConfig?.RouteId, context, body, promptText);

            if (context.Request.Headers.TryGetValue(ConfirmHeader, out var tokenValues))
            {
                string token = tokenValues.ToString();
                if (!confirmTokenService.TryConsumeToken(token, confirmRequest))
                {
                    await WriteInvalidConfirmTokenAsync(context, ct);
                    return;
                }

                // Token valid => proceed
                context.Response.Headers[DecisionHeader] = "allow";
                await next(context);
                return;
            }

            // No token => issue one
            TimeSpan ttl = TimeSpan.FromSeconds(policy.Confirm.TtlSeconds);
            string tokenToReturn = confirmTokenService.IssueToken(confirmRequest, ttl);

            await WriteConfirmationRequiredAsync(context, piResponse, policy, tokenToReturn, ttl, ct);
            return;
        }

        // Allow
        context.Response.Headers[DecisionHeader] = "allow";
        await next(context);
    }

    private static ConfirmTokenRequest BuildConfirmRequest(
        string policyId,
        string? routeId,
        HttpContext ctx,
        string body,
        string prompt)
    {
        // Bind token to exact request (body + prompt) to prevent “confirm token reuse on different prompt”
        string bodyHash = Sha256Base64Url(body);
        string promptHash = Sha256Base64Url(prompt);
        string? userId = ctx.User.Identity?.Name; // null if anonymous

        return new ConfirmTokenRequest(policyId, routeId, userId, bodyHash, promptHash);
    }

    private static string Sha256Base64Url(string value)
    {
        byte[] bytes = Encoding.UTF8.GetBytes(value);
        byte[] hash = SHA256.HashData(bytes);
        return Convert.ToBase64String(hash).TrimEnd('=').Replace('+', '-').Replace('/', '_');
    }

    private static bool ShouldInspectRoute(RouteConfig? routeConfig)
        => routeConfig?.Metadata?.TryGetValue("InspectPrompt", out var v) == true
           && string.Equals(v, "true", StringComparison.OrdinalIgnoreCase);

    private static async Task<string> ReadRequestBodyAsync(HttpRequest request, CancellationToken ct)
    {
        request.EnableBuffering();
        using var reader = new StreamReader(request.Body, Encoding.UTF8, leaveOpen: true);
        string body = await reader.ReadToEndAsync(ct).ConfigureAwait(false);
        request.Body.Position = 0;
        return body;
    }

    private static PromptInspectionMeta CreateMeta(HttpContext context, RouteConfig? routeConfig) =>
        new()
        {
            UserId = context.User.Identity?.Name,
            Source = routeConfig?.RouteId
        };

    private static async Task WriteBlockedResponseAsync(
        HttpContext context,
        PromptInspectionResponse piResponse,
        PromptPolicy policy,
        CancellationToken ct)
    {
        var problem = new ProblemDetails
        {
            Status = StatusCodes.Status403Forbidden,
            Title = "Request blocked by policy",
            Type = "https://aegis-gateway/errors/policy-blocked",
            Detail = $"Blocked by policy '{policy.Id}'.",
            Instance = context.Request.Path
        };

        problem.Extensions["policyId"] = policy.Id;
        problem.Extensions["decision"] = "block";
        problem.Extensions["findings"] = piResponse.Findings;

        context.Response.Headers["Cache-Control"] = "no-store";
        context.Response.Headers[DecisionHeader] = "block";
        context.Response.StatusCode = problem.Status.Value;
        context.Response.ContentType = "application/problem+json";
        await context.Response.WriteAsJsonAsync(problem, ct);
    }

    private static async Task WriteConfirmationRequiredAsync(
        HttpContext context,
        PromptInspectionResponse piResponse,
        PromptPolicy policy,
        string token,
        TimeSpan ttl,
        CancellationToken ct)
    {
        var problem = new ProblemDetails
        {
            Status = StatusCodes.Status428PreconditionRequired,
            Title = "Confirmation required",
            Type = "https://aegis-gateway/errors/confirmation-required",
            Detail = $"Policy '{policy.Id}' requires confirmation before forwarding.",
            Instance = context.Request.Path
        };

        problem.Extensions["policyId"] = policy.Id;
        problem.Extensions["decision"] = "confirm";
        problem.Extensions["confirmTtlSeconds"] = (int)ttl.TotalSeconds;
        problem.Extensions["findings"] = piResponse.Findings;

        // Return token in header (and optionally also in body)
        context.Response.Headers[ConfirmHeader] = token;
        context.Response.Headers[DecisionHeader] = "confirm";
        context.Response.Headers["Cache-Control"] = "no-store";

        context.Response.StatusCode = problem.Status.Value;
        context.Response.ContentType = "application/problem+json";
        await context.Response.WriteAsJsonAsync(problem, ct);
    }

    private static async Task WriteInvalidConfirmTokenAsync(HttpContext context, CancellationToken ct)
    {
        var problem = new ProblemDetails
        {
            Status = StatusCodes.Status400BadRequest,
            Title = "Invalid confirmation token",
            Type = "https://aegis-gateway/errors/invalid-confirm-token",
            Detail = "The confirmation token is missing, expired, already used, or does not match this request.",
            Instance = context.Request.Path
        };

        context.Response.Headers["Cache-Control"] = "no-store";
        context.Response.Headers[DecisionHeader] = "confirm";
        context.Response.StatusCode = problem.Status.Value;
        context.Response.ContentType = "application/problem+json";
        await context.Response.WriteAsJsonAsync(problem, ct);
    }

    private static async Task WriteMisconfiguredResponseAsync(HttpContext context, CancellationToken ct)
    {
        var problem = new ProblemDetails
        {
            Status = StatusCodes.Status500InternalServerError,
            Title = "Prompt inspection misconfigured",
            Detail = "Prompt inspection is enabled for this route, but the gateway could not extract the prompt.",
            Type = "https://aegis-gateway/errors/prompt-extraction-failed",
            Instance = context.Request.Path
        };

        context.Response.Headers["Cache-Control"] = "no-store";
        context.Response.StatusCode = problem.Status.Value;
        context.Response.ContentType = "application/problem+json";
        await context.Response.WriteAsJsonAsync(problem, ct);
    }
}