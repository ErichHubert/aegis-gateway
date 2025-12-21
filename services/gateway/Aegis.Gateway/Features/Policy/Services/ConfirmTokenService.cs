using System.Security.Cryptography;
using Microsoft.Extensions.Caching.Memory;

namespace Aegis.Gateway.Features.Policy.Services;

public sealed class ConfirmTokenService(IMemoryCache cache) : IConfirmTokenService
{
    private const int TokenBytes = 32; // 256-bit

    public string IssueToken(ConfirmTokenRequest request, TimeSpan ttl)
    {
        string token = CreateToken();

        cache.Set(
            key: CacheKey(token),
            value: request,
            options: new MemoryCacheEntryOptions
            {
                AbsoluteExpirationRelativeToNow = ttl,
                Size = 1
            });

        return token;
    }

    public bool TryConsumeToken(string token, ConfirmTokenRequest request)
    {
        if (string.IsNullOrWhiteSpace(token))
            return false;

        if (!cache.TryGetValue(CacheKey(token), out ConfirmTokenRequest? stored) || stored is null)
            return false;

        // constant-time compare would be overkill here because token itself is random,
        // but we still compare the bound fields strictly.
        if (!Equals(stored, request))
            return false;

        // single-use: remove it now
        cache.Remove(CacheKey(token));
        return true;
    }

    private static string CreateToken()
    {
        byte[] bytes = RandomNumberGenerator.GetBytes(TokenBytes);
        return Base64UrlEncode(bytes);
    }

    private static string CacheKey(string token) => $"confirm:{token}";

    private static string Base64UrlEncode(byte[] data)
        => Convert.ToBase64String(data).TrimEnd('=').Replace('+', '-').Replace('/', '_');
}