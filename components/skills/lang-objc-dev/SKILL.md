---
name: lang-objc-dev
description: Foundational Objective-C patterns covering classes, protocols, categories, memory management (ARC/retain-release), blocks, GCD, and Foundation framework. Use when writing Objective-C code, working with Cocoa/Cocoa Touch APIs, bridging to Swift, or needing guidance on Apple platform development patterns. This is the entry point for Objective-C development.
---

# Objective-C Fundamentals

Foundational Objective-C patterns and core language features. This skill serves as both a reference for common patterns and an index to specialized Objective-C skills.

## Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                  Objective-C Skill Hierarchy                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│                  ┌─────────────────────┐                        │
│                  │   lang-objc-dev     │ ◄── You are here       │
│                  │   (foundation)      │                        │
│                  └──────────┬──────────┘                        │
│                             │                                   │
│            ┌────────────────┼────────────────┐                  │
│            │                │                │                  │
│            ▼                ▼                ▼                  │
│    ┌──────────────┐  ┌──────────┐   ┌──────────────┐          │
│    │   patterns   │  │ library  │   │    swift     │          │
│    │     -dev     │  │   -dev   │   │   -bridge    │          │
│    └──────────────┘  └──────────┘   └──────────────┘          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**This skill covers:**
- Class declaration and implementation
- Protocols (formal and informal)
- Categories and extensions
- Memory management (ARC, retain/release cycles)
- Properties and accessors
- Blocks and closures
- Grand Central Dispatch (GCD) basics
- Foundation framework essentials
- Common Objective-C idioms

**This skill does NOT cover (see specialized skills):**
- Advanced design patterns → `lang-objc-patterns-dev`
- Framework/library development → `lang-objc-library-dev`
- Swift/Objective-C interoperability → `lang-swift-objc-bridge-dev`
- iOS/macOS UI development → platform-specific skills
- Core Data patterns → `ios-coredata-dev`

---

## Quick Reference

| Task | Syntax |
|------|--------|
| Declare class | `@interface ClassName : Superclass` |
| Define method | `- (ReturnType)methodName:(Type)param` |
| Class method | `+ (ReturnType)methodName` |
| Property | `@property (attributes) Type *name;` |
| Protocol | `@protocol ProtocolName` |
| Category | `@interface ClassName (CategoryName)` |
| Block type | `ReturnType (^blockName)(ParamTypes)` |
| Strong reference | `@property (strong) Type *obj;` |
| Weak reference | `@property (weak) Type *obj;` |
| Copy property | `@property (copy) NSString *str;` |

---

## Skill Routing

Use this table to find the right specialized skill:

| When you need to... | Use this skill |
|---------------------|----------------|
| Implement MVC, Singleton, Delegate patterns | `lang-objc-patterns-dev` |
| Build reusable frameworks, static libraries | `lang-objc-library-dev` |
| Bridge Objective-C code to Swift | `lang-swift-objc-bridge-dev` |
| Work with UIKit/AppKit | Platform-specific UI skills |
| Implement Core Data models | `ios-coredata-dev` |

---

## Classes and Objects

### Class Declaration

```objc
// Header file (.h)
#import <Foundation/Foundation.h>

@interface Person : NSObject

// Properties
@property (nonatomic, strong) NSString *name;
@property (nonatomic, assign) NSInteger age;

// Instance methods
- (instancetype)initWithName:(NSString *)name age:(NSInteger)age;
- (void)greet;
- (NSString *)description;

// Class methods
+ (instancetype)personWithName:(NSString *)name age:(NSInteger)age;

@end
```

### Class Implementation

```objc
// Implementation file (.m)
#import "Person.h"

@implementation Person

- (instancetype)initWithName:(NSString *)name age:(NSInteger)age {
    self = [super init];
    if (self) {
        _name = name;
        _age = age;
    }
    return self;
}

+ (instancetype)personWithName:(NSString *)name age:(NSInteger)age {
    return [[self alloc] initWithName:name age:age];
}

- (void)greet {
    NSLog(@"Hello, my name is %@", self.name);
}

- (NSString *)description {
    return [NSString stringWithFormat:@"Person(name: %@, age: %ld)",
            self.name, (long)self.age];
}

@end
```

