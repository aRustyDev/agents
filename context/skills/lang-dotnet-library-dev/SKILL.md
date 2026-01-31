---
name: lang-dotnet-library-dev
description: .NET/C#-specific library development patterns. Use when creating NuGet packages, configuring .csproj for libraries, implementing multi-targeting, designing public APIs, generating XML documentation, publishing to NuGet, or applying .NET library best practices. Extends meta-library-dev with .NET tooling and ecosystem patterns.
---

# .NET Library Development

.NET/C#-specific patterns for library development and NuGet package publishing. This skill extends `meta-library-dev` with .NET tooling, package configuration, and ecosystem practices.

## This Skill Extends

- `meta-library-dev` - Foundational library patterns (API design, versioning, testing strategies)

For general concepts like semantic versioning, module organization principles, and testing pyramids, see the meta-skill first.

## This Skill Adds

- **.NET tooling**: .csproj configuration, SDK-style projects, build targets
- **NuGet packaging**: Package metadata, assets, multi-targeting, SourceLink
- **.NET ecosystem**: Publishing workflow, strong naming, API analyzers, nullable reference types

## This Skill Does NOT Cover

- General library patterns - see `meta-library-dev`
- F# library development - see `lang-fsharp-dev`
- ASP.NET web development - see web development skills
- Desktop application development

---

## Overview

Publishing a .NET library requires careful configuration of multiple interconnected systems:

```
┌─────────────────────────────────────────────────────────────────┐
│                    .NET Library Stack                           │
├─────────────────────────────────────────────────────────────────┤
│  Source Code (src/)                                             │
│       │                                                         │
│       ▼                                                         │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │   .csproj   │───▶│   MSBuild   │───▶│   .NET      │         │
│  │   config    │    │   Engine    │    │  Compiler   │         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
│       │                   │                   │                 │
│       │                   ▼                   ▼                 │
│       │            ┌─────────────┐    ┌─────────────┐          │
│       │            │   Assembly  │    │    XML      │          │
│       │            │    (.dll)   │    │   Docs      │          │
│       │            └─────────────┘    └─────────────┘          │
│       │                   │                   │                 │
│       ▼                   ▼                   ▼                 │
│  ┌─────────────────────────────────────────────────────┐       │
│  │                   NuGet Package                      │       │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐             │       │
│  │  │  .nuspec│  │ lib/    │  │ build/  │             │       │
│  │  │ metadata│  │ targets │  │ props   │             │       │
│  │  └─────────┘  └─────────┘  └─────────┘             │       │
│  └─────────────────────────────────────────────────────┘       │
│                          │                                      │
│                          ▼                                      │
│                    ┌───────────┐                                │
│                    │   NuGet   │                                │
│                    │  publish  │                                │
│                    └───────────┘                                │
└─────────────────────────────────────────────────────────────────┘
```

**Key Decision Points:**

| Decision | Options | Recommendation |
|----------|---------|----------------|
| Target frameworks | .NET 6+, .NET Standard, .NET Framework | .NET 6+ for new libs; multi-target for compatibility |
| Package format | PackageReference, packages.config | PackageReference (SDK-style) |
| Strong naming | Signed, Unsigned | Sign if required by consumers; otherwise skip |
| API surface | Minimal, Comprehensive | Start minimal; expand based on feedback |

---

## Quick Reference

| Task | Command |
|------|---------|
| New library project | `dotnet new classlib -n MyLib` |
| Build | `dotnet build` |
| Test | `dotnet test` |
| Pack | `dotnet pack` |
| Pack (Release) | `dotnet pack -c Release` |
| Publish to NuGet | `dotnet nuget push *.nupkg -s nuget.org -k API_KEY` |
| Install locally | `dotnet add package MyLib --source ./bin/Release` |
| List targets | `dotnet --list-sdks` |

---

## Project File Structure

### Minimal SDK-Style .csproj

