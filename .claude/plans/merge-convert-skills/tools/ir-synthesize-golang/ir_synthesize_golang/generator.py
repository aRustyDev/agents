"""Go code generator.

Generates idiomatic Go source code from IR components.
"""

from __future__ import annotations

from typing import Any


# Type mapping from common types to Go
TYPE_MAP: dict[str, str] = {
    # Python types
    "int": "int",
    "float": "float64",
    "str": "string",
    "bool": "bool",
    "bytes": "[]byte",
    "list": "[]",  # Needs element type
    "dict": "map",  # Needs key/value types
    "set": "map",  # map[T]struct{}
    "None": "",
    "NoneType": "",
    "Any": "any",
    "object": "any",
    # TypeScript types
    "number": "float64",
    "string": "string",
    "boolean": "bool",
    "void": "",
    "undefined": "",
    "null": "",
    "unknown": "any",
    "never": "",
    "Array": "[]",
    "Map": "map",
    "Set": "map",
    "Promise": "chan",  # Approximation
    "Record": "map",
    # Rust types
    "i8": "int8",
    "i16": "int16",
    "i32": "int32",
    "i64": "int64",
    "i128": "int64",  # No direct equivalent
    "isize": "int",
    "u8": "uint8",
    "u16": "uint16",
    "u32": "uint32",
    "u64": "uint64",
    "u128": "uint64",  # No direct equivalent
    "usize": "uint",
    "f32": "float32",
    "f64": "float64",
    "char": "rune",
    "String": "string",
    "&str": "string",
    "Vec": "[]",
    "HashMap": "map",
    "HashSet": "map",
    "Option": "*",  # Pointer for optional
    "Result": "",  # Handled via multiple returns
    "Box": "*",
    "Rc": "*",
    "Arc": "*",
}


