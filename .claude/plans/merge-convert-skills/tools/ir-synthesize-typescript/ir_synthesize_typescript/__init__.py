"""TypeScript synthesizer for the IR extraction/synthesis pipeline.

This package synthesizes TypeScript source code from the 5-layer IR representation,
generating valid TypeScript with proper:

- Type annotations and generics
- Interface and type alias definitions
- Import/export statements
- Class definitions with decorators
- Async/await syntax

Example:
    from ir_synthesize_typescript import TypeScriptSynthesizer
    from ir_core.base import SynthConfig, OutputFormat

    synthesizer = TypeScriptSynthesizer()
    code = synthesizer.synthesize(ir, SynthConfig(
        output_format=OutputFormat.FORMATTED,
        target_version="ES2022",
    ))

    print(code)
"""

from ir_synthesize_typescript.synthesizer import TypeScriptSynthesizer

__all__ = ["TypeScriptSynthesizer"]
__version__ = "0.1.0"
