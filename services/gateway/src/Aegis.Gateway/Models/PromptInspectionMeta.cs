using System.Text.Json.Serialization;

namespace Aegis.Gateway.Models;

internal class PromptInspectionMeta
{
    [JsonPropertyName("userId")]
    public string? UserId { get; set; }
}