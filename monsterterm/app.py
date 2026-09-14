"""MonsterTerm — terminal dashboard for the Monster P&L tracker."""

from __future__ import annotations

from textual.app import App, ComposeResult
from textual.widgets import Static

from monsterterm import __version__
from monsterterm.api import MonsterConfig, fetch_stats


class MonsterTermApp(App):
    """Main MonsterTerm application."""

    def compose(self) -> ComposeResult:
        yield Static("MonsterTerm v" + __version__)
        yield Static("Loading...", id="content")

    def on_mount(self) -> None:
        stats = fetch_stats(MonsterConfig.from_env())
        content = self.query_one("#content", Static)
        if stats:
            content.update(f"Low stock: {stats.get('low_stock_count', 'N/A')}")
        else:
            content.update("No data")
