namespace Aegis.Gateway.Services.PromptExtractors;

public interface IPromptExtractor
{
    string Name { get; }
    bool TryExtract(string body, out string prompt);
}