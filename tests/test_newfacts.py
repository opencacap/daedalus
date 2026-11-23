import json
import subprocess
import tempfile
import unittest
from pathlib import Path


SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "plugins/daedalus-writing/skills/natural-japanese/scripts/newfacts.py"
)


class NewFactsTest(unittest.TestCase):
    def test_changed_percentages_and_their_source_lines(self):
        original = "前期は１５％です。\n製品はWebGPUです。\n開始は2018/3です。"
        revised = "前期は１５％です。\n今期は５ ％です。\n製品はGPUです。\n開始は2018年3月です。"
        with tempfile.TemporaryDirectory() as tmp:
            before = Path(tmp) / "original.md"
            after = Path(tmp) / "revised.md"
            before.write_text(original, encoding="utf-8")
            after.write_text(revised, encoding="utf-8")
            output = subprocess.check_output(
                ["uv", "run", str(SCRIPT), str(before), str(after), "--json"],
                text=True,
                encoding="utf-8",
            )

        self.assertEqual(
            json.loads(output)["new_items"],
            [{"word": "5%", "lines": [{"line": 2, "text": "今期は５ ％です。"}]}],
        )
