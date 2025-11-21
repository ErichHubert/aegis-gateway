using Aegis.Gateway.Models;

namespace Aegis.Gateway.Services;

internal interface IPromptInspectionClient
{
    Task<PromptInspectionResponse> InspectAsync(
        string prompt, 
        PromptInspectionMeta? meta = null,  
        CancellationToken ct = default
        );
}