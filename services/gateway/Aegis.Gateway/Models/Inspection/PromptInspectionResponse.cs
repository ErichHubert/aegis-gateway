using System.Text.Json.Serialization;

namespace Aegis.Gateway.Models.Inspection;

public sealed class PromptInspectionResponse
{
    [JsonPropertyName("findings")]
    public List<PromptInspectionFinding> Findings { get; set; } = [];
}

