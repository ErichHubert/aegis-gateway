using Aegis.Gateway.Features.Policy.Models;

namespace Aegis.Gateway.Features.Policy;

public sealed class PolicyOptions
{
    public Dictionary<string, PromptPolicy> Policies { get; init; } = new(StringComparer.OrdinalIgnoreCase);
}