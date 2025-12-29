---
name: lang-elixir-library-dev
description: Elixir-specific library development patterns covering Hex package creation, OTP application design, Mix configuration, ExDoc documentation, typespecs, Dialyzer integration, and publishing best practices. Use when creating Elixir libraries, designing public APIs with OTP principles, managing dependencies, or publishing to Hex.pm. Extends meta-library-dev with Elixir ecosystem tooling.
---

# Elixir Library Development

Elixir-specific patterns for library development. This skill extends `meta-library-dev` with Elixir tooling, OTP design principles, and Hex ecosystem practices.

## This Skill Extends

- `meta-library-dev` - Foundational library patterns (API design, versioning, testing strategies)
- `lang-elixir-dev` - Core Elixir syntax and OTP fundamentals

For general concepts like semantic versioning, module organization principles, and testing pyramids, see the meta-skill first.

## This Skill Adds

- **Elixir tooling**: mix.exs configuration, Mix tasks, Hex publishing
- **OTP design**: Application structure, supervision trees, GenServer APIs
- **Documentation**: ExDoc, @moduledoc, @doc, doctests
- **Type safety**: Typespecs, Dialyzer, contracts
- **Hex ecosystem**: Dependencies, configuration, package metadata

## This Skill Does NOT Cover

- General library patterns - see `meta-library-dev`
- Basic Elixir syntax - see `lang-elixir-dev`
- Phoenix web development - see `lang-elixir-phoenix-dev`
- Advanced OTP patterns - see `lang-elixir-otp-dev`
- Ecto database patterns - see `lang-elixir-ecto-dev`

---

## Quick Reference

| Task | Command/Pattern |
|------|-----------------|
| New library | `mix new my_lib` |
| New supervised lib | `mix new my_lib --sup` |
| Build | `mix compile` |
| Test | `mix test` |
| Generate docs | `mix docs` |
| Type check | `mix dialyzer` |
| Format code | `mix format` |
| Publish (dry run) | `mix hex.build` |
| Publish | `mix hex.publish` |
| Audit deps | `mix hex.audit` |

---

## Mix.exs Structure

### Required Fields for Hex Publishing

```elixir
defmodule MyLib.MixProject do
  use Mix.Project

  @version "0.1.0"
  @source_url "https://github.com/username/my_lib"

  def project do
    [
      app: :my_lib,
      version: @version,
      elixir: "~> 1.14",
      start_permanent: Mix.env() == :prod,
      deps: deps(),

      # Required for Hex
      description: "A brief description of what this library does",
      package: package(),

      # Documentation
      name: "MyLib",
      source_url: @source_url,
      homepage_url: @source_url,
      docs: docs()
    ]
  end

  # Run "mix help compile.app" to learn about applications
  def application do
    [
      extra_applications: [:logger],
      mod: {MyLib.Application, []}
    ]
  end

  defp deps do
    [
      # Documentation
      {:ex_doc, "~> 0.31", only: :dev, runtime: false},

      # Type checking
      {:dialyxir, "~> 1.4", only: [:dev, :test], runtime: false},

      # Code quality
      {:credo, "~> 1.7", only: [:dev, :test], runtime: false}
    ]
  end

  defp package do
    [
      name: "my_lib",
      files: ~w(lib .formatter.exs mix.exs README* LICENSE* CHANGELOG*),
      licenses: ["Apache-2.0"],
      links: %{
        "GitHub" => @source_url,
        "Changelog" => "#{@source_url}/blob/main/CHANGELOG.md"
      },
      maintainers: ["Your Name"]
    ]
  end

  defp docs do
    [
      main: "MyLib",
      source_ref: "v#{@version}",
      source_url: @source_url,
      extras: ["README.md", "CHANGELOG.md", "LICENSE"],
      groups_for_modules: [
        "Core": [MyLib, MyLib.Config],
        "Utilities": [MyLib.Utils]
      ]
    ]
  end
end
```

### Package Configuration Best Practices

