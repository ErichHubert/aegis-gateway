# services/gateway/Dockerfile

# Runtime image (Ubuntu 24.04 "noble")
FROM mcr.microsoft.com/dotnet/aspnet:10.0-noble-chiseled@sha256:a80315337f5ca01b98f7fa8b13048cbf74f55cc8a996745ff16e40a7cea268f5 AS base

WORKDIR /app

# Listen on 8080 inside the container
ENV ASPNETCORE_URLS=http://0.0.0.0:8080
EXPOSE 8080

# Hardening: disable diagnostics/profiling inside containers by default.
# If you need profiling/debugging locally, override with -e DOTNET_EnableDiagnostics=1
ENV DOTNET_EnableDiagnostics=0

# Build image stage
FROM mcr.microsoft.com/dotnet/sdk:10.0-noble@sha256:6ba533cc61a5d8c5e7d4b3a3e33e2ddc2efef200b112e4d658303516bfd24255 AS build

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