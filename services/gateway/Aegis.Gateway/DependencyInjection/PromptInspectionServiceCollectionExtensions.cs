using Aegis.Gateway.Features.PromptInspection.Infrastructure;
using Microsoft.AspNetCore.Diagnostics.HealthChecks;
using Microsoft.Extensions.Diagnostics.HealthChecks;
using Microsoft.Extensions.Options;

namespace Aegis.Gateway.DependencyInjection;

public static class PromptInspectionServiceCollectionExtensions
{
    public static IServiceCollection AddPromptInspectionService(this IServiceCollection services)
    {
        services.AddScoped<IPromptInspectionClient, PromptInspectionClient>();
        services.AddHttpClient<IPromptInspectionClient, PromptInspectionClient>((context, client) =>
        {
            PromptInspectionOptions options = context.GetRequiredService<IOptions<PromptInspectionOptions>>().Value;
    
            client.BaseAddress = new Uri(options.BaseAddress);
            client.Timeout = TimeSpan.FromSeconds(options.TimeoutSeconds);
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