using Aegis.Gateway.Features.Policy.Models;
using Aegis.Gateway.Features.PromptInspection.Contracts;

namespace Aegis.Gateway.Features.Policy;

public interface IPolicyEvaluator
{
    PolicyActionEnum Evaluate(PromptPolicy policy, IReadOnlyList<PromptInspectionFinding> findings);
}