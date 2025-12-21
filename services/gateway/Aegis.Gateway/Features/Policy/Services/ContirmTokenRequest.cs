namespace Aegis.Gateway.Features.Policy.Services;

public sealed record ConfirmTokenRequest(
    string PolicyId,
    string? RouteId,
    string? UserId,
    string BodyHash,
    string PromptHash);