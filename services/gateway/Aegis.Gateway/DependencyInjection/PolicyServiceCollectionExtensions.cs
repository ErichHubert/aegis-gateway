using Aegis.Gateway.Features.Policy;
using Aegis.Gateway.Features.Policy.Services;

namespace Aegis.Gateway.DependencyInjection;

public static class PolicyServiceCollectionExtensions
{
    public static IServiceCollection AddPolicyService(
        this IServiceCollection services,
        IConfiguration configuration)
    {
        services.AddOptions<PolicyOptions>()
            .Configure<IConfiguration>((opt, cfg) =>
            {
                cfg.GetSection("Policies").Bind(opt.Policies);
            });
        
        services.AddMemoryCache(o => o.SizeLimit = 10_000);
        services.AddSingleton<IPolicyProvider, PolicyProvider>();
        services.AddSingleton<IPolicyEvaluator, PolicyEvaluator>();
        services.AddSingleton<IConfirmTokenService, ConfirmTokenService>();

        return services;
    }
}