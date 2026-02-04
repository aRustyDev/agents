# Objective-C

> Object-oriented language with Smalltalk-style messaging, historically the primary language for Apple development.

## Overview

Objective-C is a general-purpose, object-oriented programming language that adds Smalltalk-style messaging to C. It was created by Brad Cox and Tom Love in the early 1980s and later adopted by NeXT (and subsequently Apple) as the primary language for macOS and iOS development.

Objective-C extends C with a dynamic runtime, message passing, and a powerful reflection system. Unlike C++, it uses runtime polymorphism through message dispatch rather than compile-time virtual tables. This enables powerful metaprogramming but sacrifices some type safety and performance.

While largely superseded by Swift for new Apple development, Objective-C remains important for maintaining legacy codebases and for C/C++ interoperability that Swift cannot easily achieve.

## Family Classification

| Dimension | Classification | Notes |
|-----------|----------------|-------|
| Primary Family | Apple | Legacy Apple ecosystem |
| Secondary Family | OOP | Smalltalk-style messaging |
| Subtype | dynamic-dispatch | Runtime message resolution |

See: [Apple Family](../language-families/apple.md)

## Version History

| Version | Release | Key Changes for Conversion |
|---------|---------|---------------------------|
| Objective-C 2.0 | 2007 | Properties, fast enumeration, GC (deprecated) |
| Modern Runtime | 2007 | Non-fragile instance variables |
| ARC | 2011 | Automatic Reference Counting |
| Modules | 2012 | @import, precompiled headers replacement |
| Nullability | 2015 | nullable, nonnull annotations |
| Generics | 2015 | Lightweight generics for Swift interop |

## Feature Profile

### Type System

- **Strength:** weak (dynamic typing via id, C compatibility)
- **Inference:** none (explicit types required)
- **Generics:** lightweight (type hints, not enforced at runtime)
- **Nullability:** nullable (optional annotations)

### Memory Model

- **Management:** ARC (Automatic Reference Counting, since 2011)
- **Mutability:** default-mutable
- **Allocation:** heap (objects), stack (primitives, structs)
- **Copy semantics:** reference by default, explicit copy for NSCopying

### Control Flow

- **Structured:** if-else, for, while, switch, @try/@catch/@finally
- **Effects:** exceptions (NSException), NSError by convention
- **Async:** GCD (Grand Central Dispatch), NSOperation, completion blocks

### Data Types

- **Primitives:** C primitives (int, float, etc.), BOOL, NSInteger, CGFloat
- **Composites:** classes, structs (C), blocks
- **Collections:** NSArray, NSDictionary, NSSet, C arrays
- **Abstraction:** protocols, categories, class clusters

### Metaprogramming

- **Macros:** C preprocessor
- **Reflection:** full runtime (objc/runtime.h)
- **Code generation:** method swizzling, dynamic class creation

## Ecosystem

| Tool | Name | Notes |
|------|------|-------|
| Package Manager | CocoaPods, Carthage, SPM | SPM preferred now |
| Build System | Xcode | Primary |
| LSP | SourceKit-LSP | Shared with Swift |
| Formatter | clang-format | C family formatter |
| Linter | OCLint, Xcode analyzer | Xcode built-in |
| REPL | none (debug console) | — |
| Test Framework | XCTest | Built-in |

## Syntax Patterns

