using Aegis.Gateway.Models.Inspection;
using Aegis.Gateway.Models.Policy;
using Aegis.Gateway.Services;

namespace Aegis.Gateway.Tests.Services;

public sealed class PolicyEvaluatorTests
{
    private readonly PolicyEvaluator _sut = new();

    [Fact]
    public void Evaluate_WhenNoFindings_ReturnsAllow()
    {
        //Arrange
        var policy = new PromptPolicy();
        var findings = Array.Empty<PromptInspectionFinding>();

        //Act
        var action = _sut.Evaluate(policy, findings);

        //Assert
        Assert.Equal(PolicyActionEnum.Allow, action);
    }

    [Fact]
    public void Evaluate_WhenSeverityIsHigh_ReturnsBlock()
    {
        //Arrange
        var policy = new PromptPolicy();
        var findings = new List<PromptInspectionFinding>
        {
            new() { Type = "pii_email", Severity = "high" }
        };

        //Act
        var action = _sut.Evaluate(policy, findings);

        //Assert
        Assert.Equal(PolicyActionEnum.Block, action);
    }

    [Fact]
    public void Evaluate_WhenSeverityIsMedium_ReturnsConfirm()
    {
        //Arrange
        var policy = new PromptPolicy();
        var findings = new List<PromptInspectionFinding>
        {
            new() { Type = "pii_email", Severity = "medium" }
        };

        //Act
        var action = _sut.Evaluate(policy, findings);

        //Assert
        Assert.Equal(PolicyActionEnum.Confirm, action);
    }

    [Fact]
    public void Evaluate_WhenSeverityIsUnknown_UsesPolicyFallback()
    {
        //Arrange
        // Unknown severity should flow through as null and be handled by the policy.
        var policy = new PromptPolicy();
        var findings = new List<PromptInspectionFinding>
        {
            new() { Type = "pii_email", Severity = "not-a-severity" }
        };

        //Act
        var action = _sut.Evaluate(policy, findings);

        //Assert
        // With the default policy config, fallback is Confirm.
        Assert.Equal(PolicyActionEnum.Confirm, action);
    }

    [Fact]
    public void Evaluate_WhenTypeOverrideExists_WinsOverSeverityMapping()
    {
        //Arrange
        var policy = new PromptPolicy
        {
            TypeOverrides = new Dictionary<string, TypeOverride>(StringComparer.OrdinalIgnoreCase)
            {
                ["pii_iban"] = new TypeOverride { Action = PolicyActionEnum.Block }
            }
        };

        // Severity says allow, but the type override should block.
        var findings = new List<PromptInspectionFinding>
        {
            new() { Type = "pii_iban", Severity = "low" }
        };

        //Act
        var action = _sut.Evaluate(policy, findings);

        //Assert
        Assert.Equal(PolicyActionEnum.Block, action);
    }

    [Fact]
    public void Evaluate_ReturnsWorstActionAcrossAllFindings()
    {
        //Arrange
        var policy = new PromptPolicy();
        var findings = new List<PromptInspectionFinding>
        {
            new() { Type = "pii_email", Severity = "low" },    // Allow
            new() { Type = "pii_phone", Severity = "medium" }, // Confirm
            new() { Type = "secret_jwt", Severity = "high" },  // Block
        };

        //Act
        var action = _sut.Evaluate(policy, findings);

        //Assert
        Assert.Equal(PolicyActionEnum.Block, action);
    }

    [Fact]
    public void Evaluate_ParsesSeverityCaseInsensitively()
    {
        //Arrange
        var policy = new PromptPolicy();
        var findings = new List<PromptInspectionFinding>
        {
            new() { Type = "secret_jwt", Severity = "HiGh" }
        };

        //Act
        var action = _sut.Evaluate(policy, findings);

        //Assert
        Assert.Equal(PolicyActionEnum.Block, action);
    }
}