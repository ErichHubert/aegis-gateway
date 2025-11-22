using Aegis.Gateway.Services;
using Microsoft.Extensions.Options;

namespace Aegis.Gateway.Extensions;

public static class PromptInspectionServiceExtension
{
    public static IServiceCollection AddPromptInspectionService(this IServiceCollection services)
    {
        services.AddScoped<IPromptInspectionClient, PromptInspectionClient>();
        services.AddHttpClient<IPromptInspectionClient, PromptInspectionClient>((context, client) =>
        {
            PromptInspectionSettings settings = context.GetRequiredService<IOptions<PromptInspectionSettings>>().Value;
    
            client.BaseAddress = new Uri(settings.BaseUri);
            client.Timeout = TimeSpan.FromSeconds(5);
        });

        return services;
    }
}