namespace Aegis.Gateway.Tests.Util;

public sealed class FakeHttpMessageHandler(
    Func<HttpRequestMessage, CancellationToken, Task<HttpResponseMessage>> handler)
    : HttpMessageHandler
{
    private readonly Func<HttpRequestMessage, CancellationToken, Task<HttpResponseMessage>> _handler = handler 
        ?? throw new ArgumentNullException(nameof(handler));

    protected override Task<HttpResponseMessage> SendAsync(
        HttpRequestMessage request,
        CancellationToken cancellationToken)
        => _handler(request, cancellationToken);
}