---
name: lang-swift-dev
description: Foundational Swift development patterns covering modern Swift syntax, SwiftUI, protocol-oriented programming, and Cocoa Touch frameworks. Use when writing Swift code, building iOS/macOS/watchOS/tvOS applications, working with SwiftUI or UIKit, understanding Swift concurrency, or needing guidance on Swift project structure.
---

# Swift Development Fundamentals

Foundational Swift patterns and modern language features for Apple platform development. This skill covers core Swift syntax, SwiftUI, UIKit integration, and protocol-oriented design patterns.

## Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                   Swift Development Ecosystem                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│                    ┌──────────────────┐                         │
│                    │  lang-swift-dev  │ ◄── You are here        │
│                    │   (foundation)   │                         │
│                    └────────┬─────────┘                         │
│                             │                                   │
│         ┌───────────────────┼───────────────────┐               │
│         │                   │                   │               │
│         ▼                   ▼                   ▼               │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │   SwiftUI   │    │    UIKit    │    │   Swift     │         │
│  │ Mastery     │    │  Advanced   │    │  Package    │         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**This skill covers:**
- Core Swift syntax (optionals, closures, generics, protocols)
- SwiftUI basics (views, state management, modifiers)
- Protocol-oriented programming patterns
- Swift concurrency (async/await, actors, tasks)
- UIKit fundamentals and integration
- Xcode project structure and organization

**This skill does NOT cover:**
- Advanced SwiftUI architecture - see `swiftui-patterns-advanced`
- Complex UIKit patterns - see `uikit-advanced-patterns`
- Swift Package Manager publishing - see `swift-package-dev`
- iOS app distribution and App Store submission
- Combine framework (prefer Swift concurrency for new code)

---

## Quick Reference

| Task | Pattern |
|------|---------|
| Define optional | `var name: String?` |
| Unwrap safely | `if let name = name { }` |
| Guard unwrap | `guard let name = name else { return }` |
| Define protocol | `protocol Named { var name: String { get } }` |
| Conform to protocol | `extension MyType: Named { }` |
| Async function | `func fetch() async throws -> Data` |
| Call async | `let data = try await fetch()` |
| SwiftUI view | `struct ContentView: View { var body: some View { } }` |
| State variable | `@State private var count = 0` |

---

## Core Swift Patterns

### Optionals and Unwrapping

```swift
// Optional declaration
var username: String?
var age: Int? = nil

// Safe unwrapping with if let
if let username = username {
    print("Hello, \(username)")
} else {
    print("No username set")
}

// Guard for early exit
func greet(name: String?) {
    guard let name = name else {
        print("Name required")
        return
    }
    print("Hello, \(name)")
}

// Nil coalescing
let displayName = username ?? "Guest"

// Optional chaining
let uppercased = username?.uppercased()

// Force unwrap (use sparingly!)
let name = username!  // Crashes if nil
```

### Closures

```swift
// Basic closure
let multiply = { (a: Int, b: Int) -> Int in
    return a * b
}

// Type inference
let add = { a, b in a + b }

// Trailing closure syntax
[1, 2, 3].map { number in
    number * 2
}

// Shorthand argument names
[1, 2, 3].map { $0 * 2 }

// Capturing values
func makeIncrementer(amount: Int) -> () -> Int {
    var total = 0
    return {
        total += amount
        return total
    }
}

let incrementByTwo = makeIncrementer(amount: 2)
print(incrementByTwo())  // 2
print(incrementByTwo())  // 4

// Escaping closures (stored beyond function scope)
func fetchData(completion: @escaping (Result<Data, Error>) -> Void) {
    DispatchQueue.main.asyncAfter(deadline: .now() + 1) {
        completion(.success(Data()))
    }
}
```

### Protocols and Protocol-Oriented Programming

```swift
// Define a protocol
protocol Drawable {
    func draw()
}

protocol Identifiable {
    var id: String { get }
}

// Conform to protocols
struct Circle: Drawable {
    func draw() {
        print("Drawing circle")
    }
}

// Protocol composition
struct User: Identifiable, Codable {
    let id: String
    let name: String
}

// Protocol extensions (add default implementations)
extension Drawable {
    func draw() {
        print("Default drawing")
    }

    func render() {
        print("Rendering...")
        draw()
    }
}

// Protocol with associated types
protocol Container {
    associatedtype Item
    var items: [Item] { get }
    mutating func add(_ item: Item)
}

struct IntStack: Container {
    typealias Item = Int
    var items: [Int] = []

    mutating func add(_ item: Int) {
        items.append(item)
    }
}
```

### Generics

