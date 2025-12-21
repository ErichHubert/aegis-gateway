using Yarp.ReverseProxy.Configuration;

namespace Aegis.Gateway.Features.PromptExtraction;

public interface IPromptExtractorResolver
{
    bool TryExtractPrompt(RouteConfig? routeConfig, string body, out string prompt);
}