using System.Text.Json;
using Aegis.Gateway.Services.PromptExtractors;
using Microsoft.Extensions.Logging;
using Moq;

namespace Aegis.Gateway.Tests.Services.PromptExtractorTests;

public sealed class OllamaPromptExtractorTests
{
    private readonly Mock<ILogger<OllamaPromptExtractor>> _loggerMock = new();

    [Fact]
    public void Name_ShouldBe_Ollama()
    {
        // Arrange
        var extractor = new OllamaPromptExtractor(_loggerMock.Object);

        // Act
        string name = extractor.Name;

        // Assert
        Assert.Equal("ollama", name);
    }

    [Theory]
    [InlineData(null)]
    [InlineData("")]
    [InlineData("   ")]
    public void TryExtract_EmptyOrWhitespaceJson_ReturnsFalse_AndEmptyPrompt(string? json)
    {
        // Arrange
        var extractor = new OllamaPromptExtractor(_loggerMock.Object);

        // Act
        bool result = extractor.TryExtract(json!, out var prompt);

        // Assert
        Assert.False(result);
        Assert.Equal(string.Empty, prompt);
    }

    [Fact]
    public void TryExtract_ValidPrompt_ReturnsTrue_AndPromptValue()
    {
        // Arrange
        var extractor = new OllamaPromptExtractor(_loggerMock.Object);
        var json = """
                   {
                     "model": "llama3",
                     "prompt": "Hello Ollama"
                   }
                   """;

        // Act
        bool result = extractor.TryExtract(json, out var prompt);

        // Assert
        Assert.True(result);
        Assert.Equal("Hello Ollama", prompt);
    }

    [Fact]
    public void TryExtract_MissingPromptProperty_ReturnsFalse()
    {
        // Arrange
        var extractor = new OllamaPromptExtractor(_loggerMock.Object);
        var json = """
                   {
                     "model": "llama3"
                   }
                   """;

        // Act
        bool result = extractor.TryExtract(json, out var prompt);

        // Assert
        Assert.False(result);
        Assert.Equal(string.Empty, prompt);
    }

    [Fact]
    public void TryExtract_PromptIsNotString_ReturnsFalse()
    {
        // Arrange
        var extractor = new OllamaPromptExtractor(_loggerMock.Object);
        var json = """
                   {
                     "prompt": 12345
                   }
                   """;

        // Act
        bool result = extractor.TryExtract(json, out var prompt);

        // Assert
        Assert.False(result);
        Assert.Equal(string.Empty, prompt);
    }

    [Theory]
    [InlineData("""{ "prompt": "" }""")]
    [InlineData("""{ "prompt": "   " }""")]
    public void TryExtract_EmptyOrWhitespacePrompt_ReturnsFalse(string json)
    {
        // Arrange
        var extractor = new OllamaPromptExtractor(_loggerMock.Object);

        // Act
        bool result = extractor.TryExtract(json, out var prompt);

        // Assert
        Assert.False(result);
        Assert.Equal(string.Empty, prompt);
    }

    [Fact]
    public void TryExtract_InvalidJson_ReturnsFalse()
    {
        // Arrange
        var extractor = new OllamaPromptExtractor(_loggerMock.Object);
        var invalidJson = "{ this is not valid json";

        // Act
        bool result = extractor.TryExtract(invalidJson, out var prompt);

        // Assert
        Assert.False(result);
        Assert.Equal(string.Empty, prompt);
    }
}