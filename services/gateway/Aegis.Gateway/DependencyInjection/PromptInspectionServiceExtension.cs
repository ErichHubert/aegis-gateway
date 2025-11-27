using Aegis.Gateway.Infrastructure.PromptInspection;
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

        return services;
    }
}