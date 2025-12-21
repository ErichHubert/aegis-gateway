using System.Text;
using Aegis.Gateway.Features.PromptExtraction;
using Aegis.Gateway.Features.PromptInspection.Contracts;
using Aegis.Gateway.Features.PromptInspection.Infrastructure;
using Aegis.Gateway.Models.Policy;
using Aegis.Gateway.Services;
using Aegis.Gateway.Services.Interfaces;
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
    ILogger<PromptInspectionStep> logger)
{
    public async Task InvokeAsync(HttpContext context)
    {
        CancellationToken ct = context.RequestAborted;

        IReverseProxyFeature? proxyFeature = context.Features.Get<IReverseProxyFeature>();
        RouteConfig? routeConfig = proxyFeature?.Route.Config;

        if (!ShouldInspectRoute(routeConfig))
        {
            logger.LogDebug("Prompt inspection disabled for route {RouteId}. Skipping.", routeConfig?.RouteId);
            await next(context);
            return;
        }

        PromptPolicy policy = policyProvider.GetPolicyForRoute(routeConfig);

        logger.LogInformation(
            "Prompt inspection started for route {RouteId} using policy {PolicyId}",
            routeConfig?.RouteId,
            policy.Id);

        string body = await ReadRequestBodyAsync(context.Request, ct);
        PromptInspectionMeta meta = CreateMeta(context, routeConfig);

        if (!promptExtractorResolver.TryExtractPrompt(routeConfig, body, out var promptText))
        {
            logger.LogError(
                "Prompt inspection enabled for route {RouteId}, but no valid PromptFormat/extractor configured. Blocking request.",
                routeConfig?.RouteId);

            await WriteMisconfiguredResponseAsync(context, ct);
            return;
        }

        PromptInspectionResponse piResponse = await promptInspectionClient.InspectAsync(promptText, meta, ct);

        // Always log findings (avoid logging snippets/secrets)
        LogFindings(routeConfig, policy, piResponse.Findings);

        PolicyActionEnum decision = policyEvaluator.Evaluate(policy, piResponse.Findings);

        switch (decision)
        {
            case PolicyActionEnum.Block:
                await WriteDecisionResponseAsync(
                    context,
                    statusCode: StatusCodes.Status403Forbidden,
                    title: "Request blocked by policy",
                    type: "https://aegis-gateway/errors/policy-blocked",
                    detail: $"Blocked by policy '{policy.Id}'.",
                    policy,
                    decision,
                    piResponse,
                    ct);
                return;

            case PolicyActionEnum.Confirm:
                await WriteDecisionResponseAsync(
                    context,
                    statusCode: StatusCodes.Status409Conflict,
                    title: "Confirmation required",
                    type: "https://aegis-gateway/errors/policy-confirm",
                    detail: $"Policy '{policy.Id}' requires confirmation before forwarding.",
                    policy,
                    decision,
                    piResponse,
                    ct);
                return;

            case PolicyActionEnum.Allow:
            default:
                await next(context);
                return;
        }
    }

    private static bool ShouldInspectRoute(RouteConfig? routeConfig)
    {
        if (routeConfig?.Metadata == null)
            return false;

        return routeConfig.Metadata.TryGetValue("InspectPrompt", out var value)
               && string.Equals(value, "true", StringComparison.OrdinalIgnoreCase);
    }

    private static async Task<string> ReadRequestBodyAsync(HttpRequest request, CancellationToken ct)
    {
        request.EnableBuffering();

        using var reader = new StreamReader(request.Body, Encoding.UTF8, leaveOpen: true);
        var body = await reader.ReadToEndAsync(ct).ConfigureAwait(false);

        request.Body.Position = 0;
        return body;
    }

    private static PromptInspectionMeta CreateMeta(HttpContext context, RouteConfig? routeConfig) =>
        new()
        {
            UserId = context.User.Identity?.Name,
            Source = routeConfig?.RouteId
        };

    private void LogFindings(RouteConfig? routeConfig, PromptPolicy policy, IReadOnlyList<PromptInspectionFinding> findings)
    {
        if (findings.Count == 0)
        {
            logger.LogDebug("Prompt inspection found no issues. Route={RouteId} Policy={PolicyId}",
                routeConfig?.RouteId, policy.Id);
            return;
        }

        logger.LogInformation("Prompt inspection findings. Route={RouteId} Policy={PolicyId} Count={Count}",
            routeConfig?.RouteId, policy.Id, findings.Count);

        foreach (var f in findings)
        {
            // Avoid snippet logging (can leak secrets/PII)
            logger.LogDebug("Finding: Type={Type} Severity={Severity} Range=[{Start},{End}] Message={Message}",
                f.Type, f.Severity, f.Start, f.End, f.Message);
        }
    }

    private static async Task WriteDecisionResponseAsync(
        HttpContext context,
        int statusCode,
        string title,
        string type,
        string detail,
        PromptPolicy policy,
        PolicyActionEnum decision,
        PromptInspectionResponse piResponse,
        CancellationToken ct)
    {
        var problem = new ProblemDetails
        {
            Status = statusCode,
            Title = title,
            Type = type,
            Detail = detail,
            Instance = context.Request.Path
        };

        problem.Extensions["policyId"] = policy.Id;
        problem.Extensions["decision"] = decision.ToString().ToLowerInvariant();
        problem.Extensions["findingCount"] = piResponse.Findings.Count;

        if (decision == PolicyActionEnum.Confirm)
            problem.Extensions["confirmTtlSeconds"] = policy.Confirm.TtlSeconds;

        // Return redacted findings (no snippet), but keep positions for UI highlighting
        problem.Extensions["findings"] = RedactFindings(piResponse.Findings);

        context.Response.StatusCode = problem.Status.Value;
        context.Response.ContentType = "application/problem+json";
        await context.Response.WriteAsJsonAsync(problem, ct);
    }

    private static object[] RedactFindings(IReadOnlyList<PromptInspectionFinding> findings)
        => findings.Select(f => new
        {
            type = f.Type,
            severity = f.Severity,
            start = f.Start,
            end = f.End,
            // Do NOT return snippet by default
            // snippet = (string?)null,
            message = f.Message
        }).ToArray<object>();

    private static async Task WriteMisconfiguredResponseAsync(
        HttpContext context,
        CancellationToken ct)
    {
        var problem = new ProblemDetails
        {
            Status = StatusCodes.Status500InternalServerError,
            Title = "Prompt inspection misconfigured",
            Detail = "Prompt inspection is enabled for this route, but the gateway could not extract the prompt.",
            Type = "https://aegis-gateway/errors/prompt-extraction-failed",
            Instance = context.Request.Path
        };

        context.Response.StatusCode = problem.Status.Value;
        context.Response.ContentType = "application/problem+json";
        await context.Response.WriteAsJsonAsync(problem, ct);
    }
}