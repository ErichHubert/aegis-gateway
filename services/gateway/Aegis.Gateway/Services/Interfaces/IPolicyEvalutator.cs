using Aegis.Gateway.Models;
using Aegis.Gateway.Models.Inspection;
using Aegis.Gateway.Models.Policy;

namespace Aegis.Gateway.Services.Interfaces;

public interface IPolicyEvaluator
{
    PolicyActionEnum Evaluate(PromptPolicy policy, IReadOnlyList<PromptInspectionFinding> findings);
}