---
name: swift-charts
description: Building data visualizations in SwiftUI using Apple's Swift Charts framework
tags: [swift, swiftui, charts, data-visualization, ios]
---

# Swift Charts

## Purpose

Building data visualizations in SwiftUI using Apple's Swift Charts framework.

## Basic Charts

### Line Chart

```swift
import Charts
import SwiftUI

struct TimeSeriesView: View {
    let data: [DataPoint]

    var body: some View {
        Chart(data) { point in
            LineMark(
                x: .value("Date", point.date),
                y: .value("Value", point.value)
            )
        }
        .chartXAxis {
            AxisMarks(values: .stride(by: .month)) { value in
                AxisValueLabel(format: .dateTime.month(.abbreviated))
            }
        }
    }
}
```

### Bar Chart

```swift
struct CategoryChart: View {
    let sales: [CategorySales]

    var body: some View {
        Chart(sales) { item in
            BarMark(
                x: .value("Category", item.category),
                y: .value("Sales", item.amount)
            )
            .foregroundStyle(by: .value("Category", item.category))
        }
        .chartLegend(.hidden)
    }
}
```

### Scatter Plot

```swift
struct ScatterView: View {
    let points: [Observation]

    var body: some View {
        Chart(points) { point in
            PointMark(
                x: .value("X", point.x),
                y: .value("Y", point.y)
            )
            .foregroundStyle(by: .value("Cluster", point.cluster))
            .symbolSize(point.weight * 10)
        }
    }
}
```

### Area Chart

```swift
struct StackedAreaChart: View {
    let data: [CategoryTimeSeries]

    var body: some View {
        Chart(data) { series in
            ForEach(series.values) { point in
                AreaMark(
                    x: .value("Date", point.date),
                    y: .value("Value", point.value)
                )
            }
            .foregroundStyle(by: .value("Category", series.category))
        }
        .chartForegroundStyleScale([
            "Sales": .blue,
            "Expenses": .red,
            "Profit": .green
        ])
    }
}
```

## Advanced Marks

### Combined Marks

```swift
struct CombinedChart: View {
    let data: [DataPoint]

    var body: some View {
        Chart(data) { point in
            // Line for trend
            LineMark(
                x: .value("Date", point.date),
                y: .value("Value", point.value)
            )
            .foregroundStyle(.blue)

            // Points for individual values
            PointMark(
                x: .value("Date", point.date),
                y: .value("Value", point.value)
            )
            .foregroundStyle(.blue)

            // Rule for average
            RuleMark(y: .value("Average", average))
                .foregroundStyle(.red.opacity(0.5))
                .lineStyle(StrokeStyle(dash: [5, 5]))
        }
    }

    var average: Double {
        data.map(\.value).reduce(0, +) / Double(data.count)
    }
}
```

### Range Marks

```swift
struct RangeChart: View {
    let data: [RangeData]

    var body: some View {
        Chart(data) { item in
            // Show range
            RectangleMark(
                x: .value("Category", item.category),
                yStart: .value("Min", item.min),
                yEnd: .value("Max", item.max)
            )
            .opacity(0.3)

            // Show median
            PointMark(
                x: .value("Category", item.category),
                y: .value("Median", item.median)
            )
        }
    }
}
```

## Interactivity

### Selection

```swift
struct InteractiveChart: View {
    let data: [DataPoint]
    @State private var selectedDate: Date?

    var body: some View {
        Chart(data) { point in
            LineMark(
                x: .value("Date", point.date),
                y: .value("Value", point.value)
            )

            if let selected = selectedDate,
               let point = data.first(where: { Calendar.current.isDate($0.date, inSameDayAs: selected) }) {
                RuleMark(x: .value("Selected", point.date))
                    .foregroundStyle(.gray.opacity(0.3))

                PointMark(
                    x: .value("Date", point.date),
                    y: .value("Value", point.value)
                )
                .foregroundStyle(.red)
                .symbolSize(100)
            }
        }
        .chartXSelection(value: $selectedDate)
        .chartOverlay { proxy in
            GeometryReader { geometry in
                if let selected = selectedDate,
                   let point = data.first(where: { Calendar.current.isDate($0.date, inSameDayAs: selected) }),
                   let position = proxy.position(forX: point.date) {
                    VStack {
                        Text(point.date, format: .dateTime.month().day())
                        Text(point.value, format: .number)
                            .bold()
                    }
                    .padding(8)
                    .background(.ultraThinMaterial)
                    .cornerRadius(8)
                    .position(x: position, y: 20)
                }
            }
        }
    }
}
```

