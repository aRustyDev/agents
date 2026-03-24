---
name: lang-objc-library-dev
description: Objective-C-specific library and framework development patterns. Use when creating reusable frameworks, designing public APIs with protocols and categories, configuring Podspecs/Cartfiles/Package.swift, managing header visibility, implementing XCTest suites, writing HeaderDoc/appledoc documentation, or publishing to CocoaPods/Carthage/SPM. Extends lang-objc-dev with framework tooling and distribution practices.
---

# Objective-C Library Development

Objective-C-specific patterns for library and framework development. This skill extends `lang-objc-dev` with framework tooling, API design patterns, and ecosystem practices for creating reusable components.

## This Skill Extends

- `lang-objc-dev` - Foundational Objective-C patterns (classes, protocols, categories, memory management)

For general Objective-C syntax, memory management, and Foundation framework usage, see the foundational skill first.

## This Skill Adds

- **Framework tooling**: Xcode framework projects, umbrella headers, module maps
- **API design**: Public/private header organization, protocol-driven design, category patterns
- **Testing**: XCTest for libraries, dependency injection, mocking strategies
- **Documentation**: HeaderDoc, appledoc, inline documentation
- **Distribution**: CocoaPods, Carthage, Swift Package Manager integration

## This Skill Does NOT Cover

- General Objective-C patterns - see `lang-objc-dev`
- Swift interoperability - see `lang-swift-objc-bridge-dev`
- iOS/macOS application development - see platform-specific skills
- Advanced design patterns - see `lang-objc-patterns-dev`

---

## Quick Reference

| Task | Command/Tool |
|------|--------------|
| New framework | Xcode: File > New > Project > Framework |
| Build framework | `xcodebuild -scheme MyFramework build` |
| Run tests | `xcodebuild test -scheme MyFramework` |
| CocoaPods spec | `pod spec create MyLibrary` |
| Validate podspec | `pod lib lint MyLibrary.podspec` |
| Publish to CocoaPods | `pod trunk push MyLibrary.podspec` |
| Carthage build | `carthage build --no-skip-current` |
| SPM build | `swift build` |
| Generate docs | `appledoc --project-name MyLib *.h` |

---

## Framework Project Structure

### Standard Framework Layout

```
MyLibrary.framework/
├── MyLibrary.xcodeproj
├── MyLibrary/
│   ├── MyLibrary.h          # Umbrella header
│   ├── Info.plist
│   ├── Public/              # Public headers
│   │   ├── MLPublicClass.h
│   │   ├── MLProtocol.h
│   │   └── MLConstants.h
│   ├── Private/             # Private headers (not exported)
│   │   └── MLInternal.h
│   └── Implementation/      # .m files
│       ├── MLPublicClass.m
│       └── MLPrivateHelper.m
├── MyLibraryTests/
│   └── MyLibraryTests.m
├── MyLibrary.podspec
├── Cartfile
├── Package.swift
├── README.md
├── CHANGELOG.md
└── LICENSE
```

### Umbrella Header

```objc
// MyLibrary.h - Umbrella header that imports all public headers
#import <Foundation/Foundation.h>

//! Project version number for MyLibrary.
FOUNDATION_EXPORT double MyLibraryVersionNumber;

//! Project version string for MyLibrary.
FOUNDATION_EXPORT const unsigned char MyLibraryVersionString[];

// Public headers
#import <MyLibrary/MLPublicClass.h>
#import <MyLibrary/MLProtocol.h>
#import <MyLibrary/MLConstants.h>
#import <MyLibrary/MLCategories.h>
```

### Header Visibility Configuration

In Xcode target settings:

```
Build Phases > Headers
├── Public       # Exported headers (API)
│   ├── MyLibrary.h
│   ├── MLPublicClass.h
│   └── MLProtocol.h
├── Private      # Not exported, but visible to framework
│   └── MLInternal.h
└── Project      # Completely internal
    └── MLPrivateHelper.h
```

---

## Public API Design

### Header Organization Patterns