```xml
<Project Sdk="Microsoft.NET.Sdk">

  <PropertyGroup>
    <!-- Target Framework -->
    <TargetFramework>net8.0</TargetFramework>

    <!-- Language Features -->
    <LangVersion>latest</LangVersion>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>

    <!-- Package Metadata (Required for NuGet) -->
    <PackageId>MyCompany.MyLibrary</PackageId>
    <Version>1.0.0</Version>
    <Authors>Your Name</Authors>
    <Company>Your Company</Company>
    <Description>A brief description of what this library does</Description>
    <PackageLicenseExpression>MIT</PackageLicenseExpression>
    <PackageProjectUrl>https://github.com/username/repo</PackageProjectUrl>
    <RepositoryUrl>https://github.com/username/repo</RepositoryUrl>
    <RepositoryType>git</RepositoryType>
    <PackageTags>tag1;tag2;tag3</PackageTags>

    <!-- Documentation -->
    <GenerateDocumentationFile>true</GenerateDocumentationFile>
    <PublishRepositoryUrl>true</PublishRepositoryUrl>
    <EmbedUntrackedSources>true</EmbedUntrackedSources>
    <IncludeSymbols>true</IncludeSymbols>
    <SymbolPackageFormat>snupkg</SymbolPackageFormat>
  </PropertyGroup>

  <!-- SourceLink for debugging -->
  <ItemGroup>
    <PackageReference Include="Microsoft.SourceLink.GitHub" Version="8.0.0" PrivateAssets="All"/>
  </ItemGroup>

</Project>
```

### Multi-Targeting

```xml
<PropertyGroup>
  <!-- Multiple target frameworks -->
  <TargetFrameworks>net8.0;net6.0;netstandard2.0</TargetFrameworks>
</PropertyGroup>

<!-- Conditional dependencies based on target framework -->
<ItemGroup Condition="'$(TargetFramework)' == 'netstandard2.0'">
  <PackageReference Include="System.Memory" Version="4.5.5" />
</ItemGroup>

<ItemGroup Condition="'$(TargetFramework)' != 'netstandard2.0'">
  <!-- .NET 6+ has this built-in -->
</ItemGroup>
```

### Package Metadata Best Practices

```xml
<PropertyGroup>
  <!-- Versioning -->
  <Version>1.0.0</Version>
  <AssemblyVersion>1.0.0.0</AssemblyVersion>
  <FileVersion>1.0.0.0</FileVersion>

  <!-- Package Info -->
  <PackageId>MyCompany.MyLibrary</PackageId>
  <Title>My Library</Title>
  <Description>
    Detailed description of the library.
    Can span multiple lines.
  </Description>
  <Summary>Short one-line summary</Summary>
  <PackageReleaseNotes>
    1.0.0:
    - Initial release
    - Feature A
    - Feature B
  </PackageReleaseNotes>

  <!-- Legal -->
  <PackageLicenseExpression>MIT</PackageLicenseExpression>
  <!-- Or use license file -->
  <!-- <PackageLicenseFile>LICENSE.txt</PackageLicenseFile> -->
  <PackageRequireLicenseAcceptance>false</PackageRequireLicenseAcceptance>
  <Copyright>Copyright (c) 2025 Your Company</Copyright>

  <!-- Links -->
  <PackageProjectUrl>https://yourproject.com</PackageProjectUrl>
  <PackageReadmeFile>README.md</PackageReadmeFile>
  <PackageIcon>icon.png</PackageIcon>
  <RepositoryUrl>https://github.com/username/repo</RepositoryUrl>
  <RepositoryType>git</RepositoryType>

  <!-- Tags (semicolon-separated) -->
  <PackageTags>library;utilities;dotnet</PackageTags>
</PropertyGroup>

<!-- Include README and icon -->
<ItemGroup>
  <None Include="README.md" Pack="true" PackagePath="/" />
  <None Include="icon.png" Pack="true" PackagePath="/" />
</ItemGroup>
```

---

## Target Framework Selection

### Framework Decision Matrix

