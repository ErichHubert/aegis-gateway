namespace Aegis.Gateway.Models.Policy;

public sealed record ConfirmOptions
{
    public int TtlSeconds { get; init; } = 120;
}