"""Scala source code parser.

Parses Scala source code using regex patterns to extract:
- Case classes and classes
- Traits with type parameters and variance
- Objects and companion objects
- Functions with implicits/using clauses
- Higher-kinded types
- Pattern matching
- For comprehensions
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class Variance(Enum):
    """Type parameter variance."""
    INVARIANT = "invariant"
    COVARIANT = "covariant"
    CONTRAVARIANT = "contravariant"


class TypeParamKind(Enum):
    """Kind of type parameter."""
    SIMPLE = "simple"
    HIGHER_KINDED = "higher_kinded"


@dataclass
class TypeParam:
    """Type parameter with variance and bounds."""
    name: str
    variance: Variance = Variance.INVARIANT
    kind: TypeParamKind = TypeParamKind.SIMPLE
    arity: int = 0  # For HKT: F[_] has arity 1, F[_, _] has arity 2
    upper_bound: Optional[str] = None
    lower_bound: Optional[str] = None
    context_bounds: list[str] = field(default_factory=list)


@dataclass
class ScalaField:
    """Case class or class field."""
    name: str
    type_annotation: str
    default_value: Optional[str] = None
    is_val: bool = True
    is_private: bool = False


@dataclass
class ScalaMethod:
    """Method definition."""
    name: str
    type_params: list[TypeParam] = field(default_factory=list)
    params: list[ScalaField] = field(default_factory=list)
    implicit_params: list[ScalaField] = field(default_factory=list)
    return_type: Optional[str] = None
    body: Optional[str] = None
    is_abstract: bool = False


@dataclass
class ScalaTrait:
    """Trait definition."""
    name: str
    type_params: list[TypeParam] = field(default_factory=list)
    extends: list[str] = field(default_factory=list)
    methods: list[ScalaMethod] = field(default_factory=list)
    self_type: Optional[str] = None


@dataclass
class ScalaCaseClass:
    """Case class definition."""
    name: str
    type_params: list[TypeParam] = field(default_factory=list)
    fields: list[ScalaField] = field(default_factory=list)
    extends: list[str] = field(default_factory=list)
    methods: list[ScalaMethod] = field(default_factory=list)


@dataclass
class ScalaClass:
    """Regular class definition."""
    name: str
    type_params: list[TypeParam] = field(default_factory=list)
    constructor_params: list[ScalaField] = field(default_factory=list)
    extends: list[str] = field(default_factory=list)
    methods: list[ScalaMethod] = field(default_factory=list)
    is_abstract: bool = False
    is_sealed: bool = False


@dataclass
class ScalaObject:
    """Object definition."""
    name: str
    extends: list[str] = field(default_factory=list)
    methods: list[ScalaMethod] = field(default_factory=list)
    is_companion: bool = False


@dataclass
class ScalaGiven:
    """Given instance (Scala 3)."""
    name: Optional[str]
    type_expr: str
    body: Optional[str] = None


@dataclass
class ScalaImport:
    """Import statement."""
    path: str
    selectors: list[str] = field(default_factory=list)
    is_wildcard: bool = False


@dataclass
class ScalaFunction:
    """Top-level function."""
    name: str
    type_params: list[TypeParam] = field(default_factory=list)
    params: list[ScalaField] = field(default_factory=list)
    implicit_params: list[ScalaField] = field(default_factory=list)
    return_type: Optional[str] = None
    body: Optional[str] = None


@dataclass
class ScalaModule:
    """Parsed Scala module."""
    package: Optional[str] = None
    imports: list[ScalaImport] = field(default_factory=list)
    traits: list[ScalaTrait] = field(default_factory=list)
    case_classes: list[ScalaCaseClass] = field(default_factory=list)
    classes: list[ScalaClass] = field(default_factory=list)
    objects: list[ScalaObject] = field(default_factory=list)
    functions: list[ScalaFunction] = field(default_factory=list)
    givens: list[ScalaGiven] = field(default_factory=list)


class ScalaParser:
    """Parser for Scala source code."""

    # Package pattern
    PACKAGE_PATTERN = re.compile(r'package\s+([\w.]+)')

    # Import patterns
    IMPORT_PATTERN = re.compile(
        r'import\s+([\w.]+)(?:\.\{([^}]+)\}|\.(\*)|\.(\w+))?'
    )

    # Type parameter patterns
    TYPE_PARAM_PATTERN = re.compile(
        r'([+-]?)(\w+)(?:\[([_,\s\w]+)\])?(?:\s*<:\s*(\w+))?(?:\s*>:\s*(\w+))?(?:\s*:\s*([\w\[\]]+))?'
    )

    # Trait pattern
    TRAIT_PATTERN = re.compile(
        r'(sealed\s+)?trait\s+(\w+)(?:\[([^\]]+)\])?(?:\s+extends\s+([^{]+))?\s*\{'
    )

    # Case class pattern
    CASE_CLASS_PATTERN = re.compile(
        r'case\s+class\s+(\w+)(?:\[([^\]]+)\])?\s*\(([^)]*)\)(?:\s+extends\s+([^{]+))?'
    )

    # Class pattern
    CLASS_PATTERN = re.compile(
        r'(abstract\s+)?(sealed\s+)?class\s+(\w+)(?:\[([^\]]+)\])?\s*(?:\(([^)]*)\))?(?:\s+extends\s+([^{]+))?\s*\{'
    )

    # Object pattern
    OBJECT_PATTERN = re.compile(
        r'(case\s+)?object\s+(\w+)(?:\s+extends\s+([^{]+))?\s*\{'
    )

    # Method/def pattern
    DEF_PATTERN = re.compile(
        r'(?:override\s+)?def\s+(\w+)(?:\[([^\]]+)\])?\s*(?:\(([^)]*)\))?(?:\s*\((?:implicit|using)\s+([^)]+)\))?\s*:\s*([^=]+?)(?:\s*=\s*(.+))?$',
        re.MULTILINE
    )

    # Given pattern (Scala 3)
    GIVEN_PATTERN = re.compile(
        r'given\s+(?:(\w+)\s*:\s*)?([\w\[\],\s]+)\s+with'
    )

    # Val/var pattern for fields
    VAL_PATTERN = re.compile(
        r'(private\s+)?val\s+(\w+)\s*:\s*([^=]+?)(?:\s*=\s*(.+))?$',
        re.MULTILINE
    )

    # For comprehension pattern
    FOR_PATTERN = re.compile(
        r'for\s*\{([^}]+)\}\s*yield\s+(.+)',
        re.DOTALL
    )

    # Pattern matching
    MATCH_PATTERN = re.compile(
        r'(\w+)\s+match\s*\{([^}]+)\}',
        re.DOTALL
    )

    def __init__(self) -> None:
        """Initialize the parser."""
        pass

    def parse(self, source: str) -> ScalaModule:
        """Parse Scala source code into a module structure."""
        module = ScalaModule()

        # Parse package
        pkg_match = self.PACKAGE_PATTERN.search(source)
        if pkg_match:
            module.package = pkg_match.group(1)

        # Parse imports
        module.imports = self._parse_imports(source)

        # Parse traits
        module.traits = self._parse_traits(source)

        # Parse case classes
        module.case_classes = self._parse_case_classes(source)

        # Parse classes
        module.classes = self._parse_classes(source)

        # Parse objects
        module.objects = self._parse_objects(source)

        # Parse top-level functions
        module.functions = self._parse_functions(source)

        # Parse givens
        module.givens = self._parse_givens(source)

        return module

    def _parse_imports(self, source: str) -> list[ScalaImport]:
        """Parse import statements."""
        imports = []

        for match in self.IMPORT_PATTERN.finditer(source):
            path = match.group(1)
            selectors_str = match.group(2)
            is_wildcard = match.group(3) is not None
            single_selector = match.group(4)

            selectors = []
            if selectors_str:
                selectors = [s.strip() for s in selectors_str.split(',')]
            elif single_selector:
                selectors = [single_selector]

            imports.append(ScalaImport(
                path=path,
                selectors=selectors,
                is_wildcard=is_wildcard,
            ))

        return imports

    def _parse_type_params(self, params_str: str) -> list[TypeParam]:
        """Parse type parameter string."""
        if not params_str:
            return []

        params = []
        # Split on commas, but not within brackets
        depth = 0
        current = ""
        for char in params_str:
            if char in '[(':
                depth += 1
                current += char
            elif char in '])':
                depth -= 1
                current += char
            elif char == ',' and depth == 0:
                if current.strip():
                    params.append(current.strip())
                current = ""
            else:
                current += char
        if current.strip():
            params.append(current.strip())

        result = []
        for param_str in params:
            param = self._parse_single_type_param(param_str)
            if param:
                result.append(param)

        return result

    def _parse_single_type_param(self, param_str: str) -> Optional[TypeParam]:
        """Parse a single type parameter."""
        param_str = param_str.strip()
        if not param_str:
            return None

        # Check for variance
        variance = Variance.INVARIANT
        if param_str.startswith('+'):
            variance = Variance.COVARIANT
            param_str = param_str[1:].strip()
        elif param_str.startswith('-'):
            variance = Variance.CONTRAVARIANT
            param_str = param_str[1:].strip()

        # Check for HKT
        kind = TypeParamKind.SIMPLE
        arity = 0
        if '[' in param_str:
            name_end = param_str.index('[')
            name = param_str[:name_end].strip()
            hkt_part = param_str[name_end+1:param_str.rindex(']')]
            # Count underscores for arity
            arity = hkt_part.count('_')
            if arity > 0:
                kind = TypeParamKind.HIGHER_KINDED
        else:
            # Check for bounds
            parts = re.split(r'\s*<:\s*|\s*>:\s*|\s*:\s*', param_str)
            name = parts[0].strip()

        # Check for bounds
        upper_bound = None
        lower_bound = None
        context_bounds = []

        if '<:' in param_str:
            upper_bound = param_str.split('<:')[1].split('>:')[0].split(':')[0].strip()
        if '>:' in param_str:
            lower_bound = param_str.split('>:')[1].split('<:')[0].split(':')[0].strip()
        if ':' in param_str and '<:' not in param_str.split(':')[0]:
            ctx = param_str.split(':')[-1].strip()
            if ctx and not ctx.startswith(':'):
                context_bounds = [ctx]

        return TypeParam(
            name=name if 'name' in dir() else param_str.split()[0],
            variance=variance,
            kind=kind,
            arity=arity,
            upper_bound=upper_bound,
            lower_bound=lower_bound,
            context_bounds=context_bounds,
        )

    def _parse_params(self, params_str: str) -> list[ScalaField]:
        """Parse parameter list."""
        if not params_str or not params_str.strip():
            return []

        fields = []
        # Split on commas, respecting brackets
        depth = 0
        current = ""
        for char in params_str:
            if char in '[({':
                depth += 1
                current += char
            elif char in '])}':
                depth -= 1
                current += char
            elif char == ',' and depth == 0:
                if current.strip():
                    field = self._parse_single_param(current.strip())
                    if field:
                        fields.append(field)
                current = ""
            else:
                current += char
        if current.strip():
            field = self._parse_single_param(current.strip())
            if field:
                fields.append(field)

        return fields

    def _parse_single_param(self, param_str: str) -> Optional[ScalaField]:
        """Parse a single parameter."""
        param_str = param_str.strip()
        if not param_str:
            return None

        is_private = param_str.startswith('private ')
        if is_private:
            param_str = param_str[8:].strip()

        is_val = param_str.startswith('val ')
        is_var = param_str.startswith('var ')
        if is_val:
            param_str = param_str[4:].strip()
        elif is_var:
            param_str = param_str[4:].strip()
            is_val = False

        # Split name and type
        if ':' in param_str:
            parts = param_str.split(':', 1)
            name = parts[0].strip()
            rest = parts[1].strip()

            # Check for default value
            default_value = None
            if '=' in rest:
                type_part, default_part = rest.split('=', 1)
                type_annotation = type_part.strip()
                default_value = default_part.strip()
            else:
                type_annotation = rest
        else:
            name = param_str
            type_annotation = "Any"

        return ScalaField(
            name=name,
            type_annotation=type_annotation,
            default_value=default_value,
            is_val=is_val,
            is_private=is_private,
        )

    def _parse_traits(self, source: str) -> list[ScalaTrait]:
        """Parse trait definitions."""
        traits = []

        for match in self.TRAIT_PATTERN.finditer(source):
            is_sealed = match.group(1) is not None
            name = match.group(2)
            type_params_str = match.group(3)
            extends_str = match.group(4)

            type_params = self._parse_type_params(type_params_str) if type_params_str else []
            extends = [e.strip() for e in extends_str.split('with')] if extends_str else []

            # Find trait body and parse methods
            start = match.end()
            body = self._find_block_body(source, start - 1)
            methods = self._parse_methods(body) if body else []

            traits.append(ScalaTrait(
                name=name,
                type_params=type_params,
                extends=extends,
                methods=methods,
            ))

        return traits

    def _parse_case_classes(self, source: str) -> list[ScalaCaseClass]:
        """Parse case class definitions."""
        case_classes = []

        for match in self.CASE_CLASS_PATTERN.finditer(source):
            name = match.group(1)
            type_params_str = match.group(2)
            params_str = match.group(3)
            extends_str = match.group(4)

            type_params = self._parse_type_params(type_params_str) if type_params_str else []
            fields = self._parse_params(params_str) if params_str else []
            extends = [e.strip() for e in extends_str.split('with')] if extends_str else []

            case_classes.append(ScalaCaseClass(
                name=name,
                type_params=type_params,
                fields=fields,
                extends=extends,
            ))

        return case_classes

    def _parse_classes(self, source: str) -> list[ScalaClass]:
        """Parse class definitions."""
        classes = []

        for match in self.CLASS_PATTERN.finditer(source):
            is_abstract = match.group(1) is not None
            is_sealed = match.group(2) is not None
            name = match.group(3)
            type_params_str = match.group(4)
            params_str = match.group(5)
            extends_str = match.group(6)

            type_params = self._parse_type_params(type_params_str) if type_params_str else []
            constructor_params = self._parse_params(params_str) if params_str else []
            extends = [e.strip() for e in extends_str.split('with')] if extends_str else []

            # Find class body and parse methods
            start = match.end()
            body = self._find_block_body(source, start - 1)
            methods = self._parse_methods(body) if body else []

            classes.append(ScalaClass(
                name=name,
                type_params=type_params,
                constructor_params=constructor_params,
                extends=extends,
                methods=methods,
                is_abstract=is_abstract,
                is_sealed=is_sealed,
            ))

        return classes

    def _parse_objects(self, source: str) -> list[ScalaObject]:
        """Parse object definitions."""
        objects = []

        for match in self.OBJECT_PATTERN.finditer(source):
            is_case = match.group(1) is not None
            name = match.group(2)
            extends_str = match.group(3)

            extends = [e.strip() for e in extends_str.split('with')] if extends_str else []

            # Find object body and parse methods
            start = match.end()
            body = self._find_block_body(source, start - 1)
            methods = self._parse_methods(body) if body else []

            objects.append(ScalaObject(
                name=name,
                extends=extends,
                methods=methods,
            ))

        return objects

    def _parse_methods(self, body: str) -> list[ScalaMethod]:
        """Parse methods from a body."""
        methods = []

        for match in self.DEF_PATTERN.finditer(body):
            name = match.group(1)
            type_params_str = match.group(2)
            params_str = match.group(3)
            implicit_params_str = match.group(4)
            return_type = match.group(5).strip() if match.group(5) else None
            method_body = match.group(6)

            type_params = self._parse_type_params(type_params_str) if type_params_str else []
            params = self._parse_params(params_str) if params_str else []
            implicit_params = self._parse_params(implicit_params_str) if implicit_params_str else []

            methods.append(ScalaMethod(
                name=name,
                type_params=type_params,
                params=params,
                implicit_params=implicit_params,
                return_type=return_type,
                body=method_body.strip() if method_body else None,
                is_abstract=method_body is None,
            ))

        return methods

    def _parse_functions(self, source: str) -> list[ScalaFunction]:
        """Parse top-level function definitions."""
        functions = []

        # Find defs that are not inside class/trait/object
        # This is a simplified approach
        for match in self.DEF_PATTERN.finditer(source):
            # Check if this def is at top level (not indented significantly)
            line_start = source.rfind('\n', 0, match.start()) + 1
            indent = match.start() - line_start
            if indent > 2:
                continue  # Likely inside a class/trait/object

            name = match.group(1)
            type_params_str = match.group(2)
            params_str = match.group(3)
            implicit_params_str = match.group(4)
            return_type = match.group(5).strip() if match.group(5) else None
            func_body = match.group(6)

            type_params = self._parse_type_params(type_params_str) if type_params_str else []
            params = self._parse_params(params_str) if params_str else []
            implicit_params = self._parse_params(implicit_params_str) if implicit_params_str else []

            functions.append(ScalaFunction(
                name=name,
                type_params=type_params,
                params=params,
                implicit_params=implicit_params,
                return_type=return_type,
                body=func_body.strip() if func_body else None,
            ))

        return functions

    def _parse_givens(self, source: str) -> list[ScalaGiven]:
        """Parse given instances (Scala 3)."""
        givens = []

        for match in self.GIVEN_PATTERN.finditer(source):
            name = match.group(1)
            type_expr = match.group(2).strip()

            givens.append(ScalaGiven(
                name=name,
                type_expr=type_expr,
            ))

        return givens

    def _find_block_body(self, source: str, start: int) -> Optional[str]:
        """Find the body of a block starting with {."""
        if start >= len(source) or source[start] != '{':
            return None

        depth = 1
        pos = start + 1
        while pos < len(source) and depth > 0:
            if source[pos] == '{':
                depth += 1
            elif source[pos] == '}':
                depth -= 1
            pos += 1

        if depth == 0:
            return source[start + 1:pos - 1]
        return None
