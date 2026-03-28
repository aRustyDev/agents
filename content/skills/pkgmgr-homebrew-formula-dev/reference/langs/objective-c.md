## Objective-C Formula Patterns

> **Mapping:** Use `language: "autotools"` or `language: "make"` — most Objective-C open-source projects use autotools or plain Makefiles.

### Researching an Objective-C Project

| What | Where to Look | Command / File |
|------|---------------|----------------|
| Build system | Repo root | `configure.ac` (Autotools), `Makefile`, or Xcode project |
| Frameworks | Source files | Check for `#import <Foundation/Foundation.h>` and other frameworks |
| Runtime | Build requirements | Objective-C runtime is available on macOS by default |
| Test command | README | Check for `--help` or `--version` |

### Dependencies

```text
depends_on :macos  # Objective-C runtime only available on macOS
```

### Common Issues

- **macOS only:** Most Objective-C projects are macOS-only due to framework dependencies
- **ARC:** Check if the project uses ARC (Automatic Reference Counting)
- **Xcode:** Some projects need Xcode CLI tools: `depends_on xcode: ["14.0", :build]`
