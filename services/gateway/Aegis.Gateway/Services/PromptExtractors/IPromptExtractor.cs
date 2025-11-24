namespace Aegis.Gateway.Services.PromptExtractors;

public interface IPromptExtractor
{
    /// <summary>
    /// Name used in YARP metadata, e.g. "ollama", "openai-chat".
    /// </summary>
    string Name { get; }

    /// <summary>
    /// Extracts the prompt text from the given request body.
    /// Should fall back to the input JSON if extraction fails.
    /// </summary>
    string Extract(string body);
}