---
name: lang-java-dev
description: Foundational Java patterns covering core syntax, object-oriented programming, generics, collections, streams, lambdas, and modern Java features. Use when writing Java code, understanding the type system, working with collections/streams, or needing guidance on which specialized Java skill to use. This is the entry point for Java development.
---

# Java Fundamentals

Foundational Java patterns and core language features. This skill serves as both a reference for common patterns and an index to specialized Java skills.

## Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                      Java Skill Hierarchy                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│                    ┌───────────────────┐                        │
│                    │   lang-java-dev   │ ◄── You are here       │
│                    │   (foundation)    │                        │
│                    └─────────┬─────────┘                        │
│                              │                                  │
│     ┌────────────┬───────────┼───────────┬────────────┐        │
│     │            │           │           │            │        │
│     ▼            ▼           ▼           ▼            ▼        │
│ ┌────────┐ ┌──────────┐ ┌────────┐ ┌─────────┐ ┌──────────┐   │
│ │patterns│ │  spring  │ │library │ │  build  │ │   test   │   │
│ │  -dev  │ │   -dev   │ │  -dev  │ │  -dev   │ │   -dev   │   │
│ └────────┘ └──────────┘ └────────┘ └─────────┘ └──────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**This skill covers:**
- Core syntax (classes, interfaces, enums, records)
- Object-oriented programming (inheritance, polymorphism, encapsulation)
- Generics fundamentals
- Collections framework
- Stream API and lambda expressions
- Exception handling
- Modern Java features (records, sealed classes, pattern matching)

**This skill does NOT cover (see specialized skills):**
- Design patterns and best practices → `lang-java-patterns-dev`
- Spring framework → `lang-java-spring-dev`
- Library/package publishing → `lang-java-library-dev`
- Build tools (Maven, Gradle) → `lang-java-build-dev`
- Testing frameworks (JUnit, TestNG) → `lang-java-test-dev`

---

## Quick Reference

| Task | Pattern |
|------|---------|
| Create class | `class Name { }` |
| Create interface | `interface Name { void method(); }` |
| Create enum | `enum Status { PENDING, APPROVED }` |
| Create record | `record Point(int x, int y) {}` |
| Implement interface | `class Impl implements Interface { }` |
| Extend class | `class Child extends Parent { }` |
| Generic class | `class Box<T> { }` |
| Lambda expression | `(x, y) -> x + y` |
| Stream operation | `list.stream().filter(...).map(...)` |
| Exception handling | `try { } catch (Exception e) { }` |

---

## Skill Routing

Use this table to find the right specialized skill:

| When you need to... | Use this skill |
|---------------------|----------------|
| Apply design patterns, SOLID principles | `lang-java-patterns-dev` |
| Build Spring Boot applications | `lang-java-spring-dev` |
| Publish JARs, Maven artifacts | `lang-java-library-dev` |
| Configure Maven or Gradle | `lang-java-build-dev` |
| Write unit tests, integration tests | `lang-java-test-dev` |

---

## Core Types and Classes

### Classes

```java
// Basic class
public class User {
    // Instance variables (fields)
    private String name;
    private int age;

    // Constructor
    public User(String name, int age) {
        this.name = name;
        this.age = age;
    }

    // Getters and setters
    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    // Instance method
    public void greet() {
        System.out.println("Hello, I'm " + name);
    }

    // Static method
    public static User createDefault() {
        return new User("Anonymous", 0);
    }
}

// Usage
User user = new User("Alice", 30);
user.greet();
```

### Interfaces

```java
// Interface definition
public interface Drawable {
    // Abstract method (implicitly public abstract)
    void draw();

    // Default method (Java 8+)
    default void render() {
        System.out.println("Rendering...");
        draw();
    }

    // Static method (Java 8+)
    static void info() {
        System.out.println("Drawable interface");
    }

    // Private method (Java 9+) - helper for default methods
    private void log(String message) {
        System.out.println("LOG: " + message);
    }
}

// Implementation
public class Circle implements Drawable {
    @Override
    public void draw() {
        System.out.println("Drawing circle");
    }
}

// Multiple interfaces
public class Shape implements Drawable, Comparable<Shape> {
    @Override
    public void draw() { }

    @Override
    public int compareTo(Shape other) {
        return 0;
    }
}
```

