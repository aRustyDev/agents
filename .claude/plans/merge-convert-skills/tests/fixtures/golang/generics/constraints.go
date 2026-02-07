// Test fixtures for Go type constraints.
package generics

import (
	"cmp"
	"fmt"
)

// Custom constraint with type set
type Integer interface {
	~int | ~int8 | ~int16 | ~int32 | ~int64
}

type Unsigned interface {
	~uint | ~uint8 | ~uint16 | ~uint32 | ~uint64
}

type Float interface {
	~float32 | ~float64
}

// Combined constraint
type Numeric interface {
	Integer | Unsigned | Float
}

// Constraint with methods
type Equatable[T any] interface {
	Equal(T) bool
}

// Constraint with both type set and methods
type ComparableValue interface {
	comparable
	String() string
}

// Using constraints
func Abs[T Numeric](v T) T {
	if v < 0 {
		return -v
	}
	return v
}

func Equal[T Equatable[T]](a, b T) bool {
	return a.Equal(b)
}

// Constraint with underlying type approximation
type MyInt int

func Double[T ~int](v T) T {
	return v * 2
}

// Can use with MyInt due to ~int
func Example() {
	var x MyInt = 5
	result := Double(x) // Works because MyInt's underlying type is int
	fmt.Println(result)
}

// Constraint from standard library
func Sort[T cmp.Ordered](slice []T) {
	// Simple bubble sort for demonstration
	n := len(slice)
	for i := 0; i < n-1; i++ {
		for j := 0; j < n-i-1; j++ {
			if slice[j] > slice[j+1] {
				slice[j], slice[j+1] = slice[j+1], slice[j]
			}
		}
	}
}

// Interface constraint with multiple type parameters
type Convertible[From, To any] interface {
	Convert(From) To
}

// Struct implementing constraint
type StringToInt struct{}

func (s StringToInt) Convert(str string) int {
	// Simplified conversion
	return len(str)
}

// Using the constraint
func ConvertAll[From, To any, C Convertible[From, To]](
	converter C,
	values []From,
) []To {
	result := make([]To, len(values))
	for i, v := range values {
		result[i] = converter.Convert(v)
	}
	return result
}

// Constraint embedding
type Ordered interface {
	~int | ~int8 | ~int16 | ~int32 | ~int64 |
		~uint | ~uint8 | ~uint16 | ~uint32 | ~uint64 |
		~float32 | ~float64 |
		~string
}

// Constraint with any and comparable
type MapKey interface {
	comparable
}

type MapValue interface {
	any
}

// Generic map with constraints
type GenericMap[K MapKey, V MapValue] struct {
	data map[K]V
}

func NewGenericMap[K MapKey, V MapValue]() *GenericMap[K, V] {
	return &GenericMap[K, V]{
		data: make(map[K]V),
	}
}

func (m *GenericMap[K, V]) Set(key K, value V) {
	m.data[key] = value
}

func (m *GenericMap[K, V]) Get(key K) (V, bool) {
	v, ok := m.data[key]
	return v, ok
}

// Pointer constraint pattern
type Pointer[T any] interface {
	*T
}

func SetValue[T any, PT Pointer[T]](ptr PT, value T) {
	*ptr = value
}

// Clone constraint (for types with Clone method)
type Cloneable[T any] interface {
	Clone() T
}

func CloneSlice[T Cloneable[T]](slice []T) []T {
	result := make([]T, len(slice))
	for i, v := range slice {
		result[i] = v.Clone()
	}
	return result
}

// Example cloneable type
type Person struct {
	Name string
	Age  int
}

func (p Person) Clone() Person {
	return Person{Name: p.Name, Age: p.Age}
}
