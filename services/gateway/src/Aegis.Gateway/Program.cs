using Aegis.Gateway.Middleware;

var builder = WebApplication.CreateBuilder(args);

// Add GlobalExceptionHandler
builder.Services.AddExceptionHandler<GlobalExceptionHandler>();
builder.Services.AddProblemDetails();

builder.Services.AddReverseProxy()
    .LoadFromConfig(builder.Configuration.GetSection("ReverseProxy"));

builder.Logging.ClearProviders();
builder.Logging.AddConsole();

var app = builder.Build();

app.MapReverseProxy(proxyPipeline => proxyPipeline.UseMiddleware<PromptInspectionStep>());
app.Run();