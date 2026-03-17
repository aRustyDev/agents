# Building a native macOS data analytics notebook in Swift

## Research Prompt

> I'm looking to build a SwiftUI native app, for a data analytics capability similar to what Marimo can do. 
> 
> I'm looking for
> * Cluster analysis of high dimensional data
> * Temporal analysis of lower dimensional data
> * SQL like table/record analysis
> * Node & Edge Graph representations (ideally interactive, like D3.js)
>
>> Interesting pivot — this is a meaty project. Before I dive into research, a few things would really shape what I look for:
>> 
>> Target platform — macOS app, iPad, or universal? Data analytics UX differs significantly between them, especially for interactive graphs and SQL-style querying.
>> Data source model — Are you working with local files (CSV, Parquet, SQLite), connecting to remote databases, or both? And roughly what scale of data are we talking?
>> Purpose — Is this a portfolio piece for the job search, a personal tool you'll actually use day-to-day, or the seed of something commercial? That changes how much you'd invest in polish vs. raw capability.
>> 
>>> Q: Primary target platform?
>>> A: macOS only
>>> 
>>> Q: Primary data sources? (Select all that apply)
>>> A: Local files (CSV, Parquet, SQLite)
>>> 
>>> Q: What's the primary purpose? (Select all that apply)
>>> A: Portfolio / job search artifact
>>>
>>>> Good — macOS-only simplifies things considerably (AppKit interop, no compromise on interaction density, full keyboard/mouse). And as a portfolio piece, the architecture and code quality matter as much as the feature set.
>>>> Let me do a deep dive into the Swift/SwiftUI ecosystem for each of your four capability areas — charting libraries, cluster analysis frameworks, SQL-like data manipulation, and interactive graph/network visualization. I'll also look at how people have approached Marimo-style reactive notebook UIs natively.

**A Marimo-like reactive notebook for macOS is not only feasible — it fills a genuine gap in the Swift ecosystem.** The critical architectural stack combines DuckDB Swift for SQL analytics, Apple's Accelerate framework for numerical computing, Grape for force-directed graph visualization, and Swift Charts for 2D/3D plotting, all wired together by SwiftUI's `@Observable` data flow driving a DAG-based reactive execution engine. No such project exists today, making it a standout portfolio piece. Here's the full landscape of libraries, frameworks, and architectural decisions you need.

---

## Cluster analysis: Accelerate does the heavy lifting, but gaps remain

Swift's native ML ecosystem is thin compared to Python's, but Apple's **Accelerate framework** provides the foundational numerical computing layer. Its BLAS implementation outperforms Eigen on Apple Silicon, and LAPACK routines — particularly **`dgesvd` for singular value decomposition** — make PCA fully achievable in pure Swift. The workflow is straightforward: center your data matrix with vDSP, compute SVD via LAPACK, project onto the top-k singular vectors. Multiple open-source implementations demonstrate this pattern (LASwift, fastica-swift).

For clustering algorithms themselves, the landscape is sparser. **Create ML has no built-in k-means** — Apple's now-archived Turi Create had it, but that project is dead. K-means must be hand-rolled using Accelerate primitives (vDSP for distance computations, BLAS for matrix operations) or accessed via PythonKit bridging to scikit-learn. NSHipster's DBSCAN package (github.com/NSHipster/DBSCAN, ~80 stars) provides a clean generic implementation, but the repository is archived. **No native Swift t-SNE or UMAP implementation exists** — this is the single largest gap. PCA via Accelerate is the only on-device dimensionality reduction option; for non-linear methods, PythonKit bridging or pre-computation is required.

The key third-party libraries worth evaluating:

- **apple/swift-numerics** (~1,800 ★, active): Numerical primitives (complex numbers, elementary functions), but no matrix types or linear algebra — it's a foundation, not a solution
- **Jounce/Surge** (~5,200 ★, unmaintained since ~2021): Accelerate wrappers for matrix math, FFT, statistics — useful reference code but effectively abandoned
- **jjjkkkjjj/Matft** (~130 ★, periodically updated): NumPy-like N-dimensional array library backed by Accelerate, with broadcasting and slicing — the closest thing to numpy in Swift
- **Swift-AI** (~6,100 ★, archived): Neural networks only, stale for years

For visualization, **Swift Charts' `PointMark`** handles 2D scatter plots of clustered data with automatic cluster coloring via `.foregroundStyle(by:)`. The WWDC24 vectorized `PointPlot` API improves performance for larger datasets. Most exciting is **Chart3D** (introduced WWDC25, macOS 26+), which natively supports 3D scatter plots with interactive rotation — ideal for visualizing PCA projections across three principal components. For pre-macOS 26 targets or massive point clouds, SceneKit or Metal rendering is the fallback.

