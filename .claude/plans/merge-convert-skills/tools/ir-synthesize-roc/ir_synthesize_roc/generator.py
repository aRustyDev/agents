"""Roc code generator.

Generates idiomatic Roc source code from IR components.
"""

from __future__ import annotations

from typing import Any


# Type mapping from common types to Roc
TYPE_MAP: dict[str, str] = {
    # Python types
    "int": "I64",
    "float": "F64",
    "str": "Str",
    "bool": "Bool",
    "bytes": "List U8",
    "list": "List",
    "dict": "Dict",
    "None": "{}",
    "NoneType": "{}",
    "Any": "*",
    # TypeScript types
    "number": "F64",
    "string": "Str",
    "boolean": "Bool",
    "void": "{}",
    "undefined": "{}",
    "null": "{}",
    "unknown": "*",
    "never": "[]",  # Empty tag union
    "Array": "List",
    "Map": "Dict",
    "Promise": "Task",
    # Rust types
    "i8": "I8",
    "i16": "I16",
    "i32": "I32",
    "i64": "I64",
    "i128": "I128",
    "u8": "U8",
    "u16": "U16",
    "u32": "U32",
    "u64": "U64",
    "u128": "U128",
    "f32": "F32",
    "f64": "F64",
    "char": "U32",  # Unicode code point
    "String": "Str",
    "&str": "Str",
    "Vec": "List",
    "HashMap": "Dict",
    "Option": "",  # Handled specially
    "Result": "Result",
    # Go types
    "int32": "I32",
    "int64": "I64",
    "uint32": "U32",
    "uint64": "U64",
    "float32": "F32",
    "float64": "F64",
    "error": "[Err Str]",
}


