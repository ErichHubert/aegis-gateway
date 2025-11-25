using Aegis.Gateway.Services;
using Aegis.Gateway.Services.PromptExtractors;
using Yarp.ReverseProxy.Configuration;

namespace Aegis.Gateway.Tests.Services;

public sealed class PromptExtractorResolverTests
{
    [Fact]
    public void TryExtractPrompt_WhenRouteConfigIsNull_ReturnsFalse_AndPromptIsEmpty()
    {
        // Arrange
        var body = "test-body";
        var extractor = new TestExtractor("ollama");
        var resolver = new PromptExtractorResolver(new[] { extractor });

        // Act
        bool result = resolver.TryExtractPrompt(routeConfig: null, body, out var prompt);

        // Assert
        Assert.False(result);
        Assert.Equal(string.Empty, prompt); 
        Assert.Empty(extractor.ReceivedBodies);
    }

    [Fact]
    public void TryExtractPrompt_WhenMetadataIsNull_ReturnsFalse_AndPromptIsEmpty()
    {
        // Arrange
        var body = "test-body";
        var extractor = new TestExtractor("ollama");
        var routeConfig = new RouteConfig
        {
            RouteId = "test",
            ClusterId = "cluster-1",
            Match = new RouteMatch(),
            Metadata = null // no metadata
        };

        var resolver = new PromptExtractorResolver(new[] { extractor });

        // Act
        bool result = resolver.TryExtractPrompt(routeConfig, body, out var prompt);

        // Assert
        Assert.False(result);
        Assert.Equal(string.Empty, prompt);
        Assert.Empty(extractor.ReceivedBodies);
    }

    [Fact]
    public void TryExtractPrompt_WhenPromptFormatMissing_ReturnsFalse_AndPromptIsEmpty()
    {
        // Arrange
        var body = "test-body";
        var extractor = new TestExtractor("ollama");
        RouteConfig routeConfig = CreateRouteConfig(promptFormat: null, withMetadata: true);

        var resolver = new PromptExtractorResolver(new[] { extractor });

        // Act
        bool result = resolver.TryExtractPrompt(routeConfig, body, out var prompt);

        // Assert
        Assert.False(result);
        Assert.Equal(string.Empty, prompt);
        Assert.Empty(extractor.ReceivedBodies);
    }

    [Fact]
    public void TryExtractPrompt_WhenPromptFormatUnknown_ReturnsFalse_AndPromptIsEmpty()
    {
        // Arrange
        var body = "some-body";
        var knownExtractor = new TestExtractor("ollama");
        RouteConfig routeConfig = CreateRouteConfig(promptFormat: "unknown-format");

        var resolver = new PromptExtractorResolver(new[] { knownExtractor });

        // Act
        var result = resolver.TryExtractPrompt(routeConfig, body, out var prompt);

        // Assert
        Assert.False(result);
        Assert.Equal(string.Empty, prompt);
        Assert.Empty(knownExtractor.ReceivedBodies);
    }

    [Fact]
    public void TryExtractPrompt_WhenPromptFormatMatches_ReturnsTrue_AndUsesExtractor()
    {
        // Arrange
        var body = "hello world";
        var ollamaExtractor = new TestExtractor("ollama");
        var otherExtractor = new TestExtractor("openai");

        RouteConfig routeConfig = CreateRouteConfig(promptFormat: "ollama");

        var resolver = new PromptExtractorResolver(new IPromptExtractor[]
        {
            ollamaExtractor,
            otherExtractor
        });

        // Act
        var result = resolver.TryExtractPrompt(routeConfig, body, out var prompt);

        // Assert
        Assert.True(result);
        Assert.Equal("ollama:hello world", prompt);

        Assert.Single(ollamaExtractor.ReceivedBodies);
        Assert.Equal(body, ollamaExtractor.ReceivedBodies[0]);

        Assert.Empty(otherExtractor.ReceivedBodies);
    }

    [Fact]
    public void TryExtractPrompt_IsCaseInsensitiveOnPromptFormat()
    {
        // Arrange
        var body = "prompt";
        var ollamaExtractor = new TestExtractor("ollama");

        // PromptFormat in UpperCase
        RouteConfig routeConfig = CreateRouteConfig(promptFormat: "OLLAMA");

        var resolver = new PromptExtractorResolver(new IPromptExtractor[]
        {
            ollamaExtractor
        });

        // Act
        var result = resolver.TryExtractPrompt(routeConfig, body, out var prompt);

        // Assert
        Assert.True(result);
        Assert.Equal("ollama:prompt", prompt);

        Assert.Single(ollamaExtractor.ReceivedBodies);
        Assert.Equal(body, ollamaExtractor.ReceivedBodies[0]);
    }
    
    private sealed class TestExtractor(string name) : IPromptExtractor
    {
        public string Name { get; } = name;

        public List<string> ReceivedBodies { get; } = [];

        public string Extract(string body)
        {
            ReceivedBodies.Add(body);
            return $"{Name}:{body}";
        }
    }

    private static RouteConfig CreateRouteConfig(
        string routeId = "test-route",
        string? promptFormat = null,
        bool withMetadata = true)
    {
        IReadOnlyDictionary<string, string>? metadata = null;

        if (withMetadata)
        {
            metadata = promptFormat is null
                ? new Dictionary<string, string>() // Metadata without PromptFormat
                : new Dictionary<string, string>
                {
                    ["PromptFormat"] = promptFormat
                };
        }

        return new RouteConfig
        {
            RouteId = routeId,
            ClusterId = "cluster-1",
            Match = new RouteMatch(),
            Metadata = metadata
        };
    }
}