using System.Net;
using System.Text.Json;
using Aegis.Gateway.Models;
using Aegis.Gateway.Services;
using Aegis.Gateway.Tests.Util;
using Microsoft.Extensions.Logging;
using Moq;

namespace Aegis.Gateway.Tests.Services;

public class PromptInspectionClientTests(FakeHttpClientFixture fixture) 
    : IClassFixture<FakeHttpClientFixture>
{
    private readonly Mock<ILogger<PromptInspectionClient>> _loggerMock = new();
    private readonly FakeHttpClientFixture _fixture = fixture;

    [Fact]
    public async Task InspectAsync_Sends_Single_Request_With_Expected_Payload()
    {
        // Arrange
        var expectedJson = """
                           {
                             "isAllowed": true,
                             "findings": []
                           }
                           """;

        HttpClient fakeHttpClient = _fixture.CreateFakeClientWithJsonResponse(expectedJson, out var capturedRequests);

        var prompt = "Test prompt";
        var meta = new PromptInspectionMeta
        {
            UserId = "alice",
        };

        // Act
        var client = new PromptInspectionClient(fakeHttpClient, _loggerMock.Object);
        await client.InspectAsync(prompt, meta);

        // Assert
        // Ensure the client sends exactly one HTTP request per InspectAsync call
        Assert.Single(capturedRequests);
        
        HttpRequestMessage request = capturedRequests[0].Request;
        string? body = capturedRequests[0].Body;
        
        Assert.NotNull(body);
        
        var doc = JsonDocument.Parse(body);
        var root = doc.RootElement;
        
        // Verify that the outbound request matches the contract with the Prompt Inspection Service
        Assert.Equal(HttpMethod.Post, request.Method);
        Assert.Equal("/inspect", request.RequestUri!.AbsolutePath);
        
        Assert.True(root.TryGetProperty("prompt", out var promptProp));
        Assert.Equal(prompt, promptProp.GetString());

        Assert.True(root.TryGetProperty("meta", out var metaProp));
        Assert.Equal("alice", metaProp.GetProperty("userId").GetString());
        
        Assert.Equal("application/json; charset=utf-8",
            request.Content!.Headers.ContentType!.ToString());
    }
    
    [Fact]
    public async Task InspectAsync_ThrowsHttpRequestException_WhenStatusCodeIsNotSuccess()
    {
        // Arrange
        HttpClient fakeHttpClient = _fixture.CreateFakeClientWithStatusCode(
            HttpStatusCode.NotFound, out _);
        
        // Act & Assert
        var client = new PromptInspectionClient(fakeHttpClient, _loggerMock.Object);
        
        await Assert.ThrowsAsync<HttpRequestException>(async () =>
        {
            await client.InspectAsync("any prompt");
        });
    }
    
    [Fact]
    public async Task InspectAsync_ThrowsInvalidOperationException_WhenServiceReturnsNullBody()
    {
        // Arrange
        string jsonNull = "null";
        HttpClient fakeHttpClient = _fixture.CreateFakeClientWithJsonResponse(
            jsonNull, out _, HttpStatusCode.NoContent);

        // Act & Assert
        var client = new PromptInspectionClient(fakeHttpClient, _loggerMock.Object);
        
        await Assert.ThrowsAsync<InvalidOperationException>(async () =>
        {
            await client.InspectAsync("any prompt");
        });
    }
}