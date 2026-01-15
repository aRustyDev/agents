# Stage 6: TUI

> Add interactive Terminal User Interface with Textual.

## Objective

Build an optional TUI mode that provides real-time feedback and interactive controls.

## Dependencies

- Stage 5 complete (Observability works)
- Textual library installed

## Steps

### 6.1 Create TUI app skeleton

```python
# src/tui/app.py
"""Textual TUI application."""

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, ProgressBar, RichLog
from textual.containers import Container, Horizontal, Vertical

class AddresserApp(App):
    """TUI for skill-pr-addresser."""

    CSS_PATH = "styles.tcss"
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "refresh", "Refresh"),
        ("s", "skip", "Skip Current"),
    ]

    def __init__(self, cement_app, pr_number: int):
        super().__init__()
        self.cement_app = cement_app
        self.pr_number = pr_number
        self.addresser = None

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Horizontal(
                StagePanel(id="stage-panel"),
                FeedbackPanel(id="feedback-panel"),
            ),
            LogPanel(id="log-panel"),
            id="main",
        )
        yield Footer()

    def on_mount(self):
        """Start addressing when app mounts."""
        self.run_worker(self._run_addressing())

    async def _run_addressing(self):
        """Run addressing with progress updates."""
        from ..addresser import Addresser

        self.addresser = Addresser(self.cement_app)

        # Hook into addresser for progress updates
        # ... emit progress events
```

- [ ] Create `src/tui/__init__.py`
- [ ] Create `src/tui/app.py`

### 6.2 Create stage panel widget

```python
# src/tui/widgets.py
"""Custom TUI widgets."""

from textual.widgets import Static, ProgressBar
from textual.containers import Vertical

class StagePanel(Vertical):
    """Shows current stage and progress."""

    STAGES = [
        "Discovery",
        "Analysis",
        "Implementation",
        "Commit",
        "Status Update",
    ]

    def compose(self):
        yield Static("Stage Progress", classes="panel-title")
        yield ProgressBar(total=len(self.STAGES), id="stage-progress")
        yield Static("", id="current-stage")
        yield Static("", id="stage-details")

    def update_stage(self, stage_index: int, stage_name: str, details: str = ""):
        self.query_one("#stage-progress", ProgressBar).progress = stage_index
        self.query_one("#current-stage", Static).update(f"[bold]{stage_name}[/]")
        self.query_one("#stage-details", Static).update(details)
```

- [ ] Implement `StagePanel`

### 6.3 Create feedback panel widget

```python
class FeedbackPanel(Vertical):
    """Shows feedback items with status."""

    def compose(self):
        yield Static("Feedback Items", classes="panel-title")
        yield DataTable(id="feedback-table")

    def on_mount(self):
        table = self.query_one("#feedback-table", DataTable)
        table.add_columns("Status", "Type", "File", "Description")

    def update_items(self, items: list[dict]):
        table = self.query_one("#feedback-table", DataTable)
        table.clear()
        for item in items:
            status = "✅" if item.get("resolved") else "⏳"
            table.add_row(
                status,
                item["type"],
                item.get("file", "-"),
                item["description"][:50],
            )

    def mark_addressed(self, item_id: str):
        # Update specific row to show ✅
        ...
```

- [ ] Implement `FeedbackPanel`
- [ ] Implement `DataTable` with feedback items

### 6.4 Create log panel widget

```python
class LogPanel(Vertical):
    """Collapsible log output."""

    def compose(self):
        yield Static("Logs", classes="panel-title")
        yield RichLog(id="log-output", highlight=True, markup=True)

    def add_log(self, message: str, level: str = "info"):
        log = self.query_one("#log-output", RichLog)
        color = {
            "info": "white",
            "warning": "yellow",
            "error": "red",
            "debug": "dim",
        }.get(level, "white")
        log.write(f"[{color}]{message}[/]")
```

- [ ] Implement `LogPanel`

### 6.5 Create styles

```css
/* src/tui/styles.tcss */

Screen {
    layout: vertical;
}

#main {
    layout: vertical;
    height: 1fr;
}

#main > Horizontal {
    height: 70%;
}

#stage-panel {
    width: 40%;
    border: solid green;
    padding: 1;
}

#feedback-panel {
    width: 60%;
    border: solid blue;
    padding: 1;
}

#log-panel {
    height: 30%;
    border: solid dim;
    padding: 1;
}

.panel-title {
    text-style: bold;
    color: cyan;
    margin-bottom: 1;
}

ProgressBar {
    margin: 1 0;
}

DataTable {
    height: 100%;
}
```

- [ ] Create `src/tui/styles.tcss`

### 6.6 Wire up to controller

```python
# controllers/base.py
@ex(
    arguments=[
        (['pr_number'], {'type': int}),
        (['--tui'], {'action': 'store_true', 'help': 'Enable interactive TUI'}),
        ...
    ]
)
def address(self):
    if self.app.pargs.tui:
        from ..tui.app import AddresserApp
        tui = AddresserApp(self.app, self.app.pargs.pr_number)
        tui.run()
    else:
        # Headless mode
        ...
```

- [ ] Update controller to launch TUI

### 6.7 Add progress callback

```python
# addresser.py
class Addresser:
    def address(
        self,
        pr_number: int,
        dry_run: bool = False,
        progress_callback: callable = None,
    ) -> AddressingResult:

        def emit(stage: str, details: str = ""):
            if progress_callback:
                progress_callback(stage, details)

        emit("Discovery", f"PR #{pr_number}")
        ctx = discover(...)

        emit("Analysis", f"{len(ctx.feedback_items)} items")
        analysis = analyze_feedback(...)

        # ... etc
```

- [ ] Add `progress_callback` parameter
- [ ] Emit progress at each stage

### 6.8 Add TUI tests

```python
# tests/test_tui.py
import pytest
from textual.testing import AppTest

async def test_tui_displays_stages():
    app = AddresserApp(mock_app, 795)
    async with AppTest(app) as pilot:
        assert pilot.query_one("#stage-panel") is not None
        assert pilot.query_one("#feedback-panel") is not None

async def test_tui_updates_progress():
    # ... verify progress updates
```

- [ ] Create `tests/test_tui.py`

## Checklist Gate

Before proceeding to Stage 7:

- [ ] `just address-skill-reviews 795 --tui` launches TUI
- [ ] Stage progress shows correctly
- [ ] Feedback items display in table
- [ ] Logs stream in real-time
- [ ] `q` quits the application
- [ ] Headless mode still works (default)
- [ ] All TUI tests pass

## Files Created

| File | Purpose |
|------|---------|
| `src/tui/__init__.py` | Package marker |
| `src/tui/app.py` | Main TUI app |
| `src/tui/widgets.py` | Custom widgets |
| `src/tui/styles.tcss` | CSS styles |
| `tests/test_tui.py` | TUI tests |

## Estimated Effort

- App skeleton: ~1 hour
- Widgets: ~3 hours
- Styles: ~1 hour
- Integration: ~1 hour
- Tests: ~1 hour
- **Total: ~7 hours**