**Pattern 1: Monolithic Umbrella**
```objc
// Good for small libraries with few classes
#import <MyLibrary/MLClassA.h>
#import <MyLibrary/MLClassB.h>
#import <MyLibrary/MLClassC.h>
```

**Pattern 2: Feature-Based Modules**
```objc
// Better for larger libraries
#import <MyLibrary/MLCore.h>       // Core functionality
#import <MyLibrary/MLNetworking.h> // Network-related
#import <MyLibrary/MLUI.h>         // UI components

// Each module header imports its components
// MLCore.h:
#import <MyLibrary/MLCoreClass.h>
#import <MyLibrary/MLCoreProtocol.h>
```

**Pattern 3: Prefix-Based Organization**
```objc
// Consistent prefix prevents naming conflicts
ML  = MyLibrary
MLC = MyLibrary Core
MLN = MyLibrary Networking
MLU = MyLibrary UI

// Examples:
@interface MLCClient : NSObject
@interface MLNRequest : NSObject
@interface MLUButton : UIButton
```

### Protocol-Driven API Design

**Define clear protocols for extensibility:**

```objc
// MLDataProvider.h
@protocol MLDataProvider <NSObject>

@required
/// Fetch data asynchronously
- (void)fetchDataWithCompletion:(void (^)(NSData *_Nullable data, NSError *_Nullable error))completion;

@optional
/// Cancel ongoing fetch operation
- (void)cancelFetch;

/// Configure provider behavior
- (void)configureWithOptions:(NSDictionary<NSString *, id> *)options;

@end
```

**Provide default implementation:**

```objc
// MLDefaultDataProvider.h
@interface MLDefaultDataProvider : NSObject <MLDataProvider>

/// Designated initializer
- (instancetype)initWithBaseURL:(NSURL *)baseURL NS_DESIGNATED_INITIALIZER;

/// Convenience initializer
+ (instancetype)providerWithBaseURL:(NSURL *)baseURL;

@end

// MLDefaultDataProvider.m
@implementation MLDefaultDataProvider

- (instancetype)initWithBaseURL:(NSURL *)baseURL {
    self = [super init];
    if (self) {
        _baseURL = [baseURL copy];
    }
    return self;
}

+ (instancetype)providerWithBaseURL:(NSURL *)baseURL {
    return [[self alloc] initWithBaseURL:baseURL];
}

- (void)fetchDataWithCompletion:(void (^)(NSData *, NSError *))completion {
    // Default implementation
}

@end
```

### Category-Based API Extensions

**Provide convenience methods via categories:**

```objc
// NSString+MLAdditions.h
@interface NSString (MLAdditions)

/// Returns MD5 hash of string
- (NSString *)ml_md5Hash;

/// Returns URL-encoded string
- (NSString *)ml_urlEncode;

/// Safe subscripting that returns nil for out-of-bounds
- (nullable NSString *)ml_substringWithRange:(NSRange)range;

@end

// NSString+MLAdditions.m
@implementation NSString (MLAdditions)

- (NSString *)ml_md5Hash {
    // Implementation
    const char *cStr = [self UTF8String];
    unsigned char digest[CC_MD5_DIGEST_LENGTH];
    CC_MD5(cStr, (CC_LONG)strlen(cStr), digest);

    NSMutableString *output = [NSMutableString stringWithCapacity:CC_MD5_DIGEST_LENGTH * 2];
    for (int i = 0; i < CC_MD5_DIGEST_LENGTH; i++) {
        [output appendFormat:@"%02x", digest[i]];
    }
    return output;
}

- (NSString *)ml_urlEncode {
    NSCharacterSet *allowed = [NSCharacterSet URLQueryAllowedCharacterSet];
    return [self stringByAddingPercentEncodingWithAllowedCharacters:allowed];
}

- (nullable NSString *)ml_substringWithRange:(NSRange)range {
    if (range.location + range.length > self.length) {
        return nil;
    }
    return [self substringWithRange:range];
}

@end
```

**Naming convention for categories:**
- Prefix all methods with library prefix (e.g., `ml_`)
- Prevents collisions with other libraries or Apple's private APIs
- Makes it clear the method is from your library

### Constants and Enumerations

