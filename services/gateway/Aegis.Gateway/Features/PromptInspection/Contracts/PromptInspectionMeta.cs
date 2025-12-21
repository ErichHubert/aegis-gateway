using System.Text.Json.Serialization;

namespace Aegis.Gateway.Features.PromptInspection.Contracts;

public class PromptInspectionMeta
{
    [JsonPropertyName("userId")]
    public string? UserId { get; set; }
    public string? Source { get; set; }
}