class RocCodeGenerator:
    """Generates Roc source code from IR components."""

    def __init__(self) -> None:
        """Initialize the generator."""
        self._indent_str = "    "

    def generate_app_header(
        self,
        provides: list[str],
        platform: str,
        platform_alias: str = "pf",
    ) -> str:
        """Generate app header."""
        provides_str = ", ".join(provides)
        return f'app [{provides_str}] {{ {platform_alias}: platform "{platform}" }}\n'

    def generate_module_header(
        self,
        exposes: list[str],
    ) -> str:
        """Generate module header."""
        exposes_str = ", ".join(exposes)
        return f"module [{exposes_str}]\n"

    def generate_import(
        self,
        module: str,
        exposing: list[str] | None = None,
        alias: str | None = None,
    ) -> str:
        """Generate import statement."""
        line = f"import {module}"
        if alias:
            line = f"import {module} as {alias}"
        if exposing:
            line += f" exposing [{', '.join(exposing)}]"
        return line + "\n"

    def generate_record_type(self, type_def: Any) -> str:
        """Generate record type definition."""
        lines = []

        # Type parameters
        type_params = ""
        if type_def.type_params:
            params = [p["name"] for p in type_def.type_params]
            type_params = " " + " ".join(params)

        # Fields
        fields = []
        for prop in type_def.properties:
            name = prop.get("name", "")
            type_str = self._convert_type(prop.get("type", "*"))
            optional = prop.get("optional", False)
            field_name = f"{name}?" if optional else name
            fields.append(f"{field_name} : {type_str}")

        fields_str = ", ".join(fields)
        lines.append(f"{type_def.name}{type_params} : {{ {fields_str} }}")

        return "\n".join(lines) + "\n"

    def generate_tag_union(self, type_def: Any) -> str:
        """Generate tag union type definition."""
        # Type parameters
        type_params = ""
        if type_def.type_params:
            params = [p["name"] for p in type_def.type_params]
            type_params = " " + " ".join(params)

        # Variants
        variants = []
        for member in type_def.enum_members:
            name = member.get("name", "")
            payload = member.get("payload_types", [])
            if payload:
                payload_str = " ".join(payload)
                variants.append(f"{name} {payload_str}")
            else:
                variants.append(name)

        variants_str = ", ".join(variants)
        return f"{type_def.name}{type_params} : [{variants_str}]\n"

    def generate_function(self, func_def: Any) -> str:
        """Generate function definition."""
        lines = []

        # Type annotation
        if hasattr(func_def, "type_annotation") and func_def.type_annotation:
            lines.append(f"{func_def.name} : {func_def.type_annotation}")
        else:
            # Build type annotation from parameters and return type
            param_types = []
            for p in func_def.parameters:
                param_type = self._convert_type(
                    p.type_annotation if hasattr(p, "type_annotation") else p.get("type", "*")
                )
                param_types.append(param_type)

            return_type = self._convert_type(func_def.return_type or "*")

            if param_types:
                type_sig = ", ".join(param_types) + " -> " + return_type
            else:
                type_sig = return_type

            lines.append(f"{func_def.name} : {type_sig}")

        # Implementation
        param_names = []
        for p in func_def.parameters:
            name = p.name if hasattr(p, "name") else p.get("name", "_")
            param_names.append(name)

        if param_names:
            params_str = ", ".join(param_names)
            lines.append(f"{func_def.name} = \\{params_str} ->")
            lines.append(f"    # TODO: Implement")
        else:
            lines.append(f"{func_def.name} =")
            lines.append(f"    # TODO: Implement")

        return "\n".join(lines) + "\n"

    def generate_pattern_match(
        self,
        expr: str,
        branches: list[tuple[str, str]],
    ) -> str:
        """Generate when...is expression."""
        lines = [f"when {expr} is"]
        for pattern, body in branches:
            lines.append(f"    {pattern} -> {body}")
        return "\n".join(lines)

    def generate_result_handling(
        self,
        result_expr: str,
        ok_var: str,
        ok_body: str,
        err_var: str,
        err_body: str,
    ) -> str:
        """Generate Result handling pattern."""
        return self.generate_pattern_match(
            result_expr,
            [
                (f"Ok {ok_var}", ok_body),
                (f"Err {err_var}", err_body),
            ],
        )

    def _convert_type(self, type_str: str) -> str:
        """Convert type from source language to Roc."""
        if not type_str:
            return "*"

        # Direct mapping
        if type_str in TYPE_MAP:
            return TYPE_MAP[type_str] or "*"

        # Handle generics like List[int], Vec<i32>
        if "[" in type_str:
            base, args = self._parse_generic(type_str, "[", "]")
            return self._convert_generic(base, args)
        if "<" in type_str:
            base, args = self._parse_generic(type_str, "<", ">")
            return self._convert_generic(base, args)

        # Handle pointer/optional types
        if type_str.startswith("*"):
            inner = type_str[1:]
            return f"[Just {self._convert_type(inner)}, Nothing]"

        # Handle function types
        if "->" in type_str:
            parts = type_str.split("->")
            converted = [self._convert_type(p.strip()) for p in parts]
            return " -> ".join(converted)

        # Return as-is (assume it's already a Roc type)
        return type_str

    def _parse_generic(
        self, type_str: str, open_bracket: str, close_bracket: str
    ) -> tuple[str, list[str]]:
        """Parse generic type like List[int] or Vec<i32>."""
        idx = type_str.index(open_bracket)
        base = type_str[:idx]
        args_str = type_str[idx + 1 : -1]

        # Parse comma-separated args
        args = []
        current = ""
        depth = 0
        for c in args_str:
            if c in ("[", "<"):
                depth += 1
                current += c
            elif c in ("]", ">"):
                depth -= 1
                current += c
            elif c == "," and depth == 0:
                args.append(current.strip())
                current = ""
            else:
                current += c
        if current.strip():
            args.append(current.strip())

        return base, args

    def _convert_generic(self, base: str, args: list[str]) -> str:
        """Convert generic type to Roc equivalent."""
        converted_args = [self._convert_type(a) for a in args]

        # Handle common patterns
        if base in ("List", "list", "Vec", "Array", "[]"):
            return f"List {converted_args[0]}" if converted_args else "List *"
        if base in ("Dict", "dict", "HashMap", "Map", "map"):
            if len(converted_args) >= 2:
                return f"Dict {converted_args[0]} {converted_args[1]}"
            return "Dict Str *"
        if base in ("Set", "set", "HashSet"):
            return f"Set {converted_args[0]}" if converted_args else "Set *"
        if base in ("Optional", "Option", "Maybe"):
            inner = converted_args[0] if converted_args else "*"
            return f"[Just {inner}, Nothing]"
        if base in ("Result",):
            if len(converted_args) >= 2:
                return f"Result {converted_args[0]} {converted_args[1]}"
            return "Result * *"
        if base in ("Promise", "Future", "Task"):
            if len(converted_args) >= 1:
                return f"Task {converted_args[0]} *"
            return "Task {} *"

        # Generic user type
        if converted_args:
            return f"{base} {' '.join(converted_args)}"
        return base
