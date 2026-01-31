# Terraform Provider Testing Patterns

Comprehensive testing patterns for Terraform providers using terraform-plugin-testing.

## Installation

```bash
go get github.com/hashicorp/terraform-plugin-testing
```

## Test Setup

### Provider Factories

```go
package provider

import (
    "os"
    "testing"

    "github.com/hashicorp/terraform-plugin-framework/providerserver"
    "github.com/hashicorp/terraform-plugin-go/tfprotov6"
    "github.com/hashicorp/terraform-plugin-testing/helper/resource"
)

// Protocol 6 provider factories
var testAccProtoV6ProviderFactories = map[string]func() (tfprotov6.ProviderServer, error){
    "example": providerserver.NewProtocol6WithError(New("test")()),
}

// Pre-check function for environment validation
func testAccPreCheck(t *testing.T) {
    requiredEnvVars := []string{
        "EXAMPLE_API_KEY",
        "EXAMPLE_ENDPOINT",
    }

    for _, envVar := range requiredEnvVars {
        if v := os.Getenv(envVar); v == "" {
            t.Fatalf("%s must be set for acceptance tests", envVar)
        }
    }
}
```

### Multiple Provider Versions

```go
var testAccProtoV6ProviderFactories = map[string]func() (tfprotov6.ProviderServer, error){
    "example": providerserver.NewProtocol6WithError(New("test")()),
}

// For testing provider upgrades
var testAccProtoV5ProviderFactories = map[string]func() (tfprotov5.ProviderServer, error){
    "example": providerserver.NewProtocol5WithError(New("test")()),
}
```

## Basic Test Structure

### Create, Read, Update, Delete

```go
func TestAccThingResource_full_lifecycle(t *testing.T) {
    resourceName := "example_thing.test"

    resource.Test(t, resource.TestCase{
        PreCheck:                 func() { testAccPreCheck(t) },
        ProtoV6ProviderFactories: testAccProtoV6ProviderFactories,
        Steps: []resource.TestStep{
            // Create
            {
                Config: testAccThingResourceConfig("initial-name", "initial-description"),
                Check: resource.ComposeAggregateTestCheckFunc(
                    resource.TestCheckResourceAttr(resourceName, "name", "initial-name"),
                    resource.TestCheckResourceAttr(resourceName, "description", "initial-description"),
                    resource.TestCheckResourceAttrSet(resourceName, "id"),
                    resource.TestCheckResourceAttrSet(resourceName, "created_at"),
                ),
            },
            // ImportState
            {
                ResourceName:            resourceName,
                ImportState:             true,
                ImportStateVerify:       true,
                ImportStateVerifyIgnore: []string{"sensitive_field"},
            },
            // Update
            {
                Config: testAccThingResourceConfig("updated-name", "updated-description"),
                Check: resource.ComposeAggregateTestCheckFunc(
                    resource.TestCheckResourceAttr(resourceName, "name", "updated-name"),
                    resource.TestCheckResourceAttr(resourceName, "description", "updated-description"),
                ),
            },
            // Delete is implicit when test completes
        },
    })
}

func testAccThingResourceConfig(name, description string) string {
    return fmt.Sprintf(`
resource "example_thing" "test" {
  name        = %[1]q
  description = %[2]q
}
`, name, description)
}
```

## State Checks

### Classic Check Functions

```go
resource.ComposeAggregateTestCheckFunc(
    // Exact value match
    resource.TestCheckResourceAttr(resourceName, "name", "expected-value"),

    // Attribute exists and has any value
    resource.TestCheckResourceAttrSet(resourceName, "id"),

    // Attribute does not exist
    resource.TestCheckNoResourceAttr(resourceName, "deleted_field"),

    // Custom check function
    resource.TestCheckResourceAttrWith(resourceName, "id", func(value string) error {
        if !strings.HasPrefix(value, "thing-") {
            return fmt.Errorf("expected id to start with 'thing-', got: %s", value)
        }
        return nil
    }),

    // Check attribute matches another resource's attribute
    resource.TestCheckResourceAttrPair(
        "example_thing.test", "id",
        "example_other.test", "thing_id",
    ),

    // Check list length
    resource.TestCheckResourceAttr(resourceName, "tags.#", "2"),

    // Check map value
    resource.TestCheckResourceAttr(resourceName, "labels.environment", "test"),
)
```

### Modern State Checks (v1.13.3+)

