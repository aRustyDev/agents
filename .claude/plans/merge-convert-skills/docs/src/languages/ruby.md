# Ruby

> Dynamic, object-oriented language emphasizing programmer happiness and elegant syntax.

## Overview

Ruby is a dynamic, object-oriented programming language created by Yukihiro "Matz" Matsumoto in Japan, first released in 1995. It was designed with programmer productivity and enjoyment in mind, following the principle of least surprise (POLS).

Ruby emphasizes expressiveness and elegance, treating everything as an object including primitives. Its powerful metaprogramming capabilities enable domain-specific languages (DSLs) and the convention-over-configuration philosophy that made Ruby on Rails revolutionary.

The language excels in web development (Rails), scripting, automation, and rapid prototyping. Its focus on developer happiness and "beautiful code" has influenced many subsequent languages.

## Family Classification

| Dimension | Classification | Notes |
|-----------|----------------|-------|
| Primary Family | Dynamic | Pure OOP, duck typing |
| Secondary Family | — | Multi-paradigm (OOP, functional) |
| Subtype | scripting | Rapid development focus |

See: [Dynamic Family](../language-families/dynamic.md)

## Version History

| Version | Release | Key Changes for Conversion |
|---------|---------|---------------------------|
| 1.9 | 2007-12 | YARV VM, encoding support |
| 2.0 | 2013-02 | Keyword arguments, refinements |
| 2.6 | 2018-12 | JIT compiler (MJIT), endless range |
| 3.0 | 2020-12 | Ractor (actor concurrency), RBS types, pattern matching |
| 3.1 | 2021-12 | YJIT (faster JIT), debug gem |
| 3.2 | 2022-12 | WASI support, anonymous block forwarding |
| 3.3 | 2023-12 | Prism parser, RJIT |

## Feature Profile

### Type System

- **Strength:** dynamic (duck typing)
- **Inference:** none (optional RBS type signatures)
- **Generics:** none (duck typing)
- **Nullability:** nullable (nil as object)

### Memory Model

- **Management:** gc (mark-and-sweep + generational)
- **Mutability:** default-mutable (freeze for immutability)
- **Allocation:** heap (objects)

### Control Flow

- **Structured:** if-else, unless, case-when, while, until, begin-rescue
- **Effects:** exceptions (raise/rescue/ensure)
- **Async:** Fiber, Thread, Ractor (Ruby 3+)

### Data Types

- **Primitives:** Integer, Float, String, Symbol, true/false, nil
- **Composites:** Array, Hash, Struct, Class
- **Collections:** Array, Hash, Set, Range
- **Abstraction:** classes, modules, mixins

### Metaprogramming

- **Macros:** method-level (define_method, method_missing)
- **Reflection:** full (ObjectSpace, Module methods)
- **Code generation:** eval, class_eval, instance_eval

## Ecosystem

| Tool | Name | Notes |
|------|------|-------|
| Package Manager | RubyGems, Bundler | Bundler for dependencies |
| Build System | Rake | Make-like |
| LSP | Solargraph, ruby-lsp | ruby-lsp (Shopify) growing |
| Formatter | RuboCop | Style enforcement |
| Linter | RuboCop | Comprehensive |
| REPL | irb, pry | pry has debugging |
| Test Framework | RSpec, Minitest | RSpec is expressive |

## Syntax Patterns

