using Microsoft.AspNetCore.Diagnostics;
using Microsoft.AspNetCore.Mvc;

namespace Aegis.Gateway.Middleware;

public class GlobalExceptionHandler(
    ILogger<GlobalExceptionHandler> logger
    ) : IExceptionHandler
{
    public async ValueTask<bool> TryHandleAsync(
        HttpContext httpContext,
        Exception exception,
        CancellationToken cancellationToken)
    {
        var traceId = httpContext.TraceIdentifier;

        logger.LogError(exception, "An unhandled exception occurred while processing the request. TraceId: {TraceId}", traceId);

        httpContext.Response.StatusCode = StatusCodes.Status500InternalServerError;

        await httpContext.Response.WriteAsJsonAsync(
            new ProblemDetails
            {
                Status = httpContext.Response.StatusCode,
                Title = "Internal Server Error",
                Type = "https://tools.ietf.org/html/rfc9110#section-15.6.1",
                Extensions = { ["traceId"] = httpContext.TraceIdentifier }
            },
            cancellationToken);

        return true;
    }
}
