using Aegis.Gateway.Models;

namespace Aegis.Gateway.Services.Interfaces;

public interface IPolicyEvaluator
{
    PolicyAction Evaluate(PromptPolicy policy, IReadOnlyList<PromptInspectionFinding> findings);
}