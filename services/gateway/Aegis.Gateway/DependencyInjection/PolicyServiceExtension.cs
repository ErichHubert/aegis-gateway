using Aegis.Gateway.Models;
using Aegis.Gateway.Services;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;

namespace Aegis.Gateway.DependencyInjection;

public static class PolicyServiceExtensions
{
    public static IServiceCollection AddPolicyService(
        this IServiceCollection services,
        IConfiguration configuration)
    {
        services.AddOptions<PolicyOptions>()
            .Bind(configuration.GetSection("Policies"))
            .ValidateDataAnnotations();

        services.AddSingleton<IPolicyProvider, PolicyProvider>();
        services.AddSingleton<IPolicyEvaluator, PolicyEvaluator>();

        return services;
    }
}