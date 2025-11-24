namespace Aegis.Gateway.Services.PromptExtractors;

using System.Text.Json;

public sealed class OllamaPromptExtractor : IPromptExtractor
{
    public string Name => "ollama";

    public string Extract(string json)
    {
        if (string.IsNullOrWhiteSpace(json))
            return json;

        try
        {
            using var doc = JsonDocument.Parse(json);
            var root = doc.RootElement;

            if (root.TryGetProperty("prompt", out var promptProp) &&
                promptProp.ValueKind == JsonValueKind.String)
            {
                return promptProp.GetString() ?? json;
            }

            return json;
        }
        catch
        {
            return json;
        }
    }
}