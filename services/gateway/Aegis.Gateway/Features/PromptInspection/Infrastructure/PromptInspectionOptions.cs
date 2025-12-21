namespace Aegis.Gateway.Features.PromptInspection.Infrastructure;

public sealed record PromptInspectionOptions
{
    public string BaseAddress { get; set; } = string.Empty;
    public int TimeoutSeconds { get; set; } = 10;
}