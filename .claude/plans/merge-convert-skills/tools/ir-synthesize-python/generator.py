"""Python code generation utilities.

This module provides the PythonCodeGenerator class for generating Python code
constructs from IR elements. It handles functions, classes, imports, and type
annotations.

Example:
    generator = PythonCodeGenerator()
    code = generator.gen_function(func, context)
    type_str = generator.gen_type_annotation(type_ref, context)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ir_core.models import (
    ControlFlowGraph,
    EffectKind,
    Expression,
    ExpressionKind,
    Field_,
    Function,
    Import,
    Param,
    Statement,
    Terminator,
    TerminatorKind,
    TypeDef,
    TypeKind,
    TypeRef,
    TypeRefKind,
)

if TYPE_CHECKING:
    from .synthesizer import SynthesisContext


class PythonCodeGenerator:
    """Generate Python code constructs from IR elements.

    This class handles the low-level code generation for Python constructs,
    including proper formatting, indentation, and type annotations.

    Attributes:
        indent_size: Number of spaces per indentation level (default: 4)
    """

    def __init__(self, indent_size: int = 4) -> None:
        """Initialize the code generator.

        Args:
            indent_size: Number of spaces per indentation level
        """
        self.indent_size = indent_size

    def indent(self, code: str, level: int = 1) -> str:
        """Indent code by the specified number of levels.

        Args:
            code: Code to indent
            level: Number of indentation levels

        Returns:
            Indented code
        """
        prefix = " " * (self.indent_size * level)
        lines = code.split("\n")
        return "\n".join(prefix + line if line.strip() else line for line in lines)

    def gen_function(
        self,
        func: Function,
        context: SynthesisContext,
        is_method: bool = False,
    ) -> str:
        """Generate a function definition.

        Args:
            func: Function IR to generate
            context: Synthesis context
            is_method: Whether this is a method (affects indentation)

        Returns:
            Generated Python function code
        """
        lines: list[str] = []

        # Decorators
        decorators = self._gen_decorators(func, context)
        lines.extend(decorators)

        # Function signature
        signature = self._gen_signature(func, context)
        lines.append(signature)

        # Docstring
        if func.doc_comment and context.config.emit_docstrings:
            docstring = self._gen_docstring(func.doc_comment)
            lines.append(self.indent(docstring))

        # Body
        body = self._gen_body(func, context)
        lines.append(self.indent(body))

        return "\n".join(lines)

    def gen_class(self, type_def: TypeDef, context: SynthesisContext) -> str:
        """Generate a class definition.

        Args:
            type_def: TypeDef IR to generate
            context: Synthesis context

        Returns:
            Generated Python class code
        """
        lines: list[str] = []

        # Determine class style based on kind
        if type_def.kind == TypeKind.STRUCT:
            # Generate as dataclass
            return self._gen_dataclass(type_def, context)
        elif type_def.kind == TypeKind.INTERFACE:
            # Generate as Protocol
            return self._gen_protocol(type_def, context)

        # Regular class
        # Decorators
        decorators = self._gen_class_decorators(type_def, context)
        lines.extend(decorators)

        # Class signature
        class_sig = self._gen_class_signature(type_def, context)
        lines.append(class_sig)

        # Class body
        body_lines: list[str] = []

        # Docstring (extracted from annotations or metadata)
        docstring = self._extract_class_docstring(type_def)
        if docstring and context.config.emit_docstrings:
            body_lines.append(self._gen_docstring(docstring))

        # Class-level type annotations for fields
        for field in type_def.body.fields:
            field_line = self._gen_class_field(field, context)
            body_lines.append(field_line)

        # Methods
        for method_id in type_def.body.methods:
            method = self._find_function(method_id, context)
            if method:
                method_code = self.gen_function(method, context, is_method=True)
                body_lines.append("")  # Blank line before method
                body_lines.append(method_code)

        # Handle empty class
        if not body_lines:
            body_lines.append("pass")

        # Indent body
        for line in body_lines:
            lines.append(self.indent(line))

        return "\n".join(lines)

    def gen_import(self, imp: Import, context: SynthesisContext) -> str:
        """Generate an import statement.

        Args:
            imp: Import IR to generate
            context: Synthesis context

        Returns:
            Generated Python import statement
        """
        module_path = ".".join(imp.module_path)

        if not imp.imported_items:
            if imp.alias:
                return f"import {module_path} as {imp.alias}"
            return f"import {module_path}"

        items: list[str] = []
        for item in imp.imported_items:
            if item.alias:
                items.append(f"{item.name} as {item.alias}")
            else:
                items.append(item.name)

        return f"from {module_path} import {', '.join(items)}"

    def gen_type_annotation(
        self,
        type_ref: TypeRef,
        context: SynthesisContext,
    ) -> str:
        """Generate a type annotation from a TypeRef.

        Respects target Python version from context:
        - Python 3.9+: Use list[T], dict[K, V] (builtin generics)
        - Python 3.10+: Use X | Y syntax for unions
        - Older versions: Use typing.List, typing.Dict, typing.Union

        Args:
            type_ref: TypeRef to convert
            context: Synthesis context

        Returns:
            Python type annotation string
        """
        if type_ref.kind == TypeRefKind.NAMED:
            base = self._resolve_type_name(type_ref.type_id, context)

            # Handle generic arguments
            if type_ref.args:
                args = ", ".join(
                    self.gen_type_annotation(arg, context) for arg in type_ref.args
                )
                # Check Python version for builtin generics
                builtin_generics = ("list", "dict", "set", "tuple", "frozenset")
                if base in builtin_generics:
                    if context.supports_builtin_generics:
                        return f"{base}[{args}]"
                    else:
                        # Use typing module for older Python
                        typing_name = base.capitalize()
                        if base == "frozenset":
                            typing_name = "FrozenSet"
                        context.imports_needed.add(f"typing.{typing_name}")
                        return f"{typing_name}[{args}]"
                return f"{base}[{args}]"

            return base

        elif type_ref.kind == TypeRefKind.GENERIC:
            return type_ref.type_id or "T"

        elif type_ref.kind == TypeRefKind.FUNCTION:
            # Callable[[args], return]
            context.imports_needed.add("typing.Callable")
            params = ", ".join(
                self.gen_type_annotation(p, context) for p in type_ref.params
            )
            ret = (
                self.gen_type_annotation(type_ref.return_type, context)
                if type_ref.return_type
                else "None"
            )
            return f"Callable[[{params}], {ret}]"

        elif type_ref.kind == TypeRefKind.TUPLE:
            elements = ", ".join(
                self.gen_type_annotation(e, context) for e in type_ref.elements
            )
            if context.supports_builtin_generics:
                return f"tuple[{elements}]"
            else:
                context.imports_needed.add("typing.Tuple")
                return f"Tuple[{elements}]"

        elif type_ref.kind == TypeRefKind.UNION:
            member_strs = [
                self.gen_type_annotation(m, context) for m in type_ref.members
            ]
            if context.supports_pep604_union:
                return " | ".join(member_strs)
            else:
                context.imports_needed.add("typing.Union")
                return f"Union[{', '.join(member_strs)}]"

        elif type_ref.kind == TypeRefKind.INTERSECTION:
            # Python doesn't have intersection types natively
            # Use Protocol with multiple inheritance or just first type
            context.imports_needed.add("typing.Protocol")
            if type_ref.members:
                return self.gen_type_annotation(type_ref.members[0], context)
            return "object"

        elif type_ref.kind == TypeRefKind.REFERENCE:
            # Python doesn't distinguish references - just use the underlying type
            if type_ref.type_id:
                return self._resolve_type_name(type_ref.type_id, context)
            return "object"

        return "Any"

    def _resolve_type_name(self, type_id: str | None, context: SynthesisContext) -> str:
        """Resolve a type ID to a Python type name.

        Args:
            type_id: Type ID to resolve
            context: Synthesis context

        Returns:
            Python type name
        """
        if not type_id:
            return "Any"

        # Check type map
        if type_id in context.type_map:
            name = context.type_map[type_id]
            # Track typing imports
            if name in ("Any", "Optional", "Union", "Callable", "Sequence",
                        "Mapping", "Iterable", "Iterator", "Generator",
                        "TypeVar", "Generic", "Protocol"):
                context.imports_needed.add(f"typing.{name}")
            return name

        # Handle qualified names
        if "." in type_id:
            parts = type_id.split(".")
            # If it's a builtins type, just use the name
            if parts[0] == "builtins":
                return parts[-1]
            # Otherwise return as-is (may need import)
            return type_id

        return type_id

    def _gen_signature(self, func: Function, context: SynthesisContext) -> str:
        """Generate a function signature.

        Args:
            func: Function IR
            context: Synthesis context

        Returns:
            Function signature string
        """
        # Check for async
        prefix = "async " if self._is_async(func) else ""

        # Parameters
        params: list[str] = []

        # Add self/cls for methods
        if func.receiver:
            params.append(func.receiver.name)

        # Regular parameters
        for param in func.params:
            param_str = self._gen_param(param, context)
            params.append(param_str)

        params_str = ", ".join(params)

        # Return type
        return_type = ""
        if context.config.emit_type_hints:
            ret_type = self.gen_type_annotation(func.return_type, context)
            return_type = f" -> {ret_type}"

        return f"{prefix}def {func.name}({params_str}){return_type}:"

    def _gen_param(self, param: Param, context: SynthesisContext) -> str:
        """Generate a parameter string.

        Args:
            param: Parameter IR
            context: Synthesis context

        Returns:
            Parameter string
        """
        name = param.name

        # Handle variadic parameters
        if param.variadic:
            if name == "kwargs" or "dict" in str(param.type.type_id).lower():
                name = f"**{name}"
            else:
                name = f"*{name}"

        # Type annotation
        if context.config.emit_type_hints:
            type_str = self.gen_type_annotation(param.type, context)
            name = f"{name}: {type_str}"

        # Default value
        if param.default:
            default_str = self._gen_expression(param.default, context)
            name = f"{name} = {default_str}"

        return name

    def _gen_decorators(self, func: Function, context: SynthesisContext) -> list[str]:
        """Generate decorator lines for a function.

        Args:
            func: Function IR
            context: Synthesis context

        Returns:
            List of decorator lines
        """
        decorators: list[str] = []

        # Check for known patterns in annotations
        for annotation in func.annotations:
            if annotation.kind == "decorator":
                dec_name = annotation.value.get("name", "")
                if dec_name:
                    args = annotation.value.get("args", [])
                    if args:
                        args_str = ", ".join(str(a) for a in args)
                        decorators.append(f"@{dec_name}({args_str})")
                    else:
                        decorators.append(f"@{dec_name}")

        # Check for staticmethod/classmethod based on receiver
        if func.receiver:
            if func.receiver.name == "cls":
                decorators.insert(0, "@classmethod")

        # Check for property based on naming patterns
        if func.name.startswith("get_") and not func.params:
            # Could suggest @property, but don't auto-add
            pass

        return decorators

    def _gen_class_decorators(
        self, type_def: TypeDef, context: SynthesisContext
    ) -> list[str]:
        """Generate decorator lines for a class.

        Args:
            type_def: TypeDef IR
            context: Synthesis context

        Returns:
            List of decorator lines
        """
        decorators: list[str] = []

        for annotation in type_def.annotations:
            if annotation.kind == "decorator":
                dec_name = annotation.value.get("name", "")
                if dec_name:
                    decorators.append(f"@{dec_name}")

        return decorators

    def _gen_class_signature(
        self, type_def: TypeDef, context: SynthesisContext
    ) -> str:
        """Generate a class signature.

        Args:
            type_def: TypeDef IR
            context: Synthesis context

        Returns:
            Class signature string
        """
        name = type_def.name

        # Generic parameters
        type_params = ""
        if type_def.params:
            params = ", ".join(p.name for p in type_def.params)
            type_params = f"[{params}]"

        # Base classes (would need to be extracted from type_relationships)
        bases = ""

        return f"class {name}{type_params}{bases}:"

    def _gen_class_field(self, field: Field_, context: SynthesisContext) -> str:
        """Generate a class field annotation.

        Args:
            field: Field IR
            context: Synthesis context

        Returns:
            Field annotation string
        """
        type_str = self.gen_type_annotation(field.type, context)

        if field.default_value is not None:
            return f"{field.name}: {type_str} = {field.default_value!r}"
        return f"{field.name}: {type_str}"

    def _gen_dataclass(self, type_def: TypeDef, context: SynthesisContext) -> str:
        """Generate a dataclass from a struct TypeDef.

        Args:
            type_def: TypeDef IR
            context: Synthesis context

        Returns:
            Generated dataclass code
        """
        context.imports_needed.add("dataclasses.dataclass")

        lines: list[str] = ["@dataclass"]

        # Generic parameters
        type_params = ""
        if type_def.params:
            params = ", ".join(p.name for p in type_def.params)
            type_params = f"[{params}]"

        lines.append(f"class {type_def.name}{type_params}:")

        # Docstring
        docstring = self._extract_class_docstring(type_def)
        if docstring and context.config.emit_docstrings:
            lines.append(self.indent(self._gen_docstring(docstring)))

        # Fields
        for field in type_def.body.fields:
            field_line = self._gen_dataclass_field(field, context)
            lines.append(self.indent(field_line))

        # Methods
        for method_id in type_def.body.methods:
            method = self._find_function(method_id, context)
            if method:
                # Skip __init__ for dataclasses
                if method.name == "__init__":
                    continue
                method_code = self.gen_function(method, context, is_method=True)
                lines.append("")
                lines.append(self.indent(method_code))

        # Handle empty dataclass
        if not type_def.body.fields and not type_def.body.methods:
            lines.append(self.indent("pass"))

        return "\n".join(lines)

    def _gen_dataclass_field(
        self, field: Field_, context: SynthesisContext
    ) -> str:
        """Generate a dataclass field.

        Args:
            field: Field IR
            context: Synthesis context

        Returns:
            Dataclass field string
        """
        type_str = self.gen_type_annotation(field.type, context)

        if field.default_value is not None:
            return f"{field.name}: {type_str} = {field.default_value!r}"

        return f"{field.name}: {type_str}"

    def _gen_protocol(self, type_def: TypeDef, context: SynthesisContext) -> str:
        """Generate a Protocol from an interface TypeDef.

        Args:
            type_def: TypeDef IR
            context: Synthesis context

        Returns:
            Generated Protocol code
        """
        context.imports_needed.add("typing.Protocol")

        lines: list[str] = []

        # Generic parameters
        type_params = ""
        if type_def.params:
            params = ", ".join(p.name for p in type_def.params)
            type_params = f"[{params}]"

        lines.append(f"class {type_def.name}{type_params}(Protocol):")

        # Docstring
        docstring = self._extract_class_docstring(type_def)
        if docstring and context.config.emit_docstrings:
            lines.append(self.indent(self._gen_docstring(docstring)))

        # Required methods from method signatures
        for method_sig in type_def.body.required_methods:
            sig_line = self._gen_method_signature(method_sig, context)
            lines.append(self.indent(sig_line))
            lines.append(self.indent(self.indent("...")))

        # Handle empty protocol
        if not type_def.body.required_methods:
            lines.append(self.indent("pass"))

        return "\n".join(lines)

    def _gen_method_signature(
        self, method_sig: MethodSignature, context: SynthesisContext
    ) -> str:
        """Generate a method signature for a Protocol.

        Args:
            method_sig: MethodSignature IR
            context: Synthesis context

        Returns:
            Method signature string
        """
        # This is a stub - need to import MethodSignature
        params: list[str] = ["self"]

        for param in method_sig.params:
            param_str = self._gen_param(param, context)
            params.append(param_str)

        params_str = ", ".join(params)
        ret_type = self.gen_type_annotation(method_sig.return_type, context)

        return f"def {method_sig.name}({params_str}) -> {ret_type}:"

    def _gen_body(self, func: Function, context: SynthesisContext) -> str:
        """Generate the function body.

        Args:
            func: Function IR
            context: Synthesis context

        Returns:
            Function body code
        """
        if not func.body:
            return "..."

        return self._gen_cfg(func.body, context)

    def _gen_cfg(self, cfg: ControlFlowGraph, context: SynthesisContext) -> str:
        """Generate code from a control flow graph.

        Args:
            cfg: Control flow graph
            context: Synthesis context

        Returns:
            Generated code
        """
        if not cfg.blocks:
            return "pass"

        # For a simple single-block CFG, just generate the statements
        # A more sophisticated implementation would handle multiple blocks
        entry_block = next((b for b in cfg.blocks if b.id == cfg.entry), None)
        if not entry_block:
            return "pass"

        lines: list[str] = []

        # Generate statements
        for stmt in entry_block.statements:
            stmt_code = self._gen_statement(stmt, context)
            if stmt_code:
                lines.append(stmt_code)

        # Generate terminator
        term_code = self._gen_terminator(entry_block.terminator, context)
        if term_code:
            lines.append(term_code)

        if not lines:
            return "pass"

        return "\n".join(lines)

    def _gen_statement(self, stmt: Statement, context: SynthesisContext) -> str:
        """Generate code for a statement.

        Args:
            stmt: Statement IR
            context: Synthesis context

        Returns:
            Generated statement code
        """
        if stmt.kind == "assign":
            if stmt.target and stmt.value:
                value_str = self._gen_expression(stmt.value, context)
                # Need to resolve target name from binding
                target_name = stmt.target.split(":")[-1] if ":" in stmt.target else stmt.target
                return f"{target_name} = {value_str}"
            return ""

        elif stmt.kind == "call":
            if stmt.callee:
                callee_str = self._gen_expression(stmt.callee, context)
                args = ", ".join(
                    self._gen_expression(a, context) for a in stmt.arguments
                )
                return f"{callee_str}({args})"
            return ""

        elif stmt.kind == "noop":
            return ""

        return ""

    def _gen_terminator(
        self, term: Terminator, context: SynthesisContext
    ) -> str:
        """Generate code for a terminator.

        Args:
            term: Terminator IR
            context: Synthesis context

        Returns:
            Generated terminator code
        """
        if term.kind == TerminatorKind.RETURN:
            if term.value:
                value_str = self._gen_expression(term.value, context)
                return f"return {value_str}"
            return "return"

        elif term.kind == TerminatorKind.BRANCH:
            # if condition: goto then_block else goto else_block
            if term.condition:
                cond_str = self._gen_expression(term.condition, context)
                return f"if {cond_str}:\n    pass  # branch to {term.then_block}"
            return ""

        elif term.kind == TerminatorKind.UNREACHABLE:
            return f'raise RuntimeError("Unreachable: {term.reason or "unknown"}")'

        return ""

    def _gen_expression(
        self, expr: Expression, context: SynthesisContext
    ) -> str:
        """Generate code for an expression.

        Args:
            expr: Expression IR
            context: Synthesis context

        Returns:
            Generated expression code
        """
        if expr.kind == ExpressionKind.LITERAL:
            return self._gen_literal(expr, context)

        elif expr.kind == ExpressionKind.IDENTIFIER:
            return expr.name or ""

        elif expr.kind == ExpressionKind.CALL:
            callee = self._gen_expression(expr.callee, context) if expr.callee else ""
            args = ", ".join(
                self._gen_argument(a, context) for a in expr.arguments
            )
            return f"{callee}({args})"

        elif expr.kind == ExpressionKind.OPERATOR:
            return self._gen_operator(expr, context)

        elif expr.kind == ExpressionKind.MEMBER_ACCESS:
            obj = self._gen_expression(expr.object, context) if expr.object else ""
            return f"{obj}.{expr.member}"

        elif expr.kind == ExpressionKind.INDEX:
            coll = self._gen_expression(expr.collection, context) if expr.collection else ""
            idx = self._gen_expression(expr.index, context) if expr.index else ""
            return f"{coll}[{idx}]"

        elif expr.kind == ExpressionKind.LAMBDA:
            return self._gen_lambda(expr, context)

        elif expr.kind == ExpressionKind.CONDITIONAL:
            cond = self._gen_expression(expr.condition, context) if expr.condition else ""
            then = self._gen_expression(expr.then_expr, context) if expr.then_expr else ""
            else_ = self._gen_expression(expr.else_expr, context) if expr.else_expr else ""
            return f"{then} if {cond} else {else_}"

        elif expr.kind == ExpressionKind.TUPLE:
            elements = ", ".join(
                self._gen_expression(e, context) for e in expr.elements
            )
            return f"({elements})"

        elif expr.kind == ExpressionKind.ARRAY:
            elements = ", ".join(
                self._gen_expression(e, context) for e in expr.elements
            )
            return f"[{elements}]"

        elif expr.kind == ExpressionKind.OBJECT:
            fields = ", ".join(
                f"{f.name}: {self._gen_expression(f.value, context)}"
                for f in expr.fields
            )
            return f"{{{fields}}}"

        elif expr.kind == ExpressionKind.AWAIT:
            operand = self._gen_expression(expr.operand, context) if expr.operand else ""
            return f"await {operand}"

        elif expr.kind == ExpressionKind.THROW:
            operand = self._gen_expression(expr.operand, context) if expr.operand else ""
            return f"raise {operand}"

        return ""

    def _gen_literal(self, expr: Expression, context: SynthesisContext) -> str:
        """Generate a literal expression.

        Args:
            expr: Literal expression
            context: Synthesis context

        Returns:
            Literal code
        """
        value = expr.literal_value
        kind = expr.literal_kind

        if kind == "string" or kind == "bytes":
            return repr(value)
        elif kind == "integer" or kind == "float":
            return str(value)
        elif kind == "boolean":
            return "True" if value else "False"
        elif kind == "none":
            return "None"

        return repr(value)

    def _gen_operator(self, expr: Expression, context: SynthesisContext) -> str:
        """Generate an operator expression.

        Args:
            expr: Operator expression
            context: Synthesis context

        Returns:
            Operator expression code
        """
        op = expr.operator or ""
        operands = [
            self._gen_expression(o, context) for o in expr.operands
        ]

        # Map operator names to Python operators
        # See: https://docs.python.org/3/library/operator.html
        op_map = {
            # Arithmetic operators
            "add": "+",
            "sub": "-",
            "mul": "*",
            "div": "/",
            "truediv": "/",
            "floordiv": "//",
            "mod": "%",
            "pow": "**",
            "matmul": "@",
            "neg": "-",
            "pos": "+",
            # Comparison operators
            "eq": "==",
            "ne": "!=",
            "lt": "<",
            "le": "<=",
            "gt": ">",
            "ge": ">=",
            # Logical operators
            "and": "and",
            "or": "or",
            "not": "not",
            # Identity operators
            "is": "is",
            "is_not": "is not",
            # Membership operators
            "in": "in",
            "not_in": "not in",
            # Bitwise operators
            "bitand": "&",
            "bitor": "|",
            "bitxor": "^",
            "bitnot": "~",
            "invert": "~",
            "lshift": "<<",
            "rshift": ">>",
            # Assignment expression (Python 3.8+)
            "walrus": ":=",
        }

        py_op = op_map.get(op, op)

        if len(operands) == 1:
            # Unary operator
            return f"{py_op} {operands[0]}"
        elif len(operands) == 2:
            # Binary operator
            return f"{operands[0]} {py_op} {operands[1]}"

        return ""

    def _gen_lambda(self, expr: Expression, context: SynthesisContext) -> str:
        """Generate a lambda expression.

        Args:
            expr: Lambda expression
            context: Synthesis context

        Returns:
            Lambda code
        """
        params = ", ".join(p.name for p in expr.params)

        # Handle async lambdas (not directly supported in Python)
        if expr.is_async:
            # Can't have async lambdas, add gap
            # Would need access to context for gap tracking
            pass

        # Body
        body = ""
        if isinstance(expr.body, Expression):
            body = self._gen_expression(expr.body, context)
        else:
            # CFG body - can't be a lambda
            body = "..."

        return f"lambda {params}: {body}"

    def _gen_argument(self, arg: Argument, context: SynthesisContext) -> str:
        """Generate a function argument.

        Args:
            arg: Argument IR
            context: Synthesis context

        Returns:
            Argument code
        """

        value_str = self._gen_expression(arg.value, context)

        if arg.spread:
            return f"*{value_str}"
        elif arg.name:
            return f"{arg.name}={value_str}"
        return value_str

    def _gen_docstring(self, doc: str) -> str:
        """Generate a docstring.

        Args:
            doc: Documentation text

        Returns:
            Formatted docstring
        """
        if "\n" in doc:
            return f'"""{doc}\n"""'
        return f'"""{doc}"""'

    def _is_async(self, func: Function) -> bool:
        """Check if a function is async.

        Args:
            func: Function IR

        Returns:
            True if async
        """
        return any(e.kind == EffectKind.ASYNC for e in func.effects)

    def _extract_class_docstring(self, type_def: TypeDef) -> str | None:
        """Extract docstring from type definition annotations.

        Args:
            type_def: TypeDef IR

        Returns:
            Docstring or None
        """
        for annotation in type_def.annotations:
            if annotation.kind == "docstring":
                return annotation.value.get("text", "")
        return None

    def _find_function(
        self, func_id: str, context: SynthesisContext
    ) -> Function | None:
        """Find a function by ID in the IR.

        Args:
            func_id: Function ID to find
            context: Synthesis context

        Returns:
            Function or None
        """
        for func in context.ir.functions:
            if func.id == func_id:
                return func
        return None