```swift
// Generic function
func swap<T>(_ a: inout T, _ b: inout T) {
    let temp = a
    a = b
    b = temp
}

// Generic type
struct Stack<Element> {
    private var items: [Element] = []

    mutating func push(_ item: Element) {
        items.append(item)
    }

    mutating func pop() -> Element? {
        return items.popLast()
    }
}

// Generic constraints
func findIndex<T: Equatable>(of value: T, in array: [T]) -> Int? {
    for (index, element) in array.enumerated() {
        if element == value {
            return index
        }
    }
    return nil
}

// Where clauses
func allItemsMatch<C1: Container, C2: Container>(
    _ container1: C1,
    _ container2: C2
) -> Bool where C1.Item == C2.Item, C1.Item: Equatable {
    guard container1.items.count == container2.items.count else {
        return false
    }
    return zip(container1.items, container2.items).allSatisfy { $0 == $1 }
}
```

### Enums and Pattern Matching

```swift
// Simple enum
enum Direction {
    case north, south, east, west
}

// Enum with associated values
enum Result<Success, Failure: Error> {
    case success(Success)
    case failure(Failure)
}

// Enum with raw values
enum HTTPStatus: Int {
    case ok = 200
    case notFound = 404
    case serverError = 500
}

// Pattern matching
let result: Result<String, Error> = .success("Data")

switch result {
case .success(let value):
    print("Success: \(value)")
case .failure(let error):
    print("Error: \(error)")
}

// If case pattern matching
if case .success(let value) = result {
    print("Got value: \(value)")
}

// Recursive enums
indirect enum Expression {
    case number(Int)
    case addition(Expression, Expression)
    case multiplication(Expression, Expression)
}
```

### Property Wrappers

```swift
// Built-in property wrappers
@State private var count = 0
@Published var username = ""
@Environment(\.colorScheme) var colorScheme

// Custom property wrapper
@propertyWrapper
struct Clamped<Value: Comparable> {
    private var value: Value
    private let range: ClosedRange<Value>

    var wrappedValue: Value {
        get { value }
        set { value = min(max(newValue, range.lowerBound), range.upperBound) }
    }

    init(wrappedValue: Value, _ range: ClosedRange<Value>) {
        self.range = range
        self.value = min(max(wrappedValue, range.lowerBound), range.upperBound)
    }
}

// Usage
struct Game {
    @Clamped(0...100) var health = 100
}

var game = Game()
game.health = 150  // Clamped to 100
game.health = -10  // Clamped to 0
```

---

## Swift Concurrency

### Async/Await

```swift
// Define async function
func fetchUser(id: String) async throws -> User {
    let url = URL(string: "https://api.example.com/users/\(id)")!
    let (data, _) = try await URLSession.shared.data(from: url)
    return try JSONDecoder().decode(User.self, from: data)
}

// Call async function
Task {
    do {
        let user = try await fetchUser(id: "123")
        print("Fetched user: \(user.name)")
    } catch {
        print("Error: \(error)")
    }
}

// Async let (parallel execution)
func loadData() async throws -> (User, [Post]) {
    async let user = fetchUser(id: "123")
    async let posts = fetchPosts(userId: "123")
    return try await (user, posts)
}

// Async sequences
func processLines(url: URL) async throws {
    for try await line in url.lines {
        print("Line: \(line)")
    }
}
```

### Actors

```swift
// Actor for thread-safe state
actor BankAccount {
    private var balance: Double = 0

    func deposit(amount: Double) {
        balance += amount
    }

    func withdraw(amount: Double) -> Bool {
        guard balance >= amount else {
            return false
        }
        balance -= amount
        return true
    }

    func getBalance() -> Double {
        return balance
    }
}

// Usage (automatically synchronized)
let account = BankAccount()

Task {
    await account.deposit(amount: 100)
    let balance = await account.getBalance()
    print("Balance: \(balance)")
}
```

### Tasks and Task Groups

```swift
// Detached task
Task.detached {
    await performBackgroundWork()
}

// Task group (structured concurrency)
func fetchAllUsers() async throws -> [User] {
    try await withThrowingTaskGroup(of: User.self) { group in
        for id in 1...10 {
            group.addTask {
                try await fetchUser(id: String(id))
            }
        }

        var users: [User] = []
        for try await user in group {
            users.append(user)
        }
        return users
    }
}

// Task cancellation
let task = Task {
    for i in 1...100 {
        if Task.isCancelled {
            print("Task cancelled at \(i)")
            return
        }
        await doWork(i)
    }
}

// Cancel after delay
Task {
    try await Task.sleep(nanoseconds: 1_000_000_000)
    task.cancel()
}
```

---

## SwiftUI Fundamentals

### View Basics

```swift
import SwiftUI

struct ContentView: View {
    var body: some View {
        VStack(spacing: 20) {
            Text("Hello, World!")
                .font(.largeTitle)
                .foregroundColor(.blue)

            Image(systemName: "star.fill")
                .font(.system(size: 50))

            Button("Tap Me") {
                print("Button tapped")
            }
        }
        .padding()
    }
}
```

