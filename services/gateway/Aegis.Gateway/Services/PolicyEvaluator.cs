using Aegis.Gateway.Models;
using Aegis.Gateway.Models.Inspection;
using Aegis.Gateway.Models.Policy;
using Aegis.Gateway.Services.Interfaces;

namespace Aegis.Gateway.Services;

public sealed class PolicyEvaluator : IPolicyEvaluator
{
    public PolicyActionEnum Evaluate(PromptPolicy policy, IReadOnlyList<PromptInspectionFinding> findings)
    {
        var worst = PolicyActionEnum.Allow;

        foreach (var f in findings)
        {
            var severity = TryParseSeverity(f.Severity, out var s) ? s : (SeverityEnum?)null;

            var action = policy.ResolveAction(severity, f.Type);
            worst = Max(worst, action);

            if (worst == PolicyActionEnum.Block)
                break;
        }

        return worst;
    }

    private static bool TryParseSeverity(string? severity, out SeverityEnum parsed)
    {
        if (!string.IsNullOrWhiteSpace(severity) &&
            Enum.TryParse(severity, ignoreCase: true, out SeverityEnum sev))
        {
            parsed = sev;
            return true;
        }

        parsed = default;
        return false;
    }

    private static PolicyActionEnum Max(PolicyActionEnum a, PolicyActionEnum b)
        => (PolicyActionEnum)Math.Max((int)a, (int)b);
}