| Target Framework | Use When | Compatibility |
|------------------|----------|---------------|
| `net8.0` | Modern apps, latest features | .NET 8+ only |
| `net6.0` | LTS support, wide compatibility | .NET 6+ |
| `netstandard2.0` | Maximum compatibility | .NET Framework 4.6.1+, .NET Core 2.0+, Mono, Xamarin |
| `netstandard2.1` | Modern features, no .NET Framework | .NET Core 3.0+, Mono 6.4+, Xamarin |
| `net48` | .NET Framework specific features | .NET Framework 4.8 only |

### Multi-Targeting Strategy

```xml
<PropertyGroup>
  <!-- Recommended: Cover modern + legacy -->
  <TargetFrameworks>net8.0;net6.0;netstandard2.0</TargetFrameworks>
</PropertyGroup>

<!-- Use preprocessor directives for platform-specific code -->
```

```csharp
#if NET8_0_OR_GREATER
    // Use .NET 8 specific features
    public async Task<T> ProcessAsync<T>(CancellationToken ct = default)
    {
        await Task.CompletedTask;
        return default!;
    }
#elif NETSTANDARD2_0
    // Fallback for .NET Standard
    public Task<T> ProcessAsync<T>()
    {
        return Task.FromResult(default(T));
    }
#endif
```

### Common Preprocessor Symbols

| Symbol | Target Framework |
|--------|------------------|
| `NET8_0` | .NET 8.0 |
| `NET6_0` | .NET 6.0 |
| `NETSTANDARD2_0` | .NET Standard 2.0 |
| `NETSTANDARD2_1` | .NET Standard 2.1 |
| `NET8_0_OR_GREATER` | .NET 8.0 and later |
| `NETCOREAPP` | Any .NET Core/.NET 5+ |
| `NETFRAMEWORK` | Any .NET Framework |

---

## Public API Design

### Namespace Organization

```csharp
// Root namespace matches package ID
namespace MyCompany.MyLibrary
{
    // Core types in root namespace
    public class Client { }
    public interface IClientFactory { }
}

namespace MyCompany.MyLibrary.Models
{
    // Data models in dedicated namespace
    public class Request { }
    public class Response { }
}

namespace MyCompany.MyLibrary.Extensions
{
    // Extension methods in dedicated namespace
    public static class StringExtensions { }
}

namespace MyCompany.MyLibrary.Internal
{
    // Internal helpers (not public API)
    internal static class Helpers { }
}
```

### Access Modifiers Strategy

```csharp
// Public - Part of stable API
public class PublicClass { }

// Public types with internal constructors
public sealed class Config
{
    // Force use of builder/factory
    internal Config() { }
}

// Internal - Implementation details
internal class InternalHelper { }

// Private protected - Derived classes in same assembly only
protected internal class ExtensibleInternal { }

// Use InternalsVisibleTo for testing
[assembly: InternalsVisibleTo("MyLibrary.Tests")]
```

### Nullable Reference Types

```csharp
// Enable in .csproj
// <Nullable>enable</Nullable>

// Nullable parameters and returns
public string? FindUser(string? searchTerm)
{
    if (string.IsNullOrEmpty(searchTerm))
        return null;

    return "found";
}

// Non-nullable parameters
public void ProcessData(string data)
{
    // 'data' is guaranteed non-null by compiler
    Console.WriteLine(data.Length);
}

// Nullable value types
public int? TryParse(string input)
{
    if (int.TryParse(input, out var result))
        return result;

    return null;
}
```

### API Design Best Practices

**Use abstract classes for base implementations:**
```csharp
public abstract class ClientBase
{
    protected ClientBase(ClientOptions options)
    {
        Options = options ?? throw new ArgumentNullException(nameof(options));
    }

    protected ClientOptions Options { get; }

    public abstract Task<Response> ExecuteAsync(Request request);
}
```

**Prefer interfaces for contracts:**
```csharp
public interface IDataStore
{
    Task<T?> GetAsync<T>(string key, CancellationToken ct = default);
    Task SetAsync<T>(string key, T value, CancellationToken ct = default);
    Task DeleteAsync(string key, CancellationToken ct = default);
}
```