```go
import (
    "github.com/hashicorp/terraform-plugin-testing/statecheck"
    "github.com/hashicorp/terraform-plugin-testing/knownvalue"
    "github.com/hashicorp/terraform-plugin-testing/tfjsonpath"
)

{
    Config: testAccThingResourceConfig("test"),
    ConfigStateChecks: []statecheck.StateCheck{
        // Exact string match
        statecheck.ExpectKnownValue(
            "example_thing.test",
            tfjsonpath.New("name"),
            knownvalue.StringExact("test"),
        ),

        // Not null
        statecheck.ExpectKnownValue(
            "example_thing.test",
            tfjsonpath.New("id"),
            knownvalue.NotNull(),
        ),

        // Boolean value
        statecheck.ExpectKnownValue(
            "example_thing.test",
            tfjsonpath.New("enabled"),
            knownvalue.Bool(true),
        ),

        // Numeric range (using custom check)
        statecheck.ExpectKnownValue(
            "example_thing.test",
            tfjsonpath.New("count"),
            knownvalue.Int64Exact(5),
        ),

        // List contains
        statecheck.ExpectKnownValue(
            "example_thing.test",
            tfjsonpath.New("tags"),
            knownvalue.ListSizeExact(2),
        ),

        // Nested attribute
        statecheck.ExpectKnownValue(
            "example_thing.test",
            tfjsonpath.New("config").AtMapKey("timeout"),
            knownvalue.Int64Exact(30),
        ),
    },
}
```

## Plan Checks

### Pre-Apply Plan Checks

```go
import (
    "github.com/hashicorp/terraform-plugin-testing/plancheck"
)

{
    Config: testAccThingResourceConfig("test"),
    ConfigPlanChecks: resource.ConfigPlanChecks{
        PreApply: []plancheck.PlanCheck{
            // Expect specific action
            plancheck.ExpectResourceAction("example_thing.test", plancheck.ResourceActionCreate),

            // Expect no changes (for testing no-op scenarios)
            plancheck.ExpectEmptyPlan(),

            // Expect non-empty plan
            plancheck.ExpectNonEmptyPlan(),

            // Expect known value in plan
            plancheck.ExpectKnownValue(
                "example_thing.test",
                tfjsonpath.New("name"),
                knownvalue.StringExact("test"),
            ),

            // Expect unknown value (will be computed)
            plancheck.ExpectUnknownValue(
                "example_thing.test",
                tfjsonpath.New("id"),
            ),

            // Expect sensitive value
            plancheck.ExpectSensitiveValue(
                "example_thing.test",
                tfjsonpath.New("api_key"),
            ),
        },
    },
}
```

### Post-Apply Plan Checks

```go
{
    Config: testAccThingResourceConfig("test"),
    ConfigPlanChecks: resource.ConfigPlanChecks{
        PostApplyPostRefresh: []plancheck.PlanCheck{
            // Verify no drift after apply
            plancheck.ExpectEmptyPlan(),
        },
    },
}
```

### Resource Action Assertions

```go
// Available actions
plancheck.ResourceActionCreate
plancheck.ResourceActionUpdate
plancheck.ResourceActionDestroy
plancheck.ResourceActionDestroyBeforeCreate
plancheck.ResourceActionCreateBeforeDestroy
plancheck.ResourceActionReplace
plancheck.ResourceActionNoop

// Example: Verify update doesn't trigger replace
{
    Config: testAccThingResourceConfig("updated"),
    ConfigPlanChecks: resource.ConfigPlanChecks{
        PreApply: []plancheck.PlanCheck{
            plancheck.ExpectResourceAction("example_thing.test", plancheck.ResourceActionUpdate),
        },
    },
}
```

## Import Testing

### Basic Import

```go
{
    ResourceName:      "example_thing.test",
    ImportState:       true,
    ImportStateVerify: true,
}
```

### Import with ID

```go
{
    ResourceName:      "example_thing.test",
    ImportState:       true,
    ImportStateId:     "custom-import-id",
    ImportStateVerify: true,
}
```

### Import Ignoring Fields

```go
{
    ResourceName:            "example_thing.test",
    ImportState:             true,
    ImportStateVerify:       true,
    ImportStateVerifyIgnore: []string{
        "password",           // Sensitive fields not returned by API
        "computed_timestamp", // Computed values that may differ
    },
}
```

### Custom Import Verification

```go
{
    ResourceName:  "example_thing.test",
    ImportState:   true,
    ImportStateCheck: func(states []*terraform.InstanceState) error {
        if len(states) != 1 {
            return fmt.Errorf("expected 1 state, got %d", len(states))
        }
        if states[0].Attributes["name"] == "" {
            return fmt.Errorf("expected name to be set after import")
        }
        return nil
    },
}
```

## Drift Detection

### Simulating External Changes

```go
func TestAccThingResource_drift_detection(t *testing.T) {
    var resourceID string

    resource.Test(t, resource.TestCase{
        PreCheck:                 func() { testAccPreCheck(t) },
        ProtoV6ProviderFactories: testAccProtoV6ProviderFactories,
        Steps: []resource.TestStep{
            // Create resource
            {
                Config: testAccThingResourceConfig("original"),
                Check: resource.ComposeAggregateTestCheckFunc(
                    resource.TestCheckResourceAttrWith("example_thing.test", "id", func(value string) error {
                        resourceID = value
                        return nil
                    }),
                ),
            },
            // Simulate drift and verify correction
            {
                PreConfig: func() {
                    // Modify resource outside of Terraform
                    client := getTestClient()
                    err := client.UpdateThing(context.Background(), resourceID, "drifted-name")
                    if err != nil {
                        t.Fatalf("failed to simulate drift: %s", err)
                    }
                },
                Config: testAccThingResourceConfig("original"),
                Check: resource.ComposeAggregateTestCheckFunc(
                    // Verify Terraform corrected the drift
                    resource.TestCheckResourceAttr("example_thing.test", "name", "original"),
                ),
                ConfigPlanChecks: resource.ConfigPlanChecks{
                    PreApply: []plancheck.PlanCheck{
                        // Should detect the drift and plan an update
                        plancheck.ExpectResourceAction("example_thing.test", plancheck.ResourceActionUpdate),
                    },
                },
            },
        },
    })
}
```

