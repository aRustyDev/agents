"""Scala source code extractor.

Main extractor implementation that transforms Scala source code
into the 5-layer IR representation.
"""

from __future__ import annotations

import logging
from typing import Any

from ir_core.base import (
    ExtractConfig,
    Extractor,
    register_extractor,
)
from ir_core.models import (
    Annotation,
    FunctionDef,
    GapMarker,
    GapSeverity,
    IRVersion,
    Parameter,
    StructuralInfo,
    TypeDef,
    TypeKind,
)

from ir_extract_scala.parser import (
    ScalaCaseClass,
    ScalaClass,
    ScalaField,
    ScalaFunction,
    ScalaMethod,
    ScalaModule,
    ScalaObject,
    ScalaParser,
    ScalaTrait,
    TypeParam,
    TypeParamKind,
    Variance,
)

logger = logging.getLogger(__name__)


@register_extractor("scala")
class ScalaExtractor(Extractor):
    """Scala source code extractor.

    Extracts structured IR from Scala source code with special handling for:

    - Higher-kinded types (F[_])
    - Variance annotations (+T, -T)
    - Implicits and given instances
    - Case classes and sealed traits
    - Pattern matching
    - For comprehensions
    - Type classes
    """

    def __init__(self) -> None:
        """Initialize the extractor."""
        self._parser = ScalaParser()

    def extract(self, source: str, path: str, config: ExtractConfig) -> IRVersion:
        """Extract IR from Scala source code.

        Args:
            source: Scala source code
            path: Source file path
            config: Extraction configuration

        Returns:
            Extracted IR version
        """
        logger.info(f"Extracting IR from Scala source: {path}")

        # Parse source
        module = self._parser.parse(source)

        # Create IR version
        ir = IRVersion(
            version="ir-v1.0",
            source_language="scala",
            source_path=path,
        )

        # Extract structural info
        ir.structural = self._extract_structural(module)

        # Extract types
        ir.types = self._extract_types(module)

        # Extract functions
        ir.functions = self._extract_functions(module)

        # Generate semantic annotations
        ir.annotations = self._generate_annotations(module)

        # Detect gaps
        ir.gaps = self._detect_gaps(module)

        return ir

    def supported_version(self) -> str:
        """Return the IR schema version this extractor produces."""
        return "ir-v1.0"

    def _extract_structural(self, module: ScalaModule) -> StructuralInfo:
        """Extract structural information."""
        imports = []

        for imp in module.imports:
            import_entry: dict[str, Any] = {"module": imp.path}
            if imp.selectors:
                import_entry["selectors"] = imp.selectors
            if imp.is_wildcard:
                import_entry["wildcard"] = True
            imports.append(import_entry)

        exports = []
        # Export all public types and functions
        for trait in module.traits:
            exports.append(trait.name)
        for cc in module.case_classes:
            exports.append(cc.name)
        for cls in module.classes:
            exports.append(cls.name)
        for obj in module.objects:
            exports.append(obj.name)

        return StructuralInfo(
            imports=imports,
            exports=exports,
        )

    def _extract_types(self, module: ScalaModule) -> list[TypeDef]:
        """Extract type definitions."""
        types = []

        # Extract traits
        for trait in module.traits:
            types.append(self._extract_trait(trait))

        # Extract case classes
        for cc in module.case_classes:
            types.append(self._extract_case_class(cc))

        # Extract classes
        for cls in module.classes:
            types.append(self._extract_class(cls))

        # Extract objects
        for obj in module.objects:
            types.append(self._extract_object(obj))

        return types

    def _extract_trait(self, trait: ScalaTrait) -> TypeDef:
        """Extract trait as interface type."""
        type_params = self._convert_type_params(trait.type_params)
        methods = [self._convert_method_to_signature(m) for m in trait.methods]

        return TypeDef(
            name=trait.name,
            kind=TypeKind.INTERFACE,
            type_params=type_params,
            methods=methods,
            extends=trait.extends if trait.extends else None,
        )

    def _extract_case_class(self, cc: ScalaCaseClass) -> TypeDef:
        """Extract case class as struct type."""
        type_params = self._convert_type_params(cc.type_params)
        properties = [self._convert_field_to_property(f) for f in cc.fields]

        return TypeDef(
            name=cc.name,
            kind=TypeKind.STRUCT,
            type_params=type_params,
            properties=properties,
            extends=cc.extends if cc.extends else None,
        )

    def _extract_class(self, cls: ScalaClass) -> TypeDef:
        """Extract class as class type."""
        type_params = self._convert_type_params(cls.type_params)
        properties = [self._convert_field_to_property(f) for f in cls.constructor_params]
        methods = [self._convert_method_to_signature(m) for m in cls.methods]

        kind = TypeKind.CLASS
        if cls.is_abstract:
            kind = TypeKind.INTERFACE  # Abstract class treated as interface

        return TypeDef(
            name=cls.name,
            kind=kind,
            type_params=type_params,
            properties=properties,
            methods=methods,
            extends=cls.extends if cls.extends else None,
        )

    def _extract_object(self, obj: ScalaObject) -> TypeDef:
        """Extract object as singleton type."""
        methods = [self._convert_method_to_signature(m) for m in obj.methods]

        return TypeDef(
            name=obj.name,
            kind=TypeKind.CLASS,
            methods=methods,
            extends=obj.extends if obj.extends else None,
            # Mark as singleton
        )

    def _convert_type_params(self, params: list[TypeParam]) -> list[dict[str, Any]]:
        """Convert type parameters to IR format."""
        result = []
        for param in params:
            entry: dict[str, Any] = {"name": param.name}

            if param.variance != Variance.INVARIANT:
                entry["variance"] = param.variance.value

            if param.kind == TypeParamKind.HIGHER_KINDED:
                entry["kind"] = "higher_kinded"
                entry["arity"] = param.arity

            if param.upper_bound:
                entry["upper_bound"] = param.upper_bound

            if param.lower_bound:
                entry["lower_bound"] = param.lower_bound

            if param.context_bounds:
                entry["context_bounds"] = param.context_bounds

            result.append(entry)

        return result

    def _convert_field_to_property(self, field: ScalaField) -> dict[str, Any]:
        """Convert field to property dict."""
        prop: dict[str, Any] = {
            "name": field.name,
            "type": field.type_annotation,
        }
        if field.default_value:
            prop["default"] = field.default_value
        if field.is_private:
            prop["visibility"] = "private"
        return prop

    def _convert_method_to_signature(self, method: ScalaMethod) -> dict[str, Any]:
        """Convert method to signature dict."""
        sig: dict[str, Any] = {"name": method.name}

        if method.type_params:
            sig["type_params"] = self._convert_type_params(method.type_params)

        if method.params:
            sig["params"] = [
                {"name": p.name, "type": p.type_annotation}
                for p in method.params
            ]

        if method.implicit_params:
            sig["implicit_params"] = [
                {"name": p.name, "type": p.type_annotation}
                for p in method.implicit_params
            ]

        if method.return_type:
            sig["return_type"] = method.return_type

        if method.is_abstract:
            sig["abstract"] = True

        return sig

    def _extract_functions(self, module: ScalaModule) -> list[FunctionDef]:
        """Extract function definitions."""
        functions = []

        # Top-level functions
        for func in module.functions:
            functions.append(self._convert_function(func))

        # Object methods as functions
        for obj in module.objects:
            for method in obj.methods:
                func = FunctionDef(
                    name=f"{obj.name}.{method.name}",
                    parameters=[
                        Parameter(name=p.name, type_annotation=p.type_annotation)
                        for p in method.params
                    ],
                    return_type=method.return_type,
                )
                if method.implicit_params:
                    func.metadata = {
                        "implicit_params": [
                            {"name": p.name, "type": p.type_annotation}
                            for p in method.implicit_params
                        ]
                    }
                functions.append(func)

        return functions

    def _convert_function(self, func: ScalaFunction) -> FunctionDef:
        """Convert Scala function to FunctionDef."""
        parameters = [
            Parameter(name=p.name, type_annotation=p.type_annotation)
            for p in func.params
        ]

        result = FunctionDef(
            name=func.name,
            parameters=parameters,
            return_type=func.return_type,
        )

        if func.type_params:
            result.metadata = result.metadata or {}
            result.metadata["type_params"] = self._convert_type_params(func.type_params)

        if func.implicit_params:
            result.metadata = result.metadata or {}
            result.metadata["implicit_params"] = [
                {"name": p.name, "type": p.type_annotation}
                for p in func.implicit_params
            ]

        return result

    def _generate_annotations(self, module: ScalaModule) -> list[Annotation]:
        """Generate semantic annotations."""
        annotations = []

        # SC-001: Higher-kinded types
        for trait in module.traits:
            for param in trait.type_params:
                if param.kind == TypeParamKind.HIGHER_KINDED:
                    annotations.append(Annotation(
                        kind="SC-001",
                        target=f"trait:{trait.name}",
                        value={
                            "pattern": "higher_kinded_type",
                            "param": param.name,
                            "arity": param.arity,
                        },
                    ))

        # SC-002: Variance annotations
        for trait in module.traits:
            for param in trait.type_params:
                if param.variance != Variance.INVARIANT:
                    annotations.append(Annotation(
                        kind="SC-002",
                        target=f"trait:{trait.name}",
                        value={
                            "pattern": "variance",
                            "param": param.name,
                            "variance": param.variance.value,
                        },
                    ))

        # SC-003: Implicit parameters
        for obj in module.objects:
            for method in obj.methods:
                if method.implicit_params:
                    annotations.append(Annotation(
                        kind="SC-003",
                        target=f"method:{obj.name}.{method.name}",
                        value={
                            "pattern": "implicit_params",
                            "count": len(method.implicit_params),
                        },
                    ))

        # SC-004: Given instances
        for given in module.givens:
            annotations.append(Annotation(
                kind="SC-004",
                target=f"given:{given.name or 'anonymous'}",
                value={
                    "pattern": "given_instance",
                    "type": given.type_expr,
                },
            ))

        # SC-005: Case classes (product types)
        for cc in module.case_classes:
            annotations.append(Annotation(
                kind="SC-005",
                target=f"case_class:{cc.name}",
                value={
                    "pattern": "case_class",
                    "field_count": len(cc.fields),
                },
            ))

        return annotations

    def _detect_gaps(self, module: ScalaModule) -> list[GapMarker]:
        """Detect potential gaps for cross-language conversion."""
        gaps = []

        # SC-010: Higher-kinded types (not available in many languages)
        for trait in module.traits:
            for param in trait.type_params:
                if param.kind == TypeParamKind.HIGHER_KINDED:
                    gaps.append(GapMarker(
                        kind="SC-010",
                        description=f"Higher-kinded type parameter '{param.name}' in '{trait.name}'",
                        location=f"trait:{trait.name}",
                        severity=GapSeverity.HIGH,
                        suggestion="Use concrete types or protocol-based dispatch",
                    ))

        # SC-011: Variance annotations
        for trait in module.traits:
            for param in trait.type_params:
                if param.variance != Variance.INVARIANT:
                    gaps.append(GapMarker(
                        kind="SC-011",
                        description=f"Variance annotation on '{param.name}' in '{trait.name}'",
                        location=f"trait:{trait.name}",
                        severity=GapSeverity.MEDIUM,
                        suggestion="Variance may need manual verification in target language",
                    ))

        # SC-012: Implicit parameters
        for obj in module.objects:
            for method in obj.methods:
                if method.implicit_params:
                    gaps.append(GapMarker(
                        kind="SC-012",
                        description=f"Implicit parameters in '{obj.name}.{method.name}'",
                        location=f"method:{obj.name}.{method.name}",
                        severity=GapSeverity.MEDIUM,
                        suggestion="Convert to explicit parameters",
                    ))

        # SC-013: Given instances
        for given in module.givens:
            gaps.append(GapMarker(
                kind="SC-013",
                description=f"Given instance for '{given.type_expr}'",
                location=f"given:{given.name or 'anonymous'}",
                severity=GapSeverity.MEDIUM,
                suggestion="Convert to explicit type class instance",
            ))

        # SC-014: Self types
        for trait in module.traits:
            if trait.self_type:
                gaps.append(GapMarker(
                    kind="SC-014",
                    description=f"Self type in trait '{trait.name}'",
                    location=f"trait:{trait.name}",
                    severity=GapSeverity.MEDIUM,
                    suggestion="May require careful translation to mixins or composition",
                ))

        # SC-015: Context bounds
        for trait in module.traits:
            for param in trait.type_params:
                if param.context_bounds:
                    gaps.append(GapMarker(
                        kind="SC-015",
                        description=f"Context bound on '{param.name}' in '{trait.name}'",
                        location=f"trait:{trait.name}",
                        severity=GapSeverity.MEDIUM,
                        suggestion="Convert to explicit type class constraint",
                    ))

        return gaps
