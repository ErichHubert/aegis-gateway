using Aegis.Gateway.Extensions;
using Aegis.Gateway.Middleware;
using Aegis.Gateway.Services;

var builder = WebApplication.CreateBuilder(args);

//load configuration
builder.Services.Configure<PromptInspectionSettings>(builder.Configuration.GetSection("PromptInspectionService"));

//Add PromptInspectionService
builder.Services.AddPromptInspectionService();

// Add GlobalExceptionHandler
builder.Services.AddExceptionHandler<GlobalExceptionHandler>();
builder.Services.AddProblemDetails();

builder.Services.AddReverseProxy()
    .LoadFromConfig(builder.Configuration.GetSection("ReverseProxy"));

//Add Logging
builder.Logging.ClearProviders();
builder.Logging.AddConsole();

var app = builder.Build();

app.UseExceptionHandler();
app.MapReverseProxy(proxyPipeline => proxyPipeline.UseMiddleware<PromptInspectionStep>());
app.Run();