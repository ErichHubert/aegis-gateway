namespace Aegis.Gateway.Features.Policy.Models;

public sealed record ConfirmOptions
{
    public int TtlSeconds { get; init; } = 120;
}