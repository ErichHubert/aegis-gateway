using Aegis.Gateway.Models;
using Aegis.Gateway.Models.Policy;
using Microsoft.Extensions.Options;
using Yarp.ReverseProxy.Configuration;

namespace Aegis.Gateway.Services;

public sealed class PolicyProvider(IOptionsMonitor<PolicyOptions> options) : IPolicyProvider
{
    public PromptPolicy GetPolicyForRoute(RouteConfig? route)
    {
        var policyId = route?.Metadata?.GetValueOrDefault("PolicyId")?.Trim();

        if (string.IsNullOrWhiteSpace(policyId))
            policyId = PromptPolicy.DefaultId;

        if (options.CurrentValue.Policies.TryGetValue(policyId, out var policy))
        {
            // Return a copy with the Id set
            return policy with { Id = policyId };
        }

        // Fallback: return a default policy
        return new PromptPolicy { Id = policyId };
    }
}

public sealed class PolicyOptions
{
    public Dictionary<string, PromptPolicy> Policies { get; init; } = new(StringComparer.OrdinalIgnoreCase);
}