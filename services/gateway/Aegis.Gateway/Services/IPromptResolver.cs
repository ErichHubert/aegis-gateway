using Yarp.ReverseProxy.Configuration;

namespace Aegis.Gateway.Services;

public interface IPromptExtractorResolver
{
    string ExtractPrompt(RouteConfig? routeConfig, string body);
}