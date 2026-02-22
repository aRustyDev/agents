# Design Token JSON

Output style for generating W3C Design Tokens Community Group (DTCG) format JSON. Use this style when extracting design tokens to a platform-agnostic format.

## W3C Design Tokens Format

The W3C DTCG format uses a nested JSON structure with `$value` and `$type` properties:

```json
{
  "$schema": "https://design-tokens.github.io/community-group/format/",
  "<groupName>": {
    "<tokenName>": {
      "$value": "<value>",
      "$type": "<type>",
      "$description": "<description>"
    }
  }
}
```

## Token Types

### Color Tokens

```json
{
  "color": {
    "primary": {
      "50": {
        "$value": "#E3F2FD",
        "$type": "color",
        "$description": "Lightest primary shade"
      },
      "500": {
        "$value": "#2196F3",
        "$type": "color",
        "$description": "Primary brand color"
      },
      "900": {
        "$value": "#0D47A1",
        "$type": "color",
        "$description": "Darkest primary shade"
      }
    },
    "semantic": {
      "background": {
        "$value": "{color.neutral.50}",
        "$type": "color",
        "$description": "Default background color"
      },
      "surface": {
        "$value": "{color.neutral.100}",
        "$type": "color",
        "$description": "Surface/card background"
      },
      "error": {
        "$value": "#D32F2F",
        "$type": "color",
        "$description": "Error state color"
      }
    }
  }
}
```

### Typography Tokens

```json
{
  "typography": {
    "fontFamily": {
      "primary": {
        "$value": "Inter, system-ui, sans-serif",
        "$type": "fontFamily",
        "$description": "Primary font stack"
      },
      "mono": {
        "$value": "JetBrains Mono, monospace",
        "$type": "fontFamily",
        "$description": "Monospace font for code"
      }
    },
    "fontSize": {
      "xs": {
        "$value": "0.75rem",
        "$type": "dimension",
        "$description": "12px - Extra small text"
      },
      "sm": {
        "$value": "0.875rem",
        "$type": "dimension",
        "$description": "14px - Small text"
      },
      "base": {
        "$value": "1rem",
        "$type": "dimension",
        "$description": "16px - Base text size"
      },
      "lg": {
        "$value": "1.125rem",
        "$type": "dimension",
        "$description": "18px - Large text"
      }
    },
    "fontWeight": {
      "regular": {
        "$value": 400,
        "$type": "fontWeight"
      },
      "medium": {
        "$value": 500,
        "$type": "fontWeight"
      },
      "semibold": {
        "$value": 600,
        "$type": "fontWeight"
      },
      "bold": {
        "$value": 700,
        "$type": "fontWeight"
      }
    },
    "lineHeight": {
      "tight": {
        "$value": 1.25,
        "$type": "number"
      },
      "normal": {
        "$value": 1.5,
        "$type": "number"
      },
      "relaxed": {
        "$value": 1.75,
        "$type": "number"
      }
    }
  }
}
```

### Spacing Tokens

```json
{
  "spacing": {
    "0": {
      "$value": "0",
      "$type": "dimension",
      "$description": "No spacing"
    },
    "1": {
      "$value": "0.25rem",
      "$type": "dimension",
      "$description": "4px"
    },
    "2": {
      "$value": "0.5rem",
      "$type": "dimension",
      "$description": "8px"
    },
    "4": {
      "$value": "1rem",
      "$type": "dimension",
      "$description": "16px"
    },
    "8": {
      "$value": "2rem",
      "$type": "dimension",
      "$description": "32px"
    }
  }
}
```

### Border Radius Tokens

```json
{
  "borderRadius": {
    "none": {
      "$value": "0",
      "$type": "dimension"
    },
    "sm": {
      "$value": "0.125rem",
      "$type": "dimension",
      "$description": "2px"
    },
    "md": {
      "$value": "0.375rem",
      "$type": "dimension",
      "$description": "6px"
    },
    "lg": {
      "$value": "0.5rem",
      "$type": "dimension",
      "$description": "8px"
    },
    "full": {
      "$value": "9999px",
      "$type": "dimension",
      "$description": "Fully rounded"
    }
  }
}
```