### State Management

```swift
struct CounterView: View {
    // State for view-local data
    @State private var count = 0

    var body: some View {
        VStack {
            Text("Count: \(count)")
                .font(.largeTitle)

            Button("Increment") {
                count += 1
            }
        }
    }
}

// ObservableObject for shared state
class UserViewModel: ObservableObject {
    @Published var username = ""
    @Published var isLoggedIn = false

    func login() {
        // Perform login
        isLoggedIn = true
    }
}

struct LoginView: View {
    @StateObject private var viewModel = UserViewModel()

    var body: some View {
        VStack {
            TextField("Username", text: $viewModel.username)
                .textFieldStyle(.roundedBorder)

            Button("Login") {
                viewModel.login()
            }

            if viewModel.isLoggedIn {
                Text("Welcome, \(viewModel.username)!")
            }
        }
        .padding()
    }
}

// Environment values
struct ThemedView: View {
    @Environment(\.colorScheme) var colorScheme

    var body: some View {
        Text("Theme: \(colorScheme == .dark ? "Dark" : "Light")")
    }
}
```

### Lists and Navigation

```swift
struct Item: Identifiable {
    let id = UUID()
    let title: String
}

struct ItemListView: View {
    let items = [
        Item(title: "First"),
        Item(title: "Second"),
        Item(title: "Third")
    ]

    var body: some View {
        NavigationView {
            List(items) { item in
                NavigationLink(destination: DetailView(item: item)) {
                    Text(item.title)
                }
            }
            .navigationTitle("Items")
        }
    }
}

struct DetailView: View {
    let item: Item

    var body: some View {
        Text("Detail for \(item.title)")
            .navigationTitle(item.title)
    }
}
```

### Custom Modifiers and ViewBuilder

```swift
// Custom view modifier
struct CardModifier: ViewModifier {
    func body(content: Content) -> some View {
        content
            .padding()
            .background(Color.white)
            .cornerRadius(10)
            .shadow(radius: 5)
    }
}

extension View {
    func cardStyle() -> some View {
        modifier(CardModifier())
    }
}

// ViewBuilder pattern
@ViewBuilder
func conditionalView(showText: Bool) -> some View {
    if showText {
        Text("Visible")
    } else {
        Image(systemName: "eye.slash")
    }
}
```

---

## UIKit Integration

### UIKit in SwiftUI (UIViewRepresentable)

```swift
import UIKit
import SwiftUI

struct TextView: UIViewRepresentable {
    @Binding var text: String

    func makeUIView(context: Context) -> UITextView {
        let textView = UITextView()
        textView.delegate = context.coordinator
        return textView
    }

    func updateUIView(_ uiView: UITextView, context: Context) {
        uiView.text = text
    }

    func makeCoordinator() -> Coordinator {
        Coordinator(text: $text)
    }

    class Coordinator: NSObject, UITextViewDelegate {
        @Binding var text: String

        init(text: Binding<String>) {
            _text = text
        }

        func textViewDidChange(_ textView: UITextView) {
            text = textView.text
        }
    }
}
```

### SwiftUI in UIKit (UIHostingController)

```swift
import UIKit
import SwiftUI

class ViewController: UIViewController {
    override func viewDidLoad() {
        super.viewDidLoad()

        // Embed SwiftUI view in UIKit
        let swiftUIView = ContentView()
        let hostingController = UIHostingController(rootView: swiftUIView)

        addChild(hostingController)
        view.addSubview(hostingController.view)
        hostingController.view.frame = view.bounds
        hostingController.didMove(toParent: self)
    }
}
```

### Basic UIKit Patterns

```swift
// UIViewController lifecycle
class MyViewController: UIViewController {
    override func viewDidLoad() {
        super.viewDidLoad()
        // Setup after view loads
    }

    override func viewWillAppear(_ animated: Bool) {
        super.viewWillAppear(animated)
        // Before view appears
    }

    override func viewDidAppear(_ animated: Bool) {
        super.viewDidAppear(animated)
        // After view appears
    }
}

// Delegation pattern
protocol DataSourceDelegate: AnyObject {
    func didReceiveData(_ data: String)
}

class DataSource {
    weak var delegate: DataSourceDelegate?

    func fetchData() {
        // Fetch data
        delegate?.didReceiveData("Data")
    }
}
```

---

## Project Structure

### Swift Package Structure

```
MyPackage/
├── Package.swift
├── Sources/
│   └── MyPackage/
│       ├── MyPackage.swift
│       └── Models/
│           └── User.swift
├── Tests/
│   └── MyPackageTests/
│       └── MyPackageTests.swift
└── README.md
```

### iOS App Structure

