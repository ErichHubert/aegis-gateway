using System.Text;
using System.Text.Json;
using Aegis.Gateway.Infrastructure.PromptInspection;
using Aegis.Gateway.Middleware;
using Aegis.Gateway.Models.Inspection;
using Aegis.Gateway.Models.Policy;
using Aegis.Gateway.Services;
using Aegis.Gateway.Services.Interfaces;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Logging.Abstractions;
using Moq;
using Yarp.ReverseProxy.Configuration;
using Yarp.ReverseProxy.Forwarder;
using Yarp.ReverseProxy.Model;

namespace Aegis.Gateway.Tests.Middleware;

public sealed class PromptInspectionStepTests
{
    private readonly ILogger<PromptInspectionStep> _logger = NullLogger<PromptInspectionStep>.Instance;

    [Fact]
    public async Task InvokeAsync_WhenRouteNotMarkedForInspection_CallsNext_AndSkipsInspection()
    {
        // Arrange
        var promptClientMock = new Mock<IPromptInspectionClient>(MockBehavior.Strict);
        var extractorResolverMock = new Mock<IPromptExtractorResolver>(MockBehavior.Strict);
        var policyProviderMock = new Mock<IPolicyProvider>(MockBehavior.Strict);
        var policyEvaluatorMock = new Mock<IPolicyEvaluator>(MockBehavior.Strict);

        var spy = new NextSpy();
        RequestDelegate next = spy.Invoke;

        var middleware = new PromptInspectionStep(
            next,
            promptClientMock.Object,
            extractorResolverMock.Object,
            policyProviderMock.Object,
            policyEvaluatorMock.Object,
            _logger);

        DefaultHttpContext context = CreateHttpContext(body: """{"prompt":"hello"}""");

        // Route exists, but InspectPrompt is not enabled => Metadata will be null => skip inspection
        RouteConfig routeConfig = CreateRouteConfig(inspectPrompt: false);
        AttachReverseProxyFeature(context, routeConfig);

        // Act
        await middleware.InvokeAsync(context);

        // Assert
        Assert.True(spy.WasCalled);

        extractorResolverMock.Verify(x => x.TryExtractPrompt(
                It.IsAny<RouteConfig?>(),
                It.IsAny<string>(),
                out It.Ref<string>.IsAny),
            Times.Never);

        promptClientMock.Verify(x => x.InspectAsync(
                It.IsAny<string>(),
                It.IsAny<PromptInspectionMeta>(),
                It.IsAny<CancellationToken>()),
            Times.Never);

        policyProviderMock.Verify(x => x.GetPolicyForRoute(It.IsAny<RouteConfig?>()), Times.Never);
        policyEvaluatorMock.Verify(x => x.Evaluate(It.IsAny<PromptPolicy>(), It.IsAny<IReadOnlyList<PromptInspectionFinding>>()), Times.Never);
    }

    [Fact]
    public async Task InvokeAsync_WhenExtractorFails_Returns500_WithMisconfiguredProblemDetails()
    {
        // Arrange
        var promptClientMock = new Mock<IPromptInspectionClient>(MockBehavior.Strict);
        var extractorResolverMock = new Mock<IPromptExtractorResolver>();
        var policyProviderMock = new Mock<IPolicyProvider>(MockBehavior.Strict);
        var policyEvaluatorMock = new Mock<IPolicyEvaluator>(MockBehavior.Strict);

        var body = """{"prompt":"hello"}""";
        var dummyPrompt = string.Empty;

        extractorResolverMock.Setup(x => x.TryExtractPrompt(
                It.IsAny<RouteConfig?>(),
                It.IsAny<string>(),
                out dummyPrompt))
            .Returns(false);

        var spy = new NextSpy();
        RequestDelegate next = spy.Invoke;

        var middleware = new PromptInspectionStep(
            next,
            promptClientMock.Object,
            extractorResolverMock.Object,
            policyProviderMock.Object,
            policyEvaluatorMock.Object,
            _logger);

        DefaultHttpContext context = CreateHttpContext(body);

        RouteConfig routeConfig = CreateRouteConfig(inspectPrompt: true, promptFormat: "ollama");
        AttachReverseProxyFeature(context, routeConfig);

        // IMPORTANT: middleware now loads policy BEFORE extraction -> set up strict mock
        policyProviderMock
            .Setup(x => x.GetPolicyForRoute(It.Is<RouteConfig?>(rc => rc == routeConfig)))
            .Returns(new PromptPolicy());

        // Act
        await middleware.InvokeAsync(context);

        // Assert
        Assert.False(spy.WasCalled);

        extractorResolverMock.Verify(x => x.TryExtractPrompt(
                It.Is<RouteConfig?>(rc => rc == routeConfig),
                It.IsAny<string>(),
                out dummyPrompt),
            Times.Once);

        Assert.Equal(StatusCodes.Status500InternalServerError, context.Response.StatusCode);

        ProblemDetails problem = await ReadProblemDetailsAsync(context.Response);
        Assert.False(string.IsNullOrWhiteSpace(problem.Title));
        Assert.False(string.IsNullOrWhiteSpace(problem.Detail));

        // No inspection call on extractor failure
        promptClientMock.Verify(x => x.InspectAsync(
                It.IsAny<string>(),
                It.IsAny<PromptInspectionMeta>(),
                It.IsAny<CancellationToken>()),
            Times.Never);

        // No evaluation when extractor fails
        policyEvaluatorMock.Verify(x => x.Evaluate(It.IsAny<PromptPolicy>(), It.IsAny<IReadOnlyList<PromptInspectionFinding>>()), Times.Never);
    }