**Define constants in a dedicated header:**

```objc
// MLConstants.h
#import <Foundation/Foundation.h>

/// Notification names
FOUNDATION_EXPORT NSNotificationName const MLDidCompleteNotification;
FOUNDATION_EXPORT NSNotificationName const MLDidFailNotification;

/// Error domain
FOUNDATION_EXPORT NSErrorDomain const MLErrorDomain;

/// Error codes
typedef NS_ERROR_ENUM(MLErrorDomain, MLErrorCode) {
    MLErrorCodeUnknown = 0,
    MLErrorCodeInvalidParameter = 1,
    MLErrorCodeNetworkFailure = 2,
    MLErrorCodeAuthenticationRequired = 3,
};

/// Configuration keys
FOUNDATION_EXPORT NSString * const MLConfigurationKeyTimeout;
FOUNDATION_EXPORT NSString * const MLConfigurationKeyRetryCount;

/// Options
typedef NS_OPTIONS(NSUInteger, MLOptions) {
    MLOptionNone         = 0,
    MLOptionVerbose      = 1 << 0,
    MLOptionAsync        = 1 << 1,
    MLOptionPersistent   = 1 << 2,
};

// MLConstants.m
NSNotificationName const MLDidCompleteNotification = @"MLDidCompleteNotification";
NSNotificationName const MLDidFailNotification = @"MLDidFailNotification";

NSErrorDomain const MLErrorDomain = @"com.example.mylibrary.error";

NSString * const MLConfigurationKeyTimeout = @"timeout";
NSString * const MLConfigurationKeyRetryCount = @"retryCount";
```

### Version Information

```objc
// MLVersion.h
#import <Foundation/Foundation.h>

/// Current library version
FOUNDATION_EXPORT NSString * const MLVersionString;

/// Version components
FOUNDATION_EXPORT NSInteger const MLVersionMajor;
FOUNDATION_EXPORT NSInteger const MLVersionMinor;
FOUNDATION_EXPORT NSInteger const MLVersionPatch;

// MLVersion.m
NSString * const MLVersionString = @"1.2.3";
NSInteger const MLVersionMajor = 1;
NSInteger const MLVersionMinor = 2;
NSInteger const MLVersionPatch = 3;
```

---

## XCTest Testing Strategies

### Test Target Organization

```
MyLibraryTests/
├── Unit/
│   ├── MLClassATests.m
│   ├── MLClassBTests.m
│   └── MLUtilsTests.m
├── Integration/
│   ├── MLNetworkingTests.m
│   └── MLDataFlowTests.m
├── Helpers/
│   ├── MLTestHelpers.h
│   ├── MLTestHelpers.m
│   └── MLMockObjects.m
└── Resources/
    ├── test_data.json
    └── fixture.plist
```

### Unit Test Patterns

