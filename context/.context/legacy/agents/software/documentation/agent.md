#### Stage 1: Initial Discovery (Architecture Understanding)
1. Read all modules in this order to understand the flow:
  - `__init__.py`, `main.py` (entry points)
  - `honk.py`, `datadumper.py` (orchestration)
  - `conf.py`, `auth.py`, `utils.py`, `csv.py` (infrastructure)
  - All data dumpers (in size order)

2. For each module, capture:
  - Primary business purpose
  - Key classes and their relationships
  - External dependencies
  - Integration touchpoints

#### Stage 2: Deep Analysis (Implementation Details)
1. Re-read each module focusing on:
  - Method signatures and their business purposes
  - Data flow through the module
  - Error handling strategies
  - Async patterns and concurrency
  - State management approaches

2. Create detailed notes on:
  - How each function serves the business need
  - Complex logic flows that need diagrams
  - Security-sensitive operations
  - Performance-critical sections

#### Stage 3: Relationship Mapping (Integration Analysis)
1. Trace workflows across modules:
  - Authentication flow from CLI to API calls
  - Data collection workflow for each service
  - Error propagation and handling
  - Configuration usage patterns

2. Identify and document:
  - Shared patterns across dumpers
  - Common utility usage
  - Cross-cutting concerns
  - Abstraction hierarchies

#### Stage 4: Documentation Generation
1. Create the overview `index.md` with complete architecture
2. For each module, generate documentation following the template
3. Ensure all diagrams are:
  - Mermaid-compatible for GitLab rendering
  - Focused on business understanding
  - Showing actual relationships from code
