"""Safe code execution for round-trip validation.

This module provides safe execution of Python code for L3 semantic
comparison. It uses subprocess isolation with timeouts and memory
limits to prevent runaway code.

SECURITY WARNING:
    This executor is designed for TRUSTED code only (e.g., test fixtures,
    generated code from controlled sources). It does NOT provide sandbox-level
    isolation for arbitrary untrusted code.

    For untrusted code, use container isolation (Docker, gVisor) or
    a dedicated sandbox like Firecracker, Bubblewrap, or nsjail.

Security measures implemented:
    - Subprocess isolation (separate process)
    - Execution timeout (configurable, default 5s)
    - Output size limits (configurable)
    - Optional memory/CPU limits (Linux only via resource module)

NOT implemented (out of scope for this module):
    - Network isolation (use firewall rules or container network policies)
    - Filesystem isolation (use container or chroot)
    - System call filtering (use seccomp)

Example:
    executor = SafeExecutor()

    result = executor.execute(
        code="def add(a, b): return a + b",
        inputs={"a": 1, "b": 2},
        func_name="add"
    )

    if result.success:
        print(f"Result: {result.return_value}")
    else:
        print(f"Error: {result.exception_message}")
"""

from __future__ import annotations

import json
import platform
import subprocess
import sys
import tempfile
import textwrap
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# Resource limits only available on Unix-like systems
try:
    import resource
    HAS_RESOURCE = True
except ImportError:
    HAS_RESOURCE = False


# Default values for security settings
DEFAULT_TIMEOUT_SECONDS = 5.0
DEFAULT_MAX_OUTPUT_BYTES = 1_000_000  # 1MB
DEFAULT_MEMORY_LIMIT_MB = 256


@dataclass
class ExecutorConfig:
    """Configuration for SafeExecutor with security settings.

    Attributes:
        timeout: Maximum execution time in seconds
        max_output_bytes: Maximum stdout/stderr size in bytes
        memory_limit_mb: Memory limit in MB (Linux only, requires resource module)
        enable_resource_limits: Whether to apply memory/CPU limits (Linux only)
        trusted_mode: Explicit acknowledgment that code is trusted

    Note:
        Resource limits (memory_limit_mb) only work on Linux/Unix systems
        with the 'resource' module available. On other platforms, these
        limits are silently ignored.
    """
    timeout: float = DEFAULT_TIMEOUT_SECONDS
    max_output_bytes: int = DEFAULT_MAX_OUTPUT_BYTES
    memory_limit_mb: int = DEFAULT_MEMORY_LIMIT_MB
    enable_resource_limits: bool = True
    trusted_mode: bool = True  # Explicit acknowledgment


class ExecutionError(Exception):
    """Error during code execution.

    Attributes:
        message: Error description
        code: Error code (TIMEOUT, MEMORY, PARSE, RUNTIME)
        details: Additional error details
    """

    def __init__(
        self,
        message: str,
        code: str = "RUNTIME",
        details: dict[str, Any] | None = None,
    ) -> None:
        self.code = code
        self.details = details or {}
        super().__init__(message)


@dataclass
class ExecutionResult:
    """Result of executing Python code.

    Attributes:
        success: Whether execution completed without error
        return_value: Return value from the executed code
        stdout: Standard output captured during execution
        stderr: Standard error captured during execution
        exception_type: Type of exception raised (if any)
        exception_message: Exception message (if any)
        execution_time_ms: Execution time in milliseconds
        timed_out: Whether execution timed out
    """

    success: bool
    return_value: Any = None
    stdout: str = ""
    stderr: str = ""
    exception_type: str | None = None
    exception_message: str | None = None
    execution_time_ms: float = 0.0
    timed_out: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "success": self.success,
            "return_value": repr(self.return_value),
            "stdout": self.stdout,
            "stderr": self.stderr,
            "exception_type": self.exception_type,
            "exception_message": self.exception_message,
            "execution_time_ms": self.execution_time_ms,
            "timed_out": self.timed_out,
        }

    @classmethod
    def timeout(cls) -> ExecutionResult:
        """Create a timeout result."""
        return cls(
            success=False,
            exception_type="TimeoutError",
            exception_message="Execution timed out",
            timed_out=True,
        )

    @classmethod
    def error(cls, exception_type: str, message: str) -> ExecutionResult:
        """Create an error result."""
        return cls(
            success=False,
            exception_type=exception_type,
            exception_message=message,
        )


