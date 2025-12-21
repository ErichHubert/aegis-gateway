using System.Text.Json.Serialization;

namespace Aegis.Gateway.Features.PromptInspection.Contracts;

public sealed record PromptInspectionFinding
{
    [JsonPropertyName("type")]
    public string Type { get; init; } = string.Empty;

    [JsonPropertyName("start")]
    public int Start { get; init; }

    [JsonPropertyName("end")]
    public int End { get; init; }

    [JsonPropertyName("snippet")]
    public string? Snippet { get; init; }
    
    [JsonPropertyName("message")]
    public string? Message { get; init; }
    
    [JsonPropertyName("severity")]
    public string Severity { get; init; } = string.Empty;
    
    [JsonPropertyName("confidence")]
    public float Confidence { get; init; }
}