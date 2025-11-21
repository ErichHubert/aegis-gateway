using Yarp.ReverseProxy.Configuration;
using Yarp.ReverseProxy.Model;

namespace Aegis.Gateway.Middleware;

public sealed class PromptInspectionMiddleware(RequestDelegate next, ILogger<PromptInspectionMiddleware> logger)
{
    public async Task InvokeAsync(HttpContext context)
    {
        logger.LogInformation("Prompt inspection started");

        IReverseProxyFeature? proxyFeature = context.Features.Get<IReverseProxyFeature>();
        RouteConfig? routeConfig = proxyFeature?.Route?.Config;
        
        if (routeConfig?.Metadata == null ||
            !routeConfig.Metadata.TryGetValue("InspectPrompt", out var inspectValue) ||
            !string.Equals(inspectValue, "true", StringComparison.OrdinalIgnoreCase))
        {
            logger.LogInformation("Prompt inspection is disabled for provided route. Prompt inspection skipped.");
            await next(context);
        }
        
        
    }
}