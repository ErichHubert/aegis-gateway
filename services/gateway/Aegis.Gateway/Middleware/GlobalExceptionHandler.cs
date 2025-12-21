using Microsoft.AspNetCore.Diagnostics;
using Microsoft.AspNetCore.Mvc;

namespace Aegis.Gateway.Middleware;

public class GlobalExceptionHandler(
    ILogger<GlobalExceptionHandler> logger,
    IHostEnvironment environment
) : IExceptionHandler
{
    public async ValueTask<bool> TryHandleAsync(
        HttpContext httpContext,
        Exception exception,
        CancellationToken cancellationToken)
    {
        string traceId = httpContext.TraceIdentifier;

        logger.LogError(
            exception,
            "An unhandled exception occurred while processing the request. TraceId: {TraceId}",
            traceId);

        int statusCode = StatusCodes.Status500InternalServerError;
        var problem = new ProblemDetails
        {
            Status = statusCode,
            Title = "Internal Server Error",
            Type = "https://tools.ietf.org/html/rfc9110#section-15.6.1",
            Instance = httpContext.Request.Path,
            Extensions =  { { "traceId", traceId } }
        };

        problem.Detail = environment.IsProduction() 
            ? exception.ToString() 
            : "An unexpected error occurred. Please contact support with the trace ID.";

        // If the response has already started, we can't write a proper body anymore
        if (httpContext.Response.HasStarted)
        {
            logger.LogWarning(
                "The response has already started, the global exception handler will not modify the response. TraceId: {TraceId}",
                traceId);

            return false;
        }

        httpContext.Response.Clear();
        httpContext.Response.StatusCode = statusCode;
        httpContext.Response.ContentType = "application/problem+json";

        await httpContext.Response.WriteAsJsonAsync(problem, cancellationToken);

        return true;
    }
}