**Recommended approach**: Implement k-means manually using Accelerate (it's ~200 lines with vDSP distance calculations), use the archived DBSCAN package as-is (it's small and correct), do PCA via LAPACK SVD, and bridge to Python via PythonKit only for t-SNE/UMAP when needed. This hybrid gives you native performance for 90% of workflows.

---

## Time-series visualization hits a performance ceiling at ~3K points

**Swift Charts is excellent for small-to-medium time-series but fundamentally unsuitable for large-dataset analytics.** Testing on M3 Max hardware shows smooth interaction up to roughly **2–3K data points** per series; at 10K points, even the WWDC24 vectorized `PointPlot` API produces sluggish selection; at 100K points, the app is effectively unusable. This is a hard architectural limit — Swift Charts prioritizes accessibility (built-in VoiceOver, Audio Graphs) and declarative elegance over raw throughput.

For a data analytics app, a **hybrid rendering strategy** is essential. Use Swift Charts for summary panels, overview visualizations, and anything under 3K points — its native SwiftUI integration, automatic date axis formatting, and scrollable time ranges (iOS 17+) are unmatched for developer productivity. For the primary exploration view where users zoom and pan across large time series, you need either a **custom Metal/Core Graphics renderer** or the commercial **SciChart** library (the only option benchmarked to handle millions of points at interactive frame rates on Apple platforms).

The third-party charting landscape is consolidating. **DGCharts** (formerly danielgindi/Charts, ~28,000 ★) remains the most-starred Swift charting library but is in decline — 891 open issues, slowing commits, and no native SwiftUI API (requires UIViewRepresentable wrappers). **SwiftUICharts** by willdale (~950 ★) is a lightweight native SwiftUI option but is essentially a single-developer project with limited chart types. Neither solves the large-dataset problem.

For temporal analysis computations, **no comprehensive Swift time-series library exists**. The ecosystem gap is stark: no rolling statistics, no STL decomposition, no ARIMA, no maintained anomaly detection library. You must build these from Accelerate primitives:

- **Moving averages**: `vDSP_vswsum` (sliding window sum) divided by window size
- **FFT spectral analysis**: `vDSP.FFT` for frequency-domain analysis
- **Signal filtering**: `vDSP.Biquad` for low-pass/high-pass/band-pass IIR filters
- **Smoothing**: Convolution via `vDSP_conv` with custom kernels

One developer ported Twitter's S-H-ESD anomaly detection algorithm to Swift (building custom STL decomposition and Student-T distribution packages from scratch), demonstrating the approach is feasible but also highlighting how much foundational work is missing. For advanced time-series analytics (seasonal decomposition, forecasting), **PythonKit bridging to statsmodels/scikit-learn is the pragmatic path**.

---

## DuckDB Swift is the linchpin for SQL-over-files

**DuckDB's official Swift bindings are the single most important library for this project.** Available at github.com/duckdb/duckdb-swift (~118 ★, 631 commits, MIT license), this is not a community wrapper — it's maintained by the core DuckDB team and mirrors every DuckDB release. It provides an idiomatic Swift API with `Sendable` conformance for Swift concurrency, wrapping the DuckDB C++ analytical engine.

DuckDB solves the entire SQL-over-files problem in one dependency. It queries **CSV files** directly (`SELECT * FROM read_csv('data.csv')`), reads **Parquet files** natively with filter and projection pushdown (`SELECT * FROM read_parquet('file.parquet')`), and can attach **SQLite databases** via the sqlite_scanner extension. Users write standard SQL with full analytical capabilities: window functions, CTEs, correlated subqueries, complex types, and more. Results can feed directly into Apple's TabularData `DataFrame` for display or into Swift Charts for visualization. The package includes a working SwiftUI example app (ExoplanetExplorer).

**Apple's TabularData framework** (macOS 12+) complements DuckDB as the display and light-manipulation layer. It reads CSV and JSON natively, supports filtering, grouping, joining, and aggregation — but has no SQL interface, no Parquet support, and limited analytical operations. Think of it as the "last mile" between query results and SwiftUI views.