### Abstract Classes

```java
public abstract class Animal {
    private String name;

    public Animal(String name) {
        this.name = name;
    }

    // Abstract method - must be implemented by subclasses
    public abstract void makeSound();

    // Concrete method - inherited by subclasses
    public void sleep() {
        System.out.println(name + " is sleeping");
    }
}

public class Dog extends Animal {
    public Dog(String name) {
        super(name);
    }

    @Override
    public void makeSound() {
        System.out.println("Woof!");
    }
}
```

### Enums

```java
// Simple enum
public enum Status {
    PENDING,
    APPROVED,
    REJECTED
}

// Enum with fields and methods
public enum Planet {
    MERCURY(3.303e+23, 2.4397e6),
    VENUS(4.869e+24, 6.0518e6),
    EARTH(5.976e+24, 6.37814e6);

    private final double mass;
    private final double radius;

    Planet(double mass, double radius) {
        this.mass = mass;
        this.radius = radius;
    }

    public double getMass() {
        return mass;
    }

    public double surfaceGravity() {
        return 6.67300E-11 * mass / (radius * radius);
    }
}

// Enum with abstract methods
public enum Operation {
    PLUS {
        public double apply(double x, double y) { return x + y; }
    },
    MINUS {
        public double apply(double x, double y) { return x - y; }
    };

    public abstract double apply(double x, double y);
}
```

### Records (Java 14+)

```java
// Immutable data carrier
public record Point(int x, int y) {}

// Usage
Point p = new Point(10, 20);
System.out.println(p.x());  // Auto-generated accessor
System.out.println(p);       // Auto-generated toString()

// Record with custom methods
public record Person(String name, int age) {
    // Compact constructor for validation
    public Person {
        if (age < 0) {
            throw new IllegalArgumentException("Age cannot be negative");
        }
    }

    // Additional methods
    public boolean isAdult() {
        return age >= 18;
    }
}

// Record with static factory
public record Range(int start, int end) {
    public static Range of(int start, int end) {
        if (start > end) {
            throw new IllegalArgumentException("Invalid range");
        }
        return new Range(start, end);
    }
}
```

### Sealed Classes (Java 17+)

```java
// Sealed class restricts which classes can extend it
public sealed class Shape
    permits Circle, Rectangle, Triangle {
}

public final class Circle extends Shape {
    private final double radius;

    public Circle(double radius) {
        this.radius = radius;
    }
}

public final class Rectangle extends Shape {
    private final double width, height;

    public Rectangle(double width, double height) {
        this.width = width;
        this.height = height;
    }
}

public non-sealed class Triangle extends Shape {
    // non-sealed allows further extension
}
```

---

## Generics

### Generic Classes

```java
// Basic generic class
public class Box<T> {
    private T value;

    public void set(T value) {
        this.value = value;
    }

    public T get() {
        return value;
    }
}

// Usage
Box<String> stringBox = new Box<>();
stringBox.set("Hello");
String value = stringBox.get();

// Multiple type parameters
public class Pair<K, V> {
    private K key;
    private V value;

    public Pair(K key, V value) {
        this.key = key;
        this.value = value;
    }

    public K getKey() { return key; }
    public V getValue() { return value; }
}
```

### Generic Methods

```java
// Generic method
public static <T> T getFirst(List<T> list) {
    if (list.isEmpty()) {
        return null;
    }
    return list.get(0);
}

// Usage - type inference
List<String> names = List.of("Alice", "Bob");
String first = getFirst(names);

// Multiple type parameters
public static <K, V> Pair<K, V> makePair(K key, V value) {
    return new Pair<>(key, value);
}
```

