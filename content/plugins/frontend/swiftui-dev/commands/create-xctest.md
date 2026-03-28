# Create XCTest

Generate an XCTest unit test file with proper setup and patterns.

## Arguments

- `<name>` - Test target name (e.g., `ItemViewModel` creates `ItemViewModelTests`)
- `--path <path>` - Target directory (default: Tests/)
- `--async` - Include async test patterns
- `--mock <name>` - Generate mock for dependency

## Output

Creates `<Name>Tests.swift` with:

- XCTestCase subclass
- setUp/tearDown
- Test method templates
- Mock objects if specified

## Template

```swift
import XCTest
@testable import MyApp

final class <Name>Tests: XCTestCase {
    // MARK: - Properties

    var sut: <Name>!

    // MARK: - Lifecycle

    override func setUp() {
        super.setUp()
        sut = <Name>()
    }

    override func tearDown() {
        sut = nil
        super.tearDown()
    }

    // MARK: - Tests

    func test_<scenario>_<expectedBehavior>() {
        // Given

        // When

        // Then
    }
}
```

## Examples

```bash
# Basic test file
/create-xctest ItemViewModel

# Async tests
/create-xctest DataService --async

# With mock generation
/create-xctest ItemViewModel --mock ItemRepository

# In specific path
/create-xctest ItemViewModel --path Tests/ViewModelTests
```

## Generated Patterns

### Standard Test

```swift
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
        mockRepository.items = [Item(id: "1", name: "Test")]

        // When
        await sut.loadItems()

        // Then
        XCTAssertEqual(sut.items.count, 1)
        XCTAssertFalse(sut.isLoading)
    }

    func test_loadItems_failure_setsError() async {
        // Given
        mockRepository.shouldFail = true

        // When
        await sut.loadItems()

        // Then
        XCTAssertNotNil(sut.error)
        XCTAssertTrue(sut.items.isEmpty)
    }
}
```

### Mock Generation

```swift
final class MockItemRepository: ItemRepository {
    var items: [Item] = []
    var shouldFail = false

    func fetchAll() async throws -> [Item] {
        if shouldFail {
            throw NSError(domain: "Test", code: -1)
        }
        return items
    }

    func save(_ item: Item) async throws {
        items.append(item)
    }

    func delete(_ item: Item) async throws {
        items.removeAll { $0.id == item.id }
    }
}
```

## Naming Convention

Tests follow: `test_<methodOrScenario>_<expectedBehavior>()`

- `test_init_setsDefaultValues()`
- `test_loadItems_success_populatesItems()`
- `test_loadItems_failure_setsError()`
- `test_deleteItem_removesFromList()`
