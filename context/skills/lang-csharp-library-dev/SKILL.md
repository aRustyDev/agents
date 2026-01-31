---
name: lang-csharp-library-dev
description: C#-specific library development patterns. Use when creating .NET class libraries, designing NuGet packages, configuring project files, implementing strong naming and versioning, writing XML documentation, unit testing with xUnit/NUnit, source generators, and multi-targeting. Extends meta-library-dev with .NET tooling and ecosystem patterns.
---

# C# Library Development

C#-specific patterns for .NET library development. This skill extends `meta-library-dev` with .NET tooling, API design guidelines, and NuGet ecosystem practices.

## This Skill Extends

- `meta-library-dev` - Foundational library patterns (API design, versioning, testing strategies)

For general concepts like semantic versioning, module organization principles, and testing pyramids, see the meta-skill first.

## This Skill Adds

- **.NET tooling**: .csproj configuration, dotnet CLI, NuGet packaging
- **.NET idioms**: API design guidelines, strong naming, XML documentation
- **.NET ecosystem**: NuGet publishing, multi-targeting, source generators

## This Skill Does NOT Cover

- General library patterns - see `meta-library-dev`
- ASP.NET Core - see `lang-csharp-aspnet-dev`
- Entity Framework - see `lang-csharp-ef-dev`
- Desktop application development

---

## Overview

Publishing a .NET library requires understanding the modern .NET SDK project system and NuGet ecosystem:

```
┌─────────────────────────────────────────────────────────────────┐
│                    .NET Library Stack                           │
├─────────────────────────────────────────────────────────────────┤
│  Source Code (*.cs)                                             │
│       │                                                         │
│       ▼                                                         │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │  .csproj    │───▶│  C# Compiler│───▶│   Assembly  │         │
│  │   Config    │    │   (Roslyn)  │    │    (.dll)   │         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
│       │                   │                   │                 │
│       │                   ▼                   │                 │
│       │            ┌─────────────┐            │                 │
│       │            │ XML Docs    │            │                 │
│       │            │   (.xml)    │            │                 │
│       │            └─────────────┘            │                 │
│       │                   │                   │                 │
│       ▼                   ▼                   ▼                 │
│  ┌─────────────────────────────────────────────────────┐       │
│  │                  NuGet Package                       │       │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐             │       │
│  │  │  .dll   │  │  .xml   │  │ .nupkg  │             │       │
│  │  │ Assembly│  │  Docs   │  │Metadata │             │       │
│  │  └─────────┘  └─────────┘  └─────────┘             │       │
│  └─────────────────────────────────────────────────────┘       │
│                          │                                      │
│                          ▼                                      │
│                    ┌───────────┐                                │
│                    │  NuGet    │                                │
│                    │  Publish  │                                │
│                    └───────────┘                                │
└─────────────────────────────────────────────────────────────────┘
```

**Key Decision Points:**

| Decision | Options | Recommendation |
|----------|---------|----------------|
| Target framework | .NET 6+, .NET Standard 2.0, .NET Framework 4.x | .NET 8+ for new libraries; multi-target if broad compatibility needed |
| Testing framework | xUnit, NUnit, MSTest | xUnit for new projects; NUnit for compatibility |
| Documentation | XML comments, DocFX, Sandcastle | XML comments required; DocFX for rich docs |
| Strong naming | Signed, Unsigned | Sign only if required by consumers |

---

## Quick Reference

| Task | Command |
|------|---------|
| New class library | `dotnet new classlib -n MyLibrary` |
| Build | `dotnet build` |
| Test | `dotnet test` |
| Pack | `dotnet pack` |
| Publish to NuGet | `dotnet nuget push *.nupkg -s nuget.org -k <key>` |
| Multi-target build | `dotnet build -f net8.0` |
| Generate docs | `dotnet build -p:GenerateDocumentationFile=true` |

---

## Project File Structure (.csproj)

### Required Fields for NuGet Publishing

