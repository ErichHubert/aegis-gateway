using Aegis.Gateway.Services;
using Aegis.Gateway.Services.PromptExtractors;

namespace Aegis.Gateway.Extensions;

public static class PromptExtractionServiceExtension
{
    public static IServiceCollection AddPromptExtractionService(this IServiceCollection services)
    {
        services.AddSingleton<IPromptExtractor, OllamaPromptExtractor>();
        services.AddSingleton<IPromptExtractor, OpenAiChatPromptExtractor>();
        services.AddSingleton<IPromptExtractorResolver, PromptExtractorResolver>();

        return services;
    }
}