### Creating Instances

```objc
// Using designated initializer
Person *person1 = [[Person alloc] initWithName:@"Alice" age:30];

// Using convenience class method
Person *person2 = [Person personWithName:@"Bob" age:25];

// Calling methods
[person1 greet];
NSLog(@"%@", person1.description);

// Accessing properties
NSString *name = person1.name;
person1.age = 31;
```

---

## Properties and Accessors

### Property Attributes

```objc
@interface User : NSObject

// Memory management
@property (strong) NSObject *strongRef;      // Retains object (default)
@property (weak) id<Delegate> delegate;      // Weak reference, no retain
@property (assign) NSInteger count;          // Simple assignment (scalars)
@property (copy) NSString *username;         // Creates copy on assignment

// Atomicity
@property (atomic) NSString *threadSafe;     // Thread-safe (default, slower)
@property (nonatomic) NSString *fast;        // Not thread-safe (faster)

// Read/write
@property (readonly) NSString *identifier;   // No setter generated
@property (readwrite) NSString *editable;    // Both getter/setter (default)

// Custom accessors
@property (getter=isEnabled) BOOL enabled;   // Custom getter name
@property (setter=setCustomValue:) id value; // Custom setter name

@end
```

### Custom Getters and Setters

```objc
@implementation User {
    NSString *_computedProperty;
}

// Custom getter
- (NSString *)computedProperty {
    if (!_computedProperty) {
        _computedProperty = [self calculateValue];
    }
    return _computedProperty;
}

// Custom setter with validation
- (void)setUsername:(NSString *)username {
    if (username.length > 0) {
        _username = [username copy];
    }
}

@end
```

### Property Synthesis

```objc
@implementation User

// Automatic synthesis (Xcode does this automatically)
// @synthesize username = _username;

// Manual backing variable name
@synthesize customName = _backingVariable;

// Dynamic property (implemented at runtime)
@dynamic runtimeProperty;

@end
```

---

## Protocols

### Defining Protocols

```objc
// Formal protocol
@protocol Drawable <NSObject>

@required  // Must be implemented
- (void)draw;
- (CGRect)bounds;

@optional  // Can be implemented
- (void)setColor:(UIColor *)color;
- (UIColor *)color;

@end
```

### Adopting Protocols

```objc
// Header: Adopt protocol
@interface Circle : NSObject <Drawable>
@property (nonatomic, assign) CGFloat radius;
@end

// Implementation
@implementation Circle

- (void)draw {
    // Drawing implementation
    NSLog(@"Drawing circle with radius %f", self.radius);
}

- (CGRect)bounds {
    return CGRectMake(0, 0, self.radius * 2, self.radius * 2);
}

// Optional method
- (void)setColor:(UIColor *)color {
    // Optional color implementation
}

@end
```

### Protocol Types and Conformance

```objc
// Variable can hold any object conforming to Drawable
id<Drawable> drawable = [[Circle alloc] init];

// Check protocol conformance
if ([object conformsToProtocol:@protocol(Drawable)]) {
    [(id<Drawable>)object draw];
}

// Check if optional method is implemented
if ([drawable respondsToSelector:@selector(setColor:)]) {
    [drawable setColor:[UIColor blueColor]];
}
```

### Multiple Protocol Adoption

```objc
@interface AdvancedShape : NSObject <Drawable, Serializable, Comparable>
@end
```

---

## Categories and Extensions

### Categories (Public)

```objc
// Header: NSString+Validation.h
@interface NSString (Validation)
- (BOOL)isValidEmail;
- (BOOL)isValidURL;
@end

// Implementation: NSString+Validation.m
@implementation NSString (Validation)

- (BOOL)isValidEmail {
    NSString *pattern = @"[A-Z0-9a-z._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}";
    NSPredicate *predicate = [NSPredicate predicateWithFormat:@"SELF MATCHES %@", pattern];
    return [predicate evaluateWithObject:self];
}

- (BOOL)isValidURL {
    return [NSURL URLWithString:self] != nil;
}

@end

// Usage
#import "NSString+Validation.h"
NSString *email = @"user@example.com";
if ([email isValidEmail]) {
    NSLog(@"Valid email");
}
```

