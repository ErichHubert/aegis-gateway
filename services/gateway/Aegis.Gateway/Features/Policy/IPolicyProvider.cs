using Aegis.Gateway.Features.Policy.Models;

namespace Aegis.Gateway.Features.Policy;

public interface IPolicyProvider
{
    PromptPolicy GetPolicyForRoute(Yarp.ReverseProxy.Configuration.RouteConfig? route);
}