**Use builder pattern for complex configuration:**
```csharp
public class ClientBuilder
{
    private string? _baseUrl;
    private TimeSpan _timeout = TimeSpan.FromSeconds(30);
    private IAuthProvider? _authProvider;

    public ClientBuilder WithBaseUrl(string baseUrl)
    {
        _baseUrl = baseUrl;
        return this;
    }

    public ClientBuilder WithTimeout(TimeSpan timeout)
    {
        _timeout = timeout;
        return this;
    }

    public ClientBuilder WithAuth(IAuthProvider authProvider)
    {
        _authProvider = authProvider;
        return this;
    }

    public Client Build()
    {
        if (string.IsNullOrEmpty(_baseUrl))
            throw new InvalidOperationException("BaseUrl is required");

        return new Client(_baseUrl, _timeout, _authProvider);
    }
}
```

**Provide factory methods:**
```csharp
public class Client
{
    private Client(string baseUrl, TimeSpan timeout, IAuthProvider? auth)
    {
        // Private constructor
    }

    // Simple factory
    public static Client Create(string baseUrl)
    {
        return new Client(baseUrl, TimeSpan.FromSeconds(30), null);
    }

    // Builder factory
    public static ClientBuilder CreateBuilder()
    {
        return new ClientBuilder();
    }
}
```

---

## XML Documentation

### Documentation Comments

```csharp
/// <summary>
/// Processes the specified data asynchronously.
/// </summary>
/// <param name="data">The data to process. Cannot be null.</param>
/// <param name="options">Optional processing options.</param>
/// <param name="cancellationToken">Cancellation token for the operation.</param>
/// <returns>
/// A task representing the asynchronous operation. The task result contains
/// the processed result.
/// </returns>
/// <exception cref="ArgumentNullException">
/// Thrown when <paramref name="data"/> is null.
/// </exception>
/// <exception cref="InvalidOperationException">
/// Thrown when the processor is not initialized.
/// </exception>
/// <example>
/// <code>
/// var processor = new DataProcessor();
/// var result = await processor.ProcessAsync(myData);
/// Console.WriteLine($"Processed: {result}");
/// </code>
/// </example>
/// <remarks>
/// This method uses advanced algorithms to process data efficiently.
/// For large datasets, consider using <see cref="ProcessBatchAsync"/>.
/// </remarks>
/// <seealso cref="ProcessBatchAsync"/>
public async Task<Result> ProcessAsync(
    Data data,
    ProcessingOptions? options = null,
    CancellationToken cancellationToken = default)
{
    // Implementation
}
```

### Common Documentation Tags

| Tag | Purpose | Example |
|-----|---------|---------|
| `<summary>` | Brief description | `<summary>Gets the user name.</summary>` |
| `<param>` | Parameter description | `<param name="id">The user ID.</param>` |
| `<returns>` | Return value description | `<returns>The user object.</returns>` |
| `<exception>` | Exceptions thrown | `<exception cref="ArgumentNullException">...</exception>` |
| `<remarks>` | Additional details | `<remarks>This is thread-safe.</remarks>` |
| `<example>` | Usage example | `<example><code>...</code></example>` |
| `<see>` | Reference to type/member | `<see cref="OtherClass"/>` |
| `<seealso>` | Related members | `<seealso cref="RelatedMethod"/>` |
| `<typeparam>` | Generic type parameter | `<typeparam name="T">The type.</typeparam>` |

### Documentation File Generation

```xml
<PropertyGroup>
  <!-- Generate XML documentation -->
  <GenerateDocumentationFile>true</GenerateDocumentationFile>

  <!-- Optional: Treat warnings as errors -->
  <TreatWarningsAsErrors>true</TreatWarningsAsErrors>

  <!-- Or suppress specific warnings -->
  <NoWarn>CS1591</NoWarn> <!-- Missing XML comment -->
</PropertyGroup>
```

---

## NuGet Package Assets

### Package Folder Structure

```
MyLibrary.1.0.0.nupkg
├── lib/
│   ├── net8.0/
│   │   ├── MyLibrary.dll
│   │   └── MyLibrary.xml
│   ├── net6.0/
│   │   ├── MyLibrary.dll
│   │   └── MyLibrary.xml
│   └── netstandard2.0/
│       ├── MyLibrary.dll
│       └── MyLibrary.xml
├── build/
│   └── MyLibrary.props
├── buildTransitive/
│   └── MyLibrary.targets
├── README.md
├── icon.png
└── MyLibrary.nuspec
```

