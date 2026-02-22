# SwiftUI Testing

## Purpose

Testing strategies for SwiftUI applications including unit tests, UI tests, and preview-based testing.

## XCTest Unit Testing

### Testing ViewModels

```swift
import XCTest
@testable import MyApp

final class ItemViewModelTests: XCTestCase {
    var sut: ItemViewModel!
    var mockRepository: MockItemRepository!

    override func setUp() {
        super.setUp()
        mockRepository = MockItemRepository()
        sut = ItemViewModel(repository: mockRepository)
    }

    override func tearDown() {
        sut = nil
        mockRepository = nil
        super.tearDown()
    }

    func test_loadItems_success_populatesItems() async {
        // Given
        let expectedItems = [Item(id: "1", name: "Test")]
        mockRepository.items = expectedItems

        // When
        await sut.loadItems()

        // Then
        XCTAssertEqual(sut.items, expectedItems)
        XCTAssertFalse(sut.isLoading)
        XCTAssertNil(sut.errorMessage)
    }

    func test_loadItems_failure_setsError() async {
        // Given
        mockRepository.shouldFail = true

        // When
        await sut.loadItems()

        // Then
        XCTAssertTrue(sut.items.isEmpty)
        XCTAssertNotNil(sut.errorMessage)
    }
}
```

### Testing @Observable Classes

```swift
import XCTest
@testable import MyApp

final class ShoppingCartTests: XCTestCase {
    func test_addProduct_increasesQuantity() {
        // Given
        let cart = ShoppingCart()
        let product = Product(id: "1", name: "Widget", price: 9.99)

        // When
        cart.add(product)
        cart.add(product)

        // Then
        XCTAssertEqual(cart.items.count, 1)
        XCTAssertEqual(cart.items.first?.quantity, 2)
    }

    func test_total_calculatesCorrectly() {
        // Given
        let cart = ShoppingCart()
        cart.items = [
            CartItem(productId: "1", price: 10.00, quantity: 2),
            CartItem(productId: "2", price: 5.00, quantity: 1)
        ]

        // Then
        XCTAssertEqual(cart.total, 25.00)
    }
}
```

### Testing Async Code

```swift
func test_fetchData_withCancellation() async {
    // Given
    let viewModel = DataViewModel()
    let task = Task {
        await viewModel.fetchData()
    }

    // When
    task.cancel()
    await task.value

    // Then
    XCTAssertTrue(Task.isCancelled)
}

func test_fetchData_withTimeout() async throws {
    // Given
    let viewModel = SlowViewModel()

    // When/Then - should complete within 5 seconds
    try await withTimeout(seconds: 5) {
        await viewModel.fetchData()
    }
}

// Helper
func withTimeout<T>(seconds: Double, operation: @escaping () async throws -> T) async throws -> T {
    try await withThrowingTaskGroup(of: T.self) { group in
        group.addTask {
            try await operation()
        }
        group.addTask {
            try await Task.sleep(for: .seconds(seconds))
            throw TimeoutError()
        }
        let result = try await group.next()!
        group.cancelAll()
        return result
    }
}
```

## XCUITest UI Testing

### Basic UI Test Structure

```swift
import XCTest

final class ItemListUITests: XCTestCase {
    var app: XCUIApplication!

    override func setUp() {
        super.setUp()
        continueAfterFailure = false
        app = XCUIApplication()
        app.launchArguments = ["--uitesting"]
        app.launch()
    }

    func test_addItem_appearsInList() {
        // Given
        let addButton = app.buttons["addItemButton"]
        let nameField = app.textFields["itemNameField"]
        let saveButton = app.buttons["saveButton"]

        // When
        addButton.tap()
        nameField.tap()
        nameField.typeText("New Item")
        saveButton.tap()

        // Then
        let newItem = app.staticTexts["New Item"]
        XCTAssertTrue(newItem.waitForExistence(timeout: 2))
    }
}
```

### Page Object Pattern

```swift
// Page object for Item List screen
struct ItemListPage {
    let app: XCUIApplication

    var addButton: XCUIElement {
        app.buttons["addItemButton"]
    }

    var itemList: XCUIElement {
        app.collectionViews["itemList"]
    }

    func item(named name: String) -> XCUIElement {
        app.staticTexts[name]
    }

    func tapAdd() -> AddItemPage {
        addButton.tap()
        return AddItemPage(app: app)
    }

    func waitForItems() {
        _ = itemList.waitForExistence(timeout: 5)
    }
}

// Page object for Add Item screen
struct AddItemPage {
    let app: XCUIApplication

    var nameField: XCUIElement {
        app.textFields["itemNameField"]
    }

    var saveButton: XCUIElement {
        app.buttons["saveButton"]
    }

    func enterName(_ name: String) -> Self {
        nameField.tap()
        nameField.typeText(name)
        return self
    }

    func save() -> ItemListPage {
        saveButton.tap()
        return ItemListPage(app: app)
    }
}

// Usage in test
func test_addItem_pageObject() {
    let listPage = ItemListPage(app: app)
    listPage.waitForItems()

    let result = listPage
        .tapAdd()
        .enterName("New Item")
        .save()

    XCTAssertTrue(result.item(named: "New Item").exists)
}
```

