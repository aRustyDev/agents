"""TypeScript code generator.

Generates TypeScript source code from IR representations.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from ir_core.models import FunctionDef, TypeDef, TypeKind

logger = logging.getLogger(__name__)


# Type mapping from IR to TypeScript
TYPE_MAP = {
    # Python types to TypeScript
    "int": "number",
    "float": "number",
    "str": "string",
    "bool": "boolean",
    "None": "void",
    "NoneType": "void",
    "bytes": "Uint8Array",
    "list": "Array",
    "dict": "Record",
    "set": "Set",
    "tuple": "readonly",
    "Any": "any",
    "object": "object",
    # Rust types to TypeScript
    "i8": "number",
    "i16": "number",
    "i32": "number",
    "i64": "number",
    "i128": "bigint",
    "u8": "number",
    "u16": "number",
    "u32": "number",
    "u64": "number",
    "u128": "bigint",
    "f32": "number",
    "f64": "number",
    "char": "string",
    "String": "string",
    "&str": "string",
    "Vec": "Array",
    "HashMap": "Map",
    "HashSet": "Set",
    "Option": "T | null",
    "Result": "T",  # Simplified
    "()": "void",
    # Generic types
    "Optional": "T | null | undefined",
    "List": "Array",
    "Dict": "Record",
    "Tuple": "readonly",
}


@dataclass
class GeneratorConfig:
    """Configuration for TypeScript code generation."""

    indent_size: int = 2
    use_tabs: bool = False
    line_length: int = 100
    emit_type_annotations: bool = True
    emit_readonly: bool = True
    emit_export: bool = True
    strict_null_checks: bool = True
    es_version: str = "ES2022"


class TypeScriptCodeGenerator:
    """Generates TypeScript source code from IR."""

    def __init__(self, config: GeneratorConfig | None = None) -> None:
        """Initialize the generator."""
        self.config = config or GeneratorConfig()
        self._indent_char = "\t" if self.config.use_tabs else " " * self.config.indent_size
        self._output: list[str] = []
        self._current_indent = 0

    def generate(
        self,
        types: list[TypeDef],
        functions: list[FunctionDef],
        imports: list[dict[str, Any]] | None = None,
    ) -> str:
        """Generate TypeScript code from IR components.

        Args:
            types: List of type definitions
            functions: List of function definitions
            imports: Optional list of import specifications

        Returns:
            Generated TypeScript source code
        """
        self._output = []
        self._current_indent = 0

        # Generate imports if provided
        if imports:
            for imp in imports:
                self._generate_import(imp)
            self._output.append("")

        # Generate type definitions
        for type_def in types:
            self._generate_type(type_def)
            self._output.append("")

        # Generate functions
        for func in functions:
            self._generate_function(func)
            self._output.append("")

        return "\n".join(self._output).rstrip() + "\n"

    def _indent(self) -> str:
        """Get current indentation string."""
        return self._indent_char * self._current_indent

    def _emit(self, line: str) -> None:
        """Emit a line of code."""
        if line:
            self._output.append(f"{self._indent()}{line}")
        else:
            self._output.append("")

    def _generate_import(self, imp: dict[str, Any]) -> None:
        """Generate an import statement."""
        parts = []

        if imp.get("type_only"):
            parts.append("import type")
        else:
            parts.append("import")

        import_specifiers = []

        if imp.get("default"):
            import_specifiers.append(imp["default"])

        if imp.get("named"):
            named = ", ".join(
                f"{n['name']} as {n['alias']}" if n.get("alias") else n["name"]
                for n in imp["named"]
            )
            import_specifiers.append(f"{{ {named} }}")

        if imp.get("namespace"):
            import_specifiers.append(f"* as {imp['namespace']}")

        parts.append(", ".join(import_specifiers))
        parts.append("from")
        parts.append(f'"{imp["module"]}"')

        self._emit(" ".join(parts) + ";")

    def _generate_type(self, type_def: TypeDef) -> None:
        """Generate a type definition."""
        if type_def.kind == TypeKind.INTERFACE:
            self._generate_interface(type_def)
        elif type_def.kind == TypeKind.TYPE_ALIAS:
            self._generate_type_alias(type_def)
        elif type_def.kind == TypeKind.ENUM:
            self._generate_enum(type_def)
        elif type_def.kind == TypeKind.CLASS:
            self._generate_class(type_def)

    def _generate_interface(self, type_def: TypeDef) -> None:
        """Generate an interface definition."""
        line = ""

        if self.config.emit_export and type_def.visibility == "public":
            line += "export "

        line += f"interface {type_def.name}"

        # Type parameters
        if type_def.type_params:
            params = self._format_type_params(type_def.type_params)
            line += f"<{params}>"

        # Extends
        if type_def.extends:
            line += f" extends {', '.join(type_def.extends)}"

        line += " {"
        self._emit(line)

        self._current_indent += 1

        # Properties
        for prop in type_def.properties:
            self._generate_property(prop)

        # Methods
        for method in type_def.methods:
            self._generate_method_signature(method)

        # Index signatures
        for idx_sig in getattr(type_def, "index_signatures", []):
            key_type = idx_sig.get("key_type", "string")
            value_type = idx_sig.get("value_type", "any")
            self._emit(f"[key: {key_type}]: {value_type};")

        self._current_indent -= 1
        self._emit("}")

    def _generate_type_alias(self, type_def: TypeDef) -> None:
        """Generate a type alias."""
        line = ""

        if self.config.emit_export and type_def.visibility == "public":
            line += "export "

        line += f"type {type_def.name}"

        # Type parameters
        if type_def.type_params:
            params = self._format_type_params(type_def.type_params)
            line += f"<{params}>"

        # Aliased type
        aliased = getattr(type_def, "aliased_type", "unknown")
        line += f" = {self._map_type(aliased)};"

        self._emit(line)

    def _generate_enum(self, type_def: TypeDef) -> None:
        """Generate an enum definition."""
        line = ""

        if self.config.emit_export and type_def.visibility == "public":
            line += "export "

        if getattr(type_def, "const_enum", False):
            line += "const "

        line += f"enum {type_def.name} {{"
        self._emit(line)

        self._current_indent += 1

        for member in type_def.enum_members:
            name = member.get("name", "")
            value = member.get("value")
            if value is not None:
                self._emit(f"{name} = {value},")
            else:
                self._emit(f"{name},")

        self._current_indent -= 1
        self._emit("}")

    def _generate_class(self, type_def: TypeDef) -> None:
        """Generate a class definition."""
        # Decorators
        for decorator in getattr(type_def, "decorators", []):
            self._emit(decorator)

        line = ""

        if self.config.emit_export and type_def.visibility == "public":
            line += "export "

        if getattr(type_def, "abstract", False):
            line += "abstract "

        line += f"class {type_def.name}"

        # Type parameters
        if type_def.type_params:
            params = self._format_type_params(type_def.type_params)
            line += f"<{params}>"

        # Extends
        if type_def.extends:
            line += f" extends {type_def.extends[0]}"

        # Implements
        if type_def.implements:
            line += f" implements {', '.join(type_def.implements)}"

        line += " {"
        self._emit(line)

        self._current_indent += 1

        # Properties
        for prop in type_def.properties:
            self._generate_class_property(prop)

        if type_def.properties:
            self._emit("")

        # Constructor
        constructor = getattr(type_def, "constructor", None)
        if constructor:
            self._generate_constructor(constructor)
            self._emit("")

        # Methods
        for method in type_def.methods:
            self._generate_class_method(method)

        self._current_indent -= 1
        self._emit("}")

    def _generate_property(self, prop: dict[str, Any]) -> None:
        """Generate an interface property."""
        line = ""

        if self.config.emit_readonly and prop.get("readonly"):
            line += "readonly "

        line += prop.get("name", "")

        if prop.get("optional"):
            line += "?"

        if self.config.emit_type_annotations and prop.get("type"):
            line += f": {self._map_type(prop['type'])}"

        line += ";"
        self._emit(line)

    def _generate_class_property(self, prop: dict[str, Any]) -> None:
        """Generate a class property."""
        line = ""

        visibility = prop.get("visibility", "public")
        if visibility != "public":
            line += f"{visibility} "

        if prop.get("static"):
            line += "static "

        if self.config.emit_readonly and prop.get("readonly"):
            line += "readonly "

        line += prop.get("name", "")

        if prop.get("optional"):
            line += "?"

        if self.config.emit_type_annotations and prop.get("type"):
            line += f": {self._map_type(prop['type'])}"

        line += ";"
        self._emit(line)

    def _generate_method_signature(self, method: dict[str, Any]) -> None:
        """Generate a method signature for interfaces."""
        line = method.get("name", "")

        # Type parameters
        if method.get("type_params"):
            params = self._format_type_params(method["type_params"])
            line += f"<{params}>"

        # Parameters
        params = self._format_parameters(method.get("parameters", []))
        line += f"({params})"

        # Return type
        if self.config.emit_type_annotations and method.get("return_type"):
            line += f": {self._map_type(method['return_type'])}"

        line += ";"
        self._emit(line)

    def _generate_constructor(self, constructor: dict[str, Any]) -> None:
        """Generate a constructor."""
        params = self._format_parameters(constructor.get("parameters", []))
        self._emit(f"constructor({params}) {{")
        self._current_indent += 1
        self._emit("// Constructor implementation")
        self._current_indent -= 1
        self._emit("}")

    def _generate_class_method(self, method: dict[str, Any]) -> None:
        """Generate a class method."""
        line = ""

        visibility = method.get("visibility", "public")
        if visibility != "public":
            line += f"{visibility} "

        if method.get("static"):
            line += "static "

        if method.get("abstract"):
            line += "abstract "

        if method.get("async"):
            line += "async "

        line += method.get("name", "")

        # Type parameters
        if method.get("type_params"):
            params = self._format_type_params(method["type_params"])
            line += f"<{params}>"

        # Parameters
        params = self._format_parameters(method.get("parameters", []))
        line += f"({params})"

        # Return type
        if self.config.emit_type_annotations and method.get("return_type"):
            line += f": {self._map_type(method['return_type'])}"

        if method.get("abstract"):
            line += ";"
            self._emit(line)
        else:
            line += " {"
            self._emit(line)
            self._current_indent += 1
            self._emit("// Method implementation")
            self._current_indent -= 1
            self._emit("}")

    def _generate_function(self, func: FunctionDef) -> None:
        """Generate a function definition."""
        line = ""

        if self.config.emit_export and func.visibility == "public":
            line += "export "

        if func.async_:
            line += "async "

        line += f"function {func.name}"

        # Type parameters
        if func.type_params:
            params = self._format_type_params(func.type_params)
            line += f"<{params}>"

        # Parameters
        params = self._format_func_parameters(func.parameters)
        line += f"({params})"

        # Return type
        if self.config.emit_type_annotations and func.return_type:
            return_type = self._map_type(func.return_type)
            if func.async_ and not return_type.startswith("Promise"):
                return_type = f"Promise<{return_type}>"
            line += f": {return_type}"

        line += " {"
        self._emit(line)
        self._current_indent += 1
        self._emit("// Function implementation")
        self._current_indent -= 1
        self._emit("}")

    def _format_type_params(self, type_params: list[dict[str, Any]]) -> str:
        """Format type parameters."""
        parts = []
        for param in type_params:
            part = param.get("name", "T")
            if param.get("constraint"):
                part += f" extends {param['constraint']}"
            if param.get("default"):
                part += f" = {param['default']}"
            parts.append(part)
        return ", ".join(parts)

    def _format_parameters(self, parameters: list[dict[str, Any]]) -> str:
        """Format method/function parameters."""
        parts = []
        for param in parameters:
            part = ""
            if param.get("rest"):
                part += "..."
            part += param.get("name", "arg")
            if param.get("optional"):
                part += "?"
            if self.config.emit_type_annotations and param.get("type"):
                part += f": {self._map_type(param['type'])}"
            parts.append(part)
        return ", ".join(parts)

    def _format_func_parameters(self, parameters: list[Any]) -> str:
        """Format function parameters from Parameter objects."""
        parts = []
        for param in parameters:
            part = ""
            if getattr(param, "rest", False):
                part += "..."
            part += param.name
            if getattr(param, "optional", False):
                part += "?"
            if self.config.emit_type_annotations and param.type_annotation:
                part += f": {self._map_type(param.type_annotation)}"
            parts.append(part)
        return ", ".join(parts)

    def _map_type(self, type_str: str | None) -> str:
        """Map an IR type to TypeScript type."""
        if not type_str:
            return "unknown"

        type_str = type_str.strip()

        # Direct mapping
        if type_str in TYPE_MAP:
            return TYPE_MAP[type_str]

        # Handle generic types like List[int] -> Array<number>
        if "[" in type_str and not type_str.startswith("["):
            base, args = self._parse_generic_type(type_str)
            mapped_base = TYPE_MAP.get(base, base)
            mapped_args = [self._map_type(arg) for arg in args]
            return f"{mapped_base}<{', '.join(mapped_args)}>"

        # Handle tuple types [int, str] -> [number, string]
        if type_str.startswith("[") and type_str.endswith("]"):
            inner = type_str[1:-1]
            if inner:
                elements = [e.strip() for e in inner.split(",")]
                mapped = [self._map_type(e) for e in elements]
                return f"[{', '.join(mapped)}]"
            return "[]"

        # Handle union types int | str -> number | string
        if " | " in type_str:
            parts = [p.strip() for p in type_str.split("|")]
            mapped = [self._map_type(p) for p in parts]
            return " | ".join(mapped)

        # Handle Optional[T] -> T | null
        if type_str.startswith("Optional["):
            inner = type_str[9:-1]
            return f"{self._map_type(inner)} | null"

        # Return as-is if no mapping found
        return type_str

    def _parse_generic_type(self, type_str: str) -> tuple[str, list[str]]:
        """Parse a generic type like List[int, str] into base and args."""
        bracket_idx = type_str.index("[")
        base = type_str[:bracket_idx]
        args_str = type_str[bracket_idx + 1 : -1]

        # Handle nested generics
        args = []
        current = []
        depth = 0
        for char in args_str:
            if char == "[":
                depth += 1
                current.append(char)
            elif char == "]":
                depth -= 1
                current.append(char)
            elif char == "," and depth == 0:
                args.append("".join(current).strip())
                current = []
            else:
                current.append(char)
        if current:
            args.append("".join(current).strip())

        return base, args
