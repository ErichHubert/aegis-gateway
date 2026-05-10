# services/gateway/Dockerfile

# Runtime image (Ubuntu 24.04 "noble")
FROM mcr.microsoft.com/dotnet/aspnet:10.0-noble-chiseled@sha256:f43461f1774d09e4da09014531b8098547ea601a8552958dee2f977f8c1842b5 AS base

WORKDIR /app

# Listen on 8080 inside the container
ENV ASPNETCORE_URLS=http://0.0.0.0:8080
EXPOSE 8080

# Hardening: disable diagnostics/profiling inside containers by default.
# If you need profiling/debugging locally, override with -e DOTNET_EnableDiagnostics=1
ENV DOTNET_EnableDiagnostics=0

# Build image stage
FROM mcr.microsoft.com/dotnet/sdk:10.0-noble@sha256:8a90a473da5205a16979de99d2fc20975e922c68304f5c79d564e666dc3982fc AS build

ARG BUILD_CONFIGURATION=Release
WORKDIR /src

# Copy csproj first to maximize layer caching for restore
COPY ["Aegis.Gateway/Aegis.Gateway.csproj", "Aegis.Gateway/"]
RUN dotnet restore "Aegis.Gateway/Aegis.Gateway.csproj"

# Copy the remaining source
COPY . .
WORKDIR "/src/Aegis.Gateway"

# Build without restoring again
RUN dotnet build "Aegis.Gateway.csproj" -c $BUILD_CONFIGURATION -o /app/build --no-restore

FROM build AS publish
ARG BUILD_CONFIGURATION=Release

# Publish without restoring/building again
RUN dotnet publish "Aegis.Gateway.csproj" \
    -c $BUILD_CONFIGURATION \
    -o /app/publish \
    /p:UseAppHost=false \
    --no-restore

FROM base AS final
WORKDIR /app

# Copy published output and run as non-root.
# The official aspnet images ship an 'app' user; this keeps runtime least-privileged.
COPY --chown=app:app --from=publish /app/publish .
USER app

ENTRYPOINT ["dotnet", "Aegis.Gateway.dll"]