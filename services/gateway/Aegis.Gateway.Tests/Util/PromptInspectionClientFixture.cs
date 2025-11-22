using System.Net;
using System.Text;
using Aegis.Gateway.Services;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Logging.Abstractions;

namespace Aegis.Gateway.Tests.Util;

public class PromptInspectionClientFixture
{
    public sealed record CapturedRequest(HttpRequestMessage Request, string? Body);
    
    public PromptInspectionClient CreateFakeClientWithJsonResponse(
        string json,
        out List<CapturedRequest> capturedRequests,
        HttpStatusCode statusCode = HttpStatusCode.OK)
    {
        return CreateFakeClient(
            handlerFunc: (request, ct) =>
            {
                var response = new HttpResponseMessage(statusCode)
                {
                    Content = new StringContent(json, Encoding.UTF8, "application/json")
                };
                return Task.FromResult(response);
            },
            out capturedRequests);
    }

    public PromptInspectionClient CreateFakeClientWithStatusCode(
        HttpStatusCode statusCode,
        out List<CapturedRequest> capturedRequests)
    {
        return CreateFakeClient(
            handlerFunc: (request, ct) =>
            {
                var response = new HttpResponseMessage(statusCode);
                return Task.FromResult(response);
            },
            out capturedRequests);
    }
    
    public PromptInspectionClient CreateFakeClient(
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
            return await handlerFunc(request, ct);
        });

        var httpClient = new HttpClient(handler)
        {
            BaseAddress = new Uri("http://anyservice")
        };

        ILogger<PromptInspectionClient> logger = NullLogger<PromptInspectionClient>.Instance;

        capturedRequests = requests;
        return new PromptInspectionClient(httpClient, logger);
    }
}