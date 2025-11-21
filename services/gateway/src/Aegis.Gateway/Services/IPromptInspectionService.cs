using Aegis.Gateway.Models;

namespace Aegis.Gateway.Services;

internal interface IPromptInspectionService
{
    Task<PromptInspectionResponse> InspectAsync(string prompt,  CancellationToken cancellationToken = default);
}