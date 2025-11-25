using Aegis.Gateway.Services;
using Aegis.Gateway.Services.PromptExtractors;
using Moq;
using Yarp.ReverseProxy.Configuration;

namespace Aegis.Gateway.Tests.Services;

public sealed class PromptExtractorResolverTests
{
    [Fact]
    public void TryExtractPrompt_WhenRouteConfigIsNull_ReturnsFalse_AndPromptIsEmpty()
    {
        // Arrange
        var body = "some-body";
        Mock<IPromptExtractor> extractorMock = CreateExtractorMock("failing-extractor");
        var resolver = new PromptExtractorResolver(new[] { extractorMock.Object });
        
        // Act
        bool result = resolver.TryExtractPrompt(routeConfig: null, body, out var prompt);

        // Assert
        Assert.False(result);
        Assert.Equal(string.Empty, prompt); 
        extractorMock.Verify(x => x.TryExtract(It.IsAny<string>(), out It.Ref<string>.IsAny), Times.Never);
    }

    [Fact]
    public void TryExtractPrompt_WhenMetadataIsNull_ReturnsFalse_AndPromptIsEmpty()
    {
        // Arrange
        var body = "some-body";
        Mock<IPromptExtractor> extractorMock = CreateExtractorMock("failing-extractor");
        RouteConfig routeConfig = CreateRouteConfig(promptFormat: null, withMetadata: false);
        var resolver = new PromptExtractorResolver(new[] { extractorMock.Object });

        // Act
        bool result = resolver.TryExtractPrompt(routeConfig, body, out var prompt);

        // Assert
        Assert.False(result);
        Assert.Equal(string.Empty, prompt);
        extractorMock.Verify(x => x.TryExtract(It.IsAny<string>(), out It.Ref<string>.IsAny), Times.Never);
    }

    [Fact]
    public void TryExtractPrompt_WhenPromptFormatMissing_ReturnsFalse_AndPromptIsEmpty()
    {
        // Arrange
        var body = "some-body";
        Mock<IPromptExtractor> extractorMock = CreateExtractorMock("failing-extractor");
        RouteConfig routeConfig = CreateRouteConfig(promptFormat: null, withMetadata: true);
        var resolver = new PromptExtractorResolver(new[] { extractorMock.Object });

        // Act
        bool result = resolver.TryExtractPrompt(routeConfig, body, out var prompt);

        // Assert
        Assert.False(result);
        Assert.Equal(string.Empty, prompt);
        extractorMock.Verify(x => x.TryExtract(It.IsAny<string>(), out It.Ref<string>.IsAny), Times.Never);
    }

    [Fact]
    public void TryExtractPrompt_WhenPromptFormatUnknown_ReturnsFalse_AndPromptIsEmpty()
    {
        // Arrange
        var body = "some-body";
        var extractorPromptResult = "something"; 
        Mock<IPromptExtractor> extractorMock = CreateExtractorMock(
            name: "failing-extractor",
            setupTryExtract: true,
            tryExtractResult: false,
            outPrompt: extractorPromptResult);
        
        var resolver = new PromptExtractorResolver(new[] { extractorMock.Object });
        RouteConfig routeConfig = CreateRouteConfig(promptFormat: "unknown-format");
        
        // Act
        var result = resolver.TryExtractPrompt(routeConfig, body, out var prompt);

        // Assert
        Assert.False(result);
        Assert.Equal(string.Empty, prompt);
        extractorMock.Verify(x => x.TryExtract(It.IsAny<string>(), out It.Ref<string>.IsAny), Times.Never);
    }

    [Fact]
    public void TryExtractPrompt_WhenPromptFormatMatches_ReturnsTrue_AndUsesExtractor()
    {
        // Arrange
        var body = "some-body";
        var extractorPromptResult = "something"; 
        Mock<IPromptExtractor> ollamaExtractorMock = CreateExtractorMock(
            name: "ollama",
            setupTryExtract: true,
            tryExtractResult: true,
            outPrompt: extractorPromptResult);
        
        Mock<IPromptExtractor> otherExtractorMock = CreateExtractorMock(
            name: "openai",
            setupTryExtract: true,
            tryExtractResult: false,
            outPrompt: extractorPromptResult);

        RouteConfig routeConfig = CreateRouteConfig(promptFormat: "ollama");

        var resolver = new PromptExtractorResolver(new IPromptExtractor[]
        {
            ollamaExtractorMock.Object,
            otherExtractorMock.Object
        });

        // Act
        var result = resolver.TryExtractPrompt(routeConfig, body, out var prompt);

        // Assert
        Assert.True(result);
        Assert.Equal(extractorPromptResult, prompt);
        ollamaExtractorMock.Verify(x => x.TryExtract(It.IsAny<string>(), out It.Ref<string>.IsAny), Times.Once);
        otherExtractorMock.Verify(x => x.TryExtract(It.IsAny<string>(), out It.Ref<string>.IsAny), Times.Never);
    }

    [Fact]
    public void TryExtractPrompt_IsCaseInsensitiveOnPromptFormat()
    {
        // Arrange
        var body = "something";
        var extractorPromptResult = "something"; 
        Mock<IPromptExtractor> ollamaExtractorMock = CreateExtractorMock(
            name: "ollama",
            setupTryExtract: true,
            tryExtractResult: true,
            outPrompt: extractorPromptResult);

        // PromptFormat in UpperCase
        RouteConfig routeConfig = CreateRouteConfig(promptFormat: "OLLAMA");

        var resolver = new PromptExtractorResolver(new IPromptExtractor[]
        {
            ollamaExtractorMock.Object
        });

        // Act
        var result = resolver.TryExtractPrompt(routeConfig, body, out var prompt);

        // Assert
        Assert.True(result);
        Assert.Equal(extractorPromptResult, prompt);
        ollamaExtractorMock.Verify(x => x.TryExtract(It.IsAny<string>(), out It.Ref<string>.IsAny), Times.Once);
    }

    private static Mock<IPromptExtractor> CreateExtractorMock(
        string name,
        bool setupTryExtract = false,
        bool tryExtractResult = false,
        string? outPrompt = null)
    {
        var mock = new Mock<IPromptExtractor>();
        mock.SetupGet(x => x.Name).Returns(name);

        if (setupTryExtract)
        {
            var localOut = outPrompt ?? string.Empty;
            mock.Setup(x => x.TryExtract(It.IsAny<string>(), out localOut))
                .Returns(tryExtractResult);
        }

        return mock;
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