using Aegis.Gateway.Features.Policy;

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

        services.AddSingleton<IPolicyProvider, PolicyProvider>();
        services.AddSingleton<IPolicyEvaluator, PolicyEvaluator>();

        return services;
    }
}