```objc
// MLPublicClassTests.m
#import <XCTest/XCTest.h>
#import <MyLibrary/MyLibrary.h>

@interface MLPublicClassTests : XCTestCase
@property (nonatomic, strong) MLPublicClass *sut; // System Under Test
@end

@implementation MLPublicClassTests

- (void)setUp {
    [super setUp];
    // Create fresh instance for each test
    self.sut = [[MLPublicClass alloc] init];
}

- (void)tearDown {
    // Clean up
    self.sut = nil;
    [super tearDown];
}

#pragma mark - Initialization Tests

- (void)testDesignatedInitializer {
    MLPublicClass *instance = [[MLPublicClass alloc] initWithName:@"Test"];

    XCTAssertNotNil(instance, @"Instance should not be nil");
    XCTAssertEqualObjects(instance.name, @"Test", @"Name should be set");
}

- (void)testConvenienceInitializer {
    MLPublicClass *instance = [MLPublicClass instanceWithName:@"Test"];

    XCTAssertNotNil(instance);
    XCTAssertEqualObjects(instance.name, @"Test");
}

#pragma mark - Behavior Tests

- (void)testProcessDataWithValidInput {
    NSData *input = [@"valid data" dataUsingEncoding:NSUTF8StringEncoding];
    NSError *error = nil;

    BOOL result = [self.sut processData:input error:&error];

    XCTAssertTrue(result, @"Processing should succeed");
    XCTAssertNil(error, @"No error should occur");
}

- (void)testProcessDataWithInvalidInput {
    NSError *error = nil;

    BOOL result = [self.sut processData:nil error:&error];

    XCTAssertFalse(result, @"Processing should fail");
    XCTAssertNotNil(error, @"Error should be populated");
    XCTAssertEqual(error.code, MLErrorCodeInvalidParameter);
}

#pragma mark - Async Tests

- (void)testAsyncFetchWithExpectation {
    XCTestExpectation *expectation = [self expectationWithDescription:@"Fetch completes"];

    [self.sut fetchDataWithCompletion:^(NSData *data, NSError *error) {
        XCTAssertNotNil(data, @"Data should be fetched");
        XCTAssertNil(error, @"No error should occur");
        [expectation fulfill];
    }];

    [self waitForExpectationsWithTimeout:5.0 handler:^(NSError *error) {
        if (error) {
            XCTFail(@"Timeout waiting for fetch: %@", error);
        }
    }];
}

#pragma mark - Edge Cases

- (void)testEmptyString {
    NSString *result = [self.sut processString:@""];
    XCTAssertEqualObjects(result, @"", @"Empty string should be handled");
}

- (void)testNilParameter {
    XCTAssertNoThrow([self.sut processString:nil], @"Should handle nil gracefully");
}

- (void)testLargeInput {
    NSMutableString *large = [NSMutableString string];
    for (int i = 0; i < 100000; i++) {
        [large appendString:@"x"];
    }

    NSString *result = [self.sut processString:large];
    XCTAssertNotNil(result, @"Should handle large input");
}

@end
```

### Mock Objects for Testing

```objc
// MLMockDataProvider.h
@interface MLMockDataProvider : NSObject <MLDataProvider>
@property (nonatomic, strong) NSData *mockData;
@property (nonatomic, strong) NSError *mockError;
@property (nonatomic, assign) BOOL shouldFail;
@property (nonatomic, assign) NSTimeInterval delay;
@end

// MLMockDataProvider.m
@implementation MLMockDataProvider

- (void)fetchDataWithCompletion:(void (^)(NSData *, NSError *))completion {
    dispatch_after(dispatch_time(DISPATCH_TIME_NOW, (int64_t)(self.delay * NSEC_PER_SEC)),
                   dispatch_get_main_queue(), ^{
        if (self.shouldFail) {
            completion(nil, self.mockError);
        } else {
            completion(self.mockData, nil);
        }
    });
}

@end

// Usage in tests:
- (void)testWithMockProvider {
    MLMockDataProvider *mock = [[MLMockDataProvider alloc] init];
    mock.mockData = [@"test" dataUsingEncoding:NSUTF8StringEncoding];
    mock.shouldFail = NO;

    MLClient *client = [[MLClient alloc] initWithDataProvider:mock];
    // Test client with predictable mock behavior
}
```

### Test Helpers

```objc
// MLTestHelpers.h
@interface MLTestHelpers : NSObject

/// Load JSON from test bundle
+ (NSDictionary *)loadJSONFixture:(NSString *)filename;

/// Create temporary directory for test files
+ (NSURL *)createTemporaryDirectory;

/// Clean up test resources
+ (void)cleanupTemporaryDirectory:(NSURL *)directory;

@end

// MLTestHelpers.m
@implementation MLTestHelpers

+ (NSDictionary *)loadJSONFixture:(NSString *)filename {
    NSBundle *bundle = [NSBundle bundleForClass:[self class]];
    NSURL *url = [bundle URLForResource:filename withExtension:@"json"];
    NSData *data = [NSData dataWithContentsOfURL:url];
    return [NSJSONSerialization JSONObjectWithData:data options:0 error:nil];
}

+ (NSURL *)createTemporaryDirectory {
    NSString *tempDir = NSTemporaryDirectory();
    NSString *guid = [[NSUUID UUID] UUIDString];
    NSString *path = [tempDir stringByAppendingPathComponent:guid];
    [[NSFileManager defaultManager] createDirectoryAtPath:path
                              withIntermediateDirectories:YES
                                               attributes:nil
                                                    error:nil];
    return [NSURL fileURLWithPath:path];
}

+ (void)cleanupTemporaryDirectory:(NSURL *)directory {
    [[NSFileManager defaultManager] removeItemAtURL:directory error:nil];
}

@end
```

