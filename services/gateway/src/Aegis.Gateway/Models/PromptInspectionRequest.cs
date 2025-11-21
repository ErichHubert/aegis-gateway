using System.Text.Json.Serialization;

namespace Aegis.Gateway.Models;

internal sealed class PromptInspectionRequest
{
    [JsonPropertyName("text")]
    public string Text { get; set; } = string.Empty;

    [JsonPropertyName("meta")]
    public PromptInspectionMeta Meta { get; set; } = new();
}