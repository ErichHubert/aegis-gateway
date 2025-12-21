using System.Net;
using Microsoft.Extensions.Diagnostics.HealthChecks;
using Microsoft.Extensions.Options;

namespace Aegis.Gateway.Features.PromptInspection.Infrastructure;

public class PromptInspectionHealthCheck(
    IHttpClientFactory httpClientFactory,
    IOptions<PromptInspectionOptions> options)
    : IHealthCheck
{
    private readonly PromptInspectionOptions _options = options.Value;

    public async Task<HealthCheckResult> CheckHealthAsync(
        HealthCheckContext context,
        CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrWhiteSpace(_options.BaseAddress))
        {
            return HealthCheckResult.Unhealthy("PromptInspectionService BaseAddress is not configured.");
        }

        try
        {
            var client = httpClientFactory.CreateClient("inspection-health");
            client.BaseAddress = new Uri(_options.BaseAddress);

            using var response = await client.GetAsync("/health/ready", cancellationToken);

            if (response.StatusCode == HttpStatusCode.OK)
                return HealthCheckResult.Healthy("Prompt Inspection service reachable.");

            return HealthCheckResult.Unhealthy($"Prompt Inspection service returned {response.StatusCode}.");
        }
        catch (Exception ex)
        {
            return HealthCheckResult.Unhealthy("Prompt Inspection service unreachable.", ex);
        }
    }
}