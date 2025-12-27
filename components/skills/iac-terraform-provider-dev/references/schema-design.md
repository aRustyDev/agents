# Terraform Provider Schema Design

Best practices for designing schemas in Terraform providers.

## Attribute Naming Conventions

### General Rules

- Use `snake_case` for all attribute names
- Match API field names where possible (with case conversion)
- Use descriptive, unambiguous names
- Avoid abbreviations unless industry-standard

### Common Patterns

| Concept | Naming Pattern | Example |
|---------|---------------|---------|
| Identifier | `id`, `{resource}_id` | `id`, `vpc_id` |
| Name | `name`, `display_name` | `name` |
| ARN/URN | `arn`, `{resource}_arn` | `arn`, `role_arn` |
| Timestamps | `created_at`, `updated_at` | `created_at` |
| Enabled flags | `enabled`, `{feature}_enabled` | `logging_enabled` |
| Configuration blocks | `{feature}_config`, `{feature}` | `logging_config` |
| Counts | `{resource}_count`, `max_{resource}s` | `instance_count` |

## Attribute Types

### Strings

```go
// Basic string
schema.StringAttribute{
    Required:    true,
    Description: "Name of the resource.",
}

// String with validation
schema.StringAttribute{
    Required: true,
    Validators: []validator.String{
        stringvalidator.LengthBetween(1, 64),
        stringvalidator.RegexMatches(
            regexp.MustCompile(`^[a-z][a-z0-9-]*$`),
            "must start with lowercase letter",
        ),
    },
}

// Enum-like string
schema.StringAttribute{
    Required: true,
    Validators: []validator.String{
        stringvalidator.OneOf("small", "medium", "large"),
    },
    MarkdownDescription: "Size of the instance. Valid values: `small`, `medium`, `large`.",
}
```

### Numbers

```go
// Integer
schema.Int64Attribute{
    Optional: true,
    Computed: true,
    Default:  int64default.StaticInt64(10),
    Validators: []validator.Int64{
        int64validator.Between(1, 100),
    },
}

// Float
schema.Float64Attribute{
    Optional: true,
    Validators: []validator.Float64{
        float64validator.Between(0.0, 1.0),
    },
}
```

### Booleans

```go
schema.BoolAttribute{
    Optional:    true,
    Computed:    true,
    Default:     booldefault.StaticBool(false),
    Description: "Enable logging for the resource.",
}
```

### Lists

```go
// List of strings
schema.ListAttribute{
    Optional:    true,
    ElementType: types.StringType,
    Description: "List of availability zones.",
}

// List with validation
schema.ListAttribute{
    Required:    true,
    ElementType: types.StringType,
    Validators: []validator.List{
        listvalidator.SizeAtLeast(1),
        listvalidator.SizeAtMost(10),
        listvalidator.UniqueValues(),
    },
}
```

### Sets

```go
// Set of strings (unordered, unique)
schema.SetAttribute{
    Optional:    true,
    ElementType: types.StringType,
    Description: "Set of security group IDs.",
}
```

### Maps

```go
// Map of strings (tags pattern)
schema.MapAttribute{
    Optional:    true,
    ElementType: types.StringType,
    Description: "Key-value tags for the resource.",
}
```

## Nested Attributes

### When to Use Each Type

| Type | Use Case |
|------|----------|
| `SingleNestedAttribute` | Single configuration block |
| `ListNestedAttribute` | Ordered list of blocks |
| `SetNestedAttribute` | Unordered unique blocks |
| `MapNestedAttribute` | Named configuration blocks |

### Single Nested (One Configuration Block)

```go
schema.SingleNestedAttribute{
    Optional: true,
    Attributes: map[string]schema.Attribute{
        "enabled": schema.BoolAttribute{
            Required: true,
        },
        "retention_days": schema.Int64Attribute{
            Optional: true,
            Computed: true,
            Default:  int64default.StaticInt64(30),
        },
        "destination": schema.StringAttribute{
            Optional: true,
        },
    },
    Description: "Logging configuration.",
}
```

### List Nested (Ordered, Duplicates Allowed)

```go
schema.ListNestedAttribute{
    Optional: true,
    NestedObject: schema.NestedAttributeObject{
        Attributes: map[string]schema.Attribute{
            "port": schema.Int64Attribute{
                Required: true,
                Validators: []validator.Int64{
                    int64validator.Between(1, 65535),
                },
            },
            "protocol": schema.StringAttribute{
                Required: true,
                Validators: []validator.String{
                    stringvalidator.OneOf("tcp", "udp"),
                },
            },
        },
    },
    Validators: []validator.List{
        listvalidator.SizeAtMost(50),
    },
    Description: "Ingress rules for the security group.",
}
```

