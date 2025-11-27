namespace Aegis.Gateway.Infrastructure.PromptInspection;

public sealed record PromptInspectionSettings
{
    public string BaseAddress { get; set; } = string.Empty;
    public int TimeoutSeconds { get; set; } = 10;
}