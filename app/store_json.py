import json
from pathlib import Path
from typing import Any


class JsonStore:
    # JSON store (no encryption).
    # Data shape -> {site_key:{"username":str,"password":str},...}
    def __init__(self, path: Path|str = "Passwords_data.json") -> None:
        self.path = Path(path)

    def load(self) -> dict[str,Any]:
        if not self.path.exists():
            return{}
        try:
            with self.path.open("r", encoding="utf-8")as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            return{}
        
    def save(self, data: dict[str,Any]) -> None:
    # Ensure parent exists (in case you move the file later)
        if self.path.parent and not self.path.parent.exists():
            self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)