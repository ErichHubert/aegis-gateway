namespace Aegis.Gateway.Models.Policy;

public enum Severity { Low, Medium, High }
public enum PolicyAction { Allow, Confirm, Block }

public sealed record ConfirmOptions
{
    public int TtlSeconds { get; init; } = 120;
}

public sealed record TypeOverride
{
    public PolicyAction Action { get; init; }
}

public sealed record PromptPolicy
{
    public static readonly string DefaultId = "Default";

    public string Id { get; init; } = DefaultId;

    public PolicyAction DefaultAction { get; init; } = PolicyAction.Confirm;

    public IReadOnlyDictionary<Severity, PolicyAction> SeverityToAction { get; init; }
        = new Dictionary<Severity, PolicyAction>
        {
            [Severity.Low] = PolicyAction.Allow,
            [Severity.Medium] = PolicyAction.Confirm,
            [Severity.High] = PolicyAction.Block,
        };

    public IReadOnlyDictionary<string, TypeOverride> TypeOverrides { get; init; }
        = new Dictionary<string, TypeOverride>(StringComparer.OrdinalIgnoreCase);

    public ConfirmOptions Confirm { get; init; } = new();

    public PolicyAction ResolveAction(Severity? severity, string? findingType)
    {
        if (!string.IsNullOrWhiteSpace(findingType) && TryGetOverrideAction(findingType, out var a))
            return a;

        if (severity is { } s && SeverityToAction.TryGetValue(s, out var mapped))
            return mapped;

        return DefaultAction;
    }

    private bool TryGetOverrideAction(string findingType, out PolicyAction action)
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