using Aegis.Gateway.Models;
using Aegis.Gateway.Models.Inspection;

namespace Aegis.Gateway.Infrastructure.PromptInspection;

public interface IPromptInspectionClient
{
    Task<PromptInspectionResponse> InspectAsync(
        string prompt, 
        PromptInspectionMeta? meta = null,  
        CancellationToken ct = default
        );
}