### Class Extensions (Private)

```objc
// Class extension in .m file (private interface)
@interface Person ()
// Private properties
@property (nonatomic, strong) NSMutableArray *privateData;

// Private methods
- (void)internalMethod;
@end

@implementation Person

- (void)internalMethod {
    // Implementation only visible in this file
}

@end
```

### Categories with Properties

```objc
#import <objc/runtime.h>

@interface UIView (CustomTag)
@property (nonatomic, strong) NSString *customTag;
@end

@implementation UIView (CustomTag)

static char kCustomTagKey;

- (void)setCustomTag:(NSString *)customTag {
    objc_setAssociatedObject(self, &kCustomTagKey, customTag,
                            OBJC_ASSOCIATION_RETAIN_NONATOMIC);
}

- (NSString *)customTag {
    return objc_getAssociatedObject(self, &kCustomTagKey);
}

@end
```

---

## Memory Management

### ARC (Automatic Reference Counting)

```objc
// Strong reference (default for objects)
@property (strong) NSString *name;  // Keeps object alive

// Weak reference (doesn't prevent deallocation)
@property (weak) id<Delegate> delegate;  // Becomes nil when deallocated

// Unretained (like weak but doesn't nil out)
@property (unsafe_unretained) id observer;  // Dangerous: can dangle

// Copy (for immutable/mutable pairs)
@property (copy) NSString *title;  // Always creates immutable copy
```

### Retain Cycles and Solutions

```objc
// PROBLEM: Retain cycle
@interface Parent : NSObject
@property (strong) Child *child;
@end

@interface Child : NSObject
@property (strong) Parent *parent;  // Creates cycle!
@end

// SOLUTION 1: Weak reference
@interface Child : NSObject
@property (weak) Parent *parent;  // Breaks cycle
@end

// SOLUTION 2: Block retain cycles
@interface MyClass : NSObject
@property (copy) void (^completion)(void);
@end

@implementation MyClass

- (void)setupCompletion {
    // WRONG: Captures self strongly
    self.completion = ^{
        [self doSomething];  // Retain cycle!
    };

    // CORRECT: Use weak-strong dance
    __weak typeof(self) weakSelf = self;
    self.completion = ^{
        __strong typeof(weakSelf) strongSelf = weakSelf;
        if (strongSelf) {
            [strongSelf doSomething];
        }
    };
}

@end
```

### Manual Memory Management (Pre-ARC)

```objc
// Only relevant for legacy code or when ARC is disabled

// Ownership rules (retain, release, autorelease)
- (void)legacyMemoryManagement {
    // alloc/init creates object with retain count 1
    NSString *owned = [[NSString alloc] initWithString:@"owned"];

    // retain increases retain count
    [owned retain];

    // release decreases retain count
    [owned release];
    [owned release];  // Final release, object deallocated

    // autorelease defers release until later
    NSString *temp = [[[NSString alloc] init] autorelease];

    // copy creates new object with retain count 1
    NSString *copied = [owned copy];
    [copied release];
}

// dealloc method
- (void)dealloc {
    [_property release];
    [super dealloc];  // Required in MRC
}
```

---

## Blocks (Closures)

### Block Syntax

```objc
// Block type definition
typedef void (^CompletionBlock)(BOOL success, NSError *error);
typedef NSInteger (^MathBlock)(NSInteger a, NSInteger b);

// Block variable
CompletionBlock completion = ^(BOOL success, NSError *error) {
    if (success) {
        NSLog(@"Success!");
    } else {
        NSLog(@"Error: %@", error);
    }
};

// Calling block
completion(YES, nil);

// Block as parameter
- (void)performOperationWithCompletion:(CompletionBlock)completion {
    // ... do work
    completion(YES, nil);
}
```

### Block Captures