```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <!-- Target framework(s) -->
    <TargetFramework>net8.0</TargetFramework>
    <!-- OR multi-targeting -->
    <!-- <TargetFrameworks>net8.0;netstandard2.0</TargetFrameworks> -->

    <!-- Language version -->
    <LangVersion>latest</LangVersion>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>

    <!-- NuGet package metadata -->
    <PackageId>MyCompany.MyLibrary</PackageId>
    <Version>1.0.0</Version>
    <Authors>Author Name</Authors>
    <Company>Company Name</Company>
    <Description>Brief description of the library</Description>
    <Copyright>Copyright (c) 2025 Company Name</Copyright>

    <!-- Required metadata -->
    <PackageLicenseExpression>MIT</PackageLicenseExpression>
    <!-- OR use license file -->
    <!-- <PackageLicenseFile>LICENSE.txt</PackageLicenseFile> -->

    <PackageProjectUrl>https://github.com/username/repo</PackageProjectUrl>
    <RepositoryUrl>https://github.com/username/repo</RepositoryUrl>
    <RepositoryType>git</RepositoryType>

    <!-- Recommended -->
    <PackageReadmeFile>README.md</PackageReadmeFile>
    <PackageTags>tag1;tag2;tag3</PackageTags>
    <PackageIcon>icon.png</PackageIcon>
    <PackageReleaseNotes>Release notes for this version</PackageReleaseNotes>

    <!-- Generate XML documentation -->
    <GenerateDocumentationFile>true</GenerateDocumentationFile>

    <!-- Deterministic builds for reproducibility -->
    <Deterministic>true</Deterministic>
    <ContinuousIntegrationBuild>true</ContinuousIntegrationBuild>

    <!-- Source link for debugging -->
    <PublishRepositoryUrl>true</PublishRepositoryUrl>
    <EmbedUntrackedSources>true</EmbedUntrackedSources>
    <IncludeSymbols>true</IncludeSymbols>
    <SymbolPackageFormat>snupkg</SymbolPackageFormat>
  </PropertyGroup>

  <!-- Include README and icon in package -->
  <ItemGroup>
    <None Include="README.md" Pack="true" PackagePath="\" />
    <None Include="icon.png" Pack="true" PackagePath="\" />
  </ItemGroup>

  <!-- Source link dependency -->
  <ItemGroup>
    <PackageReference Include="Microsoft.SourceLink.GitHub" Version="8.0.0" PrivateAssets="All" />
  </ItemGroup>
</Project>
```

### Multi-Targeting Configuration

```xml
<PropertyGroup>
  <TargetFrameworks>net8.0;net6.0;netstandard2.0</TargetFrameworks>
</PropertyGroup>

<!-- Conditional compilation -->
<PropertyGroup Condition="'$(TargetFramework)' == 'netstandard2.0'">
  <LangVersion>9.0</LangVersion>
</PropertyGroup>

<!-- Conditional dependencies -->
<ItemGroup Condition="'$(TargetFramework)' == 'netstandard2.0'">
  <PackageReference Include="System.Memory" Version="4.5.5" />
</ItemGroup>
```

### Strong Naming

```xml
<PropertyGroup>
  <SignAssembly>true</SignAssembly>
  <AssemblyOriginatorKeyFile>MyLibrary.snk</AssemblyOriginatorKeyFile>
  <PublicSign Condition="'$(OS)' != 'Windows_NT'">true</PublicSign>
</PropertyGroup>
```

---

## API Design Guidelines

### Namespace Organization

```csharp
// Good: Clear namespace hierarchy
namespace MyCompany.MyLibrary
{
    // Core types
}

namespace MyCompany.MyLibrary.Extensions
{
    // Extension methods
}

namespace MyCompany.MyLibrary.Abstractions
{
    // Interfaces and abstract classes
}

namespace MyCompany.MyLibrary.Internal
{
    // Internal implementation details
}
```

### Class Design Patterns

#### Immutable Value Types

```csharp
/// <summary>
/// Represents a user identifier.
/// </summary>
public readonly record struct UserId
{
    public UserId(Guid value)
    {
        if (value == Guid.Empty)
            throw new ArgumentException("User ID cannot be empty.", nameof(value));

        Value = value;
    }

    public Guid Value { get; }

    public override string ToString() => Value.ToString();
}
```

#### Builder Pattern

