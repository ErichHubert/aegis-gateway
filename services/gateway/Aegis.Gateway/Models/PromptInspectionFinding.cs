using System.Text.Json.Serialization;

namespace Aegis.Gateway.Models;

public sealed class PromptInspectionFinding
{
    [JsonPropertyName("type")]
    public string Type { get; set; } = string.Empty;

    [JsonPropertyName("start")]
    public int Start { get; set; }

    [JsonPropertyName("end")]
    public int End { get; set; }

    [JsonPropertyName("snippet")]
    public string? Snippet { get; set; }
}