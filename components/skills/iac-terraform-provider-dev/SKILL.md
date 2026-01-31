---
name: iac-terraform-provider-dev
description: Develop custom Terraform and OpenTofu providers using the Plugin Framework. Use when creating new providers, implementing CRUD operations, writing acceptance tests, debugging provider issues, or migrating from SDKv2 to Plugin Framework. Covers TDD workflow, resource/data source patterns, and terraform-plugin-testing.
---

# Terraform Provider Development

Build production-quality Terraform and OpenTofu providers using the Plugin Framework. This skill covers the complete provider development lifecycle from design through testing and release.

## Quick Start

For newcomers to Terraform provider development:

1. **Start with TDD**: Always write tests before implementation
2. **Use Plugin Framework**: Modern replacement for SDKv2
3. **Follow the structure**: Use the recommended directory layout
4. **Test thoroughly**: Acceptance tests are crucial for reliability

### 5-Minute Setup

```bash
# 1. Create provider structure
mkdir terraform-provider-{name}
cd terraform-provider-{name}

# 2. Initialize Go module
go mod init terraform-provider-{name}

# 3. Add dependencies
go get github.com/hashicorp/terraform-plugin-framework
go get github.com/hashicorp/terraform-plugin-testing

# 4. Create basic structure (see Provider Structure below)
# 5. Write your first test (see Acceptance Testing)
```

See [Getting Started Guide](references/getting-started.md) for a complete walkthrough.

## Purpose

Guide the development of custom Terraform providers following HashiCorp's best practices, with emphasis on Test-Driven Development (TDD), proper resource lifecycle management, and comprehensive acceptance testing.

## When to Use

- Create new Terraform/OpenTofu providers for APIs or services
- Implement resources, data sources, and functions in providers
- Write acceptance tests using terraform-plugin-testing
- Debug provider behavior and state management issues
- Migrate existing SDKv2 providers to Plugin Framework
- Implement import functionality for resources
- Handle sensitive data and computed attributes properly

## TDD Workflow

Follow the RED → GREEN → REFACTOR cycle for all provider development:

```
┌─────────────────────────────────────────────────────────────┐
│  RED: Write a failing test that defines expected behavior   │
│  ↓                                                          │
│  GREEN: Write minimal code to make the test pass            │
│  ↓                                                          │
│  REFACTOR: Improve code while keeping tests green           │
│  ↓                                                          │
│  REPEAT: Move to next requirement                           │
└─────────────────────────────────────────────────────────────┘
```

**Never skip the RED phase.** A test that never failed provides no confidence.

## Provider Structure

```
terraform-provider-{name}/
├── main.go                    # Provider entry point
├── go.mod                     # Go module definition
├── internal/
│   └── provider/
│       ├── provider.go        # Provider implementation
│       ├── provider_test.go   # Provider tests
│       ├── {resource}_resource.go
│       ├── {resource}_resource_test.go
│       ├── {datasource}_data_source.go
│       └── {datasource}_data_source_test.go
├── examples/
│   ├── provider/
│   │   └── provider.tf
│   ├── resources/
│   │   └── {name}_{resource}/
│   │       └── resource.tf
│   └── data-sources/
│       └── {name}_{datasource}/
│           └── data-source.tf
├── docs/                      # Generated documentation
├── templates/                 # Doc templates (optional)
└── .goreleaser.yml           # Release configuration
```

## Provider Implementation

### Basic Provider

