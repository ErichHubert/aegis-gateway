using System.Text.Json.Serialization;

namespace Aegis.Gateway.Models;

public sealed class PromptInspectionResponse
{
    [JsonPropertyName("findings")]
    public List<PromptInspectionFinding> Findings { get; set; } = [];
}

