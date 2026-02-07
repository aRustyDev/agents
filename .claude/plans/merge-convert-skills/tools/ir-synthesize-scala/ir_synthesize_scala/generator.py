"""Scala code generator.

Generates idiomatic Scala source code from IR representation.
"""

from __future__ import annotations

import re
from typing import Any, Optional

from ir_core.models import FunctionDef, TypeDef, TypeKind


# Type mapping from various languages to Scala
TYPE_MAP: dict[str, str] = {
    # Python types
    "int": "Int",
    "float": "Double",
    "str": "String",
    "bool": "Boolean",
    "bytes": "Array[Byte]",
    "None": "Unit",
    "NoneType": "Unit",
    "Any": "Any",
    "object": "AnyRef",

    # Rust types
    "i8": "Byte",
    "i16": "Short",
    "i32": "Int",
    "i64": "Long",
    "u8": "Byte",
    "u16": "Short",
    "u32": "Int",
    "u64": "Long",
    "f32": "Float",
    "f64": "Double",
    "String": "String",
    "bool": "Boolean",
    "char": "Char",
    "()" : "Unit",

    # TypeScript types
    "number": "Double",
    "string": "String",
    "boolean": "Boolean",
    "void": "Unit",
    "null": "Null",
    "undefined": "Unit",
    "unknown": "Any",
    "never": "Nothing",

    # Go types
    "int64": "Long",
    "float64": "Double",
    "error": "Throwable",

    # Roc types
    "I64": "Long",
    "I32": "Int",
    "F64": "Double",
    "F32": "Float",
    "Str": "String",
    "Bool": "Boolean",
    "U8": "Byte",
    "U64": "Long",
}

# Generic type mapping
GENERIC_TYPE_MAP: dict[str, str] = {
    # Python
    "List": "List",
    "Dict": "Map",
    "Set": "Set",
    "Tuple": "Tuple",
    "Optional": "Option",
    "Union": "Either",  # For 2 types

    # Rust
    "Vec": "List",
    "HashMap": "Map",
    "HashSet": "Set",
    "Option": "Option",
    "Result": "Either",
    "Box": "",  # Scala uses references by default

    # TypeScript
    "Array": "List",
    "Map": "Map",
    "Set": "Set",
    "Promise": "Future",

    # Go
    "[]": "List",
    "map": "Map",

    # Roc
    "List": "List",
    "Dict": "Map",
}


