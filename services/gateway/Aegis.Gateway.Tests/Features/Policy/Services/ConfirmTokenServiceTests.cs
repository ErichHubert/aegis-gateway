using System;
using System.Threading.Tasks;
using Aegis.Gateway.Features.Policy.Services;
using Microsoft.Extensions.Caching.Memory;
using Xunit;

namespace Aegis.Gateway.Tests.Features.Policy.Services;

public sealed class ConfirmTokenServiceTests
{
    private static IMemoryCache CreateCache()
        => new MemoryCache(new MemoryCacheOptions { SizeLimit = 1024 });

    private static ConfirmTokenRequest CreateRequest(string idSuffix = "1")
    {
        // The token must be bound to the same request attributes the gateway will later validate.
        // Keep these values deterministic per test while still allowing easy variation via suffix.
        return new ConfirmTokenRequest(
            PolicyId: $"policy-{idSuffix}",
            RouteId: $"route-{idSuffix}",
            UserId: $"user-{idSuffix}",
            BodyHash: $"bodyhash-{idSuffix}",
            PromptHash: $"prompthash-{idSuffix}");
    }

    [Fact]
    public void IssueToken_Returns_Base64UrlToken_AndTokensAreUnique()
    {
        // Arrange
        using var cache = CreateCache();
        var sut = new ConfirmTokenService(cache);
        var req = CreateRequest("1");

        // Act
        var t1 = sut.IssueToken(req, ttl: TimeSpan.FromMinutes(1));
        var t2 = sut.IssueToken(req, ttl: TimeSpan.FromMinutes(1));

        // Assert
        Assert.False(string.IsNullOrWhiteSpace(t1));
        Assert.False(string.IsNullOrWhiteSpace(t2));
        Assert.NotEqual(t1, t2);

        // Base64Url: no '+', '/', '='
        Assert.DoesNotContain("+", t1);
        Assert.DoesNotContain("/", t1);
        Assert.DoesNotContain("=", t1);
    }

    [Fact]
    public void TryConsumeToken_EmptyToken_ReturnsFalse()
    {
        // Arrange
        using var cache = CreateCache();
        var sut = new ConfirmTokenService(cache);
        var req = CreateRequest("1");

        // Act
        var ok1 = sut.TryConsumeToken("", req);
        var ok2 = sut.TryConsumeToken("   ", req);

        // Assert
        Assert.False(ok1);
        Assert.False(ok2);
    }

    [Fact]
    public void TryConsumeToken_UnknownToken_ReturnsFalse()
    {
        // Arrange
        using var cache = CreateCache();
        var sut = new ConfirmTokenService(cache);
        var req = CreateRequest("1");

        // Act
        var ok = sut.TryConsumeToken("does-not-exist", req);

        // Assert
        Assert.False(ok);
    }

    [Fact]
    public void TryConsumeToken_CorrectRequest_ConsumesOnce_ThenFails()
    {
        // Arrange
        using var cache = CreateCache();
        var sut = new ConfirmTokenService(cache);
        var req = CreateRequest("1");
        var token = sut.IssueToken(req, ttl: TimeSpan.FromMinutes(1));

        // Act
        var first = sut.TryConsumeToken(token, req);
        var second = sut.TryConsumeToken(token, req);

        // Assert
        Assert.True(first);
        Assert.False(second); // single-use
    }

    [Fact]
    public void TryConsumeToken_WrongRequest_DoesNotConsume_TokenStillValidForCorrectRequest()
    {
        // Arrange
        using var cache = CreateCache();
        var sut = new ConfirmTokenService(cache);

        var correctReq = CreateRequest("1");
        var wrongReq = CreateRequest("2"); // differs in all fields (policy/route/user/body/prompt)

        var token = sut.IssueToken(correctReq, ttl: TimeSpan.FromMinutes(1));

        // Act
        var wrongAttempt = sut.TryConsumeToken(token, wrongReq);
        var correctAttempt = sut.TryConsumeToken(token, correctReq);

        // Assert
        Assert.False(wrongAttempt);    // must not consume
        Assert.True(correctAttempt);   // token still usable for the bound request
    }

    [Fact]
    public async Task TryConsumeToken_AfterTtlExpires_ReturnsFalse()
    {
        // Arrange
        using var cache = CreateCache();
        var sut = new ConfirmTokenService(cache);
        var req = CreateRequest("1");

        var token = sut.IssueToken(req, ttl: TimeSpan.FromMilliseconds(50));

        // Act
        await Task.Delay(150);
        var ok = sut.TryConsumeToken(token, req);

        // Assert
        Assert.False(ok);
    }
}