```csharp
/// <summary>
/// Builds configuration instances.
/// </summary>
public sealed class ConfigurationBuilder
{
    private TimeSpan _timeout = TimeSpan.FromSeconds(30);
    private int _retryCount = 3;
    private bool _strictMode;

    public ConfigurationBuilder WithTimeout(TimeSpan timeout)
    {
        ArgumentOutOfRangeException.ThrowIfLessThan(timeout, TimeSpan.Zero);
        _timeout = timeout;
        return this;
    }

    public ConfigurationBuilder WithRetryCount(int count)
    {
        ArgumentOutOfRangeException.ThrowIfNegative(count);
        _retryCount = count;
        return this;
    }

    public ConfigurationBuilder EnableStrictMode()
    {
        _strictMode = true;
        return this;
    }

    public Configuration Build()
    {
        return new Configuration(_timeout, _retryCount, _strictMode);
    }
}

/// <summary>
/// Configuration options.
/// </summary>
public sealed class Configuration
{
    internal Configuration(TimeSpan timeout, int retryCount, bool strictMode)
    {
        Timeout = timeout;
        RetryCount = retryCount;
        StrictMode = strictMode;
    }

    public TimeSpan Timeout { get; }
    public int RetryCount { get; }
    public bool StrictMode { get; }
}
```

#### Factory Pattern

```csharp
/// <summary>
/// Factory for creating parsers.
/// </summary>
public static class ParserFactory
{
    public static IParser Create(ParserOptions options)
    {
        return options.Mode switch
        {
            ParserMode.Strict => new StrictParser(options),
            ParserMode.Lenient => new LenientParser(options),
            _ => throw new ArgumentOutOfRangeException(nameof(options.Mode))
        };
    }
}
```

### Interface Design

```csharp
/// <summary>
/// Defines a parser for input data.
/// </summary>
/// <typeparam name="TInput">The input type.</typeparam>
/// <typeparam name="TOutput">The output type.</typeparam>
public interface IParser<in TInput, out TOutput>
{
    /// <summary>
    /// Parses the input and returns the result.
    /// </summary>
    /// <param name="input">The input to parse.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>The parsed output.</returns>
    /// <exception cref="ParseException">Thrown when parsing fails.</exception>
    Task<TOutput> ParseAsync(TInput input, CancellationToken cancellationToken = default);
}
```

### Extension Methods

```csharp
/// <summary>
/// Extension methods for strings.
/// </summary>
public static class StringExtensions
{
    /// <summary>
    /// Converts the string to snake_case.
    /// </summary>
    /// <param name="value">The string to convert.</param>
    /// <returns>The snake_case string.</returns>
    public static string ToSnakeCase(this string value)
    {
        ArgumentNullException.ThrowIfNull(value);

        // Implementation
        return value;
    }

    /// <summary>
    /// Determines whether the string is null or white space.
    /// </summary>
    public static bool IsNullOrWhiteSpace([NotNullWhen(false)] this string? value)
    {
        return string.IsNullOrWhiteSpace(value);
    }
}
```

---

## XML Documentation

### Required Documentation Elements

```csharp
/// <summary>
/// Processes input data and returns the result.
/// </summary>
/// <param name="input">The input data to process.</param>
/// <param name="options">Processing options.</param>
/// <param name="cancellationToken">Cancellation token.</param>
/// <returns>
/// A task that represents the asynchronous operation.
/// The task result contains the processed output.
/// </returns>
/// <exception cref="ArgumentNullException">
/// Thrown when <paramref name="input"/> is null.
/// </exception>
/// <exception cref="ProcessingException">
/// Thrown when processing fails.
/// </exception>
/// <example>
/// <code>
/// var processor = new DataProcessor();
/// var result = await processor.ProcessAsync(data, options);
/// </code>
/// </example>
public async Task<Output> ProcessAsync(
    Input input,
    ProcessingOptions? options = null,
    CancellationToken cancellationToken = default)
{
    ArgumentNullException.ThrowIfNull(input);
    // Implementation
}
```

### Documentation for Properties

```csharp
/// <summary>
/// Gets or sets the timeout duration.
/// </summary>
/// <value>
/// The timeout duration. Default is 30 seconds.
/// </value>
/// <remarks>
/// Setting this to <see cref="TimeSpan.Zero"/> disables timeout.
/// </remarks>
public TimeSpan Timeout { get; set; } = TimeSpan.FromSeconds(30);
```

### Documentation Comments Best Practices

- Always document public APIs
- Use `<see cref=""/>` for cross-references
- Include `<example>` sections for complex APIs
- Document exceptions with `<exception>`
- Use `<remarks>` for additional context
- Include `<value>` for properties

---

## Testing Patterns

### xUnit Test Structure

