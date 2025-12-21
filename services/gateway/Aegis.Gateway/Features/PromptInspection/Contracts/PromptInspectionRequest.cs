using System.Text.Json.Serialization;

namespace Aegis.Gateway.Features.PromptInspection.Contracts;

public sealed record PromptInspectionRequest
{
    [JsonPropertyName("prompt")]        
    public string Prompt { get; init; } = string.Empty;

    [JsonPropertyName("meta")]
    public PromptInspectionMeta? Meta { get; init; } = new();
}