from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AIMode:
    key: str
    label: str
    enabled: bool
    message: str


AI_MODES = [
    AIMode(
        key="rules",
        label="Rules/templates only",
        enabled=True,
        message="Uses local rules/templates. No resume or job text leaves your machine.",
    ),
    AIMode(
        key="local",
        label="Local AI",
        enabled=False,
        message="Selectable, but local AI is not configured yet. For now it falls back to rules/templates only.",
    ),
    AIMode(
        key="api",
        label="API AI",
        enabled=False,
        message="Selectable, but API AI is not configured yet. For now it falls back to rules/templates only.",
    ),
]


def resolve_ai_mode(key_or_label: str) -> AIMode:
    normalized = key_or_label.strip().lower()
    for mode in AI_MODES:
        if normalized in {mode.key.lower(), mode.label.lower()}:
            return mode
    return AI_MODES[0]