### Scrolling Charts

```swift
struct ScrollableChart: View {
    let data: [DataPoint]
    @State private var scrollPosition: Date = .now

    var body: some View {
        Chart(data) { point in
            LineMark(
                x: .value("Date", point.date),
                y: .value("Value", point.value)
            )
        }
        .chartScrollableAxes(.horizontal)
        .chartXVisibleDomain(length: 3600 * 24 * 30) // 30 days
        .chartScrollPosition(x: $scrollPosition)
    }
}
```

## Styling

### Custom Colors

```swift
Chart(data) { point in
    BarMark(
        x: .value("Category", point.category),
        y: .value("Value", point.value)
    )
    .foregroundStyle(by: .value("Category", point.category))
}
.chartForegroundStyleScale([
    "Category A": Color.blue,
    "Category B": Color.green,
    "Category C": Color.orange
])
```

### Axis Customization

```swift
Chart(data) { point in
    LineMark(
        x: .value("Date", point.date),
        y: .value("Value", point.value)
    )
}
.chartXAxis {
    AxisMarks(preset: .aligned) { value in
        AxisGridLine()
        AxisTick()
        AxisValueLabel(format: .dateTime.month())
    }
}
.chartYAxis {
    AxisMarks(position: .leading) { value in
        AxisGridLine()
        AxisValueLabel {
            if let intValue = value.as(Int.self) {
                Text("$\(intValue)")
            }
        }
    }
}
```

### Plot Area Styling

```swift
Chart(data) { point in
    LineMark(
        x: .value("X", point.x),
        y: .value("Y", point.y)
    )
}
.chartPlotStyle { plotArea in
    plotArea
        .background(.gray.opacity(0.1))
        .border(.gray, width: 1)
}
```

## Performance (Large Datasets)

### Vectorized Plots (WWDC24)

```swift
// For datasets > 1000 points
struct LargeDatasetChart: View {
    let points: [Point]  // Thousands of points

    var body: some View {
        Chart {
            PointPlot(points, x: \.x, y: \.y)
                .foregroundStyle(.blue)
        }
    }
}
```

### Data Aggregation

```swift
struct AggregatedChart: View {
    let rawData: [DataPoint]

    var aggregatedData: [DataPoint] {
        // Aggregate to reasonable number of points
        Dictionary(grouping: rawData) { point in
            Calendar.current.startOfDay(for: point.date)
        }
        .map { date, points in
            DataPoint(
                date: date,
                value: points.map(\.value).reduce(0, +) / Double(points.count)
            )
        }
        .sorted(by: { $0.date < $1.date })
    }

    var body: some View {
        Chart(aggregatedData) { point in
            LineMark(
                x: .value("Date", point.date),
                y: .value("Value", point.value)
            )
        }
    }
}
```

## Chart3D (macOS 26+ / iOS 20+)

```swift
import Charts

struct Scatter3DView: View {
    let points: [Point3D]

    var body: some View {
        Chart3D(points) { point in
            PointMark3D(
                x: .value("X", point.x),
                y: .value("Y", point.y),
                z: .value("Z", point.z)
            )
            .foregroundStyle(by: .value("Cluster", point.cluster))
        }
        .chart3DStyle(.interactive) // Allows rotation
    }
}
```

## Common Patterns

### Empty State

```swift
struct ChartWithEmptyState: View {
    let data: [DataPoint]

    var body: some View {
        if data.isEmpty {
            ContentUnavailableView(
                "No Data",
                systemImage: "chart.bar.xaxis",
                description: Text("Add some data to see the chart")
            )
        } else {
            Chart(data) { point in
                LineMark(
                    x: .value("Date", point.date),
                    y: .value("Value", point.value)
                )
            }
        }
    }
}
```

### Loading State

```swift
struct ChartWithLoading: View {
    let data: [DataPoint]?
    let isLoading: Bool

    var body: some View {
        ZStack {
            if let data {
                Chart(data) { point in
                    LineMark(
                        x: .value("Date", point.date),
                        y: .value("Value", point.value)
                    )
                }
            }

            if isLoading {
                ProgressView()
            }
        }
    }
}
```

## Related Skills

- duckdb-swift: Data source for charts
- swiftui-data-flow: Reactive chart updates
- grape-graphs: Force-directed graph visualization
