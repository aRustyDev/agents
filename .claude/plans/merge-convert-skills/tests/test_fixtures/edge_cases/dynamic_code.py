"""Dynamic code patterns that are challenging for static analysis."""

from typing import Any, Callable


def dynamic_attribute_access(obj: Any, attr_name: str) -> Any:
    """Access an attribute dynamically."""
    return getattr(obj, attr_name)


def dynamic_method_call(obj: Any, method_name: str, *args: Any) -> Any:
    """Call a method dynamically."""
    method = getattr(obj, method_name)
    return method(*args)


def create_function(body: str) -> Callable:
    """Create a function from source code string."""
    namespace: dict = {}
    exec(f"def dynamic_func(x): return {body}", namespace)
    return namespace["dynamic_func"]


def eval_expression(expr: str, context: dict[str, Any]) -> Any:
    """Evaluate an expression in a context."""
    return eval(expr, {"__builtins__": {}}, context)


class DynamicClass:
    """A class with dynamic attribute handling."""

    def __init__(self) -> None:
        """Initialize with empty storage."""
        self._data: dict[str, Any] = {}

    def __getattr__(self, name: str) -> Any:
        """Get dynamic attribute."""
        if name.startswith("_"):
            raise AttributeError(name)
        return self._data.get(name)

    def __setattr__(self, name: str, value: Any) -> None:
        """Set dynamic attribute."""
        if name.startswith("_"):
            object.__setattr__(self, name, value)
        else:
            self._data[name] = value


def monkey_patch(cls: type, method_name: str, new_method: Callable) -> None:
    """Monkey patch a class method."""
    setattr(cls, method_name, new_method)


def create_class(name: str, bases: tuple, attrs: dict) -> type:
    """Create a class dynamically."""
    return type(name, bases, attrs)