### Bounded Type Parameters

```java
// Upper bound (extends)
public static <T extends Comparable<T>> T max(T a, T b) {
    return a.compareTo(b) > 0 ? a : b;
}

// Multiple bounds
public static <T extends Number & Comparable<T>> void process(T value) {
    // T must be a Number AND implement Comparable
}

// Lower bound (in wildcards)
public static void addNumbers(List<? super Integer> list) {
    list.add(1);
    list.add(2);
    // Can add Integer or its subtypes
}

// Upper bound wildcard
public static double sum(List<? extends Number> list) {
    double sum = 0;
    for (Number num : list) {
        sum += num.doubleValue();
    }
    return sum;
}
```

### Type Erasure and Raw Types

```java
// Type information is erased at runtime
Box<String> stringBox = new Box<>();
Box<Integer> intBox = new Box<>();
// At runtime, both are just Box

// Cannot do:
// new T()  - type parameter instantiation
// T.class  - class literal
// instanceof T  - instance check

// Raw types (avoid - legacy compatibility only)
Box rawBox = new Box();  // Warning: unchecked
```

---

## Collections Framework

### List Interface

```java
// ArrayList - dynamic array
List<String> arrayList = new ArrayList<>();
arrayList.add("Apple");
arrayList.add("Banana");
arrayList.get(0);  // "Apple"

// LinkedList - doubly-linked list
List<String> linkedList = new LinkedList<>();
linkedList.addFirst("First");
linkedList.addLast("Last");

// Immutable lists (Java 9+)
List<String> immutable = List.of("A", "B", "C");
// immutable.add("D");  // UnsupportedOperationException

// Common operations
list.size();
list.isEmpty();
list.contains("Apple");
list.remove("Banana");
list.clear();
```

### Set Interface

```java
// HashSet - unordered, no duplicates
Set<String> hashSet = new HashSet<>();
hashSet.add("Apple");
hashSet.add("Banana");
hashSet.add("Apple");  // Ignored - duplicate
// Size is 2

// TreeSet - sorted, no duplicates
Set<Integer> treeSet = new TreeSet<>();
treeSet.add(5);
treeSet.add(1);
treeSet.add(3);
// Iteration order: 1, 3, 5

// LinkedHashSet - insertion order, no duplicates
Set<String> linkedSet = new LinkedHashSet<>();

// Immutable sets (Java 9+)
Set<String> immutable = Set.of("A", "B", "C");
```

### Map Interface

```java
// HashMap - unordered key-value pairs
Map<String, Integer> hashMap = new HashMap<>();
hashMap.put("Alice", 30);
hashMap.put("Bob", 25);
int age = hashMap.get("Alice");  // 30

// TreeMap - sorted by keys
Map<String, Integer> treeMap = new TreeMap<>();

// LinkedHashMap - insertion order
Map<String, Integer> linkedMap = new LinkedHashMap<>();

// Immutable maps (Java 9+)
Map<String, Integer> immutable = Map.of(
    "Alice", 30,
    "Bob", 25
);

// Common operations
map.containsKey("Alice");
map.containsValue(30);
map.remove("Bob");
map.getOrDefault("Charlie", 0);
map.putIfAbsent("David", 35);

// Iteration
for (Map.Entry<String, Integer> entry : map.entrySet()) {
    String key = entry.getKey();
    Integer value = entry.getValue();
}

// Java 8+ forEach
map.forEach((key, value) ->
    System.out.println(key + ": " + value)
);
```

### Queue and Deque

```java
// Queue - FIFO
Queue<String> queue = new LinkedList<>();
queue.offer("First");   // Add to end
queue.offer("Second");
String head = queue.poll();  // Remove from front
String peek = queue.peek();  // View front without removing

// Deque - double-ended queue
Deque<String> deque = new ArrayDeque<>();
deque.addFirst("Front");
deque.addLast("Back");
String first = deque.removeFirst();
String last = deque.removeLast();

// Stack operations (use Deque instead of Stack class)
Deque<String> stack = new ArrayDeque<>();
stack.push("Bottom");
stack.push("Top");
String top = stack.pop();
```