```go
package provider

import (
    "context"

    "github.com/hashicorp/terraform-plugin-framework/datasource"
    "github.com/hashicorp/terraform-plugin-framework/provider"
    "github.com/hashicorp/terraform-plugin-framework/provider/schema"
    "github.com/hashicorp/terraform-plugin-framework/resource"
)

var _ provider.Provider = &ExampleProvider{}

type ExampleProvider struct {
    version string
}

type ExampleProviderModel struct {
    Endpoint types.String `tfsdk:"endpoint"`
    APIKey   types.String `tfsdk:"api_key"`
}

func New(version string) func() provider.Provider {
    return func() provider.Provider {
        return &ExampleProvider{
            version: version,
        }
    }
}

func (p *ExampleProvider) Metadata(ctx context.Context, req provider.MetadataRequest, resp *provider.MetadataResponse) {
    resp.TypeName = "example"
    resp.Version = p.version
}

func (p *ExampleProvider) Schema(ctx context.Context, req provider.SchemaRequest, resp *provider.SchemaResponse) {
    resp.Schema = schema.Schema{
        Attributes: map[string]schema.Attribute{
            "endpoint": schema.StringAttribute{
                Optional:    true,
                Description: "API endpoint URL",
            },
            "api_key": schema.StringAttribute{
                Optional:    true,
                Sensitive:   true,
                Description: "API key for authentication",
            },
        },
    }
}

func (p *ExampleProvider) Configure(ctx context.Context, req provider.ConfigureRequest, resp *provider.ConfigureResponse) {
    var config ExampleProviderModel
    resp.Diagnostics.Append(req.Config.Get(ctx, &config)...)
    if resp.Diagnostics.HasError() {
        return
    }

    // Create API client and store in resp.DataSourceData and resp.ResourceData
    client := NewAPIClient(config.Endpoint.ValueString(), config.APIKey.ValueString())
    resp.DataSourceData = client
    resp.ResourceData = client
}

func (p *ExampleProvider) Resources(ctx context.Context) []func() resource.Resource {
    return []func() resource.Resource{
        NewThingResource,
    }
}

func (p *ExampleProvider) DataSources(ctx context.Context) []func() datasource.DataSource {
    return []func() datasource.DataSource{
        NewThingDataSource,
    }
}
```

### Resource Implementation

