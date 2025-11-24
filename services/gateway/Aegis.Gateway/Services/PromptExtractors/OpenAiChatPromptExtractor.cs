namespace Aegis.Gateway.Services.PromptExtractors;

using System.Text.Json;

public sealed class OpenAiChatPromptExtractor : IPromptExtractor
{
    public string Name => "openai-chat";

    public string Extract(string json)
    {
        if (string.IsNullOrWhiteSpace(json))
            return json;

        try
        {
            using var doc = JsonDocument.Parse(json);
            var root = doc.RootElement;

            if (root.TryGetProperty("messages", out var messages) &&
                messages.ValueKind == JsonValueKind.Array)
            {
                var last = messages.EnumerateArray().LastOrDefault();
                if (last.ValueKind == JsonValueKind.Object &&
                    last.TryGetProperty("content", out var contentProp) &&
                    contentProp.ValueKind == JsonValueKind.String)
                {
                    return contentProp.GetString() ?? json;
                }
            }

            return json;
        }
        catch
        {
            return json;
        }
    }
}