### Custom Build Props/Targets

**MyLibrary.props (imported early):**
```xml
<Project>
  <PropertyGroup>
    <MyLibraryVersion>1.0.0</MyLibraryVersion>
  </PropertyGroup>
</Project>
```

**MyLibrary.targets (imported late):**
```xml
<Project>
  <Target Name="MyLibraryCustomTask" BeforeTargets="Build">
    <Message Text="Running MyLibrary custom task" Importance="high" />
  </Target>
</Project>
```

**Include in package:**
```xml
<ItemGroup>
  <None Include="build\**" Pack="true" PackagePath="build" />
  <None Include="buildTransitive\**" Pack="true" PackagePath="buildTransitive" />
</ItemGroup>
```

### Analyzers and Source Generators

**Include analyzer in package:**
```xml
<PropertyGroup>
  <IncludeBuildOutput>false</IncludeBuildOutput>
  <DevelopmentDependency>true</DevelopmentDependency>
</PropertyGroup>

<ItemGroup>
  <None Include="$(OutputPath)\$(AssemblyName).dll"
        Pack="true"
        PackagePath="analyzers/dotnet/cs"
        Visible="false" />
</ItemGroup>
```

---

## Strong Naming and Signing

### When to Strong Name

**Use strong naming if:**
- Consumers require it (e.g., enterprise environments)
- Installing in GAC
- Interop with other signed assemblies

**Skip strong naming if:**
- Open source library with no enterprise requirements
- Performance is critical (signing adds overhead)
- No explicit consumer requirements

### Signing Configuration

```xml
<PropertyGroup>
  <!-- Enable strong naming -->
  <SignAssembly>true</SignAssembly>
  <AssemblyOriginatorKeyFile>MyLibrary.snk</AssemblyOriginatorKeyFile>

  <!-- Delay signing (for open source) -->
  <DelaySign>false</DelaySign>

  <!-- Public sign (alternative to strong naming) -->
  <PublicSign Condition="'$(OS)' != 'Windows_NT'">true</PublicSign>
</PropertyGroup>
```

### Generate Key File

```bash
# Generate strong name key
dotnet new tool-manifest
dotnet tool install --local dotnet-sn
dotnet sn -k MyLibrary.snk

# Or use .NET Framework SDK
sn -k MyLibrary.snk
```

---

## SourceLink and Debugging

### SourceLink Configuration

```xml
<PropertyGroup>
  <!-- Enable SourceLink -->
  <PublishRepositoryUrl>true</PublishRepositoryUrl>
  <EmbedUntrackedSources>true</EmbedUntrackedSources>

  <!-- Generate symbol package -->
  <IncludeSymbols>true</IncludeSymbols>
  <SymbolPackageFormat>snupkg</SymbolPackageFormat>

  <!-- Deterministic builds -->
  <Deterministic>true</Deterministic>
  <ContinuousIntegrationBuild Condition="'$(CI)' == 'true'">true</ContinuousIntegrationBuild>
</PropertyGroup>

<ItemGroup>
  <!-- GitHub -->
  <PackageReference Include="Microsoft.SourceLink.GitHub" Version="8.0.0" PrivateAssets="All"/>

  <!-- Or GitLab -->
  <!-- <PackageReference Include="Microsoft.SourceLink.GitLab" Version="8.0.0" PrivateAssets="All"/> -->

  <!-- Or Azure DevOps -->
  <!-- <PackageReference Include="Microsoft.SourceLink.AzureRepos.Git" Version="8.0.0" PrivateAssets="All"/> -->
</ItemGroup>
```

### Debugging Enhancements

```xml
<PropertyGroup>
  <!-- Embed all sources in PDB -->
  <EmbedAllSources>true</EmbedAllSources>

  <!-- Portable PDB format -->
  <DebugType>portable</DebugType>

  <!-- Optimize for debugging -->
  <DebugSymbols>true</DebugSymbols>
</PropertyGroup>
```

