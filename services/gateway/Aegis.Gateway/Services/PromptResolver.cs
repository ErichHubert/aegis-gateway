using Aegis.Gateway.Services.PromptExtractors;
using Yarp.ReverseProxy.Configuration;

namespace Aegis.Gateway.Services;

public sealed class PromptExtractorResolver(
    IEnumerable<IPromptExtractor> extractors
    ) : IPromptExtractorResolver
{
    private readonly IReadOnlyDictionary<string, IPromptExtractor> _extractors = extractors.ToDictionary(
        x => x.Name, StringComparer.OrdinalIgnoreCase);
    private readonly IPromptExtractor _fallbackExtractor = new RawPromptExtractor();

    public string ExtractPrompt(RouteConfig? routeConfig, string body)
    {
        var format = routeConfig?.Metadata?.GetValueOrDefault("PromptFormat");

        if (format is not null && _extractors.TryGetValue(format, out var extractor))
        {
            return extractor.Extract(body);
        }
        
        return _fallbackExtractor.Extract(body);
    }

    private sealed class RawPromptExtractor : IPromptExtractor
    {
        public string Name => "raw";
        public string Extract(string body) => body;
    }
}