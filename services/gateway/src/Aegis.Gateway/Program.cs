using Aegis.Gateway.Middleware;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddReverseProxy()
    .LoadFromConfig(builder.Configuration.GetSection("ReverseProxy"));

var app = builder.Build();

app.MapReverseProxy(proxyPipeline => proxyPipeline.UseMiddleware<PromptInspectionMiddleware>());
app.Run();