---

## API Analyzers and Compatibility

### Enable API Analyzers

```xml
<PropertyGroup>
  <!-- Public API analyzers -->
  <EnablePackageValidation>true</EnablePackageValidation>
  <GenerateCompatibilitySuppressionFile>true</GenerateCompatibilitySuppressionFile>

  <!-- API baseline for breaking change detection -->
  <ApiCompatEnableRuleAttributesMustMatch>true</ApiCompatEnableRuleAttributesMustMatch>
</PropertyGroup>

<ItemGroup>
  <PackageReference Include="Microsoft.CodeAnalysis.PublicApiAnalyzers" Version="3.3.4">
    <PrivateAssets>all</PrivateAssets>
    <IncludeAssets>runtime; build; native; contentfiles; analyzers</IncludeAssets>
  </PackageReference>
</ItemGroup>
```

### Public API Files

**PublicAPI.Shipped.txt** (locked API surface):
```
MyCompany.MyLibrary.Client
MyCompany.MyLibrary.Client.Client(string! baseUrl) -> void
MyCompany.MyLibrary.Client.ExecuteAsync(MyCompany.MyLibrary.Request! request) -> System.Threading.Tasks.Task<MyCompany.MyLibrary.Response!>!
```

**PublicAPI.Unshipped.txt** (new APIs not yet released):
```
MyCompany.MyLibrary.Client.CancelAsync() -> System.Threading.Tasks.Task!
```

---

## Testing Libraries

### Test Project Structure

```xml
<Project Sdk="Microsoft.NET.Sdk">

  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <Nullable>enable</Nullable>
    <IsPackable>false</IsPackable>
    <IsTestProject>true</IsTestProject>
  </PropertyGroup>

  <ItemGroup>
    <!-- Testing frameworks -->
    <PackageReference Include="Microsoft.NET.Test.Sdk" Version="17.9.0" />
    <PackageReference Include="xUnit" Version="2.6.6" />
    <PackageReference Include="xunit.runner.visualstudio" Version="2.5.6" />

    <!-- Assertion libraries -->
    <PackageReference Include="FluentAssertions" Version="6.12.0" />

    <!-- Mocking -->
    <PackageReference Include="Moq" Version="4.20.70" />

    <!-- Test coverage -->
    <PackageReference Include="coverlet.collector" Version="6.0.0" />
  </ItemGroup>

  <ItemGroup>
    <!-- Reference to library project -->
    <ProjectReference Include="..\MyLibrary\MyLibrary.csproj" />
  </ItemGroup>

  <!-- Access internals for testing -->
  <ItemGroup>
    <InternalsVisibleTo Include="$(AssemblyName)" />
  </ItemGroup>

</Project>
```

### Common Test Patterns

**xUnit tests:**
```csharp
public class ClientTests
{
    [Fact]
    public async Task ExecuteAsync_ValidRequest_ReturnsResponse()
    {
        // Arrange
        var client = Client.Create("https://api.example.com");
        var request = new Request { Data = "test" };

        // Act
        var response = await client.ExecuteAsync(request);

        // Assert
        response.Should().NotBeNull();
        response.Status.Should().Be(200);
    }

    [Theory]
    [InlineData("")]
    [InlineData(null)]
    public void Create_InvalidBaseUrl_ThrowsArgumentException(string baseUrl)
    {
        // Act & Assert
        Action act = () => Client.Create(baseUrl);
        act.Should().Throw<ArgumentException>();
    }
}
```

**Testing with mocks:**
```csharp
public class ServiceTests
{
    [Fact]
    public async Task ProcessAsync_CallsDataStore()
    {
        // Arrange
        var mockStore = new Mock<IDataStore>();
        mockStore.Setup(x => x.GetAsync<string>("key", default))
                 .ReturnsAsync("value");

        var service = new Service(mockStore.Object);

        // Act
        var result = await service.ProcessAsync("key");

        // Assert
        result.Should().Be("value");
        mockStore.Verify(x => x.GetAsync<string>("key", default), Times.Once);
    }
}
```

