FROM mcr.microsoft.com/dotnet/aspnet:10.0 AS base
# Create a non-root user (security best practice)
RUN addgroup --system app && adduser --system --ingroup app app
# Set working directory for the app
WORKDIR /app
# ASP.NET Core default port inside the container
ENV ASPNETCORE_URLS=http://0.0.0.0:8080
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
COPY --from=publish /app/publish .
RUN chown -R app:app /app
USER app

# ENTRYPOINT for the ASP.NET Core app
ENTRYPOINT ["dotnet", "Aegis.Gateway.dll"]