---

## HeaderDoc and Documentation

### HeaderDoc Syntax

```objc
// MLPublicClass.h

/*!
 @class MLPublicClass
 @abstract A brief description of the class
 @discussion
 A more detailed description of what this class does,
 its purpose, and how it should be used.

 Example usage:
 @code
 MLPublicClass *instance = [[MLPublicClass alloc] initWithName:@"Example"];
 [instance processData:data error:&error];
 @endcode

 @note This class is thread-safe.
 @warning Do not use this class in a tight loop.
 */
@interface MLPublicClass : NSObject

/*!
 @property name
 @abstract The name associated with this instance
 @discussion
 The name is used to identify this instance in logs and error messages.
 Must not be nil or empty.
 */
@property (nonatomic, copy, readonly) NSString *name;

/*!
 @method initWithName:
 @abstract Designated initializer
 @param name The name for this instance. Must not be nil.
 @return An initialized instance, or nil if name is invalid
 @discussion
 This is the designated initializer for this class. All other
 initializers should call this method.

 @throws NSInvalidArgumentException if name is nil
 */
- (instancetype)initWithName:(NSString *)name NS_DESIGNATED_INITIALIZER;

/*!
 @method instanceWithName:
 @abstract Convenience class method to create instances
 @param name The name for the instance
 @return A new autoreleased instance
 */
+ (instancetype)instanceWithName:(NSString *)name;

/*!
 @method processData:error:
 @abstract Process input data
 @param data The data to process. Must not be nil.
 @param error On input, a pointer to an error object. If an error occurs,
              this pointer is set to an NSError object describing the error.
              Pass NULL if you don't care about error information.
 @return YES if processing succeeded, NO otherwise
 @discussion
 This method processes the input data according to the configured rules.
 If processing fails, the error parameter will be populated with details.

 Error codes:
 - MLErrorCodeInvalidParameter: data parameter was nil
 - MLErrorCodeProcessingFailed: processing encountered an error

 @see fetchDataWithCompletion:
 */
- (BOOL)processData:(NSData *)data error:(NSError **)error;

/*!
 @method fetchDataWithCompletion:
 @abstract Asynchronously fetch data
 @param completion Completion block called when fetch completes or fails.
                   Called on the main queue.
 @discussion
 This method fetches data asynchronously. The completion block is always
 called, either with data on success or an error on failure.

 @code
 [instance fetchDataWithCompletion:^(NSData *data, NSError *error) {
     if (error) {
         NSLog(@"Failed: %@", error);
     } else {
         // Use data
     }
 }];
 @endcode
 */
- (void)fetchDataWithCompletion:(void (^)(NSData *_Nullable data, NSError *_Nullable error))completion;

@end
```

### Nullability Annotations

```objc
NS_ASSUME_NONNULL_BEGIN

@interface MLClient : NSObject

/// Returns a value, never nil
- (NSString *)getName;

/// May return nil
- (nullable NSString *)getOptionalValue;

/// Takes non-null parameter
- (void)setName:(NSString *)name;

/// Takes nullable parameter
- (void)setOptionalValue:(nullable NSString *)value;

/// Block with nullable parameters and return
- (void)fetchWithCompletion:(void (^)(NSData *_Nullable data, NSError *_Nullable error))completion;

@end

NS_ASSUME_NONNULL_END
```

### Appledoc Configuration

Create a `.appledoc` configuration file:

```
--project-name "MyLibrary"
--project-company "Your Company"
--company-id "com.yourcompany"
--output "./Documentation"
--logformat xcode
--keep-intermediate-files
--no-repeat-first-par
--no-warn-invalid-crossref
--ignore "*.m"
--ignore "Private"
--index-desc "./README.md"
```

