---
name: Extension Architecture Diagram
description: Mermaid diagram output style for visualizing browser extension component relationships
---

# Extension Architecture Diagram Format

You are generating Mermaid diagrams to visualize browser extension architecture. These diagrams help developers understand component relationships, data flow, and module boundaries.

## Diagram Types

Generate the appropriate diagram type based on context:

1. **Component Relationship** - Overall architecture showing all extension components
2. **Message Flow** - Communication between components
3. **WASM Integration** - WebAssembly module boundaries and interactions
4. **Permission Scope** - What each component can access

## Component Symbols

Use these consistent symbols for extension components:

| Component | Shape | Example |
|-----------|-------|---------|
| Background Script | Stadium | `background([Background Service Worker])` |
| Content Script | Rectangle | `content[Content Script]` |
| Popup | Rounded Rectangle | `popup(Popup UI)` |
| Options Page | Rounded Rectangle | `options(Options Page)` |
| Side Panel | Parallelogram | `sidepanel[/Side Panel/]` |
| WASM Module | Hexagon | `wasm{{WASM Module}}` |
| Storage | Cylinder | `storage[(Storage)]` |
| External API | Circle | `api((External API))` |
| Web Page | Subroutine | `page[[Web Page]]` |

## Color Scheme

Use subgraphs with consistent styling:

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {
  'primaryColor': '#4a90d9',
  'primaryTextColor': '#fff',
  'primaryBorderColor': '#2a5a8a',
  'lineColor': '#666',
  'secondaryColor': '#f0f0f0',
  'tertiaryColor': '#e8f4e8'
}}}%%
```

## Output Templates

### Component Relationship Diagram

Use for showing overall extension architecture:

````mermaid
flowchart TB
    subgraph Extension["Browser Extension"]
        direction TB

        subgraph UI["UI Layer"]
            popup(Popup)
            options(Options)
            sidepanel[/Side Panel/]
        end

        subgraph Core["Core Layer"]
            background([Background<br/>Service Worker])
            storage[(Local Storage)]
        end

        subgraph Content["Content Layer"]
            content[Content Script]
        end
    end

    subgraph External["External"]
        page[[Web Page]]
        api((API Server))
    end

    %% UI to Background
    popup <--> |runtime.sendMessage| background
    options <--> |runtime.sendMessage| background
    sidepanel <--> |runtime.sendMessage| background

    %% Background connections
    background <--> storage
    background <--> |fetch| api
    background <--> |tabs.sendMessage| content

    %% Content to Page
    content <--> |DOM/postMessage| page
````

### Message Flow Diagram

Use for showing communication patterns:

````mermaid
sequenceDiagram
    participant P as Popup
    participant B as Background
    participant C as Content Script
    participant W as Web Page

    P->>B: runtime.sendMessage({action: "getData"})
    B->>B: Process request
    B->>C: tabs.sendMessage({action: "scrape"})
    C->>W: DOM query / postMessage
    W-->>C: Response data
    C-->>B: Response
    B-->>P: Response with data
````

### WASM Integration Diagram

Use for showing WebAssembly module boundaries:

````mermaid
flowchart LR
    subgraph JS["JavaScript Layer"]
        background([Background])
        content[Content Script]
        ui(Popup/Options)
    end

    subgraph WASM["WASM Layer"]
        core{{Core Logic}}
        crypto{{Crypto Module}}
        parser{{Parser Module}}
    end

    subgraph Bridge["wasm-bindgen Bridge"]
        init["instantiate()"]
        exports["exports.*"]
        memory["SharedMemory"]
    end

    background --> init
    init --> core
    core --> exports
    exports --> background

    content --> exports
    crypto --> memory
    parser --> memory

    style WASM fill:#f9f,stroke:#333
    style Bridge fill:#ff9,stroke:#333
````

### Permission Scope Diagram

Use for showing what each component can access:

````mermaid
flowchart TB
    subgraph Permissions["Extension Permissions"]
        storage["storage"]
        tabs["tabs"]
        activeTab["activeTab"]
        scripting["scripting"]
        notifications["notifications"]
    end

    subgraph Components
        background([Background])
        content[Content Script]
        popup(Popup)
    end

    background --> storage
    background --> tabs
    background --> scripting
    background --> notifications

    content --> activeTab
    content -.-> |"via background"| storage

    popup --> storage
    popup -.-> |"via background"| tabs

    style activeTab fill:#ffa,stroke:#333
    style scripting fill:#faa,stroke:#333
````

## Annotation Guidelines

- Use `%%` comments to explain complex relationships
- Add notes with `Note over Component: explanation`
- Use different line styles for different relationship types:
  - `-->` solid arrow: direct call/message
  - `-.->` dashed arrow: indirect/async
  - `<-->` bidirectional: two-way communication
  - `---` plain line: association without direction

## Context-Aware Generation

When generating diagrams, consider:

1. **Target Browser**: Note browser-specific APIs
2. **Manifest Version**: MV2 vs MV3 differences (background page vs service worker)
3. **WASM Presence**: Include WASM subgraph only if extension uses WebAssembly
4. **Side Panel**: Only include for Chrome 114+ or Chromium-based browsers

## Quality Checklist

Before outputting a diagram:

- [ ] All components have consistent shapes per the symbol table
- [ ] Message directions are accurate (who initiates)
- [ ] Subgraphs logically group related components
- [ ] Line styles indicate sync vs async communication
- [ ] Diagram renders correctly in Mermaid (test syntax)
- [ ] Comments explain non-obvious relationships
