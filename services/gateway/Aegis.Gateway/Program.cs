using Aegis.Gateway.DependencyInjection;
using Aegis.Gateway.Features.PromptInspection.Middleware;
using Aegis.Gateway.Infrastructure.PromptInspection;
using Aegis.Gateway.Middleware;
using Microsoft.AspNetCore.Diagnostics.HealthChecks;

var builder = WebApplication.CreateBuilder(args);

//load configuration
builder.Services.Configure<PromptInspectionOptions>(builder.Configuration.GetSection("PromptInspectionService"));

//Add PromptServices
builder.Services.AddPromptInspectionService();
builder.Services.AddPromptExtractionService();

//Add PolicyService
builder.Services.AddPolicyService(builder.Configuration);

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
app.MapPromptInspectionHealthChecks();
app.MapReverseProxy(proxyPipeline => proxyPipeline.UseMiddleware<PromptInspectionStep>());
app.Run();