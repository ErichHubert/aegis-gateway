using System.Text;
using System.Text.Json;
using Aegis.Gateway.Models;
using Aegis.Gateway.Services;
using Yarp.ReverseProxy.Configuration;
using Yarp.ReverseProxy.Model;

namespace Aegis.Gateway.Middleware;

public sealed class PromptInspectionStep(
    RequestDelegate next, 
    IPromptInspectionClient promptInspectionClient,
    ILogger<PromptInspectionStep> logger,
    CancellationToken ct = default)
{
    public async Task InvokeAsync(HttpContext context)
    {
        logger.LogInformation("Prompt inspection started");

        var proxyFeature = context.Features.Get<IReverseProxyFeature>();
        var routeConfig = proxyFeature?.Route.Config;
        
        if(!ShouldInspectRoute(routeConfig))
        {
            logger.LogInformation("Prompt inspection is disabled for provided route. Prompt inspection skipped.");
            await next(context);
            return;
        } 
        
        context.Request.EnableBuffering();

        string body;
        using (var reader = new StreamReader(context.Request.Body, Encoding.UTF8, leaveOpen: true))
        {
            body = await reader.ReadToEndAsync(ct);
        }

        context.Request.Body.Position = 0;

        var promptText = ExtractPromptFromOllamaRequest(body);

        var meta = new PromptInspectionMeta
        {
            UserId = context.User.Identity?.Name,
            Source = routeConfig?.RouteId 
        };

        PromptInspectionResponse promptInspectionResponse;
        try
        {
            promptInspectionResponse = await promptInspectionClient.InspectAsync(promptText, meta, ct);
        }
        catch (Exception ex)
        {
            logger.LogError(ex, "Error calling Prompt Inspection service");
            context.Response.StatusCode = StatusCodes.Status502BadGateway;
            await context.Response.WriteAsJsonAsync(new { error = "Error calling Prompt Inspection service" }, ct);
            return;
        }

        if (!promptInspectionResponse.IsAllowed)
        {
            context.Response.StatusCode = StatusCodes.Status403Forbidden;
            await context.Response.WriteAsJsonAsync(new
            {
                error = "Request blocked by policy",
                findings = promptInspectionResponse.Findings
            }, ct);
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
    
    private static string ExtractPromptFromOllamaRequest(string json)
    {
        if (string.IsNullOrWhiteSpace(json))
            return json;

        try
        {
            using var doc = JsonDocument.Parse(json);
            var root = doc.RootElement;

            if (root.TryGetProperty("prompt", out var promptProp) &&
                promptProp.ValueKind == JsonValueKind.String)
            {
                return promptProp.GetString() ?? json;
            }

            return json;
        }
        catch
        {
            // If anything goes wrong, just return the raw JSON
            return json;
        }
    }
}