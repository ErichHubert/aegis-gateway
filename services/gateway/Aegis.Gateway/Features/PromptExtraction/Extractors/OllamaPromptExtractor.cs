using System.Text.Json;

namespace Aegis.Gateway.Features.PromptExtraction.Extractors;

public sealed class OllamaPromptExtractor(
    ILogger<OllamaPromptExtractor> logger
    ): IPromptExtractor
{
    /// <summary>
    /// Name used in YARP route metadata, e.g.:
    /// "Metadata": { "PromptFormat": "ollama }
    /// </summary>
    public string Name => "ollama";

    /// <summary>
    /// Tries to extract the effective user prompt from an Ollama completion-style
    /// request body.
    ///
    /// Expects JSON of the form:
    /// {
    ///   "model": "llama3",
    ///   "prompt": "actual user prompt"
    /// }
    /// </summary>
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