```elixir
defp package do
  [
    # Package name (defaults to :app name)
    name: "my_lib",

    # Files to include in package
    files: ~w(
      lib
      .formatter.exs
      mix.exs
      README.md
      LICENSE
      CHANGELOG.md
    ),

    # License (required) - use SPDX identifier
    licenses: ["Apache-2.0"],
    # Or multiple: licenses: ["MIT", "Apache-2.0"]

    # Links (at least one required)
    links: %{
      "GitHub" => @source_url,
      "Docs" => "https://hexdocs.pm/my_lib",
      "Changelog" => "#{@source_url}/blob/main/CHANGELOG.md"
    },

    # Maintainers (optional but recommended)
    maintainers: ["Your Name", "Contributor Name"]
  ]
end
```

---

## OTP Application Structure

### Library without Supervision

For pure functional libraries without processes:

```elixir
# mix.exs
def application do
  [
    extra_applications: [:logger]
    # No mod: {MyLib.Application, []}
  ]
end
```

### Library with Supervision

For libraries managing processes:

```elixir
# lib/my_lib/application.ex
defmodule MyLib.Application do
  @moduledoc false
  use Application

  @impl true
  def start(_type, _args) do
    children = [
      # Registry for process lookup
      {Registry, keys: :unique, name: MyLib.Registry},

      # DynamicSupervisor for dynamic workers
      {DynamicSupervisor, name: MyLib.DynamicSupervisor, strategy: :one_for_one},

      # Your library's main supervisor
      MyLib.Supervisor
    ]

    opts = [strategy: :one_for_one, name: MyLib.ApplicationSupervisor]
    Supervisor.start_link(children, opts)
  end
end

# lib/my_lib/supervisor.ex
defmodule MyLib.Supervisor do
  use Supervisor

  def start_link(init_arg) do
    Supervisor.start_link(__MODULE__, init_arg, name: __MODULE__)
  end

  @impl true
  def init(_init_arg) do
    children = [
      {MyLib.Worker, []},
      {MyLib.Cache, []}
    ]

    Supervisor.init(children, strategy: :one_for_one)
  end
end
```

### Optional Application Start

Allow users to start your application manually:

```elixir
defmodule MyLib do
  @moduledoc """
  MyLib provides functionality for...

  ## Starting the Application

  If you're using MyLib with supervision, add it to your application's
  supervision tree:

      children = [
        MyLib
      ]

  Or start it manually:

      {:ok, _} = MyLib.start_link([])
  """

  def start_link(opts \\ []) do
    MyLib.Supervisor.start_link(opts)
  end

  def child_spec(opts) do
    %{
      id: __MODULE__,
      start: {__MODULE__, :start_link, [opts]},
      type: :supervisor
    }
  end
end
```

---

## Public API Design (Elixir-Specific)

### Client API Pattern

Separate client and server implementations:

```elixir
defmodule MyLib.Cache do
  @moduledoc """
  A simple caching server.
  """
  use GenServer

  # Client API

  @doc """
  Starts the cache with the given options.

  ## Options

    * `:name` - The name to register the cache (default: `__MODULE__`)
    * `:ttl` - Time to live in milliseconds (default: 60_000)
  """
  def start_link(opts \\ []) do
    name = Keyword.get(opts, :name, __MODULE__)
    GenServer.start_link(__MODULE__, opts, name: name)
  end

  @doc """
  Stores a value in the cache.
  """
  def put(cache \\ __MODULE__, key, value) do
    GenServer.call(cache, {:put, key, value})
  end

  @doc """
  Retrieves a value from the cache.
  """
  def get(cache \\ __MODULE__, key) do
    GenServer.call(cache, {:get, key})
  end

  @doc """
  Deletes a key from the cache.
  """
  def delete(cache \\ __MODULE__, key) do
    GenServer.cast(cache, {:delete, key})
  end

  # Server Callbacks

  @impl true
  def init(opts) do
    ttl = Keyword.get(opts, :ttl, 60_000)
    {:ok, %{data: %{}, ttl: ttl}}
  end

  @impl true
  def handle_call({:put, key, value}, _from, state) do
    new_data = Map.put(state.data, key, {value, System.monotonic_time(:millisecond)})
    {:reply, :ok, %{state | data: new_data}}
  end

  @impl true
  def handle_call({:get, key}, _from, state) do
    case Map.get(state.data, key) do
      {value, timestamp} ->
        if System.monotonic_time(:millisecond) - timestamp < state.ttl do
          {:reply, {:ok, value}, state}
        else
          {:reply, {:error, :expired}, state}
        end

      nil ->
        {:reply, {:error, :not_found}, state}
    end
  end

  @impl true
  def handle_cast({:delete, key}, state) do
    new_data = Map.delete(state.data, key)
    {:noreply, %{state | data: new_data}}
  end
end
```

