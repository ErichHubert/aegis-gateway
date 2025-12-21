namespace Aegis.Gateway.Features.Policy.Models;

public sealed record TypeOverride
{
    public PolicyActionEnum Action { get; init; }
}