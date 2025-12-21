using System.Text.Json.Serialization;

namespace Aegis.Gateway.Features.PromptInspection.Contracts;

public sealed class PromptInspectionRequest
{
    [JsonPropertyName("prompt")]        
    public string Prompt { get; set; } = string.Empty;

    [JsonPropertyName("meta")]
    public PromptInspectionMeta? Meta { get; set; } = new();
}