### Shadow Tokens

```json
{
  "shadow": {
    "sm": {
      "$value": {
        "color": "#00000026",
        "offsetX": "0",
        "offsetY": "1px",
        "blur": "2px",
        "spread": "0"
      },
      "$type": "shadow",
      "$description": "Small elevation shadow"
    },
    "md": {
      "$value": {
        "color": "#0000001a",
        "offsetX": "0",
        "offsetY": "4px",
        "blur": "6px",
        "spread": "-1px"
      },
      "$type": "shadow",
      "$description": "Medium elevation shadow"
    },
    "lg": {
      "$value": [
        {
          "color": "#0000001a",
          "offsetX": "0",
          "offsetY": "10px",
          "blur": "15px",
          "spread": "-3px"
        },
        {
          "color": "#0000000d",
          "offsetX": "0",
          "offsetY": "4px",
          "blur": "6px",
          "spread": "-2px"
        }
      ],
      "$type": "shadow",
      "$description": "Large elevation with layered shadows"
    }
  }
}
```

### Duration Tokens

```json
{
  "duration": {
    "instant": {
      "$value": "0ms",
      "$type": "duration",
      "$description": "No animation"
    },
    "fast": {
      "$value": "150ms",
      "$type": "duration",
      "$description": "Quick interactions"
    },
    "normal": {
      "$value": "300ms",
      "$type": "duration",
      "$description": "Standard transitions"
    },
    "slow": {
      "$value": "500ms",
      "$type": "duration",
      "$description": "Deliberate animations"
    }
  }
}
```

## Token References

Use curly braces to reference other tokens:

```json
{
  "color": {
    "brand": {
      "$value": "#2196F3",
      "$type": "color"
    }
  },
  "button": {
    "primary": {
      "background": {
        "$value": "{color.brand}",
        "$type": "color",
        "$description": "Uses brand color"
      }
    }
  }
}
```

## Complete Example

```json
{
  "$schema": "https://design-tokens.github.io/community-group/format/",
  "color": {
    "primitive": {
      "blue": {
        "500": { "$value": "#2196F3", "$type": "color" }
      },
      "gray": {
        "50": { "$value": "#FAFAFA", "$type": "color" },
        "900": { "$value": "#212121", "$type": "color" }
      }
    },
    "semantic": {
      "background": { "$value": "{color.primitive.gray.50}", "$type": "color" },
      "text": { "$value": "{color.primitive.gray.900}", "$type": "color" },
      "primary": { "$value": "{color.primitive.blue.500}", "$type": "color" }
    }
  },
  "typography": {
    "fontFamily": {
      "sans": { "$value": "Inter, sans-serif", "$type": "fontFamily" }
    },
    "fontSize": {
      "base": { "$value": "1rem", "$type": "dimension" }
    }
  },
  "spacing": {
    "4": { "$value": "1rem", "$type": "dimension" }
  },
  "borderRadius": {
    "md": { "$value": "0.375rem", "$type": "dimension" }
  }
}
```

## Metadata Properties

Optional metadata for documentation:

| Property | Description | Example |
|----------|-------------|---------|
| `$description` | Human-readable description | `"Primary brand color"` |
| `$extensions` | Tool-specific metadata | `{ "figma": { "variableId": "..." } }` |

## Source Mapping

When extracting from design tools, include source metadata:

```json
{
  "color": {
    "primary": {
      "$value": "#2196F3",
      "$type": "color",
      "$description": "Primary brand color",
      "$extensions": {
        "com.figma": {
          "variableId": "VariableID:1234",
          "collectionId": "VariableCollectionID:5678"
        },
        "com.sketch": {
          "swatchId": "abc-123"
        }
      }
    }
  }
}
```

## File Organization

For large design systems, split into multiple files:

```text
tokens/
├── colors.json       # Color tokens
├── typography.json   # Font tokens
├── spacing.json      # Spacing tokens
├── shadows.json      # Shadow tokens
└── index.json        # Imports all token files
```

## Validation

Generated JSON should:

1. Use valid JSON syntax
2. Include `$type` on all token values
3. Use correct type names per W3C spec
4. Resolve all token references to valid paths
5. Include `$description` for documentation