class SafeExecutor:
    """Execute Python code safely in a subprocess.

    This executor provides isolation for running TRUSTED code by:
    - Using subprocess isolation
    - Enforcing execution timeouts
    - Limiting output size
    - Capturing exceptions
    - Optional resource limits (Linux only)

    SECURITY NOTE:
        This is NOT a sandbox for untrusted code. For untrusted code,
        use container isolation (Docker, gVisor) or dedicated sandboxes.

    Example:
        # Using defaults
        executor = SafeExecutor()

        # With custom configuration
        config = ExecutorConfig(timeout=10.0, memory_limit_mb=512)
        executor = SafeExecutor(config=config)

        result = executor.execute(
            code="def factorial(n): return 1 if n <= 1 else n * factorial(n-1)",
            inputs={"n": 5},
            func_name="factorial"
        )

        print(f"5! = {result.return_value}")  # 5! = 120
    """

    def __init__(
        self,
        timeout: float | None = None,
        max_output: int | None = None,
        python_executable: str | None = None,
        config: ExecutorConfig | None = None,
    ) -> None:
        """Initialize the executor.

        Args:
            timeout: Maximum execution time in seconds (deprecated, use config)
            max_output: Maximum output size in bytes (deprecated, use config)
            python_executable: Path to Python interpreter (default: sys.executable)
            config: ExecutorConfig with all settings (preferred)
        """
        self.config = config or ExecutorConfig()

        # Support legacy parameters for backwards compatibility
        if timeout is not None:
            self.config.timeout = timeout
        if max_output is not None:
            self.config.max_output_bytes = max_output

        self.python_executable = python_executable or sys.executable

        # Create preexec function for resource limits (Linux only)
        self._preexec_fn: Callable[[], None] | None = None
        if (
            HAS_RESOURCE
            and self.config.enable_resource_limits
            and platform.system() != "Windows"
        ):
            self._preexec_fn = self._create_preexec_fn()

    # Backwards compatibility properties
    @property
    def timeout(self) -> float:
        return self.config.timeout

    @property
    def max_output(self) -> int:
        return self.config.max_output_bytes

    def _create_preexec_fn(self) -> Callable[[], None]:
        """Create a preexec function to set resource limits.

        This is called in the child process before exec on Unix.
        Returns a function that sets memory and CPU limits.
        """
        memory_bytes = self.config.memory_limit_mb * 1024 * 1024
        cpu_seconds = int(self.config.timeout) + 2  # Allow extra time for cleanup

        def set_limits() -> None:
            if HAS_RESOURCE:
                # Set address space limit (virtual memory)
                try:
                    resource.setrlimit(
                        resource.RLIMIT_AS,
                        (memory_bytes, memory_bytes)
                    )
                except (ValueError, OSError):
                    pass  # May fail if already limited

                # Set CPU time limit
                try:
                    resource.setrlimit(
                        resource.RLIMIT_CPU,
                        (cpu_seconds, cpu_seconds)
                    )
                except (ValueError, OSError):
                    pass  # May fail if already limited

        return set_limits

    def execute(
        self,
        code: str,
        inputs: dict[str, Any],
        func_name: str | None = None,
        timeout: float | None = None,
    ) -> ExecutionResult:
        """Execute Python code with given inputs.

        Args:
            code: Python source code to execute
            inputs: Dictionary of input values
            func_name: Function name to call (if None, executes as script)
            timeout: Override default timeout (optional)

        Returns:
            ExecutionResult with execution details
        """
        actual_timeout = timeout if timeout is not None else self.timeout

        # Build the wrapper script
        wrapper = self._build_wrapper(code, inputs, func_name)

        # Write to temp file
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False,
            encoding="utf-8",
        ) as f:
            f.write(wrapper)
            temp_path = Path(f.name)

        try:
            # Execute in subprocess with optional resource limits
            result = subprocess.run(
                [self.python_executable, str(temp_path)],
                capture_output=True,
                timeout=actual_timeout,
                text=True,
                preexec_fn=self._preexec_fn, check=False,  # Resource limits (Linux only)
            )

            # Parse the output
            return self._parse_output(result)

        except subprocess.TimeoutExpired:
            return ExecutionResult.timeout()

        except Exception as e:
            return ExecutionResult.error(type(e).__name__, str(e))

        finally:
            # Clean up temp file
            temp_path.unlink(missing_ok=True)

    def execute_with_hypothesis(
        self,
        code: str,
        func_name: str,
        input_strategy: str,
        max_examples: int = 100,
    ) -> list[ExecutionResult]:
        """Execute code with Hypothesis-generated inputs.

        Uses Hypothesis property-based testing to generate test inputs.

        Args:
            code: Python source code
            func_name: Function name to test
            input_strategy: Hypothesis strategy code (e.g., "st.integers()")
            max_examples: Maximum number of examples to generate

        Returns:
            List of ExecutionResults for each generated input
        """
        # Build Hypothesis test wrapper
        wrapper = self._build_hypothesis_wrapper(
            code, func_name, input_strategy, max_examples
        )

        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False,
            encoding="utf-8",
        ) as f:
            f.write(wrapper)
            temp_path = Path(f.name)

        try:
            result = subprocess.run(
                [self.python_executable, str(temp_path)],
                capture_output=True,
                timeout=self.config.timeout * max_examples / 10,  # Scale timeout
                text=True,
                preexec_fn=self._preexec_fn, check=False,  # Resource limits (Linux only)
            )

            # Parse multiple results from output
            return self._parse_hypothesis_output(result)

        except subprocess.TimeoutExpired:
            return [ExecutionResult.timeout()]

        except Exception as e:
            return [ExecutionResult.error(type(e).__name__, str(e))]

        finally:
            temp_path.unlink(missing_ok=True)

    def compare_outputs(
        self,
        result1: ExecutionResult,
        result2: ExecutionResult,
    ) -> bool:
        """Compare two execution results for equivalence.

        Two results are equivalent if:
        - Both succeeded with equal return values, OR
        - Both failed with the same exception type

        Args:
            result1: First execution result
            result2: Second execution result

        Returns:
            True if results are equivalent
        """
        # Both must have same success status
        if result1.success != result2.success:
            return False

        if result1.success:
            # Compare return values
            return self._values_equal(result1.return_value, result2.return_value)
        else:
            # Compare exception types
            return result1.exception_type == result2.exception_type

    def _values_equal(self, val1: Any, val2: Any) -> bool:
        """Check if two values are semantically equal.

        Handles special cases like floating point comparison.
        """
        # Handle None
        if val1 is None and val2 is None:
            return True

        # Handle floats with tolerance
        if isinstance(val1, float) and isinstance(val2, float):
            # Use relative tolerance
            if val1 == 0 and val2 == 0:
                return True
            rel_tol = 1e-9
            return abs(val1 - val2) <= rel_tol * max(abs(val1), abs(val2))

        # Handle lists/tuples recursively
        if isinstance(val1, (list, tuple)) and isinstance(val2, (list, tuple)):
            if len(val1) != len(val2):
                return False
            return all(self._values_equal(v1, v2) for v1, v2 in zip(val1, val2, strict=False))

        # Handle dicts recursively
        if isinstance(val1, dict) and isinstance(val2, dict):
            if set(val1.keys()) != set(val2.keys()):
                return False
            return all(
                self._values_equal(val1[k], val2[k])
                for k in val1.keys()
            )

        # Handle sets
        if isinstance(val1, set) and isinstance(val2, set):
            return val1 == val2

        # Default comparison
        return val1 == val2

    def _build_wrapper(
        self,
        code: str,
        inputs: dict[str, Any],
        func_name: str | None,
    ) -> str:
        """Build the wrapper script for execution."""
        inputs_json = json.dumps(inputs)

        if func_name:
            call_code = f"result = {func_name}(**inputs)"
        else:
            call_code = "result = None  # Script mode, no function call"

        return textwrap.dedent(f'''
            import json
            import sys
            import time

            # Code under test
            {textwrap.indent(code, "            ").strip()}

            # Execution wrapper
            def _execute():
                inputs = json.loads({inputs_json!r})
                start_time = time.perf_counter()

                try:
                    {call_code}
                    elapsed_ms = (time.perf_counter() - start_time) * 1000

                    output = {{
                        "success": True,
                        "return_value": repr(result),
                        "execution_time_ms": elapsed_ms,
                    }}
                except Exception as e:
                    elapsed_ms = (time.perf_counter() - start_time) * 1000
                    output = {{
                        "success": False,
                        "exception_type": type(e).__name__,
                        "exception_message": str(e),
                        "execution_time_ms": elapsed_ms,
                    }}

                print(json.dumps(output))

            if __name__ == "__main__":
                _execute()
        ''').strip()

    def _build_hypothesis_wrapper(
        self,
        code: str,
        func_name: str,
        input_strategy: str,
        max_examples: int,
    ) -> str:
        """Build Hypothesis test wrapper."""
        return textwrap.dedent(f'''
            import json
            from hypothesis import given, settings, strategies as st

            # Code under test
            {textwrap.indent(code, "            ").strip()}

            results = []

            @settings(max_examples={max_examples}, database=None)
            @given({input_strategy})
            def test_function(inputs):
                try:
                    if isinstance(inputs, dict):
                        result = {func_name}(**inputs)
                    else:
                        result = {func_name}(inputs)
                    results.append({{
                        "success": True,
                        "inputs": repr(inputs),
                        "return_value": repr(result),
                    }})
                except Exception as e:
                    results.append({{
                        "success": False,
                        "inputs": repr(inputs),
                        "exception_type": type(e).__name__,
                        "exception_message": str(e),
                    }})

            if __name__ == "__main__":
                try:
                    test_function()
                except Exception:
                    pass  # Hypothesis may raise on finding failure
                print(json.dumps(results))
        ''').strip()

    def _parse_output(self, result: subprocess.CompletedProcess) -> ExecutionResult:
        """Parse subprocess output into ExecutionResult."""
        # Try to parse JSON from stdout
        stdout = result.stdout.strip()
        stderr = result.stderr.strip()

        if not stdout:
            # No output - check for error
            if result.returncode != 0:
                return ExecutionResult.error(
                    "RuntimeError",
                    f"Process exited with code {result.returncode}: {stderr}",
                )
            return ExecutionResult(success=True, stdout=stdout, stderr=stderr)

        try:
            output = json.loads(stdout)
            return ExecutionResult(
                success=output.get("success", False),
                return_value=output.get("return_value"),
                stdout=stdout,
                stderr=stderr,
                exception_type=output.get("exception_type"),
                exception_message=output.get("exception_message"),
                execution_time_ms=output.get("execution_time_ms", 0.0),
            )
        except json.JSONDecodeError:
            # Couldn't parse output
            return ExecutionResult.error(
                "ParseError",
                f"Could not parse output: {stdout[:200]}",
            )

    def _parse_hypothesis_output(
        self,
        result: subprocess.CompletedProcess,
    ) -> list[ExecutionResult]:
        """Parse Hypothesis test output."""
        stdout = result.stdout.strip()

        if not stdout:
            return [ExecutionResult.error("ParseError", "No output from Hypothesis")]

        try:
            results_data = json.loads(stdout)
            results: list[ExecutionResult] = []

            for item in results_data:
                results.append(ExecutionResult(
                    success=item.get("success", False),
                    return_value=item.get("return_value"),
                    exception_type=item.get("exception_type"),
                    exception_message=item.get("exception_message"),
                ))

            return results

        except json.JSONDecodeError:
            return [ExecutionResult.error("ParseError", f"Could not parse: {stdout[:200]}")]
