using Aegis.Gateway.Services;
using Aegis.Gateway.Services.PromptExtractors;

namespace Aegis.Gateway.DependencyInjection;

public static class PromptExtractionServiceCollectionExtension
{
    public static IServiceCollection AddPromptExtractionService(this IServiceCollection services)
    {
        services.AddSingleton<IPromptExtractor, OllamaPromptExtractor>();
        services.AddSingleton<IPromptExtractorResolver, PromptExtractorResolver>();

        return services;
    }
}