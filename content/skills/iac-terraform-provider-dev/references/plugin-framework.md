# Terraform Plugin Framework Reference

The Terraform Plugin Framework is the recommended SDK for building Terraform providers. It provides a more idiomatic Go experience compared to SDKv2.

## Installation

```bash
go get github.com/hashicorp/terraform-plugin-framework
go get github.com/hashicorp/terraform-plugin-go
```

## Provider Entry Point

```go
// main.go
package main

import (
    "context"
    "flag"
    "log"

    "github.com/hashicorp/terraform-plugin-framework/providerserver"
    "github.com/yourorg/terraform-provider-example/internal/provider"
)

var (
    version string = "dev"
)

func main() {
    var debug bool

    flag.BoolVar(&debug, "debug", false, "set to true to run the provider with support for debuggers")
    flag.Parse()

    opts := providerserver.ServeOpts{
        Address: "registry.terraform.io/yourorg/example",
        Debug:   debug,
    }

    err := providerserver.Serve(context.Background(), provider.New(version), opts)
    if err != nil {
        log.Fatal(err.Error())
    }
}
```

## Schema Types

### Attribute Types

| Type | Go Type | Usage |
|------|---------|-------|
| `types.String` | `string` | Text values |
| `types.Bool` | `bool` | Boolean values |
| `types.Int64` | `int64` | Integer values |
| `types.Float64` | `float64` | Floating point values |
| `types.Number` | `*big.Float` | Arbitrary precision numbers |
| `types.List` | `[]T` | Ordered collection |
| `types.Set` | `[]T` | Unordered unique collection |
| `types.Map` | `map[string]T` | Key-value pairs |
| `types.Object` | `struct` | Nested attributes |

### Attribute Modes

```go
// Required: must be set in config
schema.StringAttribute{
    Required: true,
}

// Optional: may be set in config
schema.StringAttribute{
    Optional: true,
}

// Computed: set by provider only
schema.StringAttribute{
    Computed: true,
}

// Optional + Computed: set by config or provider
schema.StringAttribute{
    Optional: true,
    Computed: true,
}
```

### Sensitive Attributes

```go
schema.StringAttribute{
    Required:    true,
    Sensitive:   true,
    Description: "API key for authentication. Value will be masked in logs.",
}
```

## Plan Modifiers

Control how values change during plan:

```go
import (
    "github.com/hashicorp/terraform-plugin-framework/resource/schema/planmodifier"
    "github.com/hashicorp/terraform-plugin-framework/resource/schema/stringplanmodifier"
    "github.com/hashicorp/terraform-plugin-framework/resource/schema/int64planmodifier"
    "github.com/hashicorp/terraform-plugin-framework/resource/schema/boolplanmodifier"
)

// Preserve value from state if unknown in plan
schema.StringAttribute{
    Computed: true,
    PlanModifiers: []planmodifier.String{
        stringplanmodifier.UseStateForUnknown(),
    },
}

// Force resource replacement when value changes
schema.StringAttribute{
    Required: true,
    PlanModifiers: []planmodifier.String{
        stringplanmodifier.RequiresReplace(),
    },
}

// Conditional replacement
schema.StringAttribute{
    Optional: true,
    PlanModifiers: []planmodifier.String{
        stringplanmodifier.RequiresReplaceIf(
            func(ctx context.Context, req planmodifier.StringRequest, resp *stringplanmodifier.RequiresReplaceIfFuncResponse) {
                resp.RequiresReplace = req.StateValue.ValueString() != "" && req.PlanValue.ValueString() != req.StateValue.ValueString()
            },
            "Replacement required when changing non-empty value",
            "Replacement required when changing non-empty value",
        ),
    },
}
```

## Validators

Input validation:

```go
import (
    "github.com/hashicorp/terraform-plugin-framework-validators/stringvalidator"
    "github.com/hashicorp/terraform-plugin-framework-validators/int64validator"
    "github.com/hashicorp/terraform-plugin-framework-validators/listvalidator"
    "github.com/hashicorp/terraform-plugin-framework/schema/validator"
)

schema.StringAttribute{
    Required: true,
    Validators: []validator.String{
        // Length constraints
        stringvalidator.LengthBetween(1, 64),
        stringvalidator.LengthAtLeast(1),
        stringvalidator.LengthAtMost(256),

        // Pattern matching
        stringvalidator.RegexMatches(
            regexp.MustCompile(`^[a-z][a-z0-9-]*$`),
            "must start with lowercase letter and contain only lowercase letters, numbers, and hyphens",
        ),

        // Allowed values
        stringvalidator.OneOf("small", "medium", "large"),

        // Conditional validation
        stringvalidator.ConflictsWith(path.Expressions{
            path.MatchRoot("other_attribute"),
        }...),

        stringvalidator.AtLeastOneOf(path.Expressions{
            path.MatchRoot("attribute_a"),
            path.MatchRoot("attribute_b"),
        }...),
    },
}

schema.Int64Attribute{
    Optional: true,
    Validators: []validator.Int64{
        int64validator.Between(1, 100),
        int64validator.AtLeast(0),
        int64validator.AtMost(1000),
    },
}
```

## Nested Attributes

### Single Nested

```go
schema.SingleNestedAttribute{
    Required: true,
    Attributes: map[string]schema.Attribute{
        "host": schema.StringAttribute{
            Required: true,
        },
        "port": schema.Int64Attribute{
            Optional: true,
            Computed: true,
        },
    },
}
```

### List Nested

```go
schema.ListNestedAttribute{
    Optional: true,
    NestedObject: schema.NestedAttributeObject{
        Attributes: map[string]schema.Attribute{
            "name": schema.StringAttribute{
                Required: true,
            },
            "value": schema.StringAttribute{
                Required: true,
            },
        },
    },
}
```

