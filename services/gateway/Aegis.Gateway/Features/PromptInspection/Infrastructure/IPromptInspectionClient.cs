using Aegis.Gateway.Features.PromptInspection.Contracts;

namespace Aegis.Gateway.Features.PromptInspection.Infrastructure;

public interface IPromptInspectionClient
{
    Task<PromptInspectionResponse> InspectAsync(
        string prompt, 
        PromptInspectionMeta? meta = null,  
        CancellationToken ct = default
        );
}