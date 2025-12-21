using Aegis.Gateway.Features.PromptExtraction;
using Aegis.Gateway.Features.PromptExtraction.Extractors;
using Aegis.Gateway.Services;

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