### Set Nested

```go
schema.SetNestedAttribute{
    Optional: true,
    NestedObject: schema.NestedAttributeObject{
        Attributes: map[string]schema.Attribute{
            "cidr": schema.StringAttribute{
                Required: true,
            },
            "description": schema.StringAttribute{
                Optional: true,
            },
        },
    },
}
```

### Map Nested

```go
schema.MapNestedAttribute{
    Optional: true,
    NestedObject: schema.NestedAttributeObject{
        Attributes: map[string]schema.Attribute{
            "enabled": schema.BoolAttribute{
                Required: true,
            },
            "priority": schema.Int64Attribute{
                Optional: true,
            },
        },
    },
}
```

## Data Source Implementation

```go
var _ datasource.DataSource = &ThingDataSource{}

type ThingDataSource struct {
    client *APIClient
}

type ThingDataSourceModel struct {
    ID     types.String `tfsdk:"id"`
    Name   types.String `tfsdk:"name"`
    Status types.String `tfsdk:"status"`
}

func NewThingDataSource() datasource.DataSource {
    return &ThingDataSource{}
}

func (d *ThingDataSource) Metadata(ctx context.Context, req datasource.MetadataRequest, resp *datasource.MetadataResponse) {
    resp.TypeName = req.ProviderTypeName + "_thing"
}

func (d *ThingDataSource) Schema(ctx context.Context, req datasource.SchemaRequest, resp *datasource.SchemaResponse) {
    resp.Schema = schema.Schema{
        Description: "Fetches a Thing by ID or name.",
        Attributes: map[string]schema.Attribute{
            "id": schema.StringAttribute{
                Optional:    true,
                Computed:    true,
                Description: "Unique identifier. Either id or name must be specified.",
            },
            "name": schema.StringAttribute{
                Optional:    true,
                Computed:    true,
                Description: "Name of the thing. Either id or name must be specified.",
            },
            "status": schema.StringAttribute{
                Computed:    true,
                Description: "Current status of the thing.",
            },
        },
    }
}

func (d *ThingDataSource) Configure(ctx context.Context, req datasource.ConfigureRequest, resp *datasource.ConfigureResponse) {
    if req.ProviderData == nil {
        return
    }
    d.client = req.ProviderData.(*APIClient)
}

func (d *ThingDataSource) Read(ctx context.Context, req datasource.ReadRequest, resp *datasource.ReadResponse) {
    var config ThingDataSourceModel
    resp.Diagnostics.Append(req.Config.Get(ctx, &config)...)
    if resp.Diagnostics.HasError() {
        return
    }

    var thing *Thing
    var err error

    if !config.ID.IsNull() {
        thing, err = d.client.GetThing(ctx, config.ID.ValueString())
    } else if !config.Name.IsNull() {
        thing, err = d.client.GetThingByName(ctx, config.Name.ValueString())
    } else {
        resp.Diagnostics.AddError(
            "Missing Required Attribute",
            "Either 'id' or 'name' must be specified.",
        )
        return
    }

    if err != nil {
        resp.Diagnostics.AddError("Error reading thing", err.Error())
        return
    }

    config.ID = types.StringValue(thing.ID)
    config.Name = types.StringValue(thing.Name)
    config.Status = types.StringValue(thing.Status)

    resp.Diagnostics.Append(resp.State.Set(ctx, config)...)
}
```

## Migration from SDKv2

### Key Differences

| SDKv2 | Plugin Framework |
|-------|------------------|
| `schema.Schema{}` | `schema.Schema{}` (different package) |
| `d.Get("attr")` | `req.Plan.Get(ctx, &model)` |
| `d.Set("attr", val)` | `resp.State.Set(ctx, model)` |
| `d.SetId("")` | `resp.State.RemoveResource(ctx)` |
| `ResourceData` | Typed model structs |
| `diag.Diagnostics` | `diag.Diagnostics` (compatible) |

### Migration Steps

1. **Update dependencies**
   ```bash
   go get github.com/hashicorp/terraform-plugin-framework
   go get github.com/hashicorp/terraform-plugin-framework-validators
   ```

2. **Create typed models**
   ```go
   // Before (SDKv2)
   d.Get("name").(string)

   // After (Framework)
   type Model struct {
       Name types.String `tfsdk:"name"`
   }
   var model Model
   req.Plan.Get(ctx, &model)
   model.Name.ValueString()
   ```

3. **Update CRUD methods**
   - `Create` → `Create(ctx, req, resp)`
   - `Read` → `Read(ctx, req, resp)`
   - `Update` → `Update(ctx, req, resp)`
   - `Delete` → `Delete(ctx, req, resp)`

4. **Update schema**
   ```go
   // Before
   "name": {
       Type:     schema.TypeString,
       Required: true,
   }

   // After
   "name": schema.StringAttribute{
       Required: true,
   }
   ```

## Protocol Version

The Plugin Framework supports both Protocol 5 (Terraform 0.12+) and Protocol 6 (Terraform 1.0+):

```go
// Protocol 6 (recommended for new providers)
providerserver.NewProtocol6WithError(New("test")())

// Protocol 5 (for backward compatibility)
providerserver.NewProtocol5WithError(New("test")())
```

## Resources

- [Plugin Framework Documentation](https://developer.hashicorp.com/terraform/plugin/framework)
- [Plugin Framework GitHub](https://github.com/hashicorp/terraform-plugin-framework)
- [Migration Guide](https://developer.hashicorp.com/terraform/plugin/framework/migrating)
- [Best Practices](https://developer.hashicorp.com/terraform/plugin/best-practices)