---

## Stream API

### Creating Streams

```java
// From collection
List<String> list = List.of("A", "B", "C");
Stream<String> stream = list.stream();

// From array
String[] array = {"A", "B", "C"};
Stream<String> stream = Arrays.stream(array);

// Using Stream.of
Stream<String> stream = Stream.of("A", "B", "C");

// Infinite streams
Stream<Integer> infinite = Stream.iterate(0, n -> n + 1);
Stream<Double> random = Stream.generate(Math::random);

// Range
IntStream.range(1, 10);        // 1 to 9
IntStream.rangeClosed(1, 10);  // 1 to 10
```

### Intermediate Operations

```java
List<String> names = List.of("Alice", "Bob", "Charlie", "David");

// filter - keep matching elements
List<String> filtered = names.stream()
    .filter(name -> name.length() > 3)
    .collect(Collectors.toList());

// map - transform elements
List<Integer> lengths = names.stream()
    .map(String::length)
    .collect(Collectors.toList());

// flatMap - flatten nested structures
List<List<String>> nested = List.of(
    List.of("A", "B"),
    List.of("C", "D")
);
List<String> flat = nested.stream()
    .flatMap(List::stream)
    .collect(Collectors.toList());

// distinct - remove duplicates
List<Integer> unique = Stream.of(1, 2, 2, 3, 3, 3)
    .distinct()
    .collect(Collectors.toList());

// sorted - sort elements
List<String> sorted = names.stream()
    .sorted()
    .collect(Collectors.toList());

// sorted with comparator
List<String> sortedByLength = names.stream()
    .sorted(Comparator.comparing(String::length))
    .collect(Collectors.toList());

// limit - take first n elements
List<String> limited = names.stream()
    .limit(2)
    .collect(Collectors.toList());

// skip - skip first n elements
List<String> skipped = names.stream()
    .skip(2)
    .collect(Collectors.toList());

// peek - perform action without modifying stream
names.stream()
    .peek(System.out::println)
    .map(String::toUpperCase)
    .collect(Collectors.toList());
```

### Terminal Operations

```java
List<Integer> numbers = List.of(1, 2, 3, 4, 5);

// collect - gather into collection
List<Integer> list = numbers.stream().collect(Collectors.toList());
Set<Integer> set = numbers.stream().collect(Collectors.toSet());

// forEach - perform action on each element
numbers.stream().forEach(System.out::println);

// reduce - combine elements
int sum = numbers.stream().reduce(0, Integer::sum);
Optional<Integer> max = numbers.stream().reduce(Integer::max);

// count - count elements
long count = numbers.stream().count();

// anyMatch, allMatch, noneMatch
boolean hasEven = numbers.stream().anyMatch(n -> n % 2 == 0);
boolean allPositive = numbers.stream().allMatch(n -> n > 0);
boolean noNegative = numbers.stream().noneMatch(n -> n < 0);

// findFirst, findAny
Optional<Integer> first = numbers.stream().findFirst();
Optional<Integer> any = numbers.stream().findAny();

// min, max
Optional<Integer> min = numbers.stream().min(Integer::compare);
Optional<Integer> max = numbers.stream().max(Integer::compare);
```

### Collectors

```java
List<String> names = List.of("Alice", "Bob", "Charlie");

// toList, toSet
List<String> list = names.stream().collect(Collectors.toList());
Set<String> set = names.stream().collect(Collectors.toSet());

// toMap
Map<String, Integer> nameToLength = names.stream()
    .collect(Collectors.toMap(
        name -> name,
        String::length
    ));

// groupingBy
Map<Integer, List<String>> byLength = names.stream()
    .collect(Collectors.groupingBy(String::length));

// partitioningBy
Map<Boolean, List<String>> partition = names.stream()
    .collect(Collectors.partitioningBy(name -> name.length() > 3));

// joining
String joined = names.stream()
    .collect(Collectors.joining(", "));

// summarizing
IntSummaryStatistics stats = names.stream()
    .collect(Collectors.summarizingInt(String::length));
```

