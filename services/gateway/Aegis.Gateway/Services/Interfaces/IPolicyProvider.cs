using Aegis.Gateway.Models.Policy;

namespace Aegis.Gateway.Services;

using Aegis.Gateway.Models;

public interface IPolicyProvider
{
    PromptPolicy GetPolicyForRoute(Yarp.ReverseProxy.Configuration.RouteConfig? route);
}