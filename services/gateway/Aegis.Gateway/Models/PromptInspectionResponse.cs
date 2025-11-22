using System.Text.Json.Serialization;

namespace Aegis.Gateway.Models;

public sealed class PromptInspectionResponse
{
    [JsonPropertyName("isAllowed")]
    public bool IsAllowed { get; set; } = false; 

    [JsonPropertyName("findings")]
    public List<PromptInspectionFinding> Findings { get; set; } = [];
}

