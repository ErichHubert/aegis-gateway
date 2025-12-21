using System.Text.Json.Serialization;

namespace Aegis.Gateway.Features.PromptInspection.Contracts;

public record PromptInspectionMeta
{
    [JsonPropertyName("userId")]
    public string? UserId { get; init; }
    public string? Source { get; init; }
}