using Aegis.Gateway.Services.PromptExtractors;
using Yarp.ReverseProxy.Configuration;

namespace Aegis.Gateway.Services;

public sealed class PromptExtractorResolver(
    IEnumerable<IPromptExtractor> extractors
    ) : IPromptExtractorResolver
{
    private readonly IReadOnlyDictionary<string, IPromptExtractor> _extractors = extractors.ToDictionary(
        x => x.Name, StringComparer.OrdinalIgnoreCase);

    public bool TryExtractPrompt(RouteConfig? routeConfig, string body, out string prompt)
    {
        prompt = string.Empty; 

        string? format = routeConfig?.Metadata?.GetValueOrDefault("PromptFormat");
        if (format is null)
            return false;

        if (!_extractors.TryGetValue(format, out var extractor))
            return false;

        prompt = extractor.Extract(body);
        return true;
    }
}