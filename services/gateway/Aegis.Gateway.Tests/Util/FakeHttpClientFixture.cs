using System.Net;
using System.Text;

namespace Aegis.Gateway.Tests.Util;

public class FakeHttpClientFixture
{
    public sealed record CapturedRequest(HttpRequestMessage Request, string? Body);
    
    public HttpClient CreateFakeClientWithJsonResponse(
        string json,
        out List<CapturedRequest> capturedRequests,
        HttpStatusCode statusCode = HttpStatusCode.OK)
    {
        return CreateFakeHttpClient(
            handlerFunc: (_, _) =>
            {
                var response = new HttpResponseMessage(statusCode)
                {
                    Content = new StringContent(json, Encoding.UTF8, "application/json")
                };
                return Task.FromResult(response);
            },
            out capturedRequests);
    }

    public HttpClient CreateFakeClientWithStatusCode(
        HttpStatusCode statusCode,
        out List<CapturedRequest> capturedRequests)
    {
        return CreateFakeHttpClient(
            handlerFunc: (_, _) =>
            {
                var response = new HttpResponseMessage(statusCode);
                return Task.FromResult(response);
            },
            out capturedRequests);
    }
    
    public HttpClient CreateFakeHttpClient(
        Func<HttpRequestMessage, CancellationToken, Task<HttpResponseMessage>> handlerFunc,
        out List<CapturedRequest> capturedRequests)
    {
        var requests = new List<CapturedRequest>();

        var handler = new FakeHttpMessageHandler(async (request, ct) =>
        {
            string? body = null;

            if (request.Content is not null)
            {
                body = await request.Content.ReadAsStringAsync(ct);
            }
            
            requests.Add(new CapturedRequest(request, body));
            
            var response = await handlerFunc(request, ct);
            
            // This reads the stream into memory, calculates the length, 
            // and automatically sets the Content-Length header.
            await response.Content.LoadIntoBufferAsync(ct);
            
            return response;
        });

        var httpClient = new HttpClient(handler)
        {
            BaseAddress = new Uri("http://anyservice")
        };

        capturedRequests = requests;
        return httpClient;
    }
}