```csharp
using Xunit;
using FluentAssertions;

namespace MyLibrary.Tests;

public class ParserTests
{
    [Fact]
    public async Task ParseAsync_ValidInput_ReturnsExpectedOutput()
    {
        // Arrange
        var parser = new Parser();
        var input = "valid input";

        // Act
        var result = await parser.ParseAsync(input);

        // Assert
        result.Should().NotBeNull();
        result.Value.Should().Be("expected");
    }

    [Theory]
    [InlineData(null)]
    [InlineData("")]
    [InlineData("   ")]
    public async Task ParseAsync_InvalidInput_ThrowsArgumentException(string input)
    {
        // Arrange
        var parser = new Parser();

        // Act & Assert
        await Assert.ThrowsAsync<ArgumentException>(
            async () => await parser.ParseAsync(input));
    }

    [Fact]
    public void Constructor_NullOptions_ThrowsArgumentNullException()
    {
        // Act & Assert
        var exception = Assert.Throws<ArgumentNullException>(
            () => new Parser(options: null!));

        exception.ParamName.Should().Be("options");
    }
}
```

### NUnit Test Structure

```csharp
using NUnit.Framework;

namespace MyLibrary.Tests;

[TestFixture]
public class ParserTests
{
    private Parser _parser = null!;

    [SetUp]
    public void SetUp()
    {
        _parser = new Parser();
    }

    [Test]
    public async Task ParseAsync_ValidInput_ReturnsExpectedOutput()
    {
        // Arrange
        var input = "valid input";

        // Act
        var result = await _parser.ParseAsync(input);

        // Assert
        Assert.That(result, Is.Not.Null);
        Assert.That(result.Value, Is.EqualTo("expected"));
    }

    [TestCase(null)]
    [TestCase("")]
    [TestCase("   ")]
    public void ParseAsync_InvalidInput_ThrowsArgumentException(string input)
    {
        // Act & Assert
        Assert.ThrowsAsync<ArgumentException>(
            async () => await _parser.ParseAsync(input));
    }

    [TearDown]
    public void TearDown()
    {
        _parser?.Dispose();
    }
}
```

### Test Project Configuration

```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <IsPackable>false</IsPackable>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
  </PropertyGroup>

  <ItemGroup>
    <!-- xUnit -->
    <PackageReference Include="xunit" Version="2.6.2" />
    <PackageReference Include="xunit.runner.visualstudio" Version="2.5.4" />

    <!-- OR NUnit -->
    <!-- <PackageReference Include="NUnit" Version="4.0.1" /> -->
    <!-- <PackageReference Include="NUnit3TestAdapter" Version="4.5.0" /> -->

    <!-- Test utilities -->
    <PackageReference Include="FluentAssertions" Version="6.12.0" />
    <PackageReference Include="Moq" Version="4.20.70" />
    <PackageReference Include="Bogus" Version="35.3.0" />

    <!-- Coverage -->
    <PackageReference Include="coverlet.collector" Version="6.0.0" />
  </ItemGroup>

  <ItemGroup>
    <ProjectReference Include="..\MyLibrary\MyLibrary.csproj" />
  </ItemGroup>
</Project>
```

---

## Source Generators

### Creating a Source Generator