---

## Publishing to NuGet

### Pre-Publish Checklist

- [ ] `dotnet build -c Release` succeeds
- [ ] `dotnet test` passes
- [ ] Version bumped in .csproj
- [ ] CHANGELOG.md updated
- [ ] README.md is current
- [ ] XML documentation complete
- [ ] `dotnet pack -c Release` succeeds
- [ ] Package contents verified
- [ ] SourceLink configured
- [ ] Symbol package generated

### Publishing Commands

```bash
# Build in Release configuration
dotnet build -c Release

# Run tests
dotnet test

# Create NuGet package
dotnet pack -c Release -o ./artifacts

# Verify package contents
dotnet nuget list source
# Or use NuGetPackageExplorer

# Publish to NuGet.org
dotnet nuget push ./artifacts/MyLibrary.1.0.0.nupkg \
  --api-key YOUR_API_KEY \
  --source https://api.nuget.org/v3/index.json

# Publish symbols
dotnet nuget push ./artifacts/MyLibrary.1.0.0.snupkg \
  --api-key YOUR_API_KEY \
  --source https://api.nuget.org/v3/index.json
```

### Local Testing

```bash
# Pack the library
dotnet pack -c Release

# Add local source
dotnet nuget add source ./bin/Release --name local

# Install from local source
dotnet add package MyLibrary --source local

# Or test directly
dotnet add package MyLibrary --source ./bin/Release
```

### Continuous Deployment

**GitHub Actions:**
```yaml
name: Publish to NuGet

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4

    - name: Setup .NET
      uses: actions/setup-dotnet@v4
      with:
        dotnet-version: 8.0.x

    - name: Restore dependencies
      run: dotnet restore

    - name: Build
      run: dotnet build -c Release --no-restore

    - name: Test
      run: dotnet test -c Release --no-build

    - name: Pack
      run: dotnet pack -c Release --no-build -o ./artifacts

    - name: Push to NuGet
      run: dotnet nuget push ./artifacts/*.nupkg --api-key ${{ secrets.NUGET_API_KEY }} --source https://api.nuget.org/v3/index.json
```

---

## Common Dependencies

### Serialization

```xml
<ItemGroup>
  <PackageReference Include="System.Text.Json" Version="8.0.0" />
  <!-- Or Newtonsoft.Json for .NET Framework compatibility -->
  <!-- <PackageReference Include="Newtonsoft.Json" Version="13.0.3" /> -->
</ItemGroup>
```

### Logging

```xml
<ItemGroup>
  <PackageReference Include="Microsoft.Extensions.Logging.Abstractions" Version="8.0.0" />
</ItemGroup>
```

### Configuration

```xml
<ItemGroup>
  <PackageReference Include="Microsoft.Extensions.Configuration.Abstractions" Version="8.0.0" />
  <PackageReference Include="Microsoft.Extensions.Options" Version="8.0.0" />
</ItemGroup>
```

### Dependency Injection

```xml
<ItemGroup>
  <PackageReference Include="Microsoft.Extensions.DependencyInjection.Abstractions" Version="8.0.0" />
</ItemGroup>
```

### Polyfills for .NET Standard

```xml
<ItemGroup Condition="'$(TargetFramework)' == 'netstandard2.0'">
  <PackageReference Include="System.Memory" Version="4.5.5" />
  <PackageReference Include="System.Threading.Tasks.Extensions" Version="4.5.4" />
  <PackageReference Include="Microsoft.Bcl.AsyncInterfaces" Version="8.0.0" />
</ItemGroup>
```

---

## Anti-Patterns

### 1. Missing Async Suffix

```csharp
// Bad: Doesn't follow async naming convention
public Task<Result> Process()

// Good: Clear async method name
public Task<Result> ProcessAsync(CancellationToken ct = default)
```

### 2. Throwing Instead of Returning Result

```csharp
// Bad: Forces exception handling
public User GetUser(int id)
{
    throw new UserNotFoundException();
}

// Good: Return nullable or Result type
public User? GetUser(int id)
{
    return null; // Or use Result<User, Error>
}
```

### 3. Mutable Public Collections

```csharp
// Bad: Callers can modify collection
public List<Item> Items { get; set; }

// Good: Expose as read-only
public IReadOnlyList<Item> Items { get; }

// Or return copy
public IEnumerable<Item> GetItems() => _items.ToList();
```

### 4. Missing CancellationToken

```csharp
// Bad: No way to cancel long-running operation
public Task<Result> ProcessAsync()

// Good: Support cancellation
public Task<Result> ProcessAsync(CancellationToken cancellationToken = default)
```

### 5. Over-Exposing Internals

```csharp
// Bad: Implementation details in public API
public class Client
{
    public HttpClient HttpClient { get; set; }
    public Dictionary<string, string> InternalCache { get; set; }
}

// Good: Hide implementation
public class Client
{
    private readonly HttpClient _httpClient;
    private readonly Dictionary<string, string> _cache;
}
```

---

## Troubleshooting

### NuGet Pack Issues

**Symptom:** Package is empty or missing files

**Fixes:**
```xml
<!-- Ensure build output is included -->
<PropertyGroup>
  <IncludeBuildOutput>true</IncludeBuildOutput>
</PropertyGroup>

<!-- Include additional files -->
<ItemGroup>
  <None Include="README.md" Pack="true" PackagePath="/" />
</ItemGroup>
```

### Multi-Targeting Build Errors

**Symptom:** Code doesn't compile for all target frameworks

**Fix:** Use conditional compilation
```csharp
#if NET8_0_OR_GREATER
    // Modern implementation
#else
    // Fallback for older frameworks
#endif
```

### Missing XML Documentation Warnings

**Symptom:** CS1591 warnings for missing documentation

**Fixes:**
```xml
<!-- Suppress warnings -->
<PropertyGroup>
  <NoWarn>CS1591</NoWarn>
</PropertyGroup>

<!-- Or treat as errors and fix -->
<PropertyGroup>
  <TreatWarningsAsErrors>true</TreatWarningsAsErrors>
</PropertyGroup>
```

### SourceLink Not Working

**Symptom:** "Step Into" doesn't work for library code

**Diagnostic:**
```bash
# Verify SourceLink in package
dotnet sourcelink test MyLibrary.1.0.0.nupkg

# Check PDB is embedded
dotnet tool install -g dotnet-symbol
dotnet symbol --symbols MyLibrary.dll
```

**Fix:** Ensure CI sets ContinuousIntegrationBuild
```xml
<PropertyGroup>
  <ContinuousIntegrationBuild Condition="'$(CI)' == 'true'">true</ContinuousIntegrationBuild>
</PropertyGroup>
```

---

## Project Structure

### Recommended Layout

```
MyLibrary/
├── src/
│   └── MyLibrary/
│       ├── MyLibrary.csproj
│       ├── Client.cs
│       ├── Models/
│       │   ├── Request.cs
│       │   └── Response.cs
│       ├── Extensions/
│       │   └── ServiceCollectionExtensions.cs
│       └── Internal/
│           └── Helpers.cs
├── tests/
│   └── MyLibrary.Tests/
│       ├── MyLibrary.Tests.csproj
│       ├── ClientTests.cs
│       └── Models/
│           └── RequestTests.cs
├── samples/
│   └── MyLibrary.Samples/
│       ├── MyLibrary.Samples.csproj
│       └── Program.cs
├── docs/
│   └── getting-started.md
├── .github/
│   └── workflows/
│       └── ci.yml
├── MyLibrary.sln
├── README.md
├── CHANGELOG.md
├── LICENSE
└── icon.png
```

---

## References

- `meta-library-dev` - Foundational library patterns
- [.NET Library Guidance](https://learn.microsoft.com/en-us/dotnet/standard/library-guidance/)
- [NuGet Best Practices](https://learn.microsoft.com/en-us/nuget/create-packages/package-authoring-best-practices)
- [API Design Guidelines](https://learn.microsoft.com/en-us/dotnet/standard/design-guidelines/)
- [SourceLink Documentation](https://github.com/dotnet/sourcelink)