For the app's internal persistence (saved queries, user preferences, notebook metadata), **GRDB.swift** (github.com/groue/GRDB.swift, ~8,100 ★, v7.9.0 released December 2025) is the strongest choice. It's the most actively maintained Swift SQLite library, with database observation via `ValueObservation` that integrates directly with SwiftUI through the `@Query` property wrapper — enabling reactive UI updates when data changes. **SQLite.swift** (~10,100 ★) is also well-maintained but lacks GRDB's observation and migration features.

The recommended data pipeline architecture:

```
User Files (.csv, .parquet, .sqlite, .json)
        ↓
   DuckDB Swift (SQL query engine, in-process)
        ↓
   TabularData DataFrame (display adapter)
        ↓
   SwiftUI Views (Tables, Charts, Markdown)
```

**Native Parquet reading without DuckDB does not exist in Swift.** Apache's arrow-swift (github.com/apache/arrow-swift, 13 ★, first release July 2025) implements the Arrow columnar format but has no Parquet reader yet. DuckDB is the only production path for Parquet on Apple platforms.

---

## Grape delivers D3-style force-directed graphs natively in SwiftUI

For interactive node-and-edge visualization, **Grape** (github.com/SwiftGraphs/Grape, ~370 ★, MIT license) is the clear winner and arguably the only serious option. Built explicitly as a D3.js-inspired force simulation for SwiftUI, it provides a declarative API with `ForceDirectedGraph`, `NodeMark`, and `LinkMark` — modeled directly after D3's force system with `ManyBodyForce`, `LinkForce`, `CenterForce`, and `CollideForce`.

Performance is excellent: Grape uses a custom Barnes-Hut approximation via `BufferedKDTree` that benchmarks **22× faster than Apple's `GKQuadtree`** — ~0.005s per tick for 77 vertices/254 edges on M1 Max in release builds. It supports both 2D and 3D layouts (including RealityView for visionOS), with built-in tap and drag gesture support. The library is actively maintained (tested against Swift 5.10 through 6.2) though it's pre-1.0, so the visualization API may see breaking changes.

The alternatives each have clear tradeoffs. **SpriteKit's physics engine** can simulate force-directed layouts using `SKPhysicsJointSpring` for edges and `SKFieldNode.electricField()` for repulsion, embedded in SwiftUI via `SpriteView` — but it's tuned for games, not graphs, and requires substantial custom code. **WKWebView with D3.js** gives immediate access to D3's vast ecosystem and excellent interactivity, but runs CPU-bound with no GPU access, produces non-native-feeling visuals, and requires JSON serialization for every data exchange between Swift and JavaScript. **GraphViz Swift bindings** (SwiftDocOrg/GraphViz, archived 2021) can invoke Graphviz's layout algorithms but produce static images only and require system GraphViz installation — problematic for distribution. **Metal rendering** handles arbitrarily large graphs at 60fps but demands enormous development effort.

For graph data structures and algorithms underneath the visualization, **SwiftGraph** (github.com/davecom/SwiftGraph, 782 ★, Apache 2.0) provides weighted/unweighted directed/undirected graphs with BFS, DFS, Dijkstra, topological sort, and cycle detection. **GameplayKit's `GKGraph`** offers pathfinding (A*) and spatial partitioning (`GKQuadtree`) but no layout algorithms — it's a complement for graph algorithms, not a visualization tool.

**Recommended approach**: Use Grape for interactive force-directed visualization, SwiftGraph for graph algorithms and data structures, and reserve WKWebView+D3.js only as a fallback for specialized visualization types (Sankey diagrams, chord diagrams) where no native Swift equivalent exists.

---

## The reactive notebook architecture maps cleanly to SwiftUI's data flow

Building a Marimo-like reactive cell system in SwiftUI is architecturally natural because **SwiftUI's `@Observable` framework already implements fine-grained dependency tracking** — the same core concept underlying Marimo's reactive execution. The key insight from Marimo's architecture is that it uses **static analysis** (Python's `ast.parse()`) to build a DAG of cell dependencies before execution, then propagates changes through descendant cells when any cell runs. This maps directly to a SwiftUI data model.

The proposed architecture centers on an `@Observable` notebook model:

```
NotebookDocument (@Observable)
├── cells: OrderedDictionary<CellID, Cell>
├── dependencyGraph: adjacency list [CellID: Set<CellID>]
├── variableStore: [String: Any]
└── executionEngine: manages subprocess compilation

Cell (@Observable)  
├── source: String (code text)
├── output: CellOutput? (execution result)
├── definitions: Set<String> (variables defined)
├── references: Set<String> (variables referenced)
└── state: .idle | .running | .stale | .error
```