```csharp
using Microsoft.CodeAnalysis;
using Microsoft.CodeAnalysis.CSharp.Syntax;
using Microsoft.CodeAnalysis.Text;
using System.Text;

[Generator]
public class MySourceGenerator : IIncrementalGenerator
{
    public void Initialize(IncrementalGeneratorInitializationContext context)
    {
        // Register attribute syntax provider
        var classDeclarations = context.SyntaxProvider
            .CreateSyntaxProvider(
                predicate: static (s, _) => IsSyntaxTargetForGeneration(s),
                transform: static (ctx, _) => GetSemanticTargetForGeneration(ctx))
            .Where(static m => m is not null);

        // Generate source
        context.RegisterSourceOutput(classDeclarations, Execute);
    }

    private static bool IsSyntaxTargetForGeneration(SyntaxNode node)
    {
        return node is ClassDeclarationSyntax { AttributeLists.Count: > 0 };
    }

    private static ClassDeclarationSyntax? GetSemanticTargetForGeneration(
        GeneratorSyntaxContext context)
    {
        var classDeclaration = (ClassDeclarationSyntax)context.Node;

        // Check for specific attribute
        foreach (var attributeList in classDeclaration.AttributeLists)
        {
            foreach (var attribute in attributeList.Attributes)
            {
                var symbol = context.SemanticModel.GetSymbolInfo(attribute).Symbol;
                if (symbol?.ContainingType.Name == "MyGeneratorAttribute")
                {
                    return classDeclaration;
                }
            }
        }

        return null;
    }

    private void Execute(SourceProductionContext context, ClassDeclarationSyntax? classDeclaration)
    {
        if (classDeclaration is null)
            return;

        var source = GenerateSource(classDeclaration);
        context.AddSource($"{classDeclaration.Identifier}.g.cs",
            SourceText.From(source, Encoding.UTF8));
    }

    private string GenerateSource(ClassDeclarationSyntax classDeclaration)
    {
        // Generate source code
        return $@"
namespace {GetNamespace(classDeclaration)}
{{
    partial class {classDeclaration.Identifier}
    {{
        // Generated code
    }}
}}";
    }

    private string GetNamespace(ClassDeclarationSyntax classDeclaration)
    {
        // Extract namespace
        return string.Empty;
    }
}
```

### Source Generator Project Configuration

```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>netstandard2.0</TargetFramework>
    <LangVersion>latest</LangVersion>
    <Nullable>enable</Nullable>
    <EnforceExtendedAnalyzerRules>true</EnforceExtendedAnalyzerRules>
  </PropertyGroup>

  <ItemGroup>
    <PackageReference Include="Microsoft.CodeAnalysis.CSharp" Version="4.8.0" PrivateAssets="all" />
    <PackageReference Include="Microsoft.CodeAnalysis.Analyzers" Version="3.3.4" PrivateAssets="all" />
  </ItemGroup>
</Project>
```

### Using the Generator

```xml
<!-- In consumer project -->
<ItemGroup>
  <ProjectReference Include="..\MyGenerator\MyGenerator.csproj"
                    OutputItemType="Analyzer"
                    ReferenceOutputAssembly="false" />
</ItemGroup>
```

---

## Versioning and Compatibility

### Semantic Versioning

```xml
<PropertyGroup>
  <!-- Major.Minor.Patch -->
  <Version>2.1.3</Version>

  <!-- Assembly version (only increment for breaking changes) -->
  <AssemblyVersion>2.0.0.0</AssemblyVersion>

  <!-- File version (increment for every build) -->
  <FileVersion>2.1.3.42</FileVersion>
</PropertyGroup>
```

### Package Version from Git

```xml
<PropertyGroup>
  <MinVerTagPrefix>v</MinVerTagPrefix>
  <MinVerDefaultPreReleaseIdentifiers>preview.0</MinVerDefaultPreReleaseIdentifiers>
</PropertyGroup>

<ItemGroup>
  <PackageReference Include="MinVer" Version="5.0.0" PrivateAssets="all" />
</ItemGroup>
```

### API Compatibility Analysis

```xml
<PropertyGroup>
  <GenerateCompatibilitySuppressionFile>true</GenerateCompatibilitySuppressionFile>
</PropertyGroup>

<ItemGroup>
  <PackageReference Include="Microsoft.DotNet.ApiCompat.Task" Version="8.0.100" PrivateAssets="all" />
</ItemGroup>
```

---

## Publishing to NuGet

### Pre-Publish Checklist

- [ ] All tests pass: `dotnet test`
- [ ] Code builds without warnings: `dotnet build -warnaserror`
- [ ] XML documentation is generated
- [ ] Package metadata is complete
- [ ] README.md is current
- [ ] CHANGELOG.md is updated
- [ ] Version number is bumped appropriately
- [ ] License file is included
- [ ] Icon is included (64x64 PNG recommended)
- [ ] Pack succeeds: `dotnet pack`
- [ ] Inspect .nupkg contents

### Publishing Commands

```bash
# Build and pack
dotnet pack -c Release

# Publish to NuGet.org
dotnet nuget push bin/Release/*.nupkg \
  --api-key YOUR_API_KEY \
  --source https://api.nuget.org/v3/index.json

# Publish to GitHub Packages
dotnet nuget push bin/Release/*.nupkg \
  --api-key YOUR_GITHUB_TOKEN \
  --source https://nuget.pkg.github.com/USERNAME/index.json
```

### Package Validation