Generate documentation:
```bash
appledoc .
```

---

## CocoaPods Distribution

### Podspec Structure

```ruby
# MyLibrary.podspec
Pod::Spec.new do |s|
  # Metadata
  s.name             = 'MyLibrary'
  s.version          = '1.2.3'
  s.summary          = 'A brief description of MyLibrary'
  s.description      = <<-DESC
    A longer description of MyLibrary that explains what it does,
    why it exists, and what problems it solves. This should be
    more detailed than the summary.
  DESC

  # Homepage and license
  s.homepage         = 'https://github.com/yourusername/mylibrary'
  s.license          = { :type => 'MIT', :file => 'LICENSE' }
  s.author           = { 'Your Name' => 'you@example.com' }
  s.source           = { :git => 'https://github.com/yourusername/mylibrary.git',
                         :tag => s.version.to_s }

  # Platform requirements
  s.ios.deployment_target = '12.0'
  s.osx.deployment_target = '10.13'
  s.watchos.deployment_target = '5.0'
  s.tvos.deployment_target = '12.0'

  # Source files
  s.source_files = 'MyLibrary/**/*.{h,m}'
  s.public_header_files = 'MyLibrary/Public/**/*.h'
  s.private_header_files = 'MyLibrary/Private/**/*.h'

  # Resources
  s.resources = 'MyLibrary/Resources/**/*'

  # Dependencies
  s.dependency 'AFNetworking', '~> 4.0'
  s.ios.dependency 'SDWebImage', '~> 5.0'

  # Frameworks
  s.frameworks = 'Foundation', 'UIKit'

  # Build settings
  s.requires_arc = true
  s.pod_target_xcconfig = {
    'DEFINES_MODULE' => 'YES'
  }

  # Subspecs for modular features
  s.subspec 'Core' do |core|
    core.source_files = 'MyLibrary/Core/**/*.{h,m}'
    core.public_header_files = 'MyLibrary/Core/Public/**/*.h'
  end

  s.subspec 'Networking' do |net|
    net.source_files = 'MyLibrary/Networking/**/*.{h,m}'
    net.dependency 'MyLibrary/Core'
    net.dependency 'AFNetworking', '~> 4.0'
  end

  s.default_subspecs = 'Core'
end
```

### CocoaPods Workflow

```bash
# Create podspec
pod spec create MyLibrary

# Validate locally
pod lib lint MyLibrary.podspec

# Validate with remote sources
pod spec lint MyLibrary.podspec

# Register with CocoaPods trunk (first time only)
pod trunk register you@example.com 'Your Name'

# Push to CocoaPods
pod trunk push MyLibrary.podspec

# Add collaborators
pod trunk add-owner MyLibrary other@example.com
```

### Podfile for Development

```ruby
# Podfile for development/testing
platform :ios, '12.0'
use_frameworks!

target 'MyLibrary' do
  # Your library dependencies
  pod 'AFNetworking', '~> 4.0'
end

target 'MyLibraryTests' do
  # Test dependencies
  pod 'OCMock', '~> 3.9'
end

# Use local development pod
# pod 'MyLibrary', :path => './'
```

---

## Carthage Distribution

### Cartfile Structure

```
# Cartfile - Dependencies for your library
github "AFNetworking/AFNetworking" ~> 4.0
```

### Carthage Compatibility

Ensure your framework is Carthage-compatible:

1. **Use shared schemes** - Make sure your framework scheme is shared
2. **Build universal frameworks** - Support both iOS devices and simulator

```bash
# Build for Carthage
carthage build --no-skip-current

# Create XCFramework (Xcode 11+)
carthage build --use-xcframeworks
```

### Build Script for Universal Framework