### Configuration API

Provide compile-time and runtime configuration:

```elixir
defmodule MyLib.Config do
  @moduledoc """
  Configuration for MyLib.

  ## Compile-time Configuration

      config :my_lib,
        default_timeout: 5000,
        max_retries: 3

  ## Runtime Configuration

      MyLib.configure(timeout: 10_000)
  """

  @doc """
  Gets a configuration value.
  """
  def get(key, default \\ nil) do
    Application.get_env(:my_lib, key, default)
  end

  @doc """
  Gets all configuration.
  """
  def get_all do
    Application.get_all_env(:my_lib)
  end

  @doc """
  Updates configuration at runtime.
  """
  def put(key, value) do
    Application.put_env(:my_lib, key, value)
  end

  @doc """
  Gets the timeout configuration.
  """
  def timeout do
    get(:default_timeout, 5000)
  end

  @doc """
  Gets the max retries configuration.
  """
  def max_retries do
    get(:max_retries, 3)
  end
end
```

### Builder Pattern with Structs

```elixir
defmodule MyLib.Query do
  @moduledoc """
  A query builder for MyLib.
  """

  defstruct [:table, :fields, :where, :limit, :offset]

  @type t :: %__MODULE__{
          table: String.t() | nil,
          fields: [atom()] | :all,
          where: keyword(),
          limit: pos_integer() | nil,
          offset: non_neg_integer() | nil
        }

  @doc """
  Creates a new query.
  """
  @spec new() :: t()
  def new do
    %__MODULE__{fields: :all, where: []}
  end

  @doc """
  Sets the table for the query.
  """
  @spec from(t(), String.t()) :: t()
  def from(%__MODULE__{} = query, table) when is_binary(table) do
    %{query | table: table}
  end

  @doc """
  Selects specific fields.
  """
  @spec select(t(), [atom()]) :: t()
  def select(%__MODULE__{} = query, fields) when is_list(fields) do
    %{query | fields: fields}
  end

  @doc """
  Adds a where clause.
  """
  @spec where(t(), keyword()) :: t()
  def where(%__MODULE__{} = query, conditions) when is_list(conditions) do
    %{query | where: query.where ++ conditions}
  end

  @doc """
  Sets the limit.
  """
  @spec limit(t(), pos_integer()) :: t()
  def limit(%__MODULE__{} = query, limit) when is_integer(limit) and limit > 0 do
    %{query | limit: limit}
  end

  @doc """
  Sets the offset.
  """
  @spec offset(t(), non_neg_integer()) :: t()
  def offset(%__MODULE__{} = query, offset) when is_integer(offset) and offset >= 0 do
    %{query | offset: offset}
  end

  @doc """
  Builds and executes the query.
  """
  @spec run(t()) :: {:ok, [map()]} | {:error, term()}
  def run(%__MODULE__{table: nil}), do: {:error, :no_table}
  def run(%__MODULE__{} = query) do
    # Implementation
    {:ok, []}
  end
end

# Usage:
# MyLib.Query.new()
# |> MyLib.Query.from("users")
# |> MyLib.Query.select([:id, :name])
# |> MyLib.Query.where(active: true)
# |> MyLib.Query.limit(10)
# |> MyLib.Query.run()
```

### Behaviour Definition

Define behaviors for extensibility:

```elixir
defmodule MyLib.Adapter do
  @moduledoc """
  Behaviour for MyLib adapters.
  """

  @type config :: keyword()
  @type result :: {:ok, term()} | {:error, term()}

  @callback init(config) :: {:ok, term()} | {:error, term()}
  @callback execute(query :: term(), state :: term()) :: result()
  @callback close(state :: term()) :: :ok

  @doc """
  Defines a default implementation for init/1.
  """
  defmacro __using__(_opts) do
    quote do
      @behaviour MyLib.Adapter

      @impl true
      def init(config) do
        {:ok, config}
      end

      defoverridable init: 1
    end
  end
end

# Implementation
defmodule MyLib.Adapters.Memory do
  use MyLib.Adapter

  @impl true
  def execute(query, state) do
    # Implementation
    {:ok, []}
  end

  @impl true
  def close(_state) do
    :ok
  end
end
```