```go
package provider

import (
    "context"
    "fmt"

    "github.com/hashicorp/terraform-plugin-framework/path"
    "github.com/hashicorp/terraform-plugin-framework/resource"
    "github.com/hashicorp/terraform-plugin-framework/resource/schema"
    "github.com/hashicorp/terraform-plugin-framework/resource/schema/planmodifier"
    "github.com/hashicorp/terraform-plugin-framework/resource/schema/stringplanmodifier"
    "github.com/hashicorp/terraform-plugin-framework/types"
)

var (
    _ resource.Resource                = &ThingResource{}
    _ resource.ResourceWithImportState = &ThingResource{}
)

type ThingResource struct {
    client *APIClient
}

type ThingResourceModel struct {
    ID          types.String `tfsdk:"id"`
    Name        types.String `tfsdk:"name"`
    Description types.String `tfsdk:"description"`
    Status      types.String `tfsdk:"status"`  // Computed
}

func NewThingResource() resource.Resource {
    return &ThingResource{}
}

func (r *ThingResource) Metadata(ctx context.Context, req resource.MetadataRequest, resp *resource.MetadataResponse) {
    resp.TypeName = req.ProviderTypeName + "_thing"
}

func (r *ThingResource) Schema(ctx context.Context, req resource.SchemaRequest, resp *resource.SchemaResponse) {
    resp.Schema = schema.Schema{
        Description: "Manages a Thing resource.",
        Attributes: map[string]schema.Attribute{
            "id": schema.StringAttribute{
                Computed:    true,
                Description: "Unique identifier for the thing.",
                PlanModifiers: []planmodifier.String{
                    stringplanmodifier.UseStateForUnknown(),
                },
            },
            "name": schema.StringAttribute{
                Required:    true,
                Description: "Name of the thing.",
            },
            "description": schema.StringAttribute{
                Optional:    true,
                Description: "Description of the thing.",
            },
            "status": schema.StringAttribute{
                Computed:    true,
                Description: "Current status of the thing.",
            },
        },
    }
}

func (r *ThingResource) Configure(ctx context.Context, req resource.ConfigureRequest, resp *resource.ConfigureResponse) {
    if req.ProviderData == nil {
        return
    }

    client, ok := req.ProviderData.(*APIClient)
    if !ok {
        resp.Diagnostics.AddError(
            "Unexpected Resource Configure Type",
            fmt.Sprintf("Expected *APIClient, got: %T", req.ProviderData),
        )
        return
    }
    r.client = client
}

func (r *ThingResource) Create(ctx context.Context, req resource.CreateRequest, resp *resource.CreateResponse) {
    var plan ThingResourceModel
    resp.Diagnostics.Append(req.Plan.Get(ctx, &plan)...)
    if resp.Diagnostics.HasError() {
        return
    }

    // Create via API
    thing, err := r.client.CreateThing(ctx, plan.Name.ValueString(), plan.Description.ValueString())
    if err != nil {
        resp.Diagnostics.AddError("Error creating thing", err.Error())
        return
    }

    // Map response to state
    plan.ID = types.StringValue(thing.ID)
    plan.Status = types.StringValue(thing.Status)

    resp.Diagnostics.Append(resp.State.Set(ctx, plan)...)
}

func (r *ThingResource) Read(ctx context.Context, req resource.ReadRequest, resp *resource.ReadResponse) {
    var state ThingResourceModel
    resp.Diagnostics.Append(req.State.Get(ctx, &state)...)
    if resp.Diagnostics.HasError() {
        return
    }

    // Read from API
    thing, err := r.client.GetThing(ctx, state.ID.ValueString())
    if err != nil {
        resp.Diagnostics.AddError("Error reading thing", err.Error())
        return
    }

    // Handle resource not found
    if thing == nil {
        resp.State.RemoveResource(ctx)
        return
    }

    // Map response to state
    state.Name = types.StringValue(thing.Name)
    state.Description = types.StringValue(thing.Description)
    state.Status = types.StringValue(thing.Status)

    resp.Diagnostics.Append(resp.State.Set(ctx, state)...)
}

func (r *ThingResource) Update(ctx context.Context, req resource.UpdateRequest, resp *resource.UpdateResponse) {
    var plan ThingResourceModel
    resp.Diagnostics.Append(req.Plan.Get(ctx, &plan)...)
    if resp.Diagnostics.HasError() {
        return
    }

    var state ThingResourceModel
    resp.Diagnostics.Append(req.State.Get(ctx, &state)...)
    if resp.Diagnostics.HasError() {
        return
    }

    // Update via API
    thing, err := r.client.UpdateThing(ctx, state.ID.ValueString(), plan.Name.ValueString(), plan.Description.ValueString())
    if err != nil {
        resp.Diagnostics.AddError("Error updating thing", err.Error())
        return
    }

    // Map response to state
    plan.ID = state.ID
    plan.Status = types.StringValue(thing.Status)

    resp.Diagnostics.Append(resp.State.Set(ctx, plan)...)
}

func (r *ThingResource) Delete(ctx context.Context, req resource.DeleteRequest, resp *resource.DeleteResponse) {
    var state ThingResourceModel
    resp.Diagnostics.Append(req.State.Get(ctx, &state)...)
    if resp.Diagnostics.HasError() {
        return
    }

    // Delete via API
    err := r.client.DeleteThing(ctx, state.ID.ValueString())
    if err != nil {
        resp.Diagnostics.AddError("Error deleting thing", err.Error())
        return
    }
}

func (r *ThingResource) ImportState(ctx context.Context, req resource.ImportStateRequest, resp *resource.ImportStateResponse) {
    resource.ImportStatePassthroughID(ctx, path.Root("id"), req, resp)
}
```

## Acceptance Testing

Terraform providers require comprehensive acceptance testing to ensure reliability in production.