```objc
- (void)demonstrateCaptures {
    NSInteger count = 0;

    // Captures count by value
    void (^block1)(void) = ^{
        NSLog(@"Count: %ld", (long)count);  // Prints captured value
    };

    count = 10;
    block1();  // Still prints 0

    // Mutable capture with __block
    __block NSInteger mutableCount = 0;
    void (^block2)(void) = ^{
        mutableCount++;  // Can modify
        NSLog(@"Mutable count: %ld", (long)mutableCount);
    };

    block2();  // Prints 1
    NSLog(@"After block: %ld", (long)mutableCount);  // Prints 1
}
```

### Common Block Patterns

```objc
// Enumeration with blocks
NSArray *numbers = @[@1, @2, @3, @4, @5];
[numbers enumerateObjectsUsingBlock:^(NSNumber *num, NSUInteger idx, BOOL *stop) {
    NSLog(@"Index %lu: %@", (unsigned long)idx, num);
    if ([num integerValue] == 3) {
        *stop = YES;  // Stop enumeration
    }
}];

// Filtering with predicates
NSPredicate *predicate = [NSPredicate predicateWithBlock:^BOOL(NSNumber *num, NSDictionary *bindings) {
    return [num integerValue] > 2;
}];
NSArray *filtered = [numbers filteredArrayUsingPredicate:predicate];

// Sorting with comparator
NSArray *sorted = [numbers sortedArrayUsingComparator:^NSComparisonResult(NSNumber *a, NSNumber *b) {
    return [a compare:b];
}];

// Completion handlers
- (void)fetchDataWithCompletion:(void (^)(NSData *data, NSError *error))completion {
    dispatch_async(dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_DEFAULT, 0), ^{
        // Fetch data
        NSData *data = [self loadData];

        dispatch_async(dispatch_get_main_queue(), ^{
            if (completion) {
                completion(data, nil);
            }
        });
    });
}
```

---

## Grand Central Dispatch (GCD)

### Dispatch Queues

```objc
// Main queue (UI updates)
dispatch_async(dispatch_get_main_queue(), ^{
    self.label.text = @"Updated on main thread";
});

// Global concurrent queue
dispatch_queue_t queue = dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_DEFAULT, 0);
dispatch_async(queue, ^{
    // Background work
    NSData *data = [self heavyComputation];

    // Update UI on main queue
    dispatch_async(dispatch_get_main_queue(), ^{
        [self updateUIWithData:data];
    });
});

// Custom serial queue
dispatch_queue_t serialQueue = dispatch_queue_create("com.example.serialQueue", DISPATCH_QUEUE_SERIAL);
dispatch_async(serialQueue, ^{
    // Serial execution
});

// Custom concurrent queue
dispatch_queue_t concurrentQueue = dispatch_queue_create("com.example.concurrentQueue", DISPATCH_QUEUE_CONCURRENT);
```

### Synchronous vs Asynchronous

```objc
// Asynchronous (doesn't block)
dispatch_async(queue, ^{
    NSLog(@"Async work");
});

// Synchronous (blocks until complete)
dispatch_sync(queue, ^{
    NSLog(@"Sync work");
});
// WARNING: Never call dispatch_sync on current queue (deadlock!)

// Dispatch after delay
dispatch_after(dispatch_time(DISPATCH_TIME_NOW, 2 * NSEC_PER_SEC),
               dispatch_get_main_queue(), ^{
    NSLog(@"Executed after 2 seconds");
});
```

### Dispatch Groups

```objc
// Wait for multiple operations
dispatch_group_t group = dispatch_group_create();
dispatch_queue_t queue = dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_DEFAULT, 0);

// Add tasks to group
dispatch_group_async(group, queue, ^{
    NSLog(@"Task 1");
});

dispatch_group_async(group, queue, ^{
    NSLog(@"Task 2");
});

// Notify when all complete
dispatch_group_notify(group, dispatch_get_main_queue(), ^{
    NSLog(@"All tasks complete");
});

// Or wait synchronously
dispatch_group_wait(group, DISPATCH_TIME_FOREVER);
```

### Dispatch Barriers

