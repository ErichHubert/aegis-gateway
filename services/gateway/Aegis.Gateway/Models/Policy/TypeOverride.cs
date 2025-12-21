namespace Aegis.Gateway.Models.Policy;

public sealed record TypeOverride
{
    public PolicyActionEnum Action { get; init; }
}