using Yarp.ReverseProxy.Configuration;

namespace Aegis.Gateway.Services;

public interface IPromptExtractorResolver
{
    bool TryExtractPrompt(RouteConfig? routeConfig, string body, out string prompt);
}