namespace Aegis.Gateway.Features.Policy.Models;

public sealed record PromptPolicy
{
    public static readonly string DefaultId = "Default";

    public string Id { get; init; } = DefaultId;

    public PolicyActionEnum DefaultAction { get; init; } = PolicyActionEnum.Confirm;

    public IReadOnlyDictionary<SeverityEnum, PolicyActionEnum> SeverityToAction { get; init; }
        = new Dictionary<SeverityEnum, PolicyActionEnum>
        {
            [SeverityEnum.Low] = PolicyActionEnum.Allow,
            [SeverityEnum.Medium] = PolicyActionEnum.Confirm,
            [SeverityEnum.High] = PolicyActionEnum.Block,
        };

    public IReadOnlyDictionary<string, TypeOverride> TypeOverrides { get; init; }
        = new Dictionary<string, TypeOverride>(StringComparer.OrdinalIgnoreCase);

    public ConfirmOptions Confirm { get; init; } = new();

    public PolicyActionEnum ResolveAction(SeverityEnum? severity, string? findingType)
    {
        if (!string.IsNullOrWhiteSpace(findingType) &&
            TypeOverrides.TryGetValue(findingType, out var overridePolicy))
        {
            return overridePolicy.Action;
        }

        if (severity.HasValue && SeverityToAction.TryGetValue(severity.Value, out var mappedAction))
        {
            return mappedAction;
        }

        return DefaultAction;
    }
}