```objc
// Ensure exclusive access in concurrent queue
dispatch_barrier_async(concurrentQueue, ^{
    // This executes exclusively (no other tasks run concurrently)
    [self.mutableArray addObject:object];
});
```

---

## Foundation Framework Essentials

### NSString

```objc
// Creating strings
NSString *literal = @"Hello";
NSString *formatted = [NSString stringWithFormat:@"Value: %d", 42];
NSString *fromFile = [NSString stringWithContentsOfFile:path
                                                encoding:NSUTF8StringEncoding
                                                   error:&error];

// String operations
NSString *upper = [str uppercaseString];
NSString *lower = [str lowercaseString];
NSRange range = [str rangeOfString:@"substring"];
BOOL contains = [str containsString:@"text"];
NSString *replaced = [str stringByReplacingOccurrencesOfString:@"old" withString:@"new"];

// Mutable strings
NSMutableString *mutable = [NSMutableString stringWithString:@"Hello"];
[mutable appendString:@" World"];
[mutable insertString:@"Beautiful " atIndex:6];
[mutable deleteCharactersInRange:NSMakeRange(0, 5)];
```

### NSArray and NSMutableArray

```objc
// Creating arrays
NSArray *array = @[@"one", @"two", @"three"];
NSArray *array2 = [NSArray arrayWithObjects:@"a", @"b", @"c", nil];

// Array operations
NSUInteger count = array.count;
id firstObject = array.firstObject;
id lastObject = array.lastObject;
id objectAtIndex = array[1];  // Modern syntax
BOOL contains = [array containsObject:@"two"];
NSUInteger index = [array indexOfObject:@"two"];

// Iteration
for (NSString *item in array) {
    NSLog(@"%@", item);
}

[array enumerateObjectsUsingBlock:^(id obj, NSUInteger idx, BOOL *stop) {
    NSLog(@"%lu: %@", (unsigned long)idx, obj);
}];

// Mutable arrays
NSMutableArray *mutable = [NSMutableArray arrayWithArray:array];
[mutable addObject:@"four"];
[mutable insertObject:@"zero" atIndex:0];
[mutable removeObject:@"two"];
[mutable removeObjectAtIndex:0];
```

### NSDictionary and NSMutableDictionary

```objc
// Creating dictionaries
NSDictionary *dict = @{
    @"name": @"Alice",
    @"age": @30,
    @"city": @"NYC"
};

// Dictionary operations
id value = dict[@"name"];  // Modern syntax
id value2 = [dict objectForKey:@"age"];
NSArray *keys = dict.allKeys;
NSArray *values = dict.allValues;
NSUInteger count = dict.count;

// Iteration
for (NSString *key in dict) {
    NSLog(@"%@: %@", key, dict[key]);
}

[dict enumerateKeysAndObjectsUsingBlock:^(id key, id obj, BOOL *stop) {
    NSLog(@"%@: %@", key, obj);
}];

// Mutable dictionaries
NSMutableDictionary *mutable = [NSMutableDictionary dictionaryWithDictionary:dict];
mutable[@"email"] = @"alice@example.com";
[mutable setObject:@31 forKey:@"age"];
[mutable removeObjectForKey:@"city"];
```

### NSSet and NSMutableSet

```objc
// Creating sets (unordered, unique elements)
NSSet *set = [NSSet setWithObjects:@"a", @"b", @"c", nil];
NSSet *set2 = [NSSet setWithArray:array];

// Set operations
BOOL contains = [set containsObject:@"a"];
NSUInteger count = set.count;

// Set algebra
NSSet *union = [set setByAddingObjectsFromSet:set2];
NSMutableSet *mutable = [set mutableCopy];
[mutable intersectSet:set2];

// Iteration
for (id object in set) {
    NSLog(@"%@", object);
}
```

### NSNumber and Boxing

