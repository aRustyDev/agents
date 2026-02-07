/**
 * Test fixtures for TypeScript function overloads.
 */

// Simple function overloads
function add(a: number, b: number): number
function add(a: string, b: string): string
function add(a: number | string, b: number | string): number | string {
  if (typeof a === 'number' && typeof b === 'number') {
    return a + b
  }
  return String(a) + String(b)
}

// Overload with different parameter counts
function createElement(tag: 'div'): HTMLDivElement
function createElement(tag: 'span'): HTMLSpanElement
function createElement(tag: 'a'): HTMLAnchorElement
function createElement(tag: string): HTMLElement
function createElement(tag: string): HTMLElement {
  return document.createElement(tag)
}

// Overload with optional parameters
function format(value: number): string
function format(value: number, precision: number): string
function format(value: number, precision?: number): string {
  if (precision !== undefined) {
    return value.toFixed(precision)
  }
  return String(value)
}

// Overload with rest parameters
function concat(...strings: string[]): string
function concat(...numbers: number[]): number
function concat(...items: (string | number)[]): string | number {
  if (typeof items[0] === 'string') {
    return (items as string[]).join('')
  }
  return (items as number[]).reduce((a, b) => a + b, 0)
}

// Generic function overloads
function first<T>(array: T[]): T
function first<T>(array: T[], count: number): T[]
function first<T>(array: T[], count?: number): T | T[] {
  if (count !== undefined) {
    return array.slice(0, count)
  }
  return array[0]
}

// Overload returning different types based on input
function parse(input: string, asNumber: true): number
function parse(input: string, asNumber: false): string
function parse(input: string, asNumber: boolean): number | string {
  if (asNumber) {
    return parseFloat(input)
  }
  return input
}

// Method overloads in class
class Calculator {
  compute(value: number): number
  compute(value: string): string
  compute(a: number, b: number): number
  compute(a: number | string, b?: number): number | string {
    if (typeof a === 'string') {
      return a.toUpperCase()
    }
    if (b !== undefined) {
      return a + b
    }
    return a * 2
  }
}

// Interface with overloaded method
interface Formatter {
  format(value: number): string
  format(value: Date): string
  format(value: boolean): string
}

// Call signature overloads in interface
interface Parser {
  (input: string): object
  (input: string, reviver: (key: string, value: unknown) => unknown): object
}

// Construct signature overloads
interface DateConstructor {
  new (): Date
  new (value: number): Date
  new (value: string): Date
  new (
    year: number,
    month: number,
    date?: number,
    hours?: number,
    minutes?: number,
    seconds?: number,
    ms?: number
  ): Date
}

// Exported overloaded function
export function convert(value: string): number
export function convert(value: number): string
export function convert(value: string | number): string | number {
  if (typeof value === 'string') {
    return parseFloat(value)
  }
  return String(value)
}
