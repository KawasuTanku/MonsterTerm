# MonsterTerm

**Terminal dashboard for the Monster P&L tracker.**

MonsterTerm is a TUI application that connects to your Monster instance via its read-only API. View stats, inventory, and monthly reports from the terminal.

## Installation

```bash
git clone https://github.com/KawasuTanku/MonsterTerm.git
cd MonsterTerm
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Configuration

Copy `.env.example` to `.env` and fill in your Monster URL and API token:

```bash
cp .env.example .env
# Edit .env with your settings
```

Or set environment variables directly:

```bash
export MONSTER_URL="https://your-monster-instance.com"
export MONSTER_TOKEN="your_api_token"
```

## Usage

```bash
monsterterm
# or
MonsterTerm
```

## Controls

- **D** — Dashboard view (stats summary)
- **I** — Inventory list
- **R** — Monthly reports
- **?** — Help
- **Q** — Quit

## Integration with TankuOS

MonsterTerm integrates with TankuOS as a store app. When installed through TankuOS:

- Theme syncs automatically via `TANKUOS_THEME` environment variable
- Credentials are stored in `~/.tankuos/Apps/MonsterTerm/configs/.env`
- Supports retro Pascal, midnight, nord, and gruvbox themes

## Requirements

- Python 3.10+
- textual
- requests

## License

MIT — same as TankuOS.
