using System.Text;
using System.Text.Json;
using Aegis.Gateway.Infrastructure.PromptInspection;
using Aegis.Gateway.Models;
using Aegis.Gateway.Services;
using Microsoft.AspNetCore.Mvc;
using Yarp.ReverseProxy.Configuration;
using Yarp.ReverseProxy.Model;

namespace Aegis.Gateway.Middleware;

public sealed class PromptInspectionStep(
    RequestDelegate next,
    IPromptInspectionClient promptInspectionClient,
    IPromptExtractorResolver promptExtractorResolver,
    ILogger<PromptInspectionStep> logger)
{
    public async Task InvokeAsync(HttpContext context)
    {
        var ct = context.RequestAborted;

        var proxyFeature = context.Features.Get<IReverseProxyFeature>();
        var routeConfig = proxyFeature?.Route.Config;

        if (!ShouldInspectRoute(routeConfig))
        {
            logger.LogDebug("Prompt inspection disabled for route {RouteId}. Skipping.", routeConfig?.RouteId);
            await next(context);
            return;
        }

        logger.LogInformation("Prompt inspection started for route {RouteId}", routeConfig?.RouteId);

        var body = await ReadRequestBodyAsync(context.Request, ct);
        var promptText = promptExtractorResolver.ExtractPrompt(routeConfig, body);
        var meta = CreateMeta(context, routeConfig);

        var piResponse = await promptInspectionClient.InspectAsync(promptText, meta, ct);

        if (!piResponse.IsAllowed)
        {
            await WriteBlockedResponseAsync(context, piResponse, ct);
            return;
        }

        await next(context);
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

    private async Task WriteBlockedResponseAsync(
        HttpContext context,
        PromptInspectionResponse piResponse,
        CancellationToken ct)
    {
        var problem = new ProblemDetails
        {
            Status = StatusCodes.Status403Forbidden,
            Title = "Request blocked by policy",
            Type = "https://aegis-gateway/errors/prompt-blocked",
            Detail = "The request was blocked based on LLM safety and data loss prevention rules.",
            Instance = context.Request.Path,
            Extensions =
            {
                ["findings"] = piResponse.Findings
            }
        };

        context.Response.StatusCode = problem.Status ?? StatusCodes.Status403Forbidden;
        context.Response.ContentType = "application/problem+json";

        await context.Response.WriteAsJsonAsync(problem, ct);
    }
}