When a cell's source changes, re-parse it to extract definitions and references, rebuild the DAG edges, then either auto-execute descendants (eager mode) or mark them `.stale` (lazy mode, preferred for expensive computations). `@Observable` on `Cell.state` and `Cell.output` automatically triggers SwiftUI view updates with minimal re-rendering — only views observing the changed properties update.

**No existing Swift reactive notebook project was found** — this is genuinely novel. For the DAG implementation, SwiftGraph provides topological sort and cycle detection out of the box, or a lightweight custom adjacency list (~150 lines) suffices. **FirebladeGraph** (github.com/fireblade-engine/graph) offers a `Node<Content>` base class with `updateFromParent()` propagation that closely mirrors the reactive cell pattern.

For code editing, the strongest options are **CodeEditorView** by mchakravarty (pure SwiftUI API, TextKit 2, macOS/iOS/visionOS, Xcode-inspired with syntax highlighting and bracket matching) and **CodeEditSourceEditor** (tree-sitter-powered, used by the CodeEdit project at ~17,900 ★). ZeeZide's **CodeEditor** package offers the simplest integration (`CodeEditor(source: $source, language: .swift)`) via Highlight.js through JavaScriptCore, supporting 180+ languages and 80+ themes.

For executing Swift code within cells, the most viable approach is **subprocess compilation**: concatenate all cells in topological order into a single `.swift` file, compile with `swiftc` via Foundation's `Process` (or Apple's new swift-subprocess package), and capture stdout/stderr. This gives full Swift language support with shared state across cells. The tradeoff is ~1–3 second compilation latency per execution, which is acceptable for a notebook workflow. For SQL cells, route directly to the embedded DuckDB engine. For markdown cells, render with SwiftUI's `AttributedString` or a Markdown parser.

---

## What makes this a compelling portfolio piece for AI/ML infrastructure roles

**The reactive notebook architecture directly mirrors the systems that AI/ML infrastructure engineers build daily.** The DAG-based execution engine is the same pattern underlying Airflow, Dagster, TensorFlow's computation graphs, and build systems like Bazel. Smart re-execution (only running affected downstream cells) demonstrates understanding of cache invalidation — one of the hardest problems in distributed systems. The plugin architecture for different cell types (code, SQL, visualization, markdown) parallels extensible platform design.

Three architectural decisions signal genuine systems depth. First, **embedding DuckDB as an in-process analytical engine** shows you understand the tradeoffs between embedded vs. client-server databases and can select the right tool for OLAP workloads. Second, **using Accelerate/Metal for computation and rendering** demonstrates hardware-aware performance thinking — the same mindset needed for GPU-accelerated ML training infrastructure. Third, **the reactive dataflow model with topological execution ordering** is a direct analog to ML pipeline orchestration and streaming data systems.

The project's novelty matters: no reactive Swift notebook exists today. Marimo is Python-only, Pluto.jl is Julia-only. A working macOS app that can be downloaded and demoed is dramatically more impressive than a GitHub README. The key is production-ready polish: proper error handling for malformed cells, graceful cycle detection in the dependency graph, lazy execution for expensive computations, and persistence as `.swift` files for git-friendliness (exactly Marimo's approach over Jupyter's `.ipynb`).

For maximum impact, the README should include an architecture diagram showing the DAG execution engine, the data flow from DuckDB through TabularData to SwiftUI views, and the reactive propagation model. Commit history showing iterative development signals engineering maturity. And framing the project as "a reactive computational notebook that reduces data science iteration time through automatic dependency-aware re-execution" speaks directly to the productivity tooling experience that infrastructure teams value.

---

## Conclusion

The Swift/macOS ecosystem for data analytics is a landscape of strong foundations with conspicuous gaps. Apple's Accelerate framework, DuckDB's official Swift bindings, Swift Charts (with its 3K-point performance ceiling), and Grape's force-directed graph visualization provide production-quality building blocks. The critical gaps — no native t-SNE/UMAP, no time-series analysis library, no Parquet reader outside DuckDB, and Swift Charts' large-dataset limitations — are manageable through strategic use of PythonKit bridging, Accelerate primitives for custom implementations, and hybrid rendering approaches.

The most important architectural insight is that **DuckDB Swift should be the central nervous system** of the app — it unifies CSV, Parquet, and SQLite querying under a single SQL interface, eliminating the need to juggle multiple file-format libraries. Pair it with `@Observable`-driven reactive cell execution, Grape for graph visualization, and a hybrid Swift Charts + Metal rendering strategy for time series, and you have a technically distinctive application that no one has built before.
