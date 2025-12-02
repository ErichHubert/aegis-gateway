using Aegis.Gateway.Infrastructure.PromptInspection;
using Microsoft.AspNetCore.Diagnostics.HealthChecks;
using Microsoft.Extensions.Diagnostics.HealthChecks;
using Microsoft.Extensions.Options;

namespace Aegis.Gateway.DependencyInjection;

public static class PromptInspectionServiceExtension
{
    public static IServiceCollection AddPromptInspectionService(this IServiceCollection services)
    {
        services.AddScoped<IPromptInspectionClient, PromptInspectionClient>();
        services.AddHttpClient<IPromptInspectionClient, PromptInspectionClient>((context, client) =>
        {
            PromptInspectionSettings settings = context.GetRequiredService<IOptions<PromptInspectionSettings>>().Value;
    
            client.BaseAddress = new Uri(settings.BaseAddress);
            client.Timeout = TimeSpan.FromSeconds(settings.TimeoutSeconds);
        });
        
        services
            .AddHealthChecks()
            .AddCheck(
                "self",
                () => HealthCheckResult.Healthy(),
                tags: ["live"])
            .AddCheck<PromptInspectionHealthCheck>(
                "inspection-service",
                tags: ["ready"]);
        
        return services;
    }
    
    public static IEndpointRouteBuilder MapPromptInspectionHealthChecks(this IEndpointRouteBuilder endpoints)
    {
        endpoints.MapHealthChecks("/health/live", new HealthCheckOptions
        {
            Predicate = r => r.Tags.Contains("live")
        });

        endpoints.MapHealthChecks("/health/ready", new HealthCheckOptions
        {
            Predicate = r => r.Tags.Contains("ready")
        });

        return endpoints;
    }
}