using System.Text.Json;
using Aegis.Gateway.Models;
using Aegis.Gateway.Tests.Util;

namespace Aegis.Gateway.Tests.Services;

public class PromptInspectionClientTests(PromptInspectionClientFixture fixture)
    : IClassFixture<PromptInspectionClientFixture>
{
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

        var client = fixture.CreateFakeClientWithJsonResponse(expectedJson, out var capturedRequests);

        var prompt = "Test prompt";
        var meta = new PromptInspectionMeta
        {
            UserId = "alice",
        };

        // Act
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
        
    }
}