class ScalaCodeGenerator:
    """Generates Scala source code from IR."""

    def __init__(self) -> None:
        """Initialize the generator."""
        self._indent = "  "

    def _convert_type(self, type_str: str) -> str:
        """Convert a type string to Scala type."""
        if not type_str:
            return "Any"

        type_str = type_str.strip()

        # Direct mapping
        if type_str in TYPE_MAP:
            return TYPE_MAP[type_str]

        # Generic types: List[T], Dict[K, V], etc.
        # Python style: List[int]
        match = re.match(r'(\w+)\[(.+)\]', type_str)
        if match:
            outer = match.group(1)
            inner = match.group(2)

            if outer in GENERIC_TYPE_MAP:
                scala_outer = GENERIC_TYPE_MAP[outer]
                if scala_outer:
                    # Convert inner types
                    inner_types = self._split_type_args(inner)
                    scala_inner = ", ".join(self._convert_type(t) for t in inner_types)
                    return f"{scala_outer}[{scala_inner}]"
                else:
                    # Box-like: just use inner type
                    return self._convert_type(inner)

        # Rust style: Vec<T>
        match = re.match(r'(\w+)<(.+)>', type_str)
        if match:
            outer = match.group(1)
            inner = match.group(2)

            if outer in GENERIC_TYPE_MAP:
                scala_outer = GENERIC_TYPE_MAP[outer]
                if scala_outer:
                    inner_types = self._split_type_args(inner)
                    scala_inner = ", ".join(self._convert_type(t) for t in inner_types)
                    return f"{scala_outer}[{scala_inner}]"
                else:
                    return self._convert_type(inner)

        # Function types: (A) -> B or A => B
        if '->' in type_str:
            parts = type_str.split('->')
            if len(parts) == 2:
                param = self._convert_type(parts[0].strip().strip('()'))
                ret = self._convert_type(parts[1].strip())
                return f"{param} => {ret}"

        # Already Scala type or custom type
        return type_str

    def _split_type_args(self, type_args: str) -> list[str]:
        """Split type arguments, respecting nested brackets."""
        args = []
        depth = 0
        current = ""

        for char in type_args:
            if char in '[<(':
                depth += 1
                current += char
            elif char in ']>)':
                depth -= 1
                current += char
            elif char == ',' and depth == 0:
                if current.strip():
                    args.append(current.strip())
                current = ""
            else:
                current += char

        if current.strip():
            args.append(current.strip())

        return args

    def generate_package(self, package_name: str) -> str:
        """Generate package declaration."""
        return f"package {package_name}\n"

    def generate_import(
        self,
        path: str,
        selectors: Optional[list[str]] = None,
        is_wildcard: bool = False,
    ) -> str:
        """Generate import statement."""
        if is_wildcard:
            return f"import {path}.*\n"
        elif selectors:
            selector_str = ", ".join(selectors)
            return f"import {path}.{{{selector_str}}}\n"
        else:
            return f"import {path}\n"

    def generate_trait(
        self,
        type_def: TypeDef,
        indent: int = 0,
    ) -> str:
        """Generate trait definition."""
        ind = self._indent * indent
        lines = []

        # Trait header
        name = type_def.name
        type_params = self._format_type_params(type_def.type_params)
        extends = self._format_extends(type_def.extends)

        header = f"{ind}trait {name}"
        if type_params:
            header += f"[{type_params}]"
        if extends:
            header += f" extends {extends}"
        header += " {"
        lines.append(header)

        # Methods
        if type_def.methods:
            for method in type_def.methods:
                lines.append(self._generate_method_signature(method, indent + 1))

        lines.append(f"{ind}}}")
        return "\n".join(lines)

    def generate_case_class(
        self,
        type_def: TypeDef,
        indent: int = 0,
    ) -> str:
        """Generate case class definition."""
        ind = self._indent * indent

        name = type_def.name
        type_params = self._format_type_params(type_def.type_params)
        extends = self._format_extends(type_def.extends)

        # Fields
        fields = []
        for prop in type_def.properties or []:
            field_type = self._convert_type(prop.get("type", "Any"))
            field_name = prop.get("name", "")
            default = prop.get("default")

            field_str = f"{field_name}: {field_type}"
            if default:
                field_str += f" = {default}"
            fields.append(field_str)

        params_str = ", ".join(fields)

        # Build case class
        header = f"{ind}case class {name}"
        if type_params:
            header += f"[{type_params}]"
        header += f"({params_str})"
        if extends:
            header += f" extends {extends}"

        return header

    def generate_class(
        self,
        type_def: TypeDef,
        indent: int = 0,
    ) -> str:
        """Generate class definition."""
        ind = self._indent * indent
        lines = []

        name = type_def.name
        type_params = self._format_type_params(type_def.type_params)
        extends = self._format_extends(type_def.extends)

        # Constructor parameters
        params = []
        for prop in type_def.properties or []:
            vis = "private " if prop.get("visibility") == "private" else ""
            field_type = self._convert_type(prop.get("type", "Any"))
            field_name = prop.get("name", "")
            params.append(f"{vis}val {field_name}: {field_type}")

        params_str = ", ".join(params) if params else ""

        # Class header
        header = f"{ind}class {name}"
        if type_params:
            header += f"[{type_params}]"
        if params_str:
            header += f"({params_str})"
        if extends:
            header += f" extends {extends}"
        header += " {"
        lines.append(header)

        # Methods
        if type_def.methods:
            for method in type_def.methods:
                if method.get("abstract"):
                    lines.append(self._generate_method_signature(method, indent + 1))
                else:
                    lines.append(self._generate_method(method, indent + 1))

        lines.append(f"{ind}}}")
        return "\n".join(lines)

    def generate_object(
        self,
        type_def: TypeDef,
        indent: int = 0,
    ) -> str:
        """Generate object definition."""
        ind = self._indent * indent
        lines = []

        name = type_def.name
        extends = self._format_extends(type_def.extends)

        header = f"{ind}object {name}"
        if extends:
            header += f" extends {extends}"
        header += " {"
        lines.append(header)

        # Methods
        if type_def.methods:
            for method in type_def.methods:
                lines.append(self._generate_method(method, indent + 1))

        lines.append(f"{ind}}}")
        return "\n".join(lines)

    def generate_function(
        self,
        func_def: FunctionDef,
        indent: int = 0,
    ) -> str:
        """Generate function definition."""
        ind = self._indent * indent

        name = func_def.name
        return_type = self._convert_type(func_def.return_type or "Unit")

        # Type parameters
        type_params = ""
        if func_def.metadata and func_def.metadata.get("type_params"):
            type_params = self._format_type_params(func_def.metadata["type_params"])

        # Parameters
        params = []
        for param in func_def.parameters:
            param_type = self._convert_type(param.type_annotation or "Any")
            params.append(f"{param.name}: {param_type}")
        params_str = ", ".join(params)

        # Implicit parameters
        implicit_str = ""
        if func_def.metadata and func_def.metadata.get("implicit_params"):
            implicits = []
            for imp in func_def.metadata["implicit_params"]:
                imp_type = self._convert_type(imp.get("type", "Any"))
                implicits.append(f"{imp.get('name')}: {imp_type}")
            implicit_str = f"(using {', '.join(implicits)})"

        # Build function
        header = f"{ind}def {name}"
        if type_params:
            header += f"[{type_params}]"
        header += f"({params_str})"
        if implicit_str:
            header += implicit_str
        header += f": {return_type} = ???"

        return header

    def _format_type_params(self, type_params: Any) -> str:
        """Format type parameters."""
        if not type_params:
            return ""

        if isinstance(type_params, list):
            parts = []
            for param in type_params:
                if isinstance(param, dict):
                    name = param.get("name", "")
                    variance = param.get("variance", "")
                    kind = param.get("kind", "")

                    prefix = ""
                    if variance == "covariant":
                        prefix = "+"
                    elif variance == "contravariant":
                        prefix = "-"

                    suffix = ""
                    if kind == "higher_kinded":
                        arity = param.get("arity", 1)
                        suffix = "[" + ", ".join(["_"] * arity) + "]"

                    parts.append(f"{prefix}{name}{suffix}")
                else:
                    parts.append(str(param))

            return ", ".join(parts)

        return str(type_params)

    def _format_extends(self, extends: Any) -> str:
        """Format extends clause."""
        if not extends:
            return ""

        if isinstance(extends, list):
            return " with ".join(extends)

        return str(extends)

    def _generate_method_signature(
        self,
        method: dict[str, Any],
        indent: int,
    ) -> str:
        """Generate abstract method signature."""
        ind = self._indent * indent

        name = method.get("name", "")
        return_type = self._convert_type(method.get("return_type", "Unit"))

        # Type parameters
        type_params = ""
        if method.get("type_params"):
            type_params = self._format_type_params(method["type_params"])

        # Parameters
        params = []
        for param in method.get("params", []):
            param_type = self._convert_type(param.get("type", "Any"))
            params.append(f"{param.get('name')}: {param_type}")
        params_str = ", ".join(params)

        # Build signature
        sig = f"{ind}def {name}"
        if type_params:
            sig += f"[{type_params}]"
        sig += f"({params_str}): {return_type}"

        return sig

    def _generate_method(
        self,
        method: dict[str, Any],
        indent: int,
    ) -> str:
        """Generate method with body."""
        sig = self._generate_method_signature(method, indent)
        return f"{sig} = ???"

    def generate_given(
        self,
        name: Optional[str],
        type_expr: str,
        indent: int = 0,
    ) -> str:
        """Generate given instance (Scala 3)."""
        ind = self._indent * indent

        if name:
            return f"{ind}given {name}: {type_expr} with\n{ind}  ???"
        else:
            return f"{ind}given {type_expr} with\n{ind}  ???"

    def generate_for_comprehension(
        self,
        generators: list[tuple[str, str]],
        yield_expr: str,
        indent: int = 0,
    ) -> str:
        """Generate for comprehension."""
        ind = self._indent * indent
        lines = [f"{ind}for {{"]

        for name, expr in generators:
            lines.append(f"{ind}  {name} <- {expr}")

        lines.append(f"{ind}}} yield {yield_expr}")
        return "\n".join(lines)

    def generate_pattern_match(
        self,
        expr: str,
        cases: list[tuple[str, str]],
        indent: int = 0,
    ) -> str:
        """Generate pattern match expression."""
        ind = self._indent * indent
        lines = [f"{ind}{expr} match {{"]

        for pattern, body in cases:
            lines.append(f"{ind}  case {pattern} => {body}")

        lines.append(f"{ind}}}")
        return "\n".join(lines)