---

## Typespecs and Dialyzer

### Basic Typespecs

```elixir
defmodule MyLib.Parser do
  @moduledoc """
  Parses data in various formats.
  """

  @type input :: String.t() | binary()
  @type parse_error :: {:error, :invalid_format | :empty_input}
  @type parse_result :: {:ok, map()} | parse_error()

  @doc """
  Parses the given input.
  """
  @spec parse(input()) :: parse_result()
  def parse(""), do: {:error, :empty_input}
  def parse(input) when is_binary(input) do
    # Implementation
    {:ok, %{}}
  end

  @spec parse!(input()) :: map()
  def parse!(input) do
    case parse(input) do
      {:ok, result} -> result
      {:error, reason} -> raise ArgumentError, "Parse failed: #{reason}"
    end
  end
end
```

### Advanced Type Definitions

```elixir
defmodule MyLib.Types do
  @moduledoc """
  Type definitions for MyLib.
  """

  # Opaque types (hide implementation)
  @opaque token :: {String.t(), pos_integer()}

  # Custom types
  @type user_id :: pos_integer()
  @type username :: String.t()
  @type user :: %{id: user_id(), name: username(), email: String.t()}

  # Union types
  @type result(success, error) :: {:ok, success} | {:error, error}

  # Generic types
  @type collection(item) :: [item] | MapSet.t(item)

  # Complex structs
  @typedoc """
  Configuration for MyLib operations.
  """
  @type config :: %{
          required(:timeout) => pos_integer(),
          required(:retries) => non_neg_integer(),
          optional(:debug) => boolean(),
          optional(:adapter) => module()
        }
end
```

### Dialyzer Configuration

```elixir
# mix.exs
def project do
  [
    # ...
    dialyzer: dialyzer()
  ]
end

defp dialyzer do
  [
    plt_file: {:no_warn, "priv/plts/dialyzer.plt"},
    plt_add_apps: [:ex_unit, :mix],
    flags: [
      :error_handling,
      :underspecs,
      :unmatched_returns
    ],
    # Paths to check
    paths: ["_build/#{Mix.env()}/lib/my_lib/ebin"],
    # Ignore specific warnings
    ignore_warnings: ".dialyzer_ignore.exs"
  ]
end
```

**.dialyzer_ignore.exs:**
```elixir
[
  # Ignore specific warnings
  {"lib/my_lib/legacy.ex", :no_return},
  ~r/.*vendored.*/
]
```

---

## ExDoc Documentation

### Module Documentation

```elixir
defmodule MyLib do
  @moduledoc """
  MyLib provides functionality for...

  ## Installation

  Add `my_lib` to your list of dependencies in `mix.exs`:

      def deps do
        [
          {:my_lib, "~> 0.1.0"}
        ]
      end

  ## Usage

      iex> MyLib.parse("data")
      {:ok, %{key: "value"}}

  ## Configuration

      config :my_lib,
        timeout: 5000,
        max_retries: 3

  ## Examples

  ### Basic Usage

      MyLib.Query.new()
      |> MyLib.Query.from("users")
      |> MyLib.Query.run()

  ### Advanced Usage

      query =
        MyLib.Query.new()
        |> MyLib.Query.from("orders")
        |> MyLib.Query.where(status: "pending")
        |> MyLib.Query.limit(100)

      case MyLib.Query.run(query) do
        {:ok, results} -> process_results(results)
        {:error, reason} -> handle_error(reason)
      end
  """

  @doc """
  Parses the given input data.

  ## Parameters

    * `input` - The input string to parse
    * `opts` - Optional keyword list of options:
      * `:strict` - Enable strict parsing (default: `false`)
      * `:format` - Output format (default: `:map`)

  ## Returns

    * `{:ok, result}` - Successfully parsed data
    * `{:error, reason}` - Parse error with reason

  ## Examples

      iex> MyLib.parse("key=value")
      {:ok, %{"key" => "value"}}

      iex> MyLib.parse("invalid", strict: true)
      {:error, :invalid_format}

      iex> MyLib.parse("a=1&b=2", format: :keyword)
      {:ok, [a: "1", b: "2"]}

  ## Error Reasons

    * `:invalid_format` - Input doesn't match expected format
    * `:empty_input` - Input is empty or nil
    * `:parse_error` - Generic parsing error
  """
  @spec parse(String.t(), keyword()) :: {:ok, map()} | {:error, atom()}
  def parse(input, opts \\ []) do
    # Implementation
  end

  @doc """
  Same as `parse/2` but raises on error.

  ## Examples

      iex> MyLib.parse!("key=value")
      %{"key" => "value"}

      iex> MyLib.parse!("invalid")
      ** (ArgumentError) invalid input
  """
  @spec parse!(String.t(), keyword()) :: map()
  def parse!(input, opts \\ []) do
    case parse(input, opts) do
      {:ok, result} -> result
      {:error, reason} -> raise ArgumentError, "parse failed: #{reason}"
    end
  end

  @doc since: "0.2.0"
  @doc deprecated: "Use parse/2 instead"
  def old_parse(input) do
    parse(input)
  end

  @doc false
  def internal_helper do
    # This won't appear in docs
  end
end
```

