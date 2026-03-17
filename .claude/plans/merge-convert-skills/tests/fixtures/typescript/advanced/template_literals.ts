// Template literal types

// Basic template literal type
type Greeting = `Hello, ${string}!`
const greeting: Greeting = 'Hello, World!'

// Combining literal types
type Vertical = 'top' | 'middle' | 'bottom'
type Horizontal = 'left' | 'center' | 'right'
type Position = `${Vertical}-${Horizontal}`
// Result: "top-left" | "top-center" | "top-right" | "middle-left" | ...

// CSS-like utilities
type CSSUnit = 'px' | 'em' | 'rem' | '%'
type CSSValue = `${number}${CSSUnit}`

const width: CSSValue = '100px'
const fontSize: CSSValue = '1.5rem'

// Event handler patterns
type EventName = 'click' | 'focus' | 'blur'
type EventHandler = `on${Capitalize<EventName>}`
// Result: "onClick" | "onFocus" | "onBlur"

// Intrinsic string manipulation types
type UppercaseGreeting = Uppercase<'hello'> // "HELLO"
type LowercaseGreeting = Lowercase<'HELLO'> // "hello"
type CapitalizedWord = Capitalize<'hello'> // "Hello"
type UncapitalizedWord = Uncapitalize<'Hello'> // "hello"

// Getter/setter pattern
type PropName = 'name' | 'age' | 'email'
type Getter<T extends string> = `get${Capitalize<T>}`
type Setter<T extends string> = `set${Capitalize<T>}`

type NameGetter = Getter<'name'> // "getName"
type NameSetter = Setter<'name'> // "setName"

// API endpoint patterns
type HttpMethod = 'get' | 'post' | 'put' | 'delete'
type Resource = 'user' | 'post' | 'comment'
type Endpoint = `/${Resource}` | `/${Resource}/:id`

// Nested template literals
type Locale = 'en' | 'es' | 'fr'
type Currency = 'USD' | 'EUR' | 'GBP'
type LocalizedPrice = `${Locale}_${Currency}`

// Function using template literals
function makeGetter<T extends string>(prop: T): Getter<T> {
  return `get${prop.charAt(0).toUpperCase()}${prop.slice(1)}` as Getter<T>
}

// Extract from template literal
type ExtractParam<T> = T extends `${string}:${infer Param}` ? Param : never
type RouteParam = ExtractParam<'/users/:id'> // "id"

// Multiple params extraction
type ExtractParams<T> = T extends `${string}:${infer Param}/${infer Rest}`
  ? Param | ExtractParams<`/${Rest}`>
  : T extends `${string}:${infer Param}`
    ? Param
    : never

type AllParams = ExtractParams<'/users/:userId/posts/:postId'>
// Result: "userId" | "postId"

// Color hex pattern
type HexDigit =
  | '0'
  | '1'
  | '2'
  | '3'
  | '4'
  | '5'
  | '6'
  | '7'
  | '8'
  | '9'
  | 'a'
  | 'b'
  | 'c'
  | 'd'
  | 'e'
  | 'f'
type HexColor = `#${string}`

function isValidHex(color: string): color is HexColor {
  return /^#[0-9a-f]{6}$/i.test(color)
}

export {
  type Greeting,
  type Position,
  type CSSValue,
  type EventHandler,
  type Getter,
  type Setter,
  type Endpoint,
  type LocalizedPrice,
  makeGetter,
  type ExtractParam,
  type ExtractParams,
  type HexColor,
  isValidHex,
  greeting,
  width,
  fontSize,
}
