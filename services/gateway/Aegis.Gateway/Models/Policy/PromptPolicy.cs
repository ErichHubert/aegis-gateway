namespace Aegis.Gateway.Models.Policy;

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
        if (!string.IsNullOrWhiteSpace(findingType) && TryGetOverrideAction(findingType, out var a))
            return a;

        if (severity is { } s && SeverityToAction.TryGetValue(s, out var mapped))
            return mapped;

        return DefaultAction;
    }

    private bool TryGetOverrideAction(string findingType, out PolicyActionEnum action)
    {
        if (TypeOverrides.TryGetValue(findingType, out var o))
        {
            action = o.Action;
            return true;
        }

        action = default;
        return false;
    }
}