```bash
#!/bin/bash
# build-universal.sh

FRAMEWORK_NAME="MyLibrary"
SCHEME="MyLibrary"

# Build for device
xcodebuild archive \
  -scheme "${SCHEME}" \
  -archivePath "build/ios.xcarchive" \
  -sdk iphoneos \
  SKIP_INSTALL=NO \
  BUILD_LIBRARY_FOR_DISTRIBUTION=YES

# Build for simulator
xcodebuild archive \
  -scheme "${SCHEME}" \
  -archivePath "build/ios-simulator.xcarchive" \
  -sdk iphonesimulator \
  SKIP_INSTALL=NO \
  BUILD_LIBRARY_FOR_DISTRIBUTION=YES

# Create XCFramework
xcodebuild -create-xcframework \
  -framework "build/ios.xcarchive/Products/Library/Frameworks/${FRAMEWORK_NAME}.framework" \
  -framework "build/ios-simulator.xcarchive/Products/Library/Frameworks/${FRAMEWORK_NAME}.framework" \
  -output "build/${FRAMEWORK_NAME}.xcframework"
```

---

## Swift Package Manager

### Package.swift

```swift
// swift-tools-version:5.5
import PackageDescription

let package = Package(
    name: "MyLibrary",
    platforms: [
        .iOS(.v12),
        .macOS(.v10_13),
        .watchOS(.v5),
        .tvOS(.v12)
    ],
    products: [
        .library(
            name: "MyLibrary",
            targets: ["MyLibrary"]),
    ],
    dependencies: [
        // External dependencies
        .package(url: "https://github.com/AFNetworking/AFNetworking.git", from: "4.0.0"),
    ],
    targets: [
        .target(
            name: "MyLibrary",
            dependencies: ["AFNetworking"],
            path: "MyLibrary",
            publicHeadersPath: "Public",
            cSettings: [
                .headerSearchPath("Private"),
            ]),
        .testTarget(
            name: "MyLibraryTests",
            dependencies: ["MyLibrary"],
            path: "MyLibraryTests"),
    ]
)
```

### SPM Directory Structure

```
MyLibrary/
├── Package.swift
├── Sources/
│   └── MyLibrary/
│       ├── include/               # Public headers
│       │   ├── MyLibrary.h
│       │   ├── MLPublicClass.h
│       │   └── MLProtocol.h
│       └── Implementation/        # .m files
│           └── MLPublicClass.m
├── Tests/
│   └── MyLibraryTests/
│       └── MyLibraryTests.m
└── README.md
```

---

## Module Maps

### Custom Module Map

```
// module.modulemap
framework module MyLibrary {
    umbrella header "MyLibrary.h"

    export *
    module * { export * }

    explicit module Private {
        header "MLInternal.h"
        export *
    }
}
```

### Module Map in Xcode

Configure in Build Settings:
```
DEFINES_MODULE = YES
MODULEMAP_FILE = $(SRCROOT)/MyLibrary/module.modulemap
```

---

## Versioning and Release Strategy

### Semantic Versioning

