"""MonsterTerm — terminal dashboard for the Monster P&L tracker."""

from __future__ import annotations

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, Container
from textual.screen import Screen, ModalScreen
from textual.widgets import Static, Button, Log
from textual.binding import Binding

from monsterterm import __version__
from monsterterm.api import MonsterConfig, fetch_stats, fetch_inventory, fetch_summary, fetch_monthly


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
        yield Static("MonsterTerm", id="menu-title")
        yield Button("Dashboard", id="menu-dashboard")
        yield Button("Inventory", id="menu-inventory")
        yield Button("Reports", id="menu-reports")
        yield Button("Help", id="menu-help")
        yield Log(id="content")
        yield Static(" D Dashboard  I Inventory  R Reports  ? Help", id="statusbar")
        yield Static(f"v{__version__}", id="stat-version")

    def on_mount(self) -> None:
        self.refresh_data()

    def refresh_data(self) -> None:
        content = self.query_one("#content", Log)
        content.clear()
        stats = fetch_stats(self.cfg)
        inventory = fetch_inventory(self.cfg)
        summary = fetch_summary(self.cfg)

        if stats:
            content.write(" STATS")
            content.write(f"   Low stock items: {stats.get('low_stock_count', 'N/A')}")
            content.write(f"   Total stock value: ${stats.get('total_stock_value', 0):,.2f}")
            content.write(f"   Recent txns (7d): {stats.get('recent_transactions_7d', 'N/A')}")
            content.write("")
        if summary:
            content.write(" SUMMARY")
            content.write(f"   Total sales: ${summary.get('total_sales', 0):,.2f}")
            content.write(f"   Total expenses: ${summary.get('total_expenses', 0):,.2f}")
            content.write(f"   Net profit: ${summary.get('net_profit', 0):,.2f}")
            content.write("")
        if inventory:
            low = [i for i in inventory if i.get("needsReorder")]
            content.write(f"Inventory: {len(inventory)} items, {len(low)} low stock")

        if not stats and not summary and not inventory:
            content.write("No data available")

    def action_dashboard(self) -> None:
        self.refresh_data()

    def action_inventory(self) -> None:
        content = self.query_one("#content", Log)
        content.clear()
        inventory = fetch_inventory(self.cfg)
        if not inventory:
            content.write("No inventory data")
            return
        content.write("INVENTORY")
        for item in inventory[:20]:
            qty = item.get("qtyOnHand", 0)
            name = item.get("name", "unknown")[:20]
            low = " LOW" if item.get("needsReorder") else ""
            content.write(f"  {name:<20} qty: {qty:>4}{low}")

    def action_reports(self) -> None:
        content = self.query_one("#content", Log)
        content.clear()
        monthly = fetch_monthly(self.cfg)
        if not monthly:
            content.write("No monthly data")
            return
        content.write("MONTHLY REPORT")
        for m in monthly[-6:]:
            month = m.get("month", "?")[:7]
            sales = m.get("sales", 0)
            content.write(f"  {month:<10} sales: ${sales:>10,.2f}")

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
        yield Static("MonsterTerm Help\n\nD - Dashboard\nI - Inventory\nR - Reports\n? - Help\nQ - Quit\n\nPress any key to close")

    def on_key(self, event) -> None:
        self.dismiss(None)


class MonsterTermApp(App):
    """Main MonsterTerm application."""

    CSS = """
    #menu-title { height: 1; text-style: bold; padding: 0 1; }
    #menu-dashboard { height: 1; border: none; padding: 0 1; }
    #menu-inventory { height: 1; border: none; padding: 0 1; }
    #menu-reports { height: 1; border: none; padding: 0 1; }
    #menu-help { height: 1; border: none; padding: 0 1; }
    #content { height: 1fr; padding: 1; }
    #statusbar { height: 1; padding: 0 1; }
    #stat-version { height: 1; dock: right; padding: 0 1; }
    Screen { layout: vertical; }
    """

    def __init__(self):
        super().__init__()
        self.cfg = MonsterConfig.from_env()
        self.dark = False

    def compose(self) -> ComposeResult:
        yield DashboardScreen(self.cfg)