```objc
// Boxing primitives
NSNumber *intNumber = @42;
NSNumber *floatNumber = @3.14f;
NSNumber *boolNumber = @YES;
NSNumber *charNumber = @'A';

// Boxing expressions
NSNumber *result = @(1 + 2 * 3);

// Unboxing
NSInteger intValue = [intNumber integerValue];
float floatValue = [floatNumber floatValue];
BOOL boolValue = [boolNumber boolValue];

// Using in collections
NSArray *numbers = @[@1, @2, @3, @4, @5];
```

---

## Common Patterns

### Singleton Pattern

```objc
@interface NetworkManager : NSObject
+ (instancetype)sharedManager;
@end

@implementation NetworkManager

+ (instancetype)sharedManager {
    static NetworkManager *shared = nil;
    static dispatch_once_t onceToken;
    dispatch_once(&onceToken, ^{
        shared = [[self alloc] init];
    });
    return shared;
}

@end

// Usage
NetworkManager *manager = [NetworkManager sharedManager];
```

### Delegate Pattern

```objc
// Define protocol
@protocol DataSourceDelegate <NSObject>
@required
- (NSInteger)numberOfItems;
@optional
- (void)didSelectItemAtIndex:(NSInteger)index;
@end

// Class with delegate
@interface DataSource : NSObject
@property (weak, nonatomic) id<DataSourceDelegate> delegate;
@end

@implementation DataSource

- (void)loadData {
    if ([self.delegate respondsToSelector:@selector(numberOfItems)]) {
        NSInteger count = [self.delegate numberOfItems];
        NSLog(@"Items: %ld", (long)count);
    }
}

- (void)selectItem:(NSInteger)index {
    if ([self.delegate respondsToSelector:@selector(didSelectItemAtIndex:)]) {
        [self.delegate didSelectItemAtIndex:index];
    }
}

@end
```

### KVO (Key-Value Observing)

```objc
// Add observer
[person addObserver:self
         forKeyPath:@"name"
            options:NSKeyValueObservingOptionNew | NSKeyValueObservingOptionOld
            context:NULL];

// Observe changes
- (void)observeValueForKeyPath:(NSString *)keyPath
                      ofObject:(id)object
                        change:(NSDictionary *)change
                       context:(void *)context {
    if ([keyPath isEqualToString:@"name"]) {
        NSString *oldValue = change[NSKeyValueChangeOldKey];
        NSString *newValue = change[NSKeyValueChangeNewKey];
        NSLog(@"Name changed from %@ to %@", oldValue, newValue);
    }
}

// Remove observer (important!)
- (void)dealloc {
    [person removeObserver:self forKeyPath:@"name"];
}
```

### Notifications

```objc
// Post notification
[[NSNotificationCenter defaultCenter] postNotificationName:@"DataUpdated"
                                                    object:self
                                                  userInfo:@{@"count": @5}];

// Observe notification
[[NSNotificationCenter defaultCenter] addObserver:self
                                         selector:@selector(handleDataUpdated:)
                                             name:@"DataUpdated"
                                           object:nil];

- (void)handleDataUpdated:(NSNotification *)notification {
    NSDictionary *userInfo = notification.userInfo;
    NSNumber *count = userInfo[@"count"];
    NSLog(@"Data updated, count: %@", count);
}

// Remove observer (important!)
- (void)dealloc {
    [[NSNotificationCenter defaultCenter] removeObserver:self];
}
```

---

## Error Handling

### NSError Pattern

```objc
// Method that can fail
- (BOOL)loadDataFromFile:(NSString *)path error:(NSError **)error {
    NSData *data = [NSData dataWithContentsOfFile:path
                                          options:0
                                            error:error];
    if (!data) {
        return NO;  // error is populated by the framework
    }

    // Process data
    return YES;
}

// Creating custom errors
- (BOOL)validateUser:(User *)user error:(NSError **)error {
    if (user.name.length == 0) {
        if (error) {
            *error = [NSError errorWithDomain:@"com.example.validation"
                                         code:100
                                     userInfo:@{
                                         NSLocalizedDescriptionKey: @"Name is required",
                                         NSLocalizedFailureReasonErrorKey: @"User name cannot be empty"
                                     }];
        }
        return NO;
    }
    return YES;
}

// Using error methods
NSError *error = nil;
BOOL success = [self loadDataFromFile:@"data.txt" error:&error];
if (!success) {
    NSLog(@"Error: %@", error.localizedDescription);
    NSLog(@"Reason: %@", error.localizedFailureReason);
}
```