class GolangCodeGenerator:
    """Generates Go source code from IR components."""

    def __init__(self) -> None:
        """Initialize the generator."""
        self._indent_level = 0
        self._indent_str = "\t"  # Go uses tabs

    def generate_package(self, name: str) -> str:
        """Generate package declaration."""
        return f"package {name}\n"

    def generate_imports(self, imports: list[dict[str, Any]]) -> str:
        """Generate import declarations."""
        if not imports:
            return ""

        lines = ["import ("]
        for imp in imports:
            path = imp.get("module", "")
            alias = imp.get("alias")
            if imp.get("blank_import"):
                lines.append(f'\t_ "{path}"')
            elif imp.get("dot_import"):
                lines.append(f'\t. "{path}"')
            elif alias:
                lines.append(f'\t{alias} "{path}"')
            else:
                lines.append(f'\t"{path}"')
        lines.append(")")
        return "\n".join(lines) + "\n"

    def generate_struct(self, type_def: Any) -> str:
        """Generate struct definition."""
        lines = []

        # Type parameters
        type_params = ""
        if type_def.type_params:
            params = []
            for p in type_def.type_params:
                constraint = p.get("constraint", "any")
                params.append(f"{p['name']} {constraint}")
            type_params = f"[{', '.join(params)}]"

        lines.append(f"type {type_def.name}{type_params} struct {{")

        # Fields
        for prop in type_def.properties:
            name = prop.get("name", "")
            type_str = self._convert_type(prop.get("type", "any"))
            tag = prop.get("tag", "")

            if prop.get("embedded"):
                lines.append(f"\t{type_str}")
            elif tag:
                lines.append(f"\t{name} {type_str} {tag}")
            else:
                lines.append(f"\t{name} {type_str}")

        lines.append("}")
        return "\n".join(lines) + "\n"

    def generate_interface(self, type_def: Any) -> str:
        """Generate interface definition."""
        lines = []

        # Type parameters
        type_params = ""
        if type_def.type_params:
            params = []
            for p in type_def.type_params:
                constraint = p.get("constraint", "any")
                params.append(f"{p['name']} {constraint}")
            type_params = f"[{', '.join(params)}]"

        lines.append(f"type {type_def.name}{type_params} interface {{")

        # Embedded interfaces
        for embedded in type_def.extends:
            lines.append(f"\t{embedded}")

        # Methods
        for method in type_def.methods:
            sig = self._generate_method_signature(method)
            lines.append(f"\t{sig}")

        lines.append("}")
        return "\n".join(lines) + "\n"

    def generate_type_alias(self, type_def: Any) -> str:
        """Generate type alias."""
        # Type parameters
        type_params = ""
        if type_def.type_params:
            params = []
            for p in type_def.type_params:
                constraint = p.get("constraint", "any")
                params.append(f"{p['name']} {constraint}")
            type_params = f"[{', '.join(params)}]"

        aliased = self._convert_type(type_def.aliased_type or "any")
        return f"type {type_def.name}{type_params} = {aliased}\n"

    def generate_function(self, func_def: Any) -> str:
        """Generate function definition."""
        lines = []

        # Build signature
        name = func_def.name

        # Type parameters
        type_params = ""
        if func_def.type_params:
            params = []
            for p in func_def.type_params:
                constraint = p.get("constraint", "any")
                params.append(f"{p['name']} {constraint}")
            type_params = f"[{', '.join(params)}]"

        # Receiver for methods
        receiver = ""
        if hasattr(func_def, "receiver") and func_def.receiver:
            recv = func_def.receiver
            recv_name = recv.get("name", "r")
            recv_type = recv.get("type", "")
            receiver = f"({recv_name} {recv_type}) "

        # Parameters
        params = []
        for p in func_def.parameters:
            param_name = p.name if hasattr(p, "name") else p.get("name", "")
            param_type = self._convert_type(
                p.type_annotation if hasattr(p, "type_annotation") else p.get("type", "any")
            )
            is_variadic = (
                p.rest if hasattr(p, "rest") else p.get("variadic", False)
            )
            if is_variadic:
                params.append(f"{param_name} ...{param_type}")
            else:
                params.append(f"{param_name} {param_type}")
        params_str = ", ".join(params)

        # Return types
        returns = []
        if func_def.return_type:
            returns.append(self._convert_type(func_def.return_type))
        if hasattr(func_def, "additional_returns"):
            for ret in func_def.additional_returns:
                ret_type = ret.get("type", "")
                if ret_type:
                    returns.append(self._convert_type(ret_type))

        if len(returns) == 0:
            return_str = ""
        elif len(returns) == 1:
            return_str = f" {returns[0]}"
        else:
            return_str = f" ({', '.join(returns)})"

        lines.append(f"func {receiver}{name}{type_params}({params_str}){return_str} {{")
        lines.append("\t// TODO: Implement")
        lines.append("}")

        return "\n".join(lines) + "\n"

    def generate_const(self, const: dict[str, Any]) -> str:
        """Generate constant declaration."""
        name = const.get("name", "")
        type_str = const.get("type", "")
        value = const.get("value", "")

        if type_str:
            return f"const {name} {type_str} = {value}\n"
        return f"const {name} = {value}\n"

    def generate_var(self, var: dict[str, Any]) -> str:
        """Generate variable declaration."""
        name = var.get("name", "")
        type_str = var.get("type", "")
        value = var.get("value")

        if value:
            if type_str:
                return f"var {name} {type_str} = {value}\n"
            return f"var {name} = {value}\n"
        return f"var {name} {type_str}\n"

    def _generate_method_signature(self, method: dict[str, Any]) -> str:
        """Generate method signature for interface."""
        name = method.get("name", "")

        # Type parameters
        type_params = ""
        if method.get("type_params"):
            params = []
            for p in method["type_params"]:
                constraint = p.get("constraint", "any")
                params.append(f"{p['name']} {constraint}")
            type_params = f"[{', '.join(params)}]"

        # Parameters
        params = []
        for p in method.get("parameters", []):
            param_name = p.get("name", "")
            param_type = self._convert_type(p.get("type", "any"))
            is_variadic = p.get("variadic", False)
            if is_variadic:
                params.append(f"{param_name} ...{param_type}")
            elif param_name:
                params.append(f"{param_name} {param_type}")
            else:
                params.append(param_type)
        params_str = ", ".join(params)

        # Returns
        returns = []
        for r in method.get("returns", []):
            ret_name = r.get("name", "")
            ret_type = self._convert_type(r.get("type", ""))
            if ret_name:
                returns.append(f"{ret_name} {ret_type}")
            elif ret_type:
                returns.append(ret_type)

        if len(returns) == 0:
            return_str = ""
        elif len(returns) == 1:
            return_str = f" {returns[0]}"
        else:
            return_str = f" ({', '.join(returns)})"

        return f"{name}{type_params}({params_str}){return_str}"

    def _convert_type(self, type_str: str) -> str:
        """Convert type from source language to Go."""
        if not type_str:
            return "any"

        # Direct mapping
        if type_str in TYPE_MAP:
            return TYPE_MAP[type_str] or "any"

        # Handle generics like List[int], Vec<i32>
        if "[" in type_str:
            base, args = self._parse_generic(type_str, "[", "]")
            return self._convert_generic(base, args)
        if "<" in type_str:
            base, args = self._parse_generic(type_str, "<", ">")
            return self._convert_generic(base, args)

        # Handle pointer types
        if type_str.startswith("*"):
            inner = type_str[1:]
            return f"*{self._convert_type(inner)}"

        # Handle slice types
        if type_str.startswith("[]"):
            inner = type_str[2:]
            return f"[]{self._convert_type(inner)}"

        # Handle map types
        if type_str.startswith("map["):
            # Parse map[K]V
            rest = type_str[4:]
            bracket_count = 1
            key_end = 0
            for i, c in enumerate(rest):
                if c == "[":
                    bracket_count += 1
                elif c == "]":
                    bracket_count -= 1
                    if bracket_count == 0:
                        key_end = i
                        break
            key = rest[:key_end]
            value = rest[key_end + 1 :]
            return f"map[{self._convert_type(key)}]{self._convert_type(value)}"

        # Handle channel types
        if type_str.startswith("chan "):
            inner = type_str[5:]
            return f"chan {self._convert_type(inner)}"
        if type_str.startswith("<-chan "):
            inner = type_str[7:]
            return f"<-chan {self._convert_type(inner)}"
        if type_str.startswith("chan<- "):
            inner = type_str[7:]
            return f"chan<- {self._convert_type(inner)}"

        # Return as-is (assume it's already a Go type or user-defined)
        return type_str

    def _parse_generic(
        self, type_str: str, open_bracket: str, close_bracket: str
    ) -> tuple[str, list[str]]:
        """Parse generic type like List[int] or HashMap<K, V>."""
        idx = type_str.index(open_bracket)
        base = type_str[:idx]
        args_str = type_str[idx + 1 : -1]

        # Parse comma-separated args, handling nested generics
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
        """Convert generic type to Go equivalent."""
        converted_args = [self._convert_type(a) for a in args]

        # Handle common patterns
        if base in ("List", "list", "Vec", "Array"):
            return f"[]{converted_args[0]}" if converted_args else "[]any"
        if base in ("Dict", "dict", "HashMap", "Map", "Record"):
            if len(converted_args) >= 2:
                return f"map[{converted_args[0]}]{converted_args[1]}"
            return "map[string]any"
        if base in ("Set", "set", "HashSet"):
            return f"map[{converted_args[0]}]struct{{}}" if converted_args else "map[any]struct{}"
        if base in ("Optional", "Option"):
            return f"*{converted_args[0]}" if converted_args else "*any"
        if base in ("Promise", "Future"):
            return f"chan {converted_args[0]}" if converted_args else "chan any"

        # Generic user type
        if converted_args:
            return f"{base}[{', '.join(converted_args)}]"
        return base
