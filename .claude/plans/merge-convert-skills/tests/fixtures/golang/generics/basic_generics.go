// Test fixtures for Go generics (Go 1.18+).
package generics

import "cmp"

// Generic function with any constraint
func Identity[T any](v T) T {
	return v
}

// Generic function with comparable constraint
func Contains[T comparable](slice []T, target T) bool {
	for _, v := range slice {
		if v == target {
			return true
		}
	}
	return false
}

// Generic function with cmp.Ordered constraint
func Max[T cmp.Ordered](a, b T) T {
	if a > b {
		return a
	}
	return b
}

func Min[T cmp.Ordered](a, b T) T {
	if a < b {
		return a
	}
	return b
}

// Generic function with multiple type parameters
func Map[T, U any](slice []T, fn func(T) U) []U {
	result := make([]U, len(slice))
	for i, v := range slice {
		result[i] = fn(v)
	}
	return result
}

func Filter[T any](slice []T, predicate func(T) bool) []T {
	var result []T
	for _, v := range slice {
		if predicate(v) {
			result = append(result, v)
		}
	}
	return result
}

func Reduce[T, U any](slice []T, initial U, fn func(U, T) U) U {
	result := initial
	for _, v := range slice {
		result = fn(result, v)
	}
	return result
}

// Generic struct
type Box[T any] struct {
	Value T
}

func NewBox[T any](v T) *Box[T] {
	return &Box[T]{Value: v}
}

func (b *Box[T]) Get() T {
	return b.Value
}

func (b *Box[T]) Set(v T) {
	b.Value = v
}

// Generic struct with constraint
type OrderedBox[T cmp.Ordered] struct {
	Value T
}

func (b *OrderedBox[T]) IsGreaterThan(other T) bool {
	return b.Value > other
}

// Generic struct with multiple type parameters
type Pair[K, V any] struct {
	Key   K
	Value V
}

func NewPair[K, V any](k K, v V) Pair[K, V] {
	return Pair[K, V]{Key: k, Value: v}
}

// Generic interface
type Container[T any] interface {
	Add(T)
	Get() T
	IsEmpty() bool
}

// Generic interface implementation
type Stack[T any] struct {
	items []T
}

func NewStack[T any]() *Stack[T] {
	return &Stack[T]{}
}

func (s *Stack[T]) Add(v T) {
	s.items = append(s.items, v)
}

func (s *Stack[T]) Get() T {
	if len(s.items) == 0 {
		var zero T
		return zero
	}
	v := s.items[len(s.items)-1]
	s.items = s.items[:len(s.items)-1]
	return v
}

func (s *Stack[T]) IsEmpty() bool {
	return len(s.items) == 0
}

// Generic with type constraint interface
type Number interface {
	~int | ~int32 | ~int64 | ~float32 | ~float64
}

func Sum[T Number](numbers []T) T {
	var sum T
	for _, n := range numbers {
		sum += n
	}
	return sum
}

// Generic with union constraint
type Stringish interface {
	~string | ~[]byte
}

func Length[T Stringish](v T) int {
	return len(v)
}

// Type set with methods
type Stringer interface {
	~string
	String() string
}

// Generic slice type
type Slice[T any] []T

func (s Slice[T]) First() (T, bool) {
	if len(s) == 0 {
		var zero T
		return zero, false
	}
	return s[0], true
}

func (s Slice[T]) Last() (T, bool) {
	if len(s) == 0 {
		var zero T
		return zero, false
	}
	return s[len(s)-1], true
}

// Generic map type
type MapType[K comparable, V any] map[K]V

func (m MapType[K, V]) Keys() []K {
	keys := make([]K, 0, len(m))
	for k := range m {
		keys = append(keys, k)
	}
	return keys
}

func (m MapType[K, V]) Values() []V {
	values := make([]V, 0, len(m))
	for _, v := range m {
		values = append(values, v)
	}
	return values
}

// Generic channel operations
func Collect[T any](ch <-chan T) []T {
	var result []T
	for v := range ch {
		result = append(result, v)
	}
	return result
}

func Send[T any](ch chan<- T, values ...T) {
	for _, v := range values {
		ch <- v
	}
}