### Set Nested (Unordered, Unique)

```go
schema.SetNestedAttribute{
    Optional: true,
    NestedObject: schema.NestedAttributeObject{
        Attributes: map[string]schema.Attribute{
            "cidr_block": schema.StringAttribute{
                Required: true,
            },
            "description": schema.StringAttribute{
                Optional: true,
            },
        },
    },
    Description: "CIDR blocks to allow.",
}
```

### Map Nested (Named Blocks)

```go
schema.MapNestedAttribute{
    Optional: true,
    NestedObject: schema.NestedAttributeObject{
        Attributes: map[string]schema.Attribute{
            "value": schema.StringAttribute{
                Required:  true,
                Sensitive: true,
            },
            "type": schema.StringAttribute{
                Optional: true,
                Computed: true,
                Default:  stringdefault.StaticString("string"),
            },
        },
    },
    Description: "Environment variables. Map keys are variable names.",
}
```

## Computed Attributes

### Types of Computed Values

```go
// Server-assigned ID
schema.StringAttribute{
    Computed:    true,
    Description: "Unique identifier assigned by the API.",
    PlanModifiers: []planmodifier.String{
        stringplanmodifier.UseStateForUnknown(),
    },
}

// Timestamps
schema.StringAttribute{
    Computed:    true,
    Description: "Timestamp when the resource was created.",
}

// Derived values
schema.StringAttribute{
    Computed:    true,
    Description: "Fully qualified domain name.",
}

// Optional with server default
schema.StringAttribute{
    Optional:    true,
    Computed:    true,
    Description: "Region. Defaults to provider region if not specified.",
}
```

## Plan Modifiers

### Common Patterns

```go
import (
    "github.com/hashicorp/terraform-plugin-framework/resource/schema/planmodifier"
    "github.com/hashicorp/terraform-plugin-framework/resource/schema/stringplanmodifier"
)

// Preserve computed value across updates
PlanModifiers: []planmodifier.String{
    stringplanmodifier.UseStateForUnknown(),
}

// Force replacement when changed
PlanModifiers: []planmodifier.String{
    stringplanmodifier.RequiresReplace(),
}

// Force replacement only if was set
PlanModifiers: []planmodifier.String{
    stringplanmodifier.RequiresReplaceIfConfigured(),
}
```

### Custom Plan Modifier

```go
type defaultValueModifier struct {
    defaultValue string
}

func (m defaultValueModifier) Description(ctx context.Context) string {
    return fmt.Sprintf("Sets default value to %q if not configured", m.defaultValue)
}

func (m defaultValueModifier) MarkdownDescription(ctx context.Context) string {
    return m.Description(ctx)
}

func (m defaultValueModifier) PlanModifyString(ctx context.Context, req planmodifier.StringRequest, resp *planmodifier.StringResponse) {
    if req.ConfigValue.IsNull() {
        resp.PlanValue = types.StringValue(m.defaultValue)
    }
}

// Usage
PlanModifiers: []planmodifier.String{
    defaultValueModifier{defaultValue: "us-west-2"},
}
```

## Validators

### String Validators

```go
import "github.com/hashicorp/terraform-plugin-framework-validators/stringvalidator"

Validators: []validator.String{
    // Length
    stringvalidator.LengthAtLeast(1),
    stringvalidator.LengthAtMost(256),
    stringvalidator.LengthBetween(1, 64),

    // Pattern
    stringvalidator.RegexMatches(
        regexp.MustCompile(`^[a-z][a-z0-9-]*$`),
        "must start with lowercase and contain only lowercase, numbers, hyphens",
    ),

    // Allowed values
    stringvalidator.OneOf("option1", "option2", "option3"),

    // Conditional
    stringvalidator.ConflictsWith(path.MatchRoot("other_field")),
    stringvalidator.AtLeastOneOf(
        path.MatchRoot("field_a"),
        path.MatchRoot("field_b"),
    ),
    stringvalidator.ExactlyOneOf(
        path.MatchRoot("field_a"),
        path.MatchRoot("field_b"),
    ),
    stringvalidator.AlsoRequires(path.MatchRoot("related_field")),

    // Format
    stringvalidator.IsURLWithHTTPorHTTPS(),
}
```

### Number Validators

```go
import "github.com/hashicorp/terraform-plugin-framework-validators/int64validator"

Validators: []validator.Int64{
    int64validator.AtLeast(0),
    int64validator.AtMost(100),
    int64validator.Between(1, 65535),
    int64validator.OneOf(1, 2, 4, 8, 16),
}
```

