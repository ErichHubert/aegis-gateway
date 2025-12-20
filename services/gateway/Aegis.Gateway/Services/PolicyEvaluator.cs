using Aegis.Gateway.Models;

namespace Aegis.Gateway.Services;

public sealed class PolicyEvaluator : IPolicyEvaluator
{
    public PolicyAction Evaluate(PromptPolicy policy, IReadOnlyList<PromptInspectionFinding> findings)
    {
        var worst = PolicyAction.Allow;

        foreach (var f in findings)
        {
            var severity = TryParseSeverity(f.Severity, out var s) ? s : (Severity?)null;

            var action = policy.ResolveAction(severity, f.Type);
            worst = Max(worst, action);

            if (worst == PolicyAction.Block)
                break;
        }

        return worst;
    }

    private static bool TryParseSeverity(string? severity, out Severity parsed)
    {
        if (!string.IsNullOrWhiteSpace(severity) &&
            Enum.TryParse(severity, ignoreCase: true, out Severity sev))
        {
            parsed = sev;
            return true;
        }

        parsed = default;
        return false;
    }

    private static PolicyAction Max(PolicyAction a, PolicyAction b)
        => (PolicyAction)Math.Max((int)a, (int)b);
}