```
MyApp/
├── MyApp/
│   ├── App/
│   │   ├── MyAppApp.swift
│   │   └── ContentView.swift
│   ├── Models/
│   │   └── User.swift
│   ├── Views/
│   │   ├── HomeView.swift
│   │   └── DetailView.swift
│   ├── ViewModels/
│   │   └── UserViewModel.swift
│   ├── Services/
│   │   └── NetworkService.swift
│   ├── Resources/
│   │   └── Assets.xcassets
│   └── Supporting Files/
│       └── Info.plist
└── MyAppTests/
    └── MyAppTests.swift
```

### Package.swift Example

```swift
// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "MyPackage",
    platforms: [
        .iOS(.v16),
        .macOS(.v13)
    ],
    products: [
        .library(
            name: "MyPackage",
            targets: ["MyPackage"]
        ),
    ],
    dependencies: [
        .package(url: "https://github.com/example/package.git", from: "1.0.0"),
    ],
    targets: [
        .target(
            name: "MyPackage",
            dependencies: []
        ),
        .testTarget(
            name: "MyPackageTests",
            dependencies: ["MyPackage"]
        ),
    ]
)
```

---

## Common Idioms

### Result Builders

```swift
@resultBuilder
struct StringBuilder {
    static func buildBlock(_ components: String...) -> String {
        components.joined(separator: " ")
    }
}

@StringBuilder
func makeGreeting() -> String {
    "Hello"
    "World"
    "from"
    "Swift"
}

print(makeGreeting())  // "Hello World from Swift"
```

### Codable for JSON

```swift
struct User: Codable {
    let id: Int
    let name: String
    let email: String

    // Custom coding keys
    enum CodingKeys: String, CodingKey {
        case id
        case name
        case email = "email_address"
    }
}

// Decode JSON
let json = """
{
    "id": 1,
    "name": "John",
    "email_address": "john@example.com"
}
""".data(using: .utf8)!

let user = try JSONDecoder().decode(User.self, from: json)

// Encode to JSON
let data = try JSONEncoder().encode(user)
```

### Error Handling

```swift
enum NetworkError: Error {
    case invalidURL
    case noData
    case decodingFailed
}

func fetchData(from urlString: String) throws -> Data {
    guard let url = URL(string: urlString) else {
        throw NetworkError.invalidURL
    }

    // Fetch data...
    guard let data = try? Data(contentsOf: url) else {
        throw NetworkError.noData
    }

    return data
}

// Using do-catch
do {
    let data = try fetchData(from: "https://api.example.com")
    print("Fetched \(data.count) bytes")
} catch NetworkError.invalidURL {
    print("Invalid URL")
} catch {
    print("Error: \(error)")
}
```

---

## Troubleshooting

### Optional Unwrapping Crashes

**Problem:** `Fatal error: Unexpectedly found nil while unwrapping an Optional value`

```swift
// Bad: Force unwrapping
let name = user.name!  // Crashes if nil

// Good: Safe unwrapping
if let name = user.name {
    print(name)
}

// Or: Guard
guard let name = user.name else {
    return
}
```

### Retain Cycles in Closures

**Problem:** Memory leaks from strong reference cycles

```swift
// Bad: Strong reference to self
class ViewController {
    var completion: (() -> Void)?

    func setup() {
        completion = {
            self.doSomething()  // Strong reference cycle
        }
    }
}

// Good: Weak or unowned self
class ViewController {
    var completion: (() -> Void)?

    func setup() {
        completion = { [weak self] in
            self?.doSomething()
        }
    }
}
```

### SwiftUI View Not Updating

**Problem:** View doesn't update when data changes

```swift
// Bad: No property wrapper
class ViewModel {
    var count = 0  // Changes won't trigger updates
}

// Good: Use @Published in ObservableObject
class ViewModel: ObservableObject {
    @Published var count = 0
}

struct ContentView: View {
    @StateObject var viewModel = ViewModel()

    var body: some View {
        Text("Count: \(viewModel.count)")
    }
}
```

### Actor Reentrancy Issues

**Problem:** Unexpected state changes in async actor methods

```swift
actor Counter {
    private var value = 0

    // Potential reentrancy issue
    func increment() async {
        await Task.sleep(1_000_000_000)
        value += 1  // Value might have changed during await
    }

    // Better: Check state after await
    func safeIncrement() async -> Int {
        let currentValue = value
        await Task.sleep(1_000_000_000)
        value = currentValue + 1
        return value
    }
}
```

---

## References

- [Swift Language Guide](https://docs.swift.org/swift-book/LanguageGuide/TheBasics.html)
- [SwiftUI Tutorials](https://developer.apple.com/tutorials/swiftui)
- [Swift Evolution Proposals](https://github.com/apple/swift-evolution)
- [WWDC Videos](https://developer.apple.com/videos/)
- [Swift by Sundell](https://www.swiftbysundell.com/)
- [Hacking with Swift](https://www.hackingwithswift.com/)