---

## Lambda Expressions and Method References

### Lambda Syntax

```java
// No parameters
Runnable r = () -> System.out.println("Hello");

// One parameter (parentheses optional)
Consumer<String> c = s -> System.out.println(s);
Consumer<String> c2 = (s) -> System.out.println(s);

// Multiple parameters
BiFunction<Integer, Integer, Integer> add = (a, b) -> a + b;

// Block body
Predicate<String> isEmpty = s -> {
    return s.isEmpty();
};

// Type declarations (optional)
BiFunction<Integer, Integer, Integer> add2 =
    (Integer a, Integer b) -> a + b;
```

### Functional Interfaces

```java
// Built-in functional interfaces

// Predicate<T> - boolean test
Predicate<String> isEmpty = String::isEmpty;
Predicate<Integer> isEven = n -> n % 2 == 0;

// Function<T, R> - transform T to R
Function<String, Integer> length = String::length;
Function<Integer, String> toString = Object::toString;

// Consumer<T> - consume T, return nothing
Consumer<String> print = System.out::println;

// Supplier<T> - supply T, no input
Supplier<String> supplier = () -> "Hello";

// BiFunction<T, U, R> - two inputs
BiFunction<Integer, Integer, Integer> add = (a, b) -> a + b;

// BiConsumer<T, U> - two inputs, no output
BiConsumer<String, Integer> printWithCount =
    (s, n) -> System.out.println(s + ": " + n);

// UnaryOperator<T> - T -> T
UnaryOperator<Integer> square = n -> n * n;

// BinaryOperator<T> - (T, T) -> T
BinaryOperator<Integer> max = Integer::max;
```

### Method References

```java
// Static method reference
Function<String, Integer> parseInt = Integer::parseInt;

// Instance method reference (bound)
String str = "Hello";
Supplier<Integer> length = str::length;

// Instance method reference (unbound)
Function<String, Integer> length2 = String::length;

// Constructor reference
Supplier<List<String>> listSupplier = ArrayList::new;
Function<String, User> userFactory = User::new;

// Array constructor reference
IntFunction<int[]> arrayMaker = int[]::new;
```

---

## Exception Handling

### Try-Catch-Finally

```java
// Basic try-catch
try {
    int result = divide(10, 0);
} catch (ArithmeticException e) {
    System.err.println("Cannot divide by zero: " + e.getMessage());
}

// Multiple catch blocks
try {
    String text = readFile("data.txt");
    int number = Integer.parseInt(text);
} catch (IOException e) {
    System.err.println("File error: " + e.getMessage());
} catch (NumberFormatException e) {
    System.err.println("Parse error: " + e.getMessage());
}

// Multi-catch (Java 7+)
try {
    // risky operation
} catch (IOException | SQLException e) {
    System.err.println("Error: " + e.getMessage());
}

// Finally block - always executes
try {
    openConnection();
    processData();
} catch (Exception e) {
    handleError(e);
} finally {
    closeConnection();  // Always runs
}
```

### Try-with-Resources

```java
// Automatic resource management (Java 7+)
try (BufferedReader reader = new BufferedReader(new FileReader("file.txt"))) {
    String line = reader.readLine();
    // reader is automatically closed
} catch (IOException e) {
    e.printStackTrace();
}

// Multiple resources
try (FileInputStream in = new FileInputStream("input.txt");
     FileOutputStream out = new FileOutputStream("output.txt")) {
    // Both streams automatically closed
} catch (IOException e) {
    e.printStackTrace();
}

// Java 9+ - resources declared outside
BufferedReader reader = new BufferedReader(new FileReader("file.txt"));
try (reader) {
    // Use reader
}
```