### Documentation Groups

```elixir
# mix.exs
defp docs do
  [
    main: "MyLib",
    logo: "assets/logo.png",
    source_ref: "v#{@version}",
    source_url: @source_url,
    extras: [
      "README.md",
      "CHANGELOG.md",
      "guides/getting_started.md",
      "guides/advanced_usage.md"
    ],
    groups_for_extras: [
      Guides: ~r/guides\/.*/
    ],
    groups_for_modules: [
      Core: [MyLib, MyLib.Config],
      Adapters: [MyLib.Adapter, MyLib.Adapters.Memory],
      Utilities: [MyLib.Utils, MyLib.Helpers]
    ],
    groups_for_functions: [
      "CRUD Operations": &(&1[:section] == :crud),
      "Query Building": &(&1[:section] == :query)
    ]
  ]
end
```

### Doctests

```elixir
defmodule MyLib.Math do
  @doc """
  Adds two numbers.

  ## Examples

      iex> MyLib.Math.add(1, 2)
      3

      iex> MyLib.Math.add(-1, 1)
      0

  Multiple lines:

      iex> result = MyLib.Math.add(10, 20)
      iex> result * 2
      60

  Pattern matching:

      iex> {:ok, result} = {:ok, MyLib.Math.add(5, 5)}
      iex> result
      10

  Exceptions:

      iex> MyLib.Math.add("a", "b")
      ** (ArithmeticError) bad argument in arithmetic expression
  """
  def add(a, b) do
    a + b
  end
end
```

Run doctests:

```elixir
# test/my_lib_test.exs
defmodule MyLibTest do
  use ExUnit.Case
  doctest MyLib
  doctest MyLib.Math
end
```

---

## Testing Patterns

### Unit Tests

```elixir
defmodule MyLib.ParserTest do
  use ExUnit.Case, async: true

  alias MyLib.Parser

  describe "parse/1" do
    test "parses valid input" do
      assert {:ok, %{"key" => "value"}} = Parser.parse("key=value")
    end

    test "returns error for invalid input" do
      assert {:error, :invalid_format} = Parser.parse("invalid")
    end

    test "handles empty input" do
      assert {:error, :empty_input} = Parser.parse("")
    end
  end

  describe "parse!/1" do
    test "returns parsed data on success" do
      assert %{"key" => "value"} = Parser.parse!("key=value")
    end

    test "raises on error" do
      assert_raise ArgumentError, fn ->
        Parser.parse!("invalid")
      end
    end
  end
end
```

### GenServer Testing

```elixir
defmodule MyLib.CacheTest do
  use ExUnit.Case, async: true

  alias MyLib.Cache

  setup do
    # Start cache for this test
    {:ok, cache} = start_supervised({Cache, name: :"cache_#{:rand.uniform(10000)}"})
    %{cache: cache}
  end

  test "stores and retrieves values", %{cache: cache} do
    assert :ok = Cache.put(cache, :key, "value")
    assert {:ok, "value"} = Cache.get(cache, :key)
  end

  test "returns error for missing keys", %{cache: cache} do
    assert {:error, :not_found} = Cache.get(cache, :missing)
  end

  test "expires old values", %{cache: cache} do
    {:ok, cache_with_ttl} = start_supervised({Cache, ttl: 100})

    Cache.put(cache_with_ttl, :key, "value")
    assert {:ok, "value"} = Cache.get(cache_with_ttl, :key)

    Process.sleep(150)
    assert {:error, :expired} = Cache.get(cache_with_ttl, :key)
  end
end
```

