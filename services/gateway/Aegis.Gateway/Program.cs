using Aegis.Gateway.Extensions;
using Aegis.Gateway.Infrastructure.PromptInspection;
using Aegis.Gateway.Middleware;

var builder = WebApplication.CreateBuilder(args);

//load configuration
builder.Services.Configure<PromptInspectionSettings>(builder.Configuration.GetSection("PromptInspectionService"));

//Add PromptServices
builder.Services.AddPromptInspectionService();
builder.Services.AddPromptExtractionService();

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