```objc
// Method definition
- (NSString *)greetName:(NSString *)name times:(NSInteger)times {
    NSMutableString *result = [NSMutableString string];
    for (NSInteger i = 0; i < times; i++) {
        [result appendFormat:@"Hello, %@! ", name];
    }
    return result;
}

// Class method
+ (instancetype)userWithId:(NSString *)userId name:(NSString *)name {
    return [[self alloc] initWithId:userId name:name];
}

// Interface declaration
@interface User : NSObject

@property (nonatomic, copy, readonly) NSString *userId;
@property (nonatomic, copy) NSString *name;
@property (nonatomic, copy, nullable) NSString *email;

- (instancetype)initWithId:(NSString *)userId name:(NSString *)name;

@end

// Implementation
@implementation User

- (instancetype)initWithId:(NSString *)userId name:(NSString *)name {
    self = [super init];
    if (self) {
        _userId = [userId copy];
        _name = [name copy];
    }
    return self;
}

- (NSString *)description {
    return [NSString stringWithFormat:@"User(%@)", self.name];
}

@end

// Protocol definition
@protocol Displayable <NSObject>

- (NSString *)displayString;

@optional
- (void)displayInView:(UIView *)view;

@end

// Category (extension)
@interface NSString (Utilities)
- (NSString *)stringByRepeating:(NSInteger)times;
@end

@implementation NSString (Utilities)
- (NSString *)stringByRepeating:(NSInteger)times {
    return [@"" stringByPaddingToLength:self.length * times
                             withString:self
                        startingAtIndex:0];
}
@end

// Block (closure)
typedef void (^CompletionHandler)(NSData * _Nullable data, NSError * _Nullable error);

- (void)fetchDataFromURL:(NSURL *)url
              completion:(CompletionHandler)completion {
    NSURLSessionDataTask *task = [[NSURLSession sharedSession]
        dataTaskWithURL:url
        completionHandler:^(NSData *data, NSURLResponse *response, NSError *error) {
            if (error) {
                completion(nil, error);
                return;
            }
            completion(data, nil);
        }];
    [task resume];
}

// Error handling (NSError convention)
- (BOOL)saveToFile:(NSString *)path error:(NSError **)error {
    if (![self isValid]) {
        if (error) {
            *error = [NSError errorWithDomain:@"UserDomain"
                                        code:100
                                    userInfo:@{NSLocalizedDescriptionKey: @"Invalid user"}];
        }
        return NO;
    }
    // Save logic...
    return YES;
}

// Using NSError
NSError *error = nil;
BOOL success = [user saveToFile:path error:&error];
if (!success) {
    NSLog(@"Error: %@", error.localizedDescription);
}

// Enumeration
typedef NS_ENUM(NSInteger, ShapeType) {
    ShapeTypeCircle,
    ShapeTypeRectangle
};

// Dynamic typing
id unknownObject = [self getObject];
if ([unknownObject respondsToSelector:@selector(displayString)]) {
    NSString *display = [unknownObject displayString];
}

// Message forwarding
- (void)forwardInvocation:(NSInvocation *)invocation {
    if ([self.delegate respondsToSelector:invocation.selector]) {
        [invocation invokeWithTarget:self.delegate];
    }
}

// GCD (async)
dispatch_async(dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_DEFAULT, 0), ^{
    // Background work
    NSData *data = [self processData];

    dispatch_async(dispatch_get_main_queue(), ^{
        // Update UI on main thread
        [self updateUIWithData:data];
    });
});

// Collection literals
NSArray *numbers = @[@1, @2, @3];
NSDictionary *user = @{@"name": @"Alice", @"age": @30};

// Modern subscript syntax
NSString *name = user[@"name"];
NSNumber *first = numbers[0];
```

## Semantic Gaps

| Gap | Severity | Workaround |
|-----|----------|------------|
| Dynamic typing risks | high | Use nullability annotations, Swift interop |
| No namespaces | moderate | Use class prefixes (NS, UI, etc.) |
| Header/implementation split | moderate | Use categories, Swift |
| Verbose syntax | moderate | Use modern features, migrate to Swift |
| Memory management complexity | moderate | Use ARC, instrument for leaks |
| No true generics | minor | Use protocols, Swift interop |

## Convert-* Coverage

| Direction | Count | Skills |
|-----------|-------|--------|
| As Source | 1 | objc-swift |
| As Target | 0 | — |

**Note:** Primary conversion target is Swift. Message passing and runtime features require careful mapping.

## Idiomatic Patterns

### Message Passing → Method Calls

```objc
// Objective-C: message
[object doSomethingWithArg:value];

// IR equivalent: method call
// object.doSomething(arg: value)
```

### Protocols → Interfaces/Traits

```objc
// Objective-C: protocol
@protocol Hashable
- (NSUInteger)hash;
@end

// IR equivalent: interface/trait
// trait Hashable { fn hash(&self) -> usize }
```

### Blocks → Closures/Lambdas

```objc
// Objective-C: block
^(NSString *s) { return s.length; }

// IR equivalent: closure
// |s: &str| s.len()
```

### NSError Pattern → Result Type

```objc
// Objective-C: NSError out parameter
- (BOOL)doWork:(NSError **)error;

// IR equivalent: Result type
// fn do_work() -> Result<(), Error>
```

## Related Languages

- **Influenced by:** C, Smalltalk
- **Influenced:** Swift (some patterns), Java (partially)
- **Compiles to:** Native machine code (via Clang)
- **FFI compatible:** C (native), C++ (Objective-C++)

## Sources

- [Objective-C Programming Language](https://developer.apple.com/library/archive/documentation/Cocoa/Conceptual/ProgrammingWithObjectiveC/)
- [Objective-C Runtime Programming Guide](https://developer.apple.com/library/archive/documentation/Cocoa/Conceptual/ObjCRuntimeGuide/)
- [Apple Developer Documentation](https://developer.apple.com/documentation/)
- [Clang Objective-C Support](https://clang.llvm.org/docs/ObjectiveCLiterals.html)

## See Also

- [Apple Family](../language-families/apple.md)
- [Swift](swift.md) - Modern successor
- [C](c.md) - Foundation language
- [Smalltalk](smalltalk.md) - Message-passing influence
