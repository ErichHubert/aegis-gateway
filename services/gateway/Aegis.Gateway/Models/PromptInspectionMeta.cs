using System.Text.Json.Serialization;

namespace Aegis.Gateway.Models;

public class PromptInspectionMeta
{
    [JsonPropertyName("userId")]
    public string? UserId { get; set; }
}