### List Validators

```go
import "github.com/hashicorp/terraform-plugin-framework-validators/listvalidator"

Validators: []validator.List{
    listvalidator.SizeAtLeast(1),
    listvalidator.SizeAtMost(10),
    listvalidator.SizeBetween(1, 5),
    listvalidator.UniqueValues(),
    listvalidator.ValueStringsAre(
        stringvalidator.LengthAtLeast(1),
    ),
}
```

## Default Values

```go
import (
    "github.com/hashicorp/terraform-plugin-framework/resource/schema/booldefault"
    "github.com/hashicorp/terraform-plugin-framework/resource/schema/int64default"
    "github.com/hashicorp/terraform-plugin-framework/resource/schema/stringdefault"
    "github.com/hashicorp/terraform-plugin-framework/resource/schema/listdefault"
)

// Static defaults
schema.BoolAttribute{
    Optional: true,
    Computed: true,
    Default:  booldefault.StaticBool(false),
}

schema.Int64Attribute{
    Optional: true,
    Computed: true,
    Default:  int64default.StaticInt64(30),
}

schema.StringAttribute{
    Optional: true,
    Computed: true,
    Default:  stringdefault.StaticString("default-value"),
}

// Empty list default
schema.ListAttribute{
    Optional:    true,
    Computed:    true,
    ElementType: types.StringType,
    Default:     listdefault.StaticValue(types.ListValueMust(types.StringType, []attr.Value{})),
}
```

## Sensitive Data

```go
// API keys, passwords
schema.StringAttribute{
    Required:    true,
    Sensitive:   true,
    Description: "API key for authentication.",
}

// Sensitive nested attribute
schema.SingleNestedAttribute{
    Optional:  true,
    Sensitive: true,  // Entire block is sensitive
    Attributes: map[string]schema.Attribute{
        "username": schema.StringAttribute{
            Required: true,
        },
        "password": schema.StringAttribute{
            Required:  true,
            Sensitive: true,
        },
    },
}
```

## Deprecation

```go
schema.StringAttribute{
    Optional:            true,
    DeprecationMessage:  "Use 'new_field' instead. This attribute will be removed in version 2.0.",
    Description:         "Deprecated: Use 'new_field' instead.",
}
```

## Documentation

### Description Best Practices

```go
schema.StringAttribute{
    Required: true,
    Description: "Name of the resource. Must be unique within the project.",
    MarkdownDescription: "Name of the resource. Must be unique within the project. " +
        "See [naming conventions](https://docs.example.com/naming) for details.",
}
```

### Using MarkdownDescription

```go
schema.StringAttribute{
    Required: true,
    MarkdownDescription: `Size of the instance.

Valid values:
- ` + "`small`" + ` - 1 vCPU, 2GB RAM
- ` + "`medium`" + ` - 2 vCPU, 4GB RAM
- ` + "`large`" + ` - 4 vCPU, 8GB RAM`,
}
```

## Anti-Patterns to Avoid

### 1. Overly Nested Structures

```go
// BAD: Too deeply nested
schema.SingleNestedAttribute{
    Attributes: map[string]schema.Attribute{
        "level1": schema.SingleNestedAttribute{
            Attributes: map[string]schema.Attribute{
                "level2": schema.SingleNestedAttribute{...},
            },
        },
    },
}

// GOOD: Flatten where possible
schema.SingleNestedAttribute{
    Attributes: map[string]schema.Attribute{
        "level1_option": schema.StringAttribute{...},
        "level2_option": schema.StringAttribute{...},
    },
}
```

### 2. Missing Descriptions

```go
// BAD: No description
schema.StringAttribute{
    Required: true,
}

// GOOD: Clear description
schema.StringAttribute{
    Required:    true,
    Description: "Unique name for the resource. Used as the primary identifier.",
}
```

### 3. Incorrect Optional/Computed

```go
// BAD: Optional without Computed for server-defaulted value
schema.StringAttribute{
    Optional: true,  // Server sets default, but not marked Computed
}

// GOOD: Optional + Computed for server-defaulted values
schema.StringAttribute{
    Optional: true,
    Computed: true,
    Description: "Region. Defaults to provider region if not specified.",
}
```

### 4. Missing Plan Modifiers for IDs

```go
// BAD: Computed ID without UseStateForUnknown
schema.StringAttribute{
    Computed: true,
}

// GOOD: Preserve ID across updates
schema.StringAttribute{
    Computed: true,
    PlanModifiers: []planmodifier.String{
        stringplanmodifier.UseStateForUnknown(),
    },
}
```