### Property-Based Testing

```elixir
defmodule MyLib.PropertyTest do
  use ExUnit.Case
  use ExUnitProperties

  alias MyLib.Parser

  property "parse never crashes" do
    check all input <- string(:printable) do
      # Should never raise
      case Parser.parse(input) do
        {:ok, _} -> :ok
        {:error, _} -> :ok
      end
    end
  end

  property "parse roundtrip" do
    check all data <- map_of(atom(:alphanumeric), string(:alphanumeric)) do
      serialized = MyLib.serialize(data)
      {:ok, parsed} = Parser.parse(serialized)
      assert parsed == data
    end
  end
end
```

### Integration Tests

```elixir
defmodule MyLib.IntegrationTest do
  use ExUnit.Case

  @moduletag :integration

  setup_all do
    # Start application
    {:ok, _} = Application.ensure_all_started(:my_lib)
    on_exit(fn -> Application.stop(:my_lib) end)
    :ok
  end

  test "end-to-end workflow" do
    # Start a process
    {:ok, pid} = MyLib.Worker.start_link([])

    # Perform operations
    assert :ok = MyLib.Worker.put(pid, :key, "value")
    assert {:ok, "value"} = MyLib.Worker.get(pid, :key)

    # Cleanup
    GenServer.stop(pid)
  end
end
```

---

## Dependency Management

### Hex Dependencies

```elixir
defp deps do
  [
    # Production dependencies
    {:jason, "~> 1.4"},
    {:plug, "~> 1.15"},

    # Optional dependencies
    {:telemetry, "~> 1.2", optional: true},

    # Development only
    {:ex_doc, "~> 0.31", only: :dev, runtime: false},
    {:dialyxir, "~> 1.4", only: [:dev, :test], runtime: false},
    {:credo, "~> 1.7", only: [:dev, :test], runtime: false},

    # Test only
    {:stream_data, "~> 1.0", only: :test},
    {:mox, "~> 1.1", only: :test}
  ]
end
```

### Version Constraints

| Constraint | Meaning | Example |
|------------|---------|---------|
| `~> 1.4` | >= 1.4.0 and < 2.0.0 | Recommended |
| `~> 1.4.5` | >= 1.4.5 and < 1.5.0 | Patch updates only |
| `>= 1.4.0` | Any version >= 1.4.0 | Too permissive |
| `== 1.4.0` | Exactly 1.4.0 | Too restrictive |

### Optional Dependencies

```elixir
# In mix.exs
defp deps do
  [
    {:jason, "~> 1.4", optional: true}
  ]
end

# In code
if Code.ensure_loaded?(Jason) do
  def encode(data), do: Jason.encode(data)
else
  def encode(_data), do: {:error, :jason_not_available}
end
```

---

## Publishing to Hex

### Pre-publish Checklist

- [ ] `mix compile --warnings-as-errors` passes
- [ ] `mix test` passes all tests
- [ ] `mix format --check-formatted` passes
- [ ] `mix credo --strict` passes (if using Credo)
- [ ] `mix dialyzer` passes (if using Dialyzer)
- [ ] `mix docs` generates correctly
- [ ] Version bumped in mix.exs
- [ ] CHANGELOG.md updated
- [ ] README.md is current
- [ ] All required package fields in mix.exs
- [ ] License file present
- [ ] `mix hex.build` succeeds

### Publishing Commands

```bash
# Build package locally
mix hex.build

# Verify package contents
unzip my_lib-0.1.0.tar -d /tmp/package
ls -la /tmp/package

# Publish to Hex (requires authentication)
mix hex.publish

# Publish docs separately (if needed)
mix hex.publish docs

# Revert a version (within 24 hours)
mix hex.publish --revert 0.1.0
```

### Hex Authentication

```bash
# Authenticate with Hex
mix hex.user auth

# Register new user
mix hex.user register

# Create API key
mix hex.user key generate
```

### Package Retirement

```bash
# Retire a version (discourage use)
mix hex.retire my_lib 0.1.0 "Security vulnerability"

# Unretire
mix hex.retire my_lib 0.1.0 --unretire
```

---

## Module Organization

### Standard Library Structure

