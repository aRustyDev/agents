# IR Schema Reference

Complete JSON Schema specification for the Intermediate Representation.

## Root Schema

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "CodebaseIR",
  "description": "Intermediate Representation for cross-language code conversion",
  "type": "object",
  "required": ["version", "source_language", "source_path"],
  "properties": {
    "version": {
      "type": "string",
      "pattern": "^\\d+\\.\\d+$",
      "description": "IR schema version"
    },
    "source_language": {
      "type": "string",
      "enum": ["python", "rust", "typescript", "go", "scala", "roc", "java", "kotlin", "swift", "elixir"]
    },
    "source_path": {
      "type": "string",
      "description": "Path to source file or directory"
    },
    "modules": {
      "type": "array",
      "items": {"$ref": "#/$defs/ModuleDef"}
    },
    "types": {
      "type": "array",
      "items": {"$ref": "#/$defs/TypeDef"}
    },
    "functions": {
      "type": "array",
      "items": {"$ref": "#/$defs/FunctionDef"}
    },
    "annotations": {
      "type": "array",
      "items": {"$ref": "#/$defs/Annotation"}
    }
  }
}
```

## Module Definition

```json
{
  "$defs": {
    "ModuleDef": {
      "type": "object",
      "required": ["name"],
      "properties": {
        "name": {"type": "string"},
        "path": {"type": "string"},
        "imports": {
          "type": "array",
          "items": {"$ref": "#/$defs/Import"}
        },
        "exports": {
          "type": "array",
          "items": {"type": "string"}
        },
        "dependencies": {
          "type": "array",
          "items": {"type": "string"}
        }
      }
    },
    "Import": {
      "type": "object",
      "required": ["module"],
      "properties": {
        "module": {"type": "string"},
        "items": {
          "type": "array",
          "items": {"type": "string"}
        },
        "alias": {"type": "string"}
      }
    }
  }
}
```

## Type Definitions

```json
{
  "$defs": {
    "TypeDef": {
      "type": "object",
      "required": ["name", "kind"],
      "properties": {
        "name": {"type": "string"},
        "kind": {
          "type": "string",
          "enum": ["struct", "enum", "interface", "alias", "class", "adt"]
        },
        "generics": {
          "type": "array",
          "items": {"$ref": "#/$defs/GenericParam"}
        },
        "properties": {
          "type": "array",
          "items": {"$ref": "#/$defs/Property"}
        },
        "methods": {
          "type": "array",
          "items": {"$ref": "#/$defs/MethodDef"}
        },
        "variants": {
          "type": "array",
          "items": {"$ref": "#/$defs/Variant"},
          "description": "For enum/ADT types"
        },
        "implements": {
          "type": "array",
          "items": {"type": "string"}
        },
        "extends": {"type": "string"}
      }
    },
    "GenericParam": {
      "type": "object",
      "required": ["name"],
      "properties": {
        "name": {"type": "string"},
        "variance": {
          "type": "string",
          "enum": ["invariant", "covariant", "contravariant"]
        },
        "bounds": {
          "type": "array",
          "items": {"type": "string"}
        },
        "default": {"type": "string"}
      }
    },
    "Property": {
      "type": "object",
      "required": ["name", "type"],
      "properties": {
        "name": {"type": "string"},
        "type": {"type": "string"},
        "nullable": {"type": "boolean", "default": false},
        "mutable": {"type": "boolean", "default": true},
        "visibility": {
          "type": "string",
          "enum": ["public", "private", "protected", "internal"]
        },
        "default": {}
      }
    },
    "Variant": {
      "type": "object",
      "required": ["name"],
      "properties": {
        "name": {"type": "string"},
        "fields": {
          "type": "array",
          "items": {"$ref": "#/$defs/Property"}
        },
        "value": {
          "description": "For simple enum variants"
        }
      }
    }
  }
}
```

## Function Definitions

```json
{
  "$defs": {
    "FunctionDef": {
      "type": "object",
      "required": ["name"],
      "properties": {
        "name": {"type": "string"},
        "parameters": {
          "type": "array",
          "items": {"$ref": "#/$defs/Parameter"}
        },
        "return_type": {"type": "string"},
        "generics": {
          "type": "array",
          "items": {"$ref": "#/$defs/GenericParam"}
        },
        "purity": {
          "type": "string",
          "enum": ["pure", "impure", "io", "async"]
        },
        "async": {"type": "boolean", "default": false},
        "visibility": {
          "type": "string",
          "enum": ["public", "private", "protected", "internal"]
        },
        "body": {
          "type": "array",
          "items": {"$ref": "#/$defs/Statement"}
        }
      }
    },
    "MethodDef": {
      "allOf": [
        {"$ref": "#/$defs/FunctionDef"},
        {
          "properties": {
            "receiver": {
              "type": "string",
              "enum": ["self", "self_mut", "self_ref", "static"]
            }
          }
        }
      ]
    },
    "Parameter": {
      "type": "object",
      "required": ["name"],
      "properties": {
        "name": {"type": "string"},
        "type": {"type": "string"},
        "default": {},
        "variadic": {"type": "boolean", "default": false}
      }
    }
  }
}
```

## Statements and Expressions

```json
{
  "$defs": {
    "Statement": {
      "type": "object",
      "required": ["kind"],
      "properties": {
        "kind": {
          "type": "string",
          "enum": [
            "binding", "assignment", "return", "expression",
            "if", "match", "loop", "for", "while",
            "break", "continue", "throw", "try"
          ]
        }
      },
      "allOf": [
        {
          "if": {"properties": {"kind": {"const": "binding"}}},
          "then": {
            "properties": {
              "name": {"type": "string"},
              "type": {"type": "string"},
              "mutable": {"type": "boolean"},
              "value": {"$ref": "#/$defs/Expression"}
            },
            "required": ["name", "value"]
          }
        },
        {
          "if": {"properties": {"kind": {"const": "if"}}},
          "then": {
            "properties": {
              "condition": {"$ref": "#/$defs/Expression"},
              "then_branch": {"type": "array", "items": {"$ref": "#/$defs/Statement"}},
              "else_branch": {"type": "array", "items": {"$ref": "#/$defs/Statement"}}
            },
            "required": ["condition", "then_branch"]
          }
        },
        {
          "if": {"properties": {"kind": {"const": "match"}}},
          "then": {
            "properties": {
              "value": {"$ref": "#/$defs/Expression"},
              "arms": {
                "type": "array",
                "items": {"$ref": "#/$defs/MatchArm"}
              }
            },
            "required": ["value", "arms"]
          }
        }
      ]
    },
    "Expression": {
      "type": "object",
      "required": ["kind"],
      "properties": {
        "kind": {
          "type": "string",
          "enum": [
            "literal", "variable", "binary_op", "unary_op",
            "call", "method_call", "field_access", "index",
            "lambda", "construct", "cast", "if_expr", "match_expr"
          ]
        }
      }
    },
    "MatchArm": {
      "type": "object",
      "required": ["pattern", "body"],
      "properties": {
        "pattern": {"$ref": "#/$defs/Pattern"},
        "guard": {"$ref": "#/$defs/Expression"},
        "body": {
          "oneOf": [
            {"$ref": "#/$defs/Expression"},
            {"type": "array", "items": {"$ref": "#/$defs/Statement"}}
          ]
        }
      }
    },
    "Pattern": {
      "type": "object",
      "required": ["kind"],
      "properties": {
        "kind": {
          "type": "string",
          "enum": [
            "wildcard", "literal", "binding", "variant",
            "tuple", "struct", "list", "or"
          ]
        }
      }
    }
  }
}
```

## Annotations

```json
{
  "$defs": {
    "Annotation": {
      "type": "object",
      "required": ["kind", "target"],
      "properties": {
        "kind": {
          "type": "string",
          "pattern": "^[A-Z]{2,3}-[A-Z]{2,3}?-?\\d{3}$",
          "description": "Gap identifier (e.g., RS-001, PY-RS-001)"
        },
        "target": {
          "type": "string",
          "description": "Element the annotation applies to"
        },
        "severity": {
          "type": "string",
          "enum": ["critical", "high", "medium", "low", "info"]
        },
        "message": {"type": "string"},
        "source_pattern": {
          "type": "string",
          "description": "Original source pattern"
        },
        "suggestion": {
          "type": "string",
          "description": "Recommended resolution"
        },
        "line": {"type": "integer"},
        "column": {"type": "integer"}
      }
    }
  }
}
```

## Type Reference Syntax

Types are referenced using a simple string syntax:

| Syntax | Meaning |
|--------|---------|
| `Int` | Primitive integer |
| `Option[T]` | Optional type |
| `Result[T,E]` | Result type |
| `List[T]` | List type |
| `Dict[K,V]` | Dictionary type |
| `Fn(A,B)->C` | Function type |
| `T & U` | Intersection type |
| `T \| U` | Union type |
| `T?` | Nullable type |
| `*T` | Pointer/reference type |

## Validation

The IR must satisfy these constraints:

1. All type references must resolve to defined types or primitives
2. All function calls must reference defined functions
3. All variable references must be in scope
4. Pattern match must be exhaustive (annotated if not verifiable)
5. Generic parameters must be used consistently
