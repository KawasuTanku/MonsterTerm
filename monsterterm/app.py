"""MonsterTerm — terminal dashboard for the Monster P&L tracker."""

from __future__ import annotations

from rich.text import Text
from textual.app import App, ComposeResult
from textual.widgets import Static
from textual.binding import Binding

from monsterterm import __version__
from monsterterm.api import MonsterConfig, fetch_stats, fetch_inventory, fetch_summary, fetch_monthly


def build_screen(title: str, sections: list[tuple[str, list[str]]], term_width: int = 80) -> Text:
    """Build a full-screen Text with retro Pascal styling."""
    t = Text()

    # Menubar
    menubar = Text()
    menubar.append(" " + title, style="#ffff55 on #000088")
    menubar.append(" " * max(1, term_width - len(title) - 1), style="on #000088")
    t.append_text(menubar)
    t.append("\n")

    # Content area
    line_count = 0
    for heading, items in sections:
        if heading:
            t.append(" " + heading, style="white on #0000aa")
            t.append(" " * max(1, term_width - len(heading) - 1), style="on #0000aa")
            t.append("\n")
            line_count += 1
        for item in items:
            t.append("   " + item, style="white on #0000aa")
            t.append(" " * max(1, term_width - len(item) - 3), style="on #0000aa")
            t.append("\n")
            line_count += 1

    # Fill remaining lines
    while line_count < 45:
        t.append(" " * term_width, style="on #0000aa")
        t.append("\n")
        line_count += 1

    # Statusbar
    status = Text()
    status.append(" D Dashboard   I Inventory   R Reports   ? Help ", style="#ffff55 on #000088")
    status.append(" " * max(1, term_width - 50 - len(__version__) - 2), style="on #000088")
    status.append(f"v{__version__} ", style="#ffff55 on #000088")
    t.append_text(status)

    return t


class MonsterTermApp(App):
    """Main MonsterTerm application."""

    BINDINGS = [
        Binding("d", "dashboard", "Dashboard"),
        Binding("i", "inventory", "Inventory"),
        Binding("r", "reports", "Reports"),
        Binding("?", "help", "Help"),
    ]

    def compose(self) -> ComposeResult:
        yield Static("", id="screen")

    def on_resize(self, event) -> None:
        self.refresh_data()

    def on_mount(self) -> None:
        self.refresh_data()

    def _term_width(self) -> int:
        return self.size.width if self.size and self.size.width > 0 else 80

    def _term_height(self) -> int:
        return self.size.height if self.size and self.size.height > 0 else 49

    def _build_dashboard(self) -> None:
        cfg = MonsterConfig.from_env()
        stats = fetch_stats(cfg)
        inventory = fetch_inventory(cfg)
        summary = fetch_summary(cfg)

        sections = []
        if stats:
            sections.append(("STATS", [
                f"Low stock items: {stats.get('low_stock_count', 'N/A')}",
                f"Total stock value: ${stats.get('total_stock_value', 0):,.2f}",
                f"Recent txns (7d): {stats.get('recent_transactions_7d', 'N/A')}",
            ]))
        if summary:
            sections.append(("SUMMARY", [
                f"Total sales: ${summary.get('revenue', 0):,.2f}",
                f"Total expenses: ${summary.get('expenses', 0):,.2f}",
                f"Net profit: ${summary.get('net', 0):,.2f}",
            ]))
        if inventory:
            low = [i for i in inventory if i.get("needs_reorder")]
            sections.append(("", [f"Inventory: {len(inventory)} items, {len(low)} low stock"]))

        if not sections:
            sections = [("No data", [])]

        screen = self.query_one("#screen", Static)
        screen.update(build_screen("MonsterTerm", sections, self._term_width()))

    def _build_inventory(self) -> None:
        cfg = MonsterConfig.from_env()
        inventory = fetch_inventory(cfg)
        sections = []
        if inventory:
            items = []
            for item in inventory[:20]:
                qty = item.get("qty_on_hand", 0)
                name = item.get("name", "unknown")[:20]
                low = " LOW" if item.get("needs_reorder") else ""
                items.append(f"{name:<20} qty: {qty:>4}{low}")
            sections = [("INVENTORY", items)]
        else:
            sections = [("No inventory data", [])]
        screen = self.query_one("#screen", Static)
        screen.update(build_screen("MonsterTerm - Inventory", sections, self._term_width()))

    def _build_reports(self) -> None:
        cfg = MonsterConfig.from_env()
        monthly = fetch_monthly(cfg)
        sections = []
        if monthly:
            items = []
            for m in monthly[-6:]:
                month = m.get("period", "?")[:7]
                sales = m.get("revenue", 0)
                items.append(f"{month:<10} sales: ${sales:>10,.2f}")
            sections = [("MONTHLY REPORT", items)]
        else:
            sections = [("No monthly data", [])]
        screen = self.query_one("#screen", Static)
        screen.update(build_screen("MonsterTerm - Reports", sections, self._term_width()))

    def _build_help(self) -> None:
        sections = [("HELP", [
            "D - Dashboard view",
            "I - Inventory list",
            "R - Monthly reports",
            "? - This help",
            "Q - Quit",
        ])]
        screen = self.query_one("#screen", Static)
        screen.update(build_screen("MonsterTerm - Help", sections, self._term_width()))

    def action_dashboard(self) -> None:
        self._build_dashboard()

    def action_inventory(self) -> None:
        self._build_inventory()

    def action_reports(self) -> None:
        self._build_reports()

    def action_help(self) -> None:
        self._build_help()

    def refresh_data(self) -> None:
        self._build_dashboard()
