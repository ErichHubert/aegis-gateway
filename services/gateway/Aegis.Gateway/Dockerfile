FROM mcr.microsoft.com/dotnet/aspnet:10.0-noble AS base
# Set working directory for the app
WORKDIR /app
# ASP.NET Core default port inside the container
ENV ASPNETCORE_URLS=http://0.0.0.0:8080

# Optional hardening: disable diagnostics in production containers
# (prevents attaching debuggers/profilers inside the container)
ENV DOTNET_EnableDiagnostics=0
EXPOSE 8080

FROM mcr.microsoft.com/dotnet/sdk:10.0 AS build
ARG BUILD_CONFIGURATION=Release
WORKDIR /src
COPY ["Aegis.Gateway/Aegis.Gateway.csproj", "Aegis.Gateway/"]
RUN dotnet restore "Aegis.Gateway/Aegis.Gateway.csproj"
COPY . .
WORKDIR "/src/Aegis.Gateway"
RUN dotnet build "Aegis.Gateway.csproj" -c $BUILD_CONFIGURATION -o /app/build

FROM build AS publish
ARG BUILD_CONFIGURATION=Release
RUN dotnet publish "Aegis.Gateway.csproj" \
    -c $BUILD_CONFIGURATION \
    -o /app/publish \
    /p:UseAppHost=false

FROM base AS final
WORKDIR /app
# Copy published bits and assign ownership to existing 'app' user in base image
COPY --chown=app:app --from=publish /app/publish .
USER app

# ENTRYPOINT for the ASP.NET Core app
ENTRYPOINT ["dotnet", "Aegis.Gateway.dll"]