### Checked vs Unchecked Exceptions

```java
// Checked exceptions - must be handled or declared
public void readFile(String path) throws IOException {
    FileReader reader = new FileReader(path);
    // Must declare throws or wrap in try-catch
}

// Unchecked exceptions - optional handling
public void divide(int a, int b) {
    int result = a / b;  // May throw ArithmeticException
    // No need to declare or catch
}

// Common checked exceptions:
// - IOException
// - SQLException
// - ClassNotFoundException

// Common unchecked exceptions:
// - NullPointerException
// - IllegalArgumentException
// - IllegalStateException
// - IndexOutOfBoundsException
```

### Custom Exceptions

```java
// Custom checked exception
public class ValidationException extends Exception {
    public ValidationException(String message) {
        super(message);
    }

    public ValidationException(String message, Throwable cause) {
        super(message, cause);
    }
}

// Custom unchecked exception
public class InvalidConfigException extends RuntimeException {
    public InvalidConfigException(String message) {
        super(message);
    }
}

// Usage
public void validate(String input) throws ValidationException {
    if (input == null || input.isEmpty()) {
        throw new ValidationException("Input cannot be empty");
    }
}
```

---

## Pattern Matching (Java 16+)

### Pattern Matching for instanceof

```java
// Old way
if (obj instanceof String) {
    String str = (String) obj;
    System.out.println(str.length());
}

// Pattern matching (Java 16+)
if (obj instanceof String str) {
    System.out.println(str.length());
}

// With negation
if (!(obj instanceof String str)) {
    return;
}
System.out.println(str.length());

// In complex conditions
if (obj instanceof String str && str.length() > 5) {
    System.out.println("Long string: " + str);
}
```

### Switch Expressions (Java 14+)

```java
// Traditional switch
int numLetters;
switch (day) {
    case MONDAY:
    case FRIDAY:
    case SUNDAY:
        numLetters = 6;
        break;
    case TUESDAY:
        numLetters = 7;
        break;
    default:
        numLetters = 0;
}

// Switch expression
int numLetters = switch (day) {
    case MONDAY, FRIDAY, SUNDAY -> 6;
    case TUESDAY -> 7;
    case THURSDAY, SATURDAY -> 8;
    case WEDNESDAY -> 9;
};

// With yield for blocks
String result = switch (day) {
    case MONDAY, TUESDAY -> {
        System.out.println("Weekday");
        yield "Work";
    }
    case SATURDAY, SUNDAY -> {
        System.out.println("Weekend");
        yield "Rest";
    }
    default -> "Unknown";
};
```

### Pattern Matching for Switch (Java 21+)

```java
// Type patterns in switch
static String format(Object obj) {
    return switch (obj) {
        case Integer i -> "Integer: " + i;
        case String s -> "String: " + s;
        case null -> "null";
        default -> "Unknown";
    };
}

// With guards
static String describe(Object obj) {
    return switch (obj) {
        case String s when s.length() > 10 -> "Long string";
        case String s -> "Short string: " + s;
        case Integer i when i > 100 -> "Large number";
        case Integer i -> "Small number: " + i;
        default -> "Other";
    };
}

// Record patterns
record Point(int x, int y) {}

static void printPoint(Object obj) {
    if (obj instanceof Point(int x, int y)) {
        System.out.println("Point at " + x + ", " + y);
    }
}
```

---

## Common Patterns

### Builder Pattern

```java
public class User {
    private final String name;
    private final String email;
    private final int age;

    private User(Builder builder) {
        this.name = builder.name;
        this.email = builder.email;
        this.age = builder.age;
    }

    public static class Builder {
        private String name;
        private String email;
        private int age;

        public Builder name(String name) {
            this.name = name;
            return this;
        }

        public Builder email(String email) {
            this.email = email;
            return this;
        }

        public Builder age(int age) {
            this.age = age;
            return this;
        }

        public User build() {
            return new User(this);
        }
    }
}

// Usage
User user = new User.Builder()
    .name("Alice")
    .email("alice@example.com")
    .age(30)
    .build();
```

