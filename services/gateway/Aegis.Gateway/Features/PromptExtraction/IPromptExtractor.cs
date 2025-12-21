namespace Aegis.Gateway.Features.PromptExtraction;

public interface IPromptExtractor
{
    string Name { get; }
    bool TryExtract(string body, out string prompt);
}