    [Fact]
    public async Task InvokeAsync_WhenInspectionBlocksRequest_Returns403_WithFindings()
    {
        // Arrange
        var promptClientMock = new Mock<IPromptInspectionClient>();
        var extractorResolverMock = new Mock<IPromptExtractorResolver>();
        var policyProviderMock = new Mock<IPolicyProvider>(MockBehavior.Strict);
        var policyEvaluatorMock = new Mock<IPolicyEvaluator>(MockBehavior.Strict);

        var body = """{"prompt":"this should be blocked"}""";
        var extractedPrompt = "this should be blocked";

        extractorResolverMock.Setup(x => x.TryExtractPrompt(
                It.IsAny<RouteConfig?>(),
                It.IsAny<string>(),
                out extractedPrompt))
            .Returns(true);

        var findings = new List<PromptInspectionFinding>
        {
            new()
            {
                Type = "secret_generic_token",
                Severity = "high",
                Start = 5,
                End = 12,
                // Snippet might exist in your model, but middleware redacts it anyway
                Snippet = "REDACTME",
                Message = "Token-like string detected"
            }
        };

        promptClientMock.Setup(x => x.InspectAsync(
                extractedPrompt,
                It.IsAny<PromptInspectionMeta>(),
                It.IsAny<CancellationToken>()))
            .ReturnsAsync(new PromptInspectionResponse
            {
                Findings = findings
            });

        var spy = new NextSpy();
        RequestDelegate next = spy.Invoke;

        var middleware = new PromptInspectionStep(
            next,
            promptClientMock.Object,
            extractorResolverMock.Object,
            policyProviderMock.Object,
            policyEvaluatorMock.Object,
            _logger);

        DefaultHttpContext context = CreateHttpContext(body);

        RouteConfig routeConfig = CreateRouteConfig(inspectPrompt: true, promptFormat: "ollama");
        AttachReverseProxyFeature(context, routeConfig);

        var policy = new PromptPolicy { Id = "Default" };

        policyProviderMock
            .Setup(x => x.GetPolicyForRoute(It.Is<RouteConfig?>(rc => rc == routeConfig)))
            .Returns(policy);

        policyEvaluatorMock
            .Setup(x => x.Evaluate(It.IsAny<PromptPolicy>(), It.IsAny<IReadOnlyList<PromptInspectionFinding>>()))
            .Returns(PolicyActionEnum.Block);

        // Act
        await middleware.InvokeAsync(context);

        // Assert
        Assert.False(spy.WasCalled);
        Assert.Equal(StatusCodes.Status403Forbidden, context.Response.StatusCode);

        ProblemDetails problem = await ReadProblemDetailsAsync(context.Response);
        Assert.False(string.IsNullOrWhiteSpace(problem.Title));
        Assert.False(string.IsNullOrWhiteSpace(problem.Detail));

        Assert.True(problem.Extensions.TryGetValue("findings", out var extFindings));
        Assert.NotNull(extFindings);

        policyEvaluatorMock.Verify(x => x.Evaluate(
            It.IsAny<PromptPolicy>(),
            It.Is<IReadOnlyList<PromptInspectionFinding>>(l => l.Count == 1)),
            Times.Once);
    }

    // ---------- Helpers ----------

    private sealed class NextSpy
    {
        public bool WasCalled { get; private set; }

        public Task Invoke(HttpContext _)
        {
            WasCalled = true;
            return Task.CompletedTask;
        }
    }

    private static DefaultHttpContext CreateHttpContext(string body)
    {
        var context = new DefaultHttpContext();

        byte[] bytes = Encoding.UTF8.GetBytes(body);
        context.Request.Body = new MemoryStream(bytes);
        context.Request.ContentType = "application/json";
        context.Request.Method = HttpMethods.Post;

        context.Response.Body = new MemoryStream();
        return context;
    }

    private static RouteConfig CreateRouteConfig(
        bool inspectPrompt,
        string? promptFormat = null,
        string routeId = "test-route")
    {
        var metadata = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);

        if (inspectPrompt)
            metadata["InspectPrompt"] = "true";

        if (promptFormat is not null)
            metadata["PromptFormat"] = promptFormat;

        return new RouteConfig
        {
            RouteId = routeId,
            ClusterId = "cluster-1",
            Match = new RouteMatch(),
            Metadata = metadata.Count > 0 ? metadata : null
        };
    }

    private static void AttachReverseProxyFeature(HttpContext context, RouteConfig routeConfig)
    {
        // Minimal ClusterState for tests
        var clusterState = new ClusterState("cluster-1");
        var routeModel = new RouteModel(routeConfig, clusterState, HttpTransformer.Default);

        var featureMock = new Mock<IReverseProxyFeature>();
        featureMock.SetupGet(f => f.Route).Returns(routeModel);

        context.Features.Set(featureMock.Object);
    }

    private static async Task<ProblemDetails> ReadProblemDetailsAsync(HttpResponse response)
    {
        response.Body.Position = 0;
        using var reader = new StreamReader(response.Body, Encoding.UTF8);
        var json = await reader.ReadToEndAsync();

        var problem = JsonSerializer.Deserialize<ProblemDetails>(
            json,
            new JsonSerializerOptions { PropertyNameCaseInsensitive = true });

        Assert.NotNull(problem);
        return problem!;
    }
}