"""JSDoc comment parser for TypeScript.

Extracts structured information from JSDoc comments including:
- @param, @returns, @type annotations
- @template for generics
- @deprecated, @example, @see tags
- @typedef and @callback definitions
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class JSDocParam:
    """JSDoc @param annotation."""

    name: str
    type_annotation: str | None = None
    description: str | None = None
    optional: bool = False
    default_value: str | None = None


@dataclass
class JSDocReturns:
    """JSDoc @returns annotation."""

    type_annotation: str | None = None
    description: str | None = None


@dataclass
class JSDocTemplate:
    """JSDoc @template annotation."""

    name: str
    constraint: str | None = None
    description: str | None = None


@dataclass
class JSDocExample:
    """JSDoc @example annotation."""

    code: str
    caption: str | None = None


@dataclass
class JSDocTypedef:
    """JSDoc @typedef annotation."""

    name: str
    type_annotation: str | None = None
    properties: list[JSDocParam] = field(default_factory=list)


@dataclass
class JSDocComment:
    """Parsed JSDoc comment block."""

    raw: str
    description: str | None = None
    params: list[JSDocParam] = field(default_factory=list)
    returns: JSDocReturns | None = None
    templates: list[JSDocTemplate] = field(default_factory=list)
    throws: list[tuple[str | None, str]] = field(default_factory=list)  # (type, desc)
    examples: list[JSDocExample] = field(default_factory=list)
    see_also: list[str] = field(default_factory=list)
    deprecated: str | None = None  # Deprecation message or empty string if deprecated
    since: str | None = None
    version: str | None = None
    author: str | None = None
    license_: str | None = None
    type_annotation: str | None = None  # @type {Type}
    typedef: JSDocTypedef | None = None
    callback: JSDocTypedef | None = None
    fires: list[str] = field(default_factory=list)
    listens: list[str] = field(default_factory=list)
    readonly: bool = False
    private: bool = False
    protected: bool = False
    public: bool = False
    internal: bool = False
    override: bool = False
    abstract: bool = False
    async_: bool = False
    generator: bool = False
    fileoverview: str | None = None
    module: str | None = None
    line: int = 0

    @property
    def is_deprecated(self) -> bool:
        """Check if marked as deprecated."""
        return self.deprecated is not None


class JSDocParser:
    """Parser for JSDoc comment blocks."""

    # Regex patterns for JSDoc tags
    TAG_PATTERN = re.compile(r"@(\w+)(?:\s+(.*))?$")
    TYPE_PATTERN = re.compile(r"\{([^}]+)\}")
    PARAM_PATTERN = re.compile(r"\{([^}]+)\}\s+(?:\[([^\]]+)\]|(\S+))(?:\s+-\s*(.*))?$")
    RETURNS_PATTERN = re.compile(r"\{([^}]+)\}(?:\s+(.*))?$")
    TEMPLATE_PATTERN = re.compile(r"(\w+)(?:\s+extends\s+(\S+))?(?:\s+-\s*(.*))?$")

    def parse(self, comment: str, line: int = 0) -> JSDocComment | None:
        """Parse a JSDoc comment block.

        Args:
            comment: Raw comment text (with /** and */)
            line: Line number where comment starts

        Returns:
            Parsed JSDocComment or None if not a valid JSDoc
        """
        if not comment.strip().startswith("/**"):
            return None

        # Remove /** and */
        content = comment.strip()
        if content.startswith("/**"):
            content = content[3:]
        if content.endswith("*/"):
            content = content[:-2]

        # Clean up lines
        lines = []
        for raw_line in content.split("\n"):
            # Remove leading * and whitespace
            cleaned = raw_line.strip()
            if cleaned.startswith("*"):
                cleaned = cleaned[1:].strip()
            lines.append(cleaned)

        result = JSDocComment(raw=comment, line=line)
        description_lines = []
        current_tag = None
        current_content: list[str] = []

        for line_text in lines:
            if line_text.startswith("@"):
                # Process previous tag
                if current_tag:
                    self._process_tag(result, current_tag, " ".join(current_content))
                elif description_lines:
                    result.description = " ".join(description_lines).strip()
                    description_lines = []

                # Parse new tag
                match = self.TAG_PATTERN.match(line_text)
                if match:
                    current_tag = match.group(1)
                    current_content = [match.group(2) or ""]
                else:
                    current_tag = None
                    current_content = []
            elif current_tag:
                current_content.append(line_text)
            else:
                description_lines.append(line_text)

        # Process final tag or description
        if current_tag:
            self._process_tag(result, current_tag, " ".join(current_content))
        elif description_lines:
            result.description = " ".join(description_lines).strip()

        return result

    def _process_tag(self, result: JSDocComment, tag: str, content: str) -> None:
        """Process a single JSDoc tag."""
        content = content.strip()

        if tag == "param":
            param = self._parse_param(content)
            if param:
                result.params.append(param)

        elif tag in ("returns", "return"):
            result.returns = self._parse_returns(content)

        elif tag == "template":
            template = self._parse_template(content)
            if template:
                result.templates.append(template)

        elif tag in ("throws", "exception"):
            throws = self._parse_throws(content)
            if throws:
                result.throws.append(throws)

        elif tag == "example":
            example = self._parse_example(content)
            if example:
                result.examples.append(example)

        elif tag == "see":
            if content:
                result.see_also.append(content)

        elif tag == "deprecated":
            result.deprecated = content or ""

        elif tag == "since":
            result.since = content

        elif tag == "version":
            result.version = content

        elif tag == "author":
            result.author = content

        elif tag == "license":
            result.license_ = content

        elif tag == "type":
            type_match = self.TYPE_PATTERN.match(content)
            if type_match:
                result.type_annotation = type_match.group(1)

        elif tag == "typedef":
            result.typedef = self._parse_typedef(content)

        elif tag == "callback":
            result.callback = self._parse_typedef(content)

        elif tag == "fires":
            if content:
                result.fires.append(content)

        elif tag == "listens":
            if content:
                result.listens.append(content)

        elif tag == "readonly":
            result.readonly = True

        elif tag == "private":
            result.private = True

        elif tag == "protected":
            result.protected = True

        elif tag == "public":
            result.public = True

        elif tag == "internal":
            result.internal = True

        elif tag == "override":
            result.override = True

        elif tag == "abstract":
            result.abstract = True

        elif tag == "async":
            result.async_ = True

        elif tag == "generator":
            result.generator = True

        elif tag == "fileoverview":
            result.fileoverview = content

        elif tag == "module":
            result.module = content

    def _parse_param(self, content: str) -> JSDocParam | None:
        """Parse @param tag content."""
        if not content:
            return None

        match = self.PARAM_PATTERN.match(content)
        if match:
            type_ann = match.group(1)
            optional_name = match.group(2)
            required_name = match.group(3)
            description = match.group(4)

            if optional_name:
                # Handle [name] or [name=default]
                if "=" in optional_name:
                    name, default = optional_name.split("=", 1)
                    return JSDocParam(
                        name=name.strip(),
                        type_annotation=type_ann,
                        description=description,
                        optional=True,
                        default_value=default.strip(),
                    )
                return JSDocParam(
                    name=optional_name.strip(),
                    type_annotation=type_ann,
                    description=description,
                    optional=True,
                )
            elif required_name:
                return JSDocParam(
                    name=required_name,
                    type_annotation=type_ann,
                    description=description,
                    optional=False,
                )

        # Fallback: try simpler parsing
        type_match = self.TYPE_PATTERN.match(content)
        if type_match:
            rest = content[type_match.end() :].strip()
            parts = rest.split(None, 1)
            if parts:
                name = parts[0]
                desc = parts[1] if len(parts) > 1 else None
                if desc and desc.startswith("- "):
                    desc = desc[2:]
                return JSDocParam(
                    name=name,
                    type_annotation=type_match.group(1),
                    description=desc,
                )

        return None

    def _parse_returns(self, content: str) -> JSDocReturns:
        """Parse @returns tag content."""
        match = self.RETURNS_PATTERN.match(content)
        if match:
            return JSDocReturns(
                type_annotation=match.group(1),
                description=match.group(2),
            )

        # Try to extract just the type
        type_match = self.TYPE_PATTERN.match(content)
        if type_match:
            rest = content[type_match.end() :].strip()
            return JSDocReturns(
                type_annotation=type_match.group(1),
                description=rest if rest else None,
            )

        return JSDocReturns(description=content if content else None)

    def _parse_template(self, content: str) -> JSDocTemplate | None:
        """Parse @template tag content."""
        if not content:
            return None

        match = self.TEMPLATE_PATTERN.match(content)
        if match:
            return JSDocTemplate(
                name=match.group(1),
                constraint=match.group(2),
                description=match.group(3),
            )

        # Simple case: just the name
        name = content.split()[0] if content else None
        if name:
            return JSDocTemplate(name=name)

        return None

    def _parse_throws(self, content: str) -> tuple[str | None, str] | None:
        """Parse @throws tag content."""
        if not content:
            return None

        type_match = self.TYPE_PATTERN.match(content)
        if type_match:
            desc = content[type_match.end() :].strip()
            return (type_match.group(1), desc)

        return (None, content)

    def _parse_example(self, content: str) -> JSDocExample:
        """Parse @example tag content."""
        # Check for caption in <caption>...</caption>
        caption = None
        code = content

        caption_match = re.match(r"<caption>(.*?)</caption>\s*(.*)", content, re.DOTALL)
        if caption_match:
            caption = caption_match.group(1).strip()
            code = caption_match.group(2).strip()

        return JSDocExample(code=code, caption=caption)

    def _parse_typedef(self, content: str) -> JSDocTypedef | None:
        """Parse @typedef tag content."""
        if not content:
            return None

        type_match = self.TYPE_PATTERN.match(content)
        if type_match:
            type_ann = type_match.group(1)
            rest = content[type_match.end() :].strip()
            name = rest.split()[0] if rest else None
            if name:
                return JSDocTypedef(name=name, type_annotation=type_ann)

        # Just a name
        name = content.split()[0] if content else None
        if name:
            return JSDocTypedef(name=name)

        return None


def extract_jsdoc_from_source(source: str) -> list[tuple[int, JSDocComment]]:
    """Extract all JSDoc comments from source code.

    Args:
        source: TypeScript source code

    Returns:
        List of (line_number, JSDocComment) tuples
    """
    parser = JSDocParser()
    results = []

    # Find all /** ... */ comments
    pattern = re.compile(r"/\*\*[\s\S]*?\*/")

    for match in pattern.finditer(source):
        start = source[: match.start()].count("\n") + 1
        comment = parser.parse(match.group(), line=start)
        if comment:
            results.append((start, comment))

    return results


def get_preceding_jsdoc(
    source: str, target_line: int, jsdoc_comments: list[tuple[int, JSDocComment]]
) -> JSDocComment | None:
    """Find the JSDoc comment immediately preceding a target line.

    Args:
        source: Source code
        target_line: Line number of the target declaration (1-indexed)
        jsdoc_comments: Pre-extracted JSDoc comments

    Returns:
        The preceding JSDoc comment if found, None otherwise
    """
    # Find JSDoc that ends right before target_line
    for start_line, jsdoc in reversed(jsdoc_comments):
        # Count lines in the JSDoc comment
        lines_in_comment = jsdoc.raw.count("\n") + 1
        end_line = start_line + lines_in_comment - 1

        # Allow for blank lines between JSDoc and declaration
        if end_line <= target_line <= end_line + 2:
            return jsdoc

    return None
