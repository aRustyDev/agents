// Test fixtures for Go function definitions.
package basics

import (
	"fmt"
	"strings"
)

// Simple function
func Add(a, b int) int {
	return a + b
}

// Function with multiple parameters of same type
func Sum(a, b, c int) int {
	return a + b + c
}

// Function with multiple returns
func Divide(a, b int) (int, int) {
	return a / b, a % b
}

// Function with named returns
func DivideNamed(a, b int) (quotient, remainder int) {
	quotient = a / b
	remainder = a % b
	return
}

// Variadic function
func SumAll(numbers ...int) int {
	total := 0
	for _, n := range numbers {
		total += n
	}
	return total
}

// Function returning function
func Multiplier(factor int) func(int) int {
	return func(x int) int {
		return x * factor
	}
}

// Function accepting function
func Apply(numbers []int, fn func(int) int) []int {
	result := make([]int, len(numbers))
	for i, n := range numbers {
		result[i] = fn(n)
	}
	return result
}

// Higher-order function
func Compose(f, g func(int) int) func(int) int {
	return func(x int) int {
		return f(g(x))
	}
}

// Anonymous function usage
func ProcessItems(items []string) []string {
	return Transform(items, func(s string) string {
		return strings.ToUpper(s)
	})
}

func Transform(items []string, fn func(string) string) []string {
	result := make([]string, len(items))
	for i, item := range items {
		result[i] = fn(item)
	}
	return result
}

// Recursive function
func Factorial(n int) int {
	if n <= 1 {
		return 1
	}
	return n * Factorial(n-1)
}

// Recursive function with accumulator
func FactorialTail(n, acc int) int {
	if n <= 1 {
		return acc
	}
	return FactorialTail(n-1, n*acc)
}

// Function with defer
func PrintWithBrackets(s string) {
	fmt.Print("[")
	defer fmt.Print("]")
	fmt.Print(s)
}

// Init function (special)
func init() {
	// Package initialization
}
