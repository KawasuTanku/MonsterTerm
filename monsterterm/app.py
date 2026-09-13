"""MonsterTerm — terminal dashboard for the Monster P&L tracker."""

from __future__ import annotations

from rich.text import Text
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, Container
from textual.screen import Screen, ModalScreen
from textual.widgets import Static, Button
from textual.binding import Binding

from monsterterm import __version__
from monsterterm.api import MonsterConfig, fetch_stats, fetch_inventory, fetch_summary, fetch_monthly


class StyledStatic(Static):
    """Static widget with retro Pascal styling (blue bg, white/yellow text)."""

    def __init__(self, content: str = "", **kwargs):
        text = Text()
        text.append(" ")
        text.append(content if content else " ", style="white on #0000aa")
        text.append(" ")
        super().__init__(text, **kwargs)

    def update_content(self, content: str) -> None:
        text = Text()
        text.append(" ")
        text.append(content, style="white on #0000aa")
        text.append(" ")
        self.update(text)


class MenuButton(Button):
    """Button styled for retro Pascal menubar."""

    def __init__(self, label: str, **kwargs):
        super().__init__(label, **kwargs)
        self.styles.background = "#000088"
        self.styles.color = "#ffff55"
        self.styles.border = "none"


class StatusStatic(Static):
    """Status bar static (blue bg, yellow text)."""

    def __init__(self, content: str = "", **kwargs):
        text = Text()
        text.append(content, style="#ffff55 on #000088")
        super().__init__(text, **kwargs)


class DashboardScreen(Screen):
    """Main dashboard view."""

    BINDINGS = [
        Binding("d", "dashboard", "Dashboard"),
        Binding("i", "inventory", "Inventory"),
        Binding("r", "reports", "Reports"),
        Binding("q", "quit", "Quit"),
        Binding("?", "help", "Help"),
    ]

    def __init__(self, cfg: MonsterConfig, **kwargs):
        super().__init__(**kwargs)
        self.cfg = cfg

    def compose(self) -> ComposeResult:
        with Container(id="desktop"):
            with Horizontal(id="menubar"):
                yield StyledStatic("MonsterTerm", id="menu-title")
                yield MenuButton("Dashboard", id="menu-dashboard", classes="menu-btn")
                yield MenuButton("Inventory", id="menu-inventory", classes="menu-btn")
                yield MenuButton("Reports", id="menu-reports", classes="menu-btn")
                yield MenuButton("Help", id="menu-help", classes="menu-btn")
            with Container(id="workspace"):
                yield StyledStatic("Loading...", id="content")
            with Horizontal(id="statusbar"):
                yield StatusStatic(" D Dashboard", id="stat-dashboard")
                yield StatusStatic(" I Inventory", id="stat-inventory")
                yield StatusStatic(" R Reports", id="stat-reports")
                yield StatusStatic(" ? Help", id="stat-help")
                yield StatusStatic(f"v{__version__} ", id="stat-version")

    def on_mount(self) -> None:
        self.refresh_data()

    def refresh_data(self) -> None:
        content = self.query_one("#content", StyledStatic)
        stats = fetch_stats(self.cfg)
        inventory = fetch_inventory(self.cfg)
        summary = fetch_summary(self.cfg)

        lines = []
        if stats:
            lines.append("┌─── Stats ───────────────────────────────┐")
            lines.append(f"│ Low stock items: {stats.get('low_stock_count', 'N/A'):<22} │")
            lines.append(f"│ Total stock value: ${stats.get('total_stock_value', 0):>10,.2f}       │")
            lines.append(f"│ Recent txns (7d): {stats.get('recent_transactions_7d', 'N/A'):<22} │")
            lines.append("└────────────────────────────────────────┘")
        if summary:
            lines.append("┌─── Summary ─────────────────────────────┐")
            lines.append(f"│ Total sales: ${summary.get('total_sales', 0):>10,.2f}             │")
            lines.append(f"│ Total expenses: ${summary.get('total_expenses', 0):>10,.2f}         │")
            lines.append(f"│ Net profit: ${summary.get('net_profit', 0):>10,.2f}             │")
            lines.append("└────────────────────────────────────────┘")
        if inventory:
            low = [i for i in inventory if i.get("needsReorder")]
            lines.append(f"Inventory: {len(inventory)} items, {len(low)} low stock")

        content.update_content("\n".join(lines) if lines else "No data available. Check MONSTER_URL and MONSTER_TOKEN.")

    def action_dashboard(self) -> None:
        self.refresh_data()

    def action_inventory(self) -> None:
        content = self.query_one("#content", StyledStatic)
        inventory = fetch_inventory(self.cfg)
        if not inventory:
            content.update_content("No inventory data")
            return
        lines = ["┌─── Inventory ───────────────────────────┐"]
        for item in inventory[:20]:
            qty = item.get("qtyOnHand", 0)
            name = item.get("name", "unknown")[:20]
            low = " LOW" if item.get("needsReorder") else ""
            lines.append(f"│ {name:<20} qty: {qty:>4}{low:<6} │")
        lines.append("└────────────────────────────────────────┘")
        content.update_content("\n".join(lines))

    def action_reports(self) -> None:
        content = self.query_one("#content", StyledStatic)
        monthly = fetch_monthly(self.cfg)
        if not monthly:
            content.update_content("No monthly data")
            return
        lines = ["┌─── Monthly Report ──────────────────────┐"]
        for m in monthly[-6:]:
            month = m.get("month", "?")[:7]
            sales = m.get("sales", 0)
            lines.append(f"│ {month:<10} sales: ${sales:>10,.2f}       │")
        lines.append("└────────────────────────────────────────┘")
        content.update_content("\n".join(lines))

    def action_help(self) -> None:
        self.app.push_screen(HelpScreen())

    def on_button_pressed(self, event: Button.Pressed) -> None:
        btn = event.button.id
        if btn == "menu-dashboard":
            self.action_dashboard()
        elif btn == "menu-inventory":
            self.action_inventory()
        elif btn == "menu-reports":
            self.action_reports()
        elif btn == "menu-help":
            self.action_help()