### Detecting Resource Deletion

```go
{
    PreConfig: func() {
        // Delete resource outside of Terraform
        client := getTestClient()
        client.DeleteThing(context.Background(), resourceID)
    },
    Config: testAccThingResourceConfig("test"),
    ConfigPlanChecks: resource.ConfigPlanChecks{
        PreApply: []plancheck.PlanCheck{
            // Should plan to recreate
            plancheck.ExpectResourceAction("example_thing.test", plancheck.ResourceActionCreate),
        },
    },
}
```

## Data Source Testing

```go
func TestAccThingDataSource_byId(t *testing.T) {
    resource.Test(t, resource.TestCase{
        PreCheck:                 func() { testAccPreCheck(t) },
        ProtoV6ProviderFactories: testAccProtoV6ProviderFactories,
        Steps: []resource.TestStep{
            {
                Config: `
resource "example_thing" "test" {
  name = "datasource-test"
}

data "example_thing" "test" {
  id = example_thing.test.id
}
`,
                Check: resource.ComposeAggregateTestCheckFunc(
                    resource.TestCheckResourceAttrPair(
                        "data.example_thing.test", "id",
                        "example_thing.test", "id",
                    ),
                    resource.TestCheckResourceAttrPair(
                        "data.example_thing.test", "name",
                        "example_thing.test", "name",
                    ),
                ),
            },
        },
    })
}
```

## Error Testing

### Expected Errors

```go
func TestAccThingResource_invalid_config(t *testing.T) {
    resource.Test(t, resource.TestCase{
        PreCheck:                 func() { testAccPreCheck(t) },
        ProtoV6ProviderFactories: testAccProtoV6ProviderFactories,
        Steps: []resource.TestStep{
            {
                Config: `
resource "example_thing" "test" {
  name = ""  # Invalid: empty name
}
`,
                ExpectError: regexp.MustCompile(`name must not be empty`),
            },
        },
    })
}
```

### API Error Handling

```go
func TestAccThingResource_not_found(t *testing.T) {
    resource.Test(t, resource.TestCase{
        PreCheck:                 func() { testAccPreCheck(t) },
        ProtoV6ProviderFactories: testAccProtoV6ProviderFactories,
        Steps: []resource.TestStep{
            {
                Config: `
data "example_thing" "test" {
  id = "non-existent-id"
}
`,
                ExpectError: regexp.MustCompile(`not found`),
            },
        },
    })
}
```

## Parallel Testing

### Unique Resource Names

```go
func TestAccThingResource_parallel(t *testing.T) {
    t.Parallel()  // Enable parallel execution

    // Use unique name to avoid conflicts
    uniqueName := fmt.Sprintf("test-%s", acctest.RandString(8))

    resource.Test(t, resource.TestCase{
        PreCheck:                 func() { testAccPreCheck(t) },
        ProtoV6ProviderFactories: testAccProtoV6ProviderFactories,
        Steps: []resource.TestStep{
            {
                Config: testAccThingResourceConfig(uniqueName),
                Check: resource.ComposeAggregateTestCheckFunc(
                    resource.TestCheckResourceAttr("example_thing.test", "name", uniqueName),
                ),
            },
        },
    })
}
```

## Running Tests

```bash
# Run all acceptance tests
TF_ACC=1 go test -v ./internal/provider/

# Run specific test
TF_ACC=1 go test -v ./internal/provider/ -run TestAccThingResource_basic

# Run with timeout (for long-running resources)
TF_ACC=1 go test -v -timeout 120m ./internal/provider/

# Run with parallelism limit
TF_ACC=1 go test -v -parallel 4 ./internal/provider/

# Run with race detection
TF_ACC=1 go test -v -race ./internal/provider/

# Run with coverage
TF_ACC=1 go test -v -coverprofile=coverage.out ./internal/provider/
go tool cover -html=coverage.out
```

## Best Practices

1. **Always test import** - Every resource should have import tests
2. **Test drift detection** - Verify resources handle external changes
3. **Use unique names** - Avoid test conflicts with random suffixes
4. **Clean up resources** - Tests should be self-cleaning
5. **Test error conditions** - Verify proper error messages
6. **Use plan checks** - Verify expected actions before apply
7. **Enable parallel tests** - Use `t.Parallel()` where safe
8. **Document test requirements** - Note any external dependencies