### Exception Handling

```objc
// Try-catch (use sparingly in Objective-C)
@try {
    NSArray *array = @[@1, @2, @3];
    id value = array[10];  // Out of bounds
}
@catch (NSException *exception) {
    NSLog(@"Exception: %@, reason: %@", exception.name, exception.reason);
}
@finally {
    NSLog(@"Cleanup code");
}

// Assertions
NSAssert(count > 0, @"Count must be positive");
NSParameterAssert(user != nil);
```

---

## Troubleshooting

### Unrecognized Selector

**Problem:** `-[ClassName selectorName:]: unrecognized selector sent to instance`

```objc
// Cause: Calling method that doesn't exist
[object methodThatDoesntExist];

// Fix 1: Check method exists
if ([object respondsToSelector:@selector(optionalMethod)]) {
    [object optionalMethod];
}

// Fix 2: Add missing method implementation
- (void)methodThatDoesntExist {
    // Implementation
}
```

### Memory Leaks and Retain Cycles

**Problem:** Objects not being deallocated

```objc
// Check for retain cycles with weak references
@property (weak) id<Delegate> delegate;  // Not strong!

// Use weak-strong dance in blocks
__weak typeof(self) weakSelf = self;
self.block = ^{
    __strong typeof(weakSelf) strongSelf = weakSelf;
    if (strongSelf) {
        [strongSelf doWork];
    }
};

// Remove observers
- (void)dealloc {
    [[NSNotificationCenter defaultCenter] removeObserver:self];
    [self.observedObject removeObserver:self forKeyPath:@"property"];
}
```

### Nil Messaging

**Problem:** Sending messages to nil

```objc
// In Objective-C, sending messages to nil is safe (returns nil/0)
NSString *str = nil;
NSUInteger length = [str length];  // Returns 0, doesn't crash

// But can hide bugs
id result = [nil someMethod];  // Returns nil, might mask issue

// Check for nil when necessary
if (object) {
    [object doSomething];
}
```

### Property Attribute Mistakes

**Problem:** Incorrect memory management

```objc
// WRONG: Strong reference to delegate (retain cycle)
@property (strong) id<Delegate> delegate;

// CORRECT: Weak reference
@property (weak) id<Delegate> delegate;

// WRONG: Mutable string without copy
@property (strong) NSString *name;
// Caller could pass NSMutableString and mutate it

// CORRECT: Use copy for strings
@property (copy) NSString *name;
```

### Thread Safety Issues

**Problem:** Accessing shared state from multiple threads

```objc
// WRONG: Direct access from multiple threads
self.mutableArray = [NSMutableArray array];
dispatch_async(queue1, ^{ [self.mutableArray addObject:obj1]; });
dispatch_async(queue2, ^{ [self.mutableArray addObject:obj2]; });

// CORRECT: Synchronize access
@synchronized(self.mutableArray) {
    [self.mutableArray addObject:obj];
}

// BETTER: Use serial queue or barrier
dispatch_barrier_async(self.concurrentQueue, ^{
    [self.mutableArray addObject:obj];
});
```

---

## References

- [Apple Developer Documentation](https://developer.apple.com/documentation/)
- [Objective-C Programming Guide](https://developer.apple.com/library/archive/documentation/Cocoa/Conceptual/ProgrammingWithObjectiveC/)
- [Memory Management Guide](https://developer.apple.com/library/archive/documentation/Cocoa/Conceptual/MemoryMgmt/)
- [Blocks Programming Topics](https://developer.apple.com/library/archive/documentation/Cocoa/Conceptual/Blocks/)
- [Concurrency Programming Guide](https://developer.apple.com/library/archive/documentation/General/Conceptual/ConcurrencyProgrammingGuide/)
- Specialized skills: `lang-objc-patterns-dev`, `lang-objc-library-dev`, `lang-swift-objc-bridge-dev`