class HelpScreen(ModalScreen):
    """Help overlay."""

    def compose(self) -> ComposeResult:
        with Vertical(id="help-box"):
            yield StyledStatic("MonsterTerm Help\n\nD - Dashboard view\nI - Inventory list\nR - Monthly reports\n? - This help\nQ - Quit\n\nPress any key to close")

    def on_key(self, event) -> None:
        self.dismiss(None)

    def on_click(self, event) -> None:
        self.dismiss(None)


class MonsterTermApp(App):
    """Main MonsterTerm application."""

    CSS = """
    #desktop {
        height: 1fr;
        layout: vertical;
        background: #0000aa;
    }
    #menubar {
        height: 1;
        background: #000088;
    }
    #menu-title {
        width: auto;
        color: #ffff55;
        text-style: bold;
    }
    .menu-btn {
        min-width: 8;
        height: 1;
        border: none;
        padding: 0 1;
        background: #000088;
        color: #ffff55;
    }
    .menu-btn:focus {
        background: #ffff55;
        color: #0000aa;
    }
    #workspace {
        height: 1fr;
        padding: 1;
        background: #0000aa;
    }
    #content {
        height: auto;
        color: #ffffff;
    }
    #statusbar {
        height: 1;
        background: #000088;
    }
    #statusbar Static {
        width: auto;
        color: #ffff55;
    }
    #stat-version {
        dock: right;
    }
    #help-box {
        width: 60;
        height: auto;
        padding: 1;
        background: #0000cc;
        color: #ffffff;
        border: solid #ffff55;
        align: center middle;
    }
    """

    def __init__(self):
        super().__init__()
        self.cfg = MonsterConfig.from_env()

    def compose(self) -> ComposeResult:
        yield DashboardScreen(self.cfg)
