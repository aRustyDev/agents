# DuckDB Swift Integration

## Purpose

Using DuckDB as an in-process analytical SQL engine for SwiftUI applications, enabling SQL queries over CSV, Parquet, and SQLite files.

## Installation

```swift
// Package.swift
dependencies: [
    .package(url: "https://github.com/duckdb/duckdb-swift", from: "1.0.0")
]
```

## Basic Usage

### Creating a Database

```swift
import DuckDB

// In-memory database
let database = try Database(store: .inMemory)
let connection = try database.connect()

// File-backed database
let database = try Database(store: .file(at: "analytics.duckdb"))
```

### Executing Queries

```swift
// Execute SQL
try connection.execute("CREATE TABLE items (id INTEGER, name VARCHAR, price DECIMAL)")

// Insert data
try connection.execute("""
    INSERT INTO items VALUES
    (1, 'Widget', 9.99),
    (2, 'Gadget', 19.99)
""")

// Query with results
let result = try connection.query("SELECT * FROM items WHERE price > 10")
```

### Processing Results

```swift
// Iterate rows
for row in result {
    let id: Int32 = row[0]!
    let name: String = row[1]!
    let price: Double = row[2]!
    print("\(id): \(name) - $\(price)")
}

// Column access
let names = result[1].cast(to: String.self)
for name in names {
    print(name ?? "NULL")
}
```

## File Queries

### CSV Files

```swift
// Query CSV directly
let result = try connection.query("""
    SELECT * FROM read_csv('data.csv')
    WHERE category = 'Electronics'
    ORDER BY price DESC
    LIMIT 10
""")

// With options
let result = try connection.query("""
    SELECT * FROM read_csv('data.csv',
        header = true,
        delim = ',',
        columns = {'id': 'INTEGER', 'name': 'VARCHAR', 'price': 'DECIMAL'}
    )
""")
```

### Parquet Files

```swift
// Query Parquet directly
let result = try connection.query("""
    SELECT
        date_trunc('month', timestamp) as month,
        SUM(amount) as total
    FROM read_parquet('transactions.parquet')
    GROUP BY 1
    ORDER BY 1
""")

// Filter pushdown (efficient)
let result = try connection.query("""
    SELECT * FROM read_parquet('large_file.parquet')
    WHERE year = 2024 AND region = 'US'
""")
```

### SQLite Integration

```swift
// Attach SQLite database
try connection.execute("INSTALL sqlite; LOAD sqlite;")
try connection.execute("ATTACH 'existing.sqlite' AS sqlite_db (TYPE sqlite)")

// Query SQLite tables
let result = try connection.query("""
    SELECT * FROM sqlite_db.users
    WHERE created_at > '2024-01-01'
""")
```

## SwiftUI Integration

### Observable Query Model

```swift
import SwiftUI
import DuckDB

@Observable
final class AnalyticsViewModel {
    var results: [[String: Any]] = []
    var isLoading = false
    var error: Error?

    private let database: Database
    private let connection: Connection

    init() throws {
        database = try Database(store: .inMemory)
        connection = try database.connect()
    }

    func executeQuery(_ sql: String) async {
        isLoading = true
        defer { isLoading = false }

        do {
            let result = try connection.query(sql)
            results = result.map { row in
                var dict: [String: Any] = [:]
                for (index, column) in result.columns.enumerated() {
                    dict[column.name] = row[index]
                }
                return dict
            }
            error = nil
        } catch {
            self.error = error
            results = []
        }
    }

    func loadCSV(from url: URL) async throws {
        try connection.execute("""
            CREATE OR REPLACE TABLE data AS
            SELECT * FROM read_csv('\(url.path)')
        """)
    }
}
```

### Results Table View

```swift
struct QueryResultsView: View {
    let results: [[String: Any]]
    let columns: [String]

    var body: some View {
        Table(results, columns: columns) { result in
            TableRow(result) { columnName in
                Text(String(describing: result[columnName] ?? "NULL"))
            }
        }
    }
}
```

### SQL Editor View

```swift
struct SQLEditorView: View {
    @State private var viewModel: AnalyticsViewModel
    @State private var query = "SELECT * FROM data LIMIT 100"

    var body: some View {
        VSplitView {
            // Query editor
            TextEditor(text: $query)
                .font(.system(.body, design: .monospaced))
                .frame(minHeight: 100)

            // Results
            if viewModel.isLoading {
                ProgressView()
            } else if let error = viewModel.error {
                Text(error.localizedDescription)
                    .foregroundStyle(.red)
            } else {
                ResultsTableView(results: viewModel.results)
            }
        }
        .toolbar {
            Button("Run") {
                Task {
                    await viewModel.executeQuery(query)
                }
            }
            .keyboardShortcut(.return, modifiers: .command)
        }
    }
}
```

## Analytical Queries

### Window Functions

```swift
let result = try connection.query("""
    SELECT
        date,
        value,
        AVG(value) OVER (
            ORDER BY date
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        ) as moving_avg_7d
    FROM time_series
""")
```

### Common Table Expressions

```swift
let result = try connection.query("""
    WITH daily_totals AS (
        SELECT
            DATE_TRUNC('day', timestamp) as day,
            SUM(amount) as total
        FROM transactions
        GROUP BY 1
    ),
    running_totals AS (
        SELECT
            day,
            total,
            SUM(total) OVER (ORDER BY day) as cumulative
        FROM daily_totals
    )
    SELECT * FROM running_totals
""")
```

### Aggregations

```swift
let result = try connection.query("""
    SELECT
        category,
        COUNT(*) as count,
        AVG(price) as avg_price,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY price) as median_price,
        STDDEV(price) as price_stddev
    FROM products
    GROUP BY category
    HAVING COUNT(*) > 10
    ORDER BY avg_price DESC
""")
```

## Performance Tips

1. **Use Parquet for large datasets** - Columnar format with compression
2. **Filter pushdown** - WHERE clauses evaluated early
3. **Projection pushdown** - Select only needed columns
4. **Parallel execution** - DuckDB uses all cores automatically
5. **Memory management** - Use `.file()` store for large datasets

## Integration with TabularData

```swift
import TabularData

extension DataFrame {
    init(duckDBResult: ResultSet) {
        var columns: [AnyColumn] = []

        for (index, column) in duckDBResult.columns.enumerated() {
            switch column.type {
            case .integer:
                let values = duckDBResult.map { $0[index] as Int64? }
                columns.append(Column<Int64?>(name: column.name, contents: values).eraseToAnyColumn())
            case .varchar:
                let values = duckDBResult.map { $0[index] as String? }
                columns.append(Column<String?>(name: column.name, contents: values).eraseToAnyColumn())
            case .double:
                let values = duckDBResult.map { $0[index] as Double? }
                columns.append(Column<Double?>(name: column.name, contents: values).eraseToAnyColumn())
            default:
                break
            }
        }

        self.init(columns: columns)
    }
}
```

## Related Skills

- swift-charts: Visualizing DuckDB results
- swiftui-architecture: Data flow patterns
- grdb-swift: Alternative SQLite approach
