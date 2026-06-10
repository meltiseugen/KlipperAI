from __future__ import annotations

import os
import subprocess
from pathlib import Path


def test_octoeverywhere_patch_round_trip_preserves_unrelated_changes(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    script = repo_root / "integrations/octoeverywhere/apply-local-klipperai-route-patch.sh"
    oe_root = tmp_path / "octoeverywhere"
    router = oe_root / "moonraker_octoeverywhere/moonrakerapirouter.py"
    ui = oe_root / "moonraker_octoeverywhere/static/oe-ui.js"
    router.parent.mkdir(parents=True)
    ui.parent.mkdir(parents=True)

    original_router = (
        "from typing import Optional\n\n"
        "class MoonrakerApiRouter:\n"
        "    def __init__(self):\n"
        '        self.Logger.info("MoonrakerApiRouter using bound to moonraker at "+self.MoonrakerHostAndPortStr)\n\n'
        "    # !! Interface Function !!\n"
        "    def MapRelativePathToAbsolutePathIfNeeded(self, relativeUrl, protocol):\n"
        "            relativeUrlLower = relativeUrl.lower()\n"
        "            return None\n\n"
        "# unrelated local router change\n"
    )
    original_ui = (
        "    oe_detect_oe_loaded_index_and_inject_helpers();\n"
        "    // unrelated local UI change\n"
    )
    router.write_text(original_router, encoding="utf-8")
    ui.write_text(original_ui, encoding="utf-8")

    env = {
        **os.environ,
        "KLIPPERAI_NO_SUDO": "1",
        "KLIPPERAI_STATE_DIR": str(tmp_path / "state"),
    }
    subprocess.run(
        ["sh", str(script), "--oe-root", str(oe_root)],
        check=True,
        env=env,
        capture_output=True,
        text=True,
    )

    assert "KlipperAI local route patch init start" in router.read_text(encoding="utf-8")
    assert "KlipperAI local route patch start" in ui.read_text(encoding="utf-8")

    subprocess.run(
        ["sh", str(script), "--oe-root", str(oe_root), "--restore-original"],
        check=True,
        env=env,
        capture_output=True,
        text=True,
    )

    assert router.read_text(encoding="utf-8") == original_router
    assert ui.read_text(encoding="utf-8") == original_ui
