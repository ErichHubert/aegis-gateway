using System.Text;
using System.Text.Json;
using Aegis.Gateway.Models;

namespace Aegis.Gateway.Services;

public sealed class PromptInspectionClient(
    HttpClient httpClient,
    ILogger<PromptInspectionClient> logger
    ) : IPromptInspectionClient
{
    public async Task<PromptInspectionResponse> InspectAsync(
        string prompt, 
        PromptInspectionMeta? meta = null, 
        CancellationToken ct = default
        )
    {
        var payload = new PromptInspectionRequest() {Prompt = prompt, Meta = meta };

        using var content = new StringContent(
            JsonSerializer.Serialize(payload, JsonSerializerOptions.Web),
            Encoding.UTF8,
            "application/json");
        
        logger.LogInformation("Sending inspection request to Prompt Inspection Service");
        using var response = await httpClient.PostAsync("/inspect", content, ct);
        response.EnsureSuccessStatusCode();

        var result = await response.Content.ReadFromJsonAsync<PromptInspectionResponse>(ct);

        if (result is null)
            throw new InvalidOperationException("Prompt Inspection Service returned null");

        return result;
    }
}