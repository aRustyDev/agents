"""Exception handling examples for testing exception pattern extraction."""

from typing import Never


class CustomError(Exception):
    """A custom exception class."""

    def __init__(self, message: str, code: int) -> None:
        super().__init__(message)
        self.code = code


class ValidationError(CustomError):
    """Validation-specific error."""

    def __init__(self, field: str, message: str) -> None:
        super().__init__(f"{field}: {message}", code=400)
        self.field = field


def simple_try_except() -> int:
    """Simple try/except block."""
    try:
        return int("not a number")
    except ValueError:
        return 0


def try_except_else() -> int:
    """Try with else clause."""
    try:
        value = int("42")
    except ValueError:
        return 0
    else:
        return value


def try_except_finally() -> int:
    """Try with finally clause."""
    resource = None
    try:
        resource = acquire_resource()
        return resource.value
    except ResourceError:
        return -1
    finally:
        if resource:
            resource.release()


def multiple_except_clauses(value: str) -> int:
    """Multiple except clauses."""
    try:
        return int(value)
    except ValueError:
        return 0
    except TypeError:
        return -1
    except Exception as e:
        print(f"Unexpected error: {e}")
        return -2


def except_with_binding() -> str:
    """Except clause with exception binding."""
    try:
        risky_operation()
    except CustomError as e:
        return f"Error code {e.code}: {e}"
    return "success"


def except_tuple() -> None:
    """Except clause with tuple of exceptions."""
    try:
        operation()
    except (ValueError, TypeError, KeyError):
        print("One of the expected errors")


def bare_except() -> None:
    """Bare except clause (catches everything)."""
    try:
        something()
    except:  # noqa: E722
        print("Something went wrong")


def nested_try_except() -> int:
    """Nested try/except blocks."""
    try:
        try:
            return risky()
        except InnerError:
            return -1
    except OuterError:
        return -2


def exception_chaining() -> None:
    """Exception chaining with 'from'."""
    try:
        parse_config()
    except ValueError as e:
        raise ConfigError("Invalid configuration") from e


def exception_suppression() -> None:
    """Exception suppression with 'from None'."""
    try:
        parse_data()
    except ValueError:
        raise DataError("Failed to parse data") from None


def reraise() -> None:
    """Reraise current exception."""
    try:
        operation()
    except Exception:
        log_error()
        raise


def raise_new_exception() -> Never:
    """Raise a new exception."""
    raise CustomError("Something went wrong", code=500)


def conditional_raise(value: int) -> int:
    """Conditional exception raising."""
    if value < 0:
        raise ValueError("Value must be non-negative")
    if value > 100:
        raise ValueError("Value must not exceed 100")
    return value


def assert_statement(value: int) -> int:
    """Using assert for validation."""
    assert value >= 0, "Value must be non-negative"
    assert value <= 100, "Value must not exceed 100"
    return value


def context_manager_exception() -> None:
    """Exception handling with context managers."""
    try:
        with open("file.txt") as f:
            content = f.read()
    except FileNotFoundError:
        print("File not found")
    except OSError as e:
        print(f"IO error: {e}")


def generator_with_exception() -> None:
    """Generator with exception handling."""
    def gen():
        try:
            yield 1
            yield 2
            raise StopIteration
        except StopIteration:
            yield 3

    for item in gen():
        print(item)


async def async_exception_handling() -> str:
    """Async function with exception handling."""
    try:
        result = await async_operation()
        return result
    except AsyncError as e:
        return f"Async error: {e}"
    finally:
        await cleanup()


# Python 3.11+ exception groups
def exception_group_example() -> None:
    """Exception groups (Python 3.11+)."""
    errors = []
    for item in items:
        try:
            process(item)
        except Exception as e:
            errors.append(e)

    if errors:
        raise ExceptionGroup("Multiple errors", errors)


def handle_exception_group() -> None:
    """Handle exception group with except*."""
    try:
        operation_that_may_fail()
    except* ValueError as eg:
        print(f"Value errors: {eg.exceptions}")
    except* TypeError as eg:
        print(f"Type errors: {eg.exceptions}")


class ExceptionInMethod:
    """Class with exception handling in methods."""

    def __init__(self, value: int) -> None:
        if value < 0:
            raise ValueError("Value must be non-negative")
        self.value = value

    def safe_divide(self, divisor: int) -> float:
        """Safe division with exception handling."""
        try:
            return self.value / divisor
        except ZeroDivisionError:
            return float("inf")

    def __enter__(self) -> "ExceptionInMethod":
        """Context manager entry."""
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object,
    ) -> bool:
        """Context manager exit with exception handling."""
        if exc_type is ValueError:
            print(f"Caught ValueError: {exc_val}")
            return True  # Suppress the exception
        return False  # Re-raise other exceptions
