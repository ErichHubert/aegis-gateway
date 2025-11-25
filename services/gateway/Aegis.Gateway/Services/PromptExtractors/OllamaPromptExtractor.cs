namespace Aegis.Gateway.Services.PromptExtractors;

using System.Text.Json;

public sealed class OllamaPromptExtractor(
    ILogger<OllamaPromptExtractor> logger
    ): IPromptExtractor
{
    public string Name => "ollama";

    public bool TryExtract(string json, out string prompt)
    {
        prompt = string.Empty;

        if (string.IsNullOrWhiteSpace(json))
            return false;

        try
        {
            using JsonDocument doc = JsonDocument.Parse(json);
            JsonElement root = doc.RootElement;

            if (!root.TryGetProperty("prompt", out var promptProp)) 
                return false;
            
            if (promptProp.ValueKind != JsonValueKind.String)
                return false;
            
            string? value = promptProp.GetString();
            if (string.IsNullOrWhiteSpace(value))
                return false;

            prompt = value;
            return true;
        }
        catch (Exception ex)
        {
            logger.LogWarning(ex, "Failed to extract prompt from Ollama request.");
            return false;
        }
    }
}