```xml
<PropertyGroup>
  <EnablePackageValidation>true</EnablePackageValidation>
  <PackageValidationBaselineVersion>1.0.0</PackageValidationBaselineVersion>
</PropertyGroup>
```

---

## Common Dependencies

### Serialization

```xml
<ItemGroup>
  <PackageReference Include="System.Text.Json" Version="8.0.0" />
  <!-- OR -->
  <PackageReference Include="Newtonsoft.Json" Version="13.0.3" />
</ItemGroup>
```

### HTTP Client

```xml
<ItemGroup>
  <PackageReference Include="Microsoft.Extensions.Http" Version="8.0.0" />
</ItemGroup>
```

### Dependency Injection

```xml
<ItemGroup>
  <PackageReference Include="Microsoft.Extensions.DependencyInjection.Abstractions" Version="8.0.0" />
</ItemGroup>
```

### Logging

```xml
<ItemGroup>
  <PackageReference Include="Microsoft.Extensions.Logging.Abstractions" Version="8.0.0" />
</ItemGroup>
```

### Options Pattern

```xml
<ItemGroup>
  <PackageReference Include="Microsoft.Extensions.Options" Version="8.0.0" />
</ItemGroup>
```

---

## Anti-Patterns

### 1. Exposing Internal Types

```csharp
// Bad: Exposes implementation detail
public Dictionary<string, List<InternalType>> GetData();

// Good: Return domain type
public DataCollection GetData();
```

### 2. Breaking Binary Compatibility

```csharp
// v1.0.0
public void Process(string input) { }

// v1.1.0 - WRONG! This breaks binary compatibility
public void Process(string input, int count) { }

// v1.1.0 - Correct: Add overload
public void Process(string input) { }
public void Process(string input, int count) { Process(input); /* new logic */ }
```

### 3. Missing Nullability Annotations

```csharp
// Bad: Unclear nullability
public string? GetName() => null;

// Good: Clear contract
[return: NotNullIfNotNull(nameof(defaultName))]
public string? GetName(string? defaultName = null)
{
    return _name ?? defaultName;
}
```

### 4. Synchronous API Over Async

```csharp
// Bad: Blocking async code
public Result Process()
{
    return ProcessAsync().GetAwaiter().GetResult(); // Deadlock risk
}

// Good: Provide both sync and async
public Result Process() { /* sync implementation */ }
public Task<Result> ProcessAsync(CancellationToken ct = default) { /* async implementation */ }
```

---

## Best Practices

### Use Nullable Reference Types

```xml
<PropertyGroup>
  <Nullable>enable</Nullable>
</PropertyGroup>
```

### Enable All Warnings

```xml
<PropertyGroup>
  <TreatWarningsAsErrors>true</TreatWarningsAsErrors>
  <WarningLevel>9999</WarningLevel>
  <EnforceCodeStyleInBuild>true</EnforceCodeStyleInBuild>
</PropertyGroup>
```

### Use EditorConfig

```ini
# .editorconfig
root = true

[*.cs]
# Naming conventions
dotnet_naming_rule.interfaces_should_be_prefixed_with_i.severity = warning
dotnet_naming_rule.interfaces_should_be_prefixed_with_i.symbols = interface
dotnet_naming_rule.interfaces_should_be_prefixed_with_i.style = begins_with_i

# Code style
csharp_prefer_braces = true:warning
csharp_using_directive_placement = outside_namespace:warning
```

### Analyzer Packages

```xml
<ItemGroup>
  <PackageReference Include="Microsoft.CodeAnalysis.NetAnalyzers" Version="8.0.0" PrivateAssets="all" />
  <PackageReference Include="StyleCop.Analyzers" Version="1.2.0-beta.556" PrivateAssets="all" />
  <PackageReference Include="Roslynator.Analyzers" Version="4.7.0" PrivateAssets="all" />
</ItemGroup>
```

---

## References

- `meta-library-dev` - Foundational library patterns
- [.NET API Design Guidelines](https://learn.microsoft.com/en-us/dotnet/standard/design-guidelines/)
- [NuGet.org](https://www.nuget.org/)
- [.NET SDK Documentation](https://learn.microsoft.com/en-us/dotnet/core/sdk)
- [Source Generators](https://learn.microsoft.com/en-us/dotnet/csharp/roslyn-sdk/source-generators-overview)
