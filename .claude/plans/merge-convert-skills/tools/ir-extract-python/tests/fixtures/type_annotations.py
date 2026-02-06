"""Type annotation examples for testing type extraction."""

from typing import (
    Any,
    Callable,
    ClassVar,
    Final,
    Generic,
    Literal,
    Optional,
    Protocol,
    TypeAlias,
    TypedDict,
    TypeVar,
    Union,
    overload,
)
from collections.abc import Iterator, Sequence


# Type variables
T = TypeVar("T")
K = TypeVar("K", bound=str)
V = TypeVar("V", int, float)


# Type aliases
UserId: TypeAlias = int
UserName: TypeAlias = str
UserMap: TypeAlias = dict[UserId, UserName]
Callback: TypeAlias = Callable[[int, str], bool]


def simple_types(a: int, b: str, c: float) -> bool:
    """Function with simple type annotations."""
    return len(b) > a * c


def optional_types(value: Optional[str]) -> str:
    """Function with Optional type."""
    return value or "default"


def union_types_old(value: Union[int, str]) -> str:
    """Function with Union type (old syntax)."""
    return str(value)


def union_types_new(value: int | str | None) -> str:
    """Function with Union type (new syntax, Python 3.10+)."""
    if value is None:
        return "none"
    return str(value)


def generic_types(items: list[int], mapping: dict[str, float]) -> set[str]:
    """Function with generic collection types."""
    return {str(k) for k in mapping.keys()}


def nested_generics(data: dict[str, list[tuple[int, str]]]) -> list[str]:
    """Function with nested generic types."""
    return [name for pairs in data.values() for _, name in pairs]


def callable_type(func: Callable[[int, str], bool], value: int) -> bool:
    """Function with Callable type."""
    return func(value, str(value))


def callable_complex(
    handler: Callable[[str, ...], Any],
    parser: Callable[..., dict[str, Any]],
) -> None:
    """Function with complex Callable types."""
    pass


def literal_type(mode: Literal["read", "write", "append"]) -> int:
    """Function with Literal type."""
    return {"read": 0, "write": 1, "append": 2}[mode]


def typevar_function(items: Sequence[T]) -> T:
    """Generic function with TypeVar."""
    return items[0]


def bounded_typevar(value: K) -> K:
    """Function with bounded TypeVar."""
    return value.upper()  # type: ignore


def constrained_typevar(value: V) -> V:
    """Function with constrained TypeVar."""
    return value * 2


@overload
def overloaded_function(value: int) -> int: ...
@overload
def overloaded_function(value: str) -> str: ...
def overloaded_function(value: int | str) -> int | str:
    """Overloaded function with multiple signatures."""
    if isinstance(value, int):
        return value * 2
    return value * 2


class TypedUser(TypedDict):
    """TypedDict for user data."""

    id: int
    name: str
    email: str
    active: bool


class PartialUser(TypedDict, total=False):
    """TypedDict with optional keys."""

    id: int
    name: str
    email: str


def typed_dict_function(user: TypedUser) -> str:
    """Function accepting TypedDict."""
    return user["name"]


class GenericClass(Generic[T]):
    """Generic class with type parameter."""

    def __init__(self, value: T) -> None:
        self.value = value

    def get(self) -> T:
        """Get the stored value."""
        return self.value

    def transform(self, func: Callable[[T], T]) -> T:
        """Transform the value."""
        return func(self.value)


class MultipleTypeParams(Generic[K, V]):
    """Generic class with multiple type parameters."""

    def __init__(self) -> None:
        self._data: dict[K, V] = {}

    def set(self, key: K, value: V) -> None:
        """Set a key-value pair."""
        self._data[key] = value

    def get(self, key: K) -> V | None:
        """Get a value by key."""
        return self._data.get(key)


class WithClassVars:
    """Class with ClassVar and Final annotations."""

    VERSION: ClassVar[str] = "1.0.0"
    MAX_SIZE: Final[int] = 100

    def __init__(self, size: int) -> None:
        self.size: int = min(size, self.MAX_SIZE)


class HasProtocol(Protocol):
    """Protocol with method requirements."""

    def process(self, data: bytes) -> str:
        """Process data and return result."""
        ...

    @property
    def name(self) -> str:
        """Get the name."""
        ...


def accepts_protocol(obj: HasProtocol) -> str:
    """Function accepting a Protocol type."""
    return obj.process(b"data")


def iterator_type() -> Iterator[int]:
    """Function returning an Iterator."""
    for i in range(10):
        yield i


def return_self_type(self: T) -> T:
    """Function with self-referential return type."""
    return self


# Forward reference
def forward_ref(data: "ForwardClass") -> "ForwardClass":
    """Function with forward reference."""
    return data


class ForwardClass:
    """Class referenced before definition."""

    def method(self) -> "ForwardClass":
        """Method with forward reference."""
        return self
