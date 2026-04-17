import json
import os
from typing import Any

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "data", "config.json")


def load_config() -> dict:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_config(config: dict) -> None:
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


def get(key: str, default: Any = None) -> Any:
    return load_config().get(key, default)


def set_value(key: str, value: Any) -> None:
    config = load_config()
    config[key] = value
    save_config(config)


def add_group(group_id: int, title: str = "") -> bool:
    config = load_config()
    groups = config.get("groups", [])
    if any(g["id"] == group_id for g in groups):
        return False
    groups.append({"id": group_id, "title": title})
    config["groups"] = groups
    save_config(config)
    return True


def remove_group(group_id: int) -> bool:
    config = load_config()
    groups = config.get("groups", [])
    new_groups = [g for g in groups if g["id"] != group_id]
    if len(new_groups) == len(groups):
        return False
    config["groups"] = new_groups
    save_config(config)
    return True


def get_groups() -> list[dict]:
    return load_config().get("groups", [])


def set_message(text: str, media_path: str | None = None) -> None:
    config = load_config()
    config["message"] = {"text": text, "media_path": media_path}
    save_config(config)


def get_message() -> dict:
    return load_config().get("message", {"text": "", "media_path": None})


def set_schedule(enabled: bool, interval_hours: int = 6, start_time: str = "09:00") -> None:
    config = load_config()
    config["schedule"] = {
        "enabled": enabled,
        "interval_hours": interval_hours,
        "start_time": start_time,
    }
    save_config(config)


def get_schedule() -> dict:
    return load_config().get("schedule", {})
