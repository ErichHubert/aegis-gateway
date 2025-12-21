using Aegis.Gateway.Features.Policy;
using Aegis.Gateway.Features.Policy.Models;
using Microsoft.Extensions.Options;
using Moq;
using Yarp.ReverseProxy.Configuration;

namespace Aegis.Gateway.Tests.Services;

public sealed class PolicyProviderTests
{
    [Fact]
    public void GetPolicyForRoute_WhenRouteIsNull_UsesDefaultPolicyId_AndReturnsConfiguredPolicy()
    {
        // Arrange
        var configured = new PromptPolicy
        {
            Confirm = new ConfirmOptions { TtlSeconds = 999 }
        };

        var policyOptions = new PolicyOptions
        {
            Policies = new Dictionary<string, PromptPolicy>(StringComparer.OrdinalIgnoreCase)
            {
                [PromptPolicy.DefaultId] = configured
            }
        };

        var optionsMonitor = new Mock<IOptionsMonitor<PolicyOptions>>(MockBehavior.Strict);
        optionsMonitor.SetupGet(x => x.CurrentValue).Returns(policyOptions);

        var provider = new PolicyProvider(optionsMonitor.Object);

        // Act
        PromptPolicy result = provider.GetPolicyForRoute(route: null);

        // Assert
        Assert.Equal(PromptPolicy.DefaultId, result.Id);
        Assert.Equal(999, result.Confirm.TtlSeconds);
    }

    [Fact]
    public void GetPolicyForRoute_WhenPolicyIdMissing_UsesDefaultPolicyId_AndReturnsConfiguredPolicy()
    {
        // Arrange
        var configured = new PromptPolicy
        {
            Confirm = new ConfirmOptions { TtlSeconds = 321 }
        };

        var policyOptions = new PolicyOptions
        {
            Policies = new Dictionary<string, PromptPolicy>(StringComparer.OrdinalIgnoreCase)
            {
                [PromptPolicy.DefaultId] = configured
            }
        };

        var optionsMonitor = new Mock<IOptionsMonitor<PolicyOptions>>(MockBehavior.Strict);
        optionsMonitor.SetupGet(x => x.CurrentValue).Returns(policyOptions);

        var provider = new PolicyProvider(optionsMonitor.Object);

        var route = new RouteConfig
        {
            RouteId = "r1",
            ClusterId = "c1",
            Match = new RouteMatch(),
            Metadata = null
        };

        // Act
        PromptPolicy result = provider.GetPolicyForRoute(route);

        // Assert
        Assert.Equal(PromptPolicy.DefaultId, result.Id);
        Assert.Equal(321, result.Confirm.TtlSeconds);
    }

    [Fact]
    public void GetPolicyForRoute_WhenPolicyIdIsPresent_TrimsValue_AndReturnsConfiguredPolicy_WithIdSet()
    {
        // Arrange
        const string policyId = "finance_strict";

        var configured = new PromptPolicy
        {
            Confirm = new ConfirmOptions { TtlSeconds = 555 }
        };

        var policyOptions = new PolicyOptions
        {
            Policies = new Dictionary<string, PromptPolicy>(StringComparer.OrdinalIgnoreCase)
            {
                [policyId] = configured
            }
        };

        var optionsMonitor = new Mock<IOptionsMonitor<PolicyOptions>>(MockBehavior.Strict);
        optionsMonitor.SetupGet(x => x.CurrentValue).Returns(policyOptions);

        var provider = new PolicyProvider(optionsMonitor.Object);

        var route = new RouteConfig
        {
            RouteId = "r1",
            ClusterId = "c1",
            Match = new RouteMatch(),
            Metadata = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase)
            {
                ["PolicyId"] = "  finance_strict  "
            }
        };

        // Act
        PromptPolicy result = provider.GetPolicyForRoute(route);

        // Assert
        Assert.Equal(policyId, result.Id);
        Assert.Equal(555, result.Confirm.TtlSeconds);
    }

    [Fact]
    public void GetPolicyForRoute_WhenPolicyIdNotFound_ReturnsDefaultPolicy_WithIdSet()
    {
        // Arrange
        const string policyId = "does_not_exist";

        var policyOptions = new PolicyOptions
        {
            Policies = new Dictionary<string, PromptPolicy>(StringComparer.OrdinalIgnoreCase)
        };

        var optionsMonitor = new Mock<IOptionsMonitor<PolicyOptions>>(MockBehavior.Strict);
        optionsMonitor.SetupGet(x => x.CurrentValue).Returns(policyOptions);

        var provider = new PolicyProvider(optionsMonitor.Object);

        var route = new RouteConfig
        {
            RouteId = "r1",
            ClusterId = "c1",
            Match = new RouteMatch(),
            Metadata = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase)
            {
                ["PolicyId"] = policyId
            }
        };

        // Act
        PromptPolicy result = provider.GetPolicyForRoute(route);

        // Assert
        Assert.Equal(policyId, result.Id);
        // Sanity check: default confirm TTL applies
        Assert.Equal(120, result.Confirm.TtlSeconds);
    }
}