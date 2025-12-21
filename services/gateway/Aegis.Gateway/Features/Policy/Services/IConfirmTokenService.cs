using Aegis.Gateway.Features.Policy.Models;

namespace Aegis.Gateway.Features.Policy.Services;

public interface IConfirmTokenService
{
    string IssueToken(ConfirmTokenRequest request, TimeSpan ttl);
    bool TryConsumeToken(string token, ConfirmTokenRequest request);
}