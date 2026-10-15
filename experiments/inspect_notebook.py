"""Read upstream notebook configuration without executing any cells."""

import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
lock = json.loads((ROOT / "upstream.lock.json").read_text(encoding="utf-8"))
for name, repo in lock["repositories"].items():
    folder = ROOT / "upstream" / name
    actual = subprocess.check_output(
        ["git", "-C", str(folder), "rev-parse", "HEAD"], text=True
    ).strip()
    if actual != repo["commit"]:
        raise SystemExit(f"Version mismatch for {name}: {actual}")
    print(f"{name}: {actual}")

path = ROOT / "upstream/art-notebooks" / lock["notebook"]
notebook = json.loads(path.read_text(encoding="utf-8"))
markers = (
    "openpipe-art[backend]", "BASE_MODEL =", "MAX_TURNS =",
    "SMITHERY_MCP_URL =", "RULER_MODEL =", "LocalBackend(",
    "async def rollout", "await ruler_score_group(", "await backend.train(",
)
for index, cell in enumerate(notebook["cells"]):
    for line in "".join(cell.get("source", [])).splitlines():
        if any(marker in line for marker in markers):
            print(f"cell[{index}] {line.strip()}")
print("Inspection complete. No notebook cells executed.")
