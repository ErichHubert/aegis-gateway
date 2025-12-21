using System.Text.Json.Serialization;

namespace Aegis.Gateway.Features.PromptInspection.Contracts;

public sealed record PromptInspectionResponse
{
    [JsonPropertyName("findings")]
    public List<PromptInspectionFinding> Findings { get; init; } = [];
}