```ruby
# Method definition
def greet(name, times: 1)
  "Hello, #{name}! " * times
end

# Block syntax
numbers.each { |n| puts n }
numbers.each do |n|
  puts n
end

# Lambda/Proc
greet = ->(name) { "Hello, #{name}!" }
greet = lambda { |name| "Hello, #{name}!" }
greet.call("World")

# Class definition
class User
  attr_reader :id, :name
  attr_accessor :email

  def initialize(id, name, email = nil)
    @id = id
    @name = name
    @email = email
  end

  def to_s
    "User(#{name})"
  end
end

# Struct (data class)
User = Struct.new(:id, :name, :email, keyword_init: true) do
  def to_s
    "User(#{name})"
  end
end

# Module (mixin)
module Displayable
  def display
    puts to_s
  end
end

class User
  include Displayable
end

# Pattern matching (Ruby 3+)
case shape
in { type: :circle, radius: r }
  Math::PI * r ** 2
in { type: :rectangle, width: w, height: h }
  w * h
end

# Hash pattern matching
case user
in { name:, email: String => email }
  puts "#{name}: #{email}"
in { name: }
  puts "#{name}: no email"
end

# Error handling
begin
  result = risky_operation
rescue NetworkError => e
  logger.error("Network failed: #{e.message}")
rescue => e
  logger.error("Unexpected: #{e.message}")
  raise
ensure
  cleanup
end

# Enumerable methods (functional style)
numbers = [1, 2, 3, 4, 5]
result = numbers
  .select { |n| n.even? }
  .map { |n| n * 2 }
  .sum

# Safe navigation operator
email = user&.profile&.email || "no-email@example.com"

# Symbols
status = :active
config = { host: "localhost", port: 8080 }

# Heredoc
message = <<~SQL
  SELECT * FROM users
  WHERE active = true
SQL

# DSL example (RSpec-like)
describe User do
  it "has a name" do
    user = User.new(name: "Alice")
    expect(user.name).to eq("Alice")
  end
end

# Metaprogramming: define_method
class User
  [:name, :email].each do |attr|
    define_method("#{attr}_valid?") do
      !send(attr).nil? && !send(attr).empty?
    end
  end
end

# Method missing
class DynamicFinder
  def method_missing(method, *args)
    if method.to_s.start_with?("find_by_")
      field = method.to_s.sub("find_by_", "")
      find_where(field => args.first)
    else
      super
    end
  end
end

# Ractor (Ruby 3 parallelism)
ractor = Ractor.new do
  result = expensive_computation
  Ractor.yield(result)
end
value = ractor.take

# Refinements (scoped monkey patching)
module StringExtensions
  refine String do
    def shout
      upcase + "!"
    end
  end
end

using StringExtensions
"hello".shout  # => "HELLO!"
```

## Semantic Gaps

| Gap | Severity | Workaround |
|-----|----------|------------|
| No static types | moderate | Use RBS, Sorbet for type checking |
| GIL limits parallelism | moderate | Use Ractor (Ruby 3+), multiprocessing |
| Slow startup | moderate | Use bootsnap, YJIT |
| Metaprogramming can obscure | minor | Follow conventions, document |
| Memory usage | moderate | Profile with memory_profiler |

## Convert-* Coverage

| Direction | Count | Skills |
|-----------|-------|--------|
| As Source | 0 | — |
| As Target | 0 | — |

**Note:** Not in current convert-* skills. Important for Rails ecosystem conversions.

## Idiomatic Patterns

### Blocks → Closures/Lambdas

```ruby
# Ruby: block
items.each { |item| process(item) }

# IR equivalent: closure/lambda
// items.for_each(|item| process(item))
```

### Mixins → Traits

```ruby
# Ruby: module mixin
module Comparable
  def <=>(other); end
end

# IR equivalent: trait
// trait Comparable { fn cmp(&self, other: &Self) -> Ordering }
```

### Method Missing → Dynamic Dispatch

```ruby
# Ruby: method_missing
def method_missing(name, *args)
  delegate.send(name, *args)
end

# IR equivalent: catch-all handler or Proxy
// impl Proxy { fn call(&self, method: &str, args: &[Value]) }
```

### Symbol → Interned String

```ruby
# Ruby: symbol
:active
method(:greet)

# IR equivalent: interned string or enum
// Symbol::Active OR "active".intern()
```

## Related Languages

- **Influenced by:** Perl, Smalltalk, Eiffel, Ada, Lisp
- **Influenced:** Python (some), Elixir (some), Crystal, Swift (some)
- **Compiles to:** YARV bytecode, native (TruffleRuby, mruby)
- **FFI compatible:** C (native extensions)

## Sources

- [Ruby Documentation](https://www.ruby-lang.org/en/documentation/)
- [Ruby Reference](https://ruby-doc.org/)
- [RubyGems](https://rubygems.org/)
- [Ruby Style Guide](https://rubystyle.guide/)

## See Also

- [Dynamic Family](../language-families/dynamic.md)
- [Python](python.md) - Dynamic comparison
- [Elixir](elixir.md) - Ruby-inspired BEAM
- [Crystal](crystal.md) - Compiled Ruby-like