| Test Pattern | Purpose | Reference |
|-------------|---------|-----------|
| Basic CRUD | Resource lifecycle testing | [Testing Patterns](references/testing-patterns.md#basic-crud) |
| Import State | Verify import functionality | [Testing Patterns](references/testing-patterns.md#import-state) |
| Plan Checks | Validate plan actions | [Testing Patterns](references/testing-patterns.md#plan-checks) |
| State Checks | Modern assertion framework | [Testing Patterns](references/testing-patterns.md#state-checks) |
| Drift Detection | Out-of-band change handling | [Testing Patterns](references/testing-patterns.md#drift-detection) |

### Essential Test Setup

```go
var testAccProtoV6ProviderFactories = map[string]func() (tfprotov6.ProviderServer, error){
    "example": providerserver.NewProtocol6WithError(New("test")()),
}

func testAccPreCheck(t *testing.T) {
    if v := os.Getenv("EXAMPLE_API_KEY"); v == "" {
        t.Fatal("EXAMPLE_API_KEY must be set for acceptance tests")
    }
}
```

### Basic Test Structure

```go
func TestAccThingResource_basic(t *testing.T) {
    resource.Test(t, resource.TestCase{
        PreCheck:                 func() { testAccPreCheck(t) },
        ProtoV6ProviderFactories: testAccProtoV6ProviderFactories,
        Steps: []resource.TestStep{
            {
                Config: testAccThingResourceConfig("test-thing"),
                Check: resource.ComposeAggregateTestCheckFunc(
                    resource.TestCheckResourceAttr("example_thing.test", "name", "test-thing"),
                    resource.TestCheckResourceAttrSet("example_thing.test", "id"),
                ),
            },
        },
    })
}
```

See [Testing Patterns Reference](references/testing-patterns.md) for advanced patterns, plan checks, state checks, and drift detection examples.

## Best Practices

### 1. Schema Design

```go
// Use appropriate attribute types
schema.StringAttribute{
    Required:    true,                    // Must be provided
    Optional:    true,                    // Can be provided
    Computed:    true,                    // Set by provider
    Sensitive:   true,                    // Masked in output
    Description: "Clear description",     // Always document
}

// Use plan modifiers for computed values
PlanModifiers: []planmodifier.String{
    stringplanmodifier.UseStateForUnknown(),  // Preserve on update
    stringplanmodifier.RequiresReplace(),      // Force recreation
}

// Use validators for input validation
Validators: []validator.String{
    stringvalidator.LengthBetween(1, 64),
    stringvalidator.RegexMatches(regexp.MustCompile(`^[a-z]`), "must start with lowercase"),
}
```

### 2. Error Handling

```go
// Always check for errors and add diagnostics
if err != nil {
    resp.Diagnostics.AddError(
        "Error Creating Resource",
        fmt.Sprintf("Could not create thing: %s", err.Error()),
    )
    return
}

// Add warnings for non-fatal issues
resp.Diagnostics.AddWarning(
    "Deprecation Notice",
    "This attribute will be removed in the next major version.",
)
```

### 3. Null vs Unknown Handling

```go
// Check for null before using value
if !plan.Description.IsNull() {
    description = plan.Description.ValueString()
}

// Check for unknown during plan
if plan.Status.IsUnknown() {
    // Value will be known after apply
}
```

### 4. Import Testing

```go
// Always test import functionality
{
    ResourceName:            "example_thing.test",
    ImportState:             true,
    ImportStateVerify:       true,
    ImportStateVerifyIgnore: []string{"password"},  // Skip sensitive fields
}
```

## Running Tests

```bash
# Run all acceptance tests
TF_ACC=1 go test -v ./internal/provider/

# Run specific test
TF_ACC=1 go test -v ./internal/provider/ -run TestAccThingResource_basic

# Run with timeout
TF_ACC=1 go test -v -timeout 120m ./internal/provider/

# Run with parallel limit
TF_ACC=1 go test -v -parallel 4 ./internal/provider/
```

## Documentation Generation

Use `tfplugindocs` to generate documentation:

```bash
# Install
go install github.com/hashicorp/terraform-plugin-docs/cmd/tfplugindocs@latest

# Generate docs
tfplugindocs generate

# Validate docs
tfplugindocs validate
```

## Reference Files

### Development Patterns
- `references/plugin-framework.md` - Plugin Framework patterns and migration from SDKv2
- `references/testing-patterns.md` - Comprehensive testing strategies and examples
- `references/schema-design.md` - Schema design patterns and validators

### CI/CD
- `references/release-workflow.md` - GoReleaser and GitHub Actions for provider releases

## Related Skills

- `iac-terraform-modules-eng` - For Terraform module development
- `iac-terraform-orchestration-ops` - For orchestration with Terragrunt, Terramate, Atmos