### Optional Pattern

```java
// Creating Optional
Optional<String> optional = Optional.of("value");
Optional<String> nullable = Optional.ofNullable(getValue());
Optional<String> empty = Optional.empty();

// Using Optional
optional.ifPresent(System.out::println);

String value = optional.orElse("default");
String value2 = optional.orElseGet(() -> getDefault());
String value3 = optional.orElseThrow(() -> new IllegalStateException());

// Transforming
Optional<Integer> length = optional.map(String::length);
Optional<String> upper = optional
    .filter(s -> s.length() > 5)
    .map(String::toUpperCase);

// Java 9+ - or(), ifPresentOrElse(), stream()
Optional<String> result = optional.or(() -> getAlternative());

optional.ifPresentOrElse(
    System.out::println,
    () -> System.out.println("Empty")
);
```

### Factory Methods

```java
public class User {
    private String name;
    private int age;

    private User(String name, int age) {
        this.name = name;
        this.age = age;
    }

    // Factory method
    public static User create(String name, int age) {
        if (age < 0) {
            throw new IllegalArgumentException("Age cannot be negative");
        }
        return new User(name, age);
    }

    // Named factory methods
    public static User createChild(String name) {
        return new User(name, 0);
    }

    public static User createAdult(String name, int age) {
        if (age < 18) {
            throw new IllegalArgumentException("Must be 18 or older");
        }
        return new User(name, age);
    }
}
```

---

## Troubleshooting

### NullPointerException

**Problem:** Accessing methods/fields on null references

```java
String str = null;
int length = str.length();  // NullPointerException
```

**Fix:** Use null checks or Optional

```java
// Null check
if (str != null) {
    int length = str.length();
}

// Optional
Optional<String> opt = Optional.ofNullable(str);
opt.ifPresent(s -> System.out.println(s.length()));
```

### ClassCastException

**Problem:** Invalid type casting

```java
Object obj = "Hello";
Integer num = (Integer) obj;  // ClassCastException
```

**Fix:** Use instanceof before casting

```java
if (obj instanceof Integer) {
    Integer num = (Integer) obj;
}

// Or pattern matching (Java 16+)
if (obj instanceof Integer num) {
    System.out.println(num);
}
```

### ConcurrentModificationException

**Problem:** Modifying collection while iterating

```java
List<String> list = new ArrayList<>(List.of("A", "B", "C"));
for (String item : list) {
    list.remove(item);  // ConcurrentModificationException
}
```

**Fix:** Use iterator's remove or collect to new list

```java
// Use iterator
Iterator<String> it = list.iterator();
while (it.hasNext()) {
    String item = it.next();
    it.remove();
}

// Or create new list
List<String> filtered = list.stream()
    .filter(item -> !item.equals("B"))
    .collect(Collectors.toList());
```

### Generic Type Erasure Issues

**Problem:** Cannot create generic array or use instanceof with generics

```java
// T[] array = new T[10];  // Error
// if (obj instanceof List<String>) {}  // Error
```

**Fix:** Use List instead of array, or unchecked cast with warning

```java
// Use List
List<T> list = new ArrayList<>();

// Or use Array.newInstance
@SuppressWarnings("unchecked")
T[] array = (T[]) Array.newInstance(componentType, size);
```

---

## References

- [Java Documentation](https://docs.oracle.com/en/java/)
- [Java Tutorial](https://docs.oracle.com/javase/tutorial/)
- [Java Language Specification](https://docs.oracle.com/javase/specs/)
- Specialized skills: `lang-java-patterns-dev`, `lang-java-spring-dev`, `lang-java-library-dev`, `lang-java-build-dev`, `lang-java-test-dev`