```
my_lib/
├── lib/
│   ├── my_lib.ex              # Main public API
│   ├── my_lib/
│   │   ├── application.ex     # OTP application
│   │   ├── supervisor.ex      # Main supervisor
│   │   ├── config.ex          # Configuration API
│   │   ├── parser.ex          # Core functionality
│   │   ├── types.ex           # Type definitions
│   │   ├── adapters/          # Adapter modules
│   │   │   ├── adapter.ex     # Behaviour definition
│   │   │   └── memory.ex      # Implementation
│   │   └── internal/          # Private modules
│   │       └── utils.ex
│   └── mix/
│       └── tasks/             # Custom Mix tasks
│           └── my_lib.gen.ex
├── test/
│   ├── my_lib_test.exs
│   ├── my_lib/
│   │   ├── parser_test.exs
│   │   └── adapters/
│   │       └── memory_test.exs
│   ├── support/
│   │   └── test_helpers.ex
│   └── test_helper.exs
├── priv/                      # Private runtime files
│   └── templates/
├── .formatter.exs
├── mix.exs
├── README.md
├── CHANGELOG.md
└── LICENSE
```

### Main Module Pattern

```elixir
defmodule MyLib do
  @moduledoc """
  Main entry point for MyLib.
  """

  # Re-export public API
  defdelegate parse(input), to: MyLib.Parser
  defdelegate parse(input, opts), to: MyLib.Parser
  defdelegate serialize(data), to: MyLib.Serializer

  # Direct implementations
  def version, do: Application.spec(:my_lib, :vsn) |> to_string()

  def child_spec(opts) do
    %{
      id: __MODULE__,
      start: {MyLib.Supervisor, :start_link, [opts]},
      type: :supervisor
    }
  end
end
```

---

## Anti-Patterns

### 1. Process Dictionary Abuse

```elixir
# Bad: Using process dictionary in libraries
def get_config do
  Process.get(:my_lib_config)
end

# Good: Explicit state passing
def get_config(%State{config: config}), do: config
```

### 2. Global Named Processes

```elixir
# Bad: Single global process
GenServer.start_link(__MODULE__, [], name: __MODULE__)

# Good: Allow multiple instances
GenServer.start_link(__MODULE__, [], name: name)
```

### 3. Missing Supervision

```elixir
# Bad: Spawning unsupervised processes
spawn(fn -> do_work() end)

# Good: Use Task.Supervisor or DynamicSupervisor
Task.Supervisor.start_child(MyLib.TaskSupervisor, fn -> do_work() end)
```

### 4. Breaking API Changes

```elixir
# v0.1.0
def fetch(id), do: {:ok, data}

# v0.2.0 - WRONG! Breaking change in minor version
def fetch(id, opts \\ []), do: {:ok, data}

# v0.2.0 - Correct: Add new function
def fetch(id), do: fetch(id, [])
def fetch_with_opts(id, opts), do: {:ok, data}
```

### 5. Missing Typespecs

```elixir
# Bad: No typespec
def process(data, opts) do
  # ...
end

# Good: Full typespec
@spec process(map(), keyword()) :: {:ok, result()} | {:error, term()}
def process(data, opts) do
  # ...
end
```

---

## Common Mix Tasks

### Custom Mix Tasks

```elixir
# lib/mix/tasks/my_lib.gen.ex
defmodule Mix.Tasks.MyLib.Gen do
  use Mix.Task

  @shortdoc "Generates MyLib configuration"
  @moduledoc """
  Generates MyLib configuration file.

      mix my_lib.gen

  ## Options

    * `--path` - Output path (default: config/my_lib.exs)
  """

  @impl Mix.Task
  def run(args) do
    {opts, _, _} = OptionParser.parse(args, switches: [path: :string])
    path = opts[:path] || "config/my_lib.exs"

    File.write!(path, """
    import Config

    config :my_lib,
      timeout: 5000,
      max_retries: 3
    """)

    Mix.shell().info("Generated #{path}")
  end
end
```

---

## References

- `meta-library-dev` - Foundational library patterns
- `lang-elixir-dev` - Core Elixir syntax and OTP
- [Hex Documentation](https://hex.pm/docs)
- [ExDoc](https://hexdocs.pm/ex_doc)
- [Dialyzer](https://www.erlang.org/doc/man/dialyzer.html)
- [Elixir Library Guidelines](https://hexdocs.pm/elixir/library-guidelines.html)