Follow [semver.org](https://semver.org):

- **MAJOR**: Incompatible API changes
- **MINOR**: Backwards-compatible functionality additions
- **PATCH**: Backwards-compatible bug fixes

### Deprecation Strategy

```objc
// Deprecate old API
- (void)oldMethod:(id)parameter
    DEPRECATED_MSG_ATTRIBUTE("Use newMethod:withOptions: instead");

// Introduce replacement
- (void)newMethod:(id)parameter
      withOptions:(NSDictionary *)options;

// Provide compatibility shim
- (void)oldMethod:(id)parameter {
    NSLog(@"Warning: oldMethod: is deprecated. Use newMethod:withOptions:");
    [self newMethod:parameter withOptions:@{}];
}
```

### Version Macro

```objc
// MLVersion.h
#define ML_VERSION_MAJOR 1
#define ML_VERSION_MINOR 2
#define ML_VERSION_PATCH 3

#define ML_VERSION_CHECK(major, minor, patch) \
    (ML_VERSION_MAJOR > (major) || \
     (ML_VERSION_MAJOR == (major) && ML_VERSION_MINOR > (minor)) || \
     (ML_VERSION_MAJOR == (major) && ML_VERSION_MINOR == (minor) && ML_VERSION_PATCH >= (patch)))

// Usage:
#if ML_VERSION_CHECK(1, 2, 0)
    // Code for version 1.2.0 and later
#endif
```

### CHANGELOG.md

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- New feature in development

## [1.2.3] - 2024-01-15

### Fixed
- Fixed crash when processing nil data
- Corrected memory leak in network layer

## [1.2.0] - 2024-01-01

### Added
- New `MLClient` class for network operations
- Support for custom data providers via `MLDataProvider` protocol

### Changed
- Improved performance of data processing by 50%
- Updated minimum deployment target to iOS 12.0

### Deprecated
- `oldMethod:` in favor of `newMethod:withOptions:`

## [1.1.0] - 2023-12-01

### Added
- Initial public release
```

---

## Troubleshooting

### Framework Not Found at Runtime

**Symptoms:** `dyld: Library not loaded: @rpath/MyLibrary.framework/MyLibrary`

**Solution:**
```
1. Check Build Settings > Runpath Search Paths
   - Should include @executable_path/Frameworks

2. Verify framework is embedded:
   - Build Phases > Embed Frameworks
   - Framework should be listed

3. For CocoaPods, ensure:
   - use_frameworks! is in Podfile
   - Run pod install after changes
```

### Duplicate Symbol Errors

**Symptoms:** `duplicate symbol _OBJC_CLASS_$_ClassName`

**Solution:**
```objc
// Ensure category methods use unique prefix
// BAD:
@implementation NSString (Additions)
- (NSString *)reverse { ... }
@end

// GOOD:
@implementation NSString (MLAdditions)
- (NSString *)ml_reverse { ... }
@end
```

### Missing Header in Umbrella

**Symptoms:** Header not visible to framework users

**Solution:**
```
1. Check header visibility in Xcode:
   - Target > Build Phases > Headers
   - Move header from Project/Private to Public

2. Add to umbrella header:
   - #import <MyLibrary/MLNewClass.h>

3. Clean and rebuild:
   - Product > Clean Build Folder (Cmd+Shift+K)
```

### Swift Bridging Issues

**Symptoms:** Objective-C types not visible in Swift

**Solution:**
```objc
// Use nullability annotations
NS_ASSUME_NONNULL_BEGIN

@interface MLClass : NSObject
- (NSString *)getName;  // Nonnull by default
- (nullable NSString *)getOptionalName;
@end

NS_ASSUME_NONNULL_END

// Use generics for collections
@property (nonatomic, copy) NSArray<NSString *> *items;
@property (nonatomic, copy) NSDictionary<NSString *, NSNumber *> *counts;
```

### Podspec Validation Failures

**Symptoms:** `pod lib lint` fails

**Solution:**
```bash
# Get verbose output
pod lib lint --verbose

# Common issues:
# 1. Missing source files
#    - Check s.source_files pattern matches actual files

# 2. Dependency conflicts
#    - Ensure dependency versions are compatible
#    - Use ~> for flexible version matching

# 3. Build settings issues
#    - Add necessary frameworks to s.frameworks
#    - Set s.requires_arc appropriately

# 4. Missing license
#    - Ensure LICENSE file exists
#    - Match s.license specification
```

---

## Best Practices Summary

1. **Prefix all public symbols** with 2-3 letter prefix (classes, protocols, constants, categories)
2. **Use nullability annotations** for Swift interoperability
3. **Document with HeaderDoc** for generated documentation
4. **Provide protocol-based APIs** for extensibility
5. **Include comprehensive tests** with XCTest
6. **Support multiple distribution methods** (CocoaPods, Carthage, SPM)
7. **Follow semantic versioning** strictly
8. **Maintain backwards compatibility** when possible
9. **Deprecate before removing** APIs
10. **Keep umbrella header clean** and organized

---

## See Also

- `lang-objc-dev` - Foundational Objective-C patterns
- `lang-swift-objc-bridge-dev` - Swift interoperability
- `lang-objc-patterns-dev` - Advanced design patterns
- [CocoaPods Guides](https://guides.cocoapods.org/)
- [Carthage Documentation](https://github.com/Carthage/Carthage)
- [Swift Package Manager Documentation](https://swift.org/package-manager/)
- [HeaderDoc User Guide](https://developer.apple.com/library/archive/documentation/DeveloperTools/Conceptual/HeaderDoc/)