### Accessibility Identifiers

```swift
// In SwiftUI View
struct ItemRow: View {
    let item: Item

    var body: some View {
        HStack {
            Text(item.name)
            Spacer()
            Button("Delete") {
                // delete action
            }
            .accessibilityIdentifier("deleteButton-\(item.id)")
        }
        .accessibilityIdentifier("itemRow-\(item.id)")
    }
}

// In UI Test
func test_deleteItem() {
    let deleteButton = app.buttons["deleteButton-item123"]
    deleteButton.tap()

    let itemRow = app.otherElements["itemRow-item123"]
    XCTAssertFalse(itemRow.exists)
}
```

## ViewInspector Testing

```swift
import XCTest
import ViewInspector
@testable import MyApp

extension ItemRow: Inspectable {}

final class ItemRowTests: XCTestCase {
    func test_displaysItemName() throws {
        // Given
        let item = Item(id: "1", name: "Test Item")
        let view = ItemRow(item: item)

        // When
        let text = try view.inspect().find(text: "Test Item")

        // Then
        XCTAssertNotNil(text)
    }

    func test_deleteButton_callsOnDelete() throws {
        // Given
        var deleteCalled = false
        let item = Item(id: "1", name: "Test")
        let view = ItemRow(item: item, onDelete: { deleteCalled = true })

        // When
        try view.inspect().find(button: "Delete").tap()

        // Then
        XCTAssertTrue(deleteCalled)
    }
}
```

## Snapshot Testing

```swift
import XCTest
import SnapshotTesting
@testable import MyApp

final class ItemRowSnapshotTests: XCTestCase {
    func test_itemRow_lightMode() {
        let view = ItemRow(item: .preview)
            .frame(width: 300)
            .environment(\.colorScheme, .light)

        assertSnapshot(of: view, as: .image)
    }

    func test_itemRow_darkMode() {
        let view = ItemRow(item: .preview)
            .frame(width: 300)
            .environment(\.colorScheme, .dark)

        assertSnapshot(of: view, as: .image)
    }

    func test_itemRow_dynamicType() {
        for category in [ContentSizeCategory.extraSmall, .large, .accessibilityExtraExtraLarge] {
            let view = ItemRow(item: .preview)
                .frame(width: 300)
                .environment(\.sizeCategory, category)

            assertSnapshot(of: view, as: .image, named: "\(category)")
        }
    }
}
```

## Preview-Based Testing

```swift
// Sample data for previews
extension Item {
    static var preview: Item {
        Item(id: "preview", name: "Preview Item", description: "A sample item")
    }

    static var previews: [Item] {
        [
            Item(id: "1", name: "First Item"),
            Item(id: "2", name: "Second Item"),
            Item(id: "3", name: "Third Item with a very long name that might wrap")
        ]
    }
}

// Comprehensive preview
#Preview("Item Row - Standard") {
    ItemRow(item: .preview)
}

#Preview("Item Row - Long Name") {
    ItemRow(item: Item(id: "1", name: "This is a very long item name"))
}

#Preview("Item Row - Dark Mode") {
    ItemRow(item: .preview)
        .preferredColorScheme(.dark)
}

#Preview("Item List - Multiple") {
    List(Item.previews) { item in
        ItemRow(item: item)
    }
}
```

## Test Organization

```text
Tests/
├── UnitTests/
│   ├── ViewModels/
│   │   └── ItemViewModelTests.swift
│   ├── Models/
│   │   └── ItemTests.swift
│   └── Services/
│       └── ItemRepositoryTests.swift
├── UITests/
│   ├── Pages/
│   │   ├── ItemListPage.swift
│   │   └── AddItemPage.swift
│   └── Flows/
│       └── ItemManagementTests.swift
└── SnapshotTests/
    └── ItemRowSnapshotTests.swift
```

## Best Practices

1. **Test ViewModels, not Views** - Business logic testing
2. **Use dependency injection** - Enable mocking
3. **Use accessibility identifiers** - Stable UI test selectors
4. **Page object pattern** - Maintainable UI tests
5. **Snapshot for visual regression** - Catch unintended changes

## Related Skills

- xctest-patterns: Advanced XCTest patterns
- swiftui-architecture: Testable architecture
