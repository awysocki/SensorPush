from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


def _as_bool(value: str | bool | None, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def _as_int(value: str | int | None, default: int, minimum: int = 1) -> int:
    if value is None:
        return default
    try:
        parsed = int(str(value).strip())
    except (TypeError, ValueError):
        return default
    return max(parsed, minimum)


def _as_float(value: str | float | int | None, default: float, minimum: float = 0.0) -> float:
    if value is None:
        return default
    try:
        parsed = float(str(value).strip())
    except (TypeError, ValueError):
        return default
    return max(parsed, minimum)


@dataclass
class RuntimeConfig:
    email: str = ""
    account_token: str = ""
    use_short_poll_updates: bool = False
    sample_limit: int = 1
    sensor_stale_hours: float = 24.0
    ntfy_topic: str = ""
    ntfy_server: str = "https://ntfy.sh"
    ntfy_token: str = ""
    ntfy_notify_recovery: bool = True

    @classmethod
    def from_sources(
        cls,
        custom_params: Mapping[str, str] | None,
        env: Mapping[str, str] | None,
    ) -> "RuntimeConfig":
        custom = custom_params or {}
        environ = env or {}

        email = str(custom.get("sensorpush_email") or environ.get("SENSORPUSH_EMAIL") or "").strip()
        account_token = str(
            custom.get("sensorpush_password")
            or custom.get("sensorpush_account_token")
            or environ.get("SENSORPUSH_PASSWORD")
            or environ.get("SENSORPUSH_ACCOUNT_TOKEN")
            or ""
        ).strip()

        use_short = _as_bool(
            custom.get("use_short_poll_updates")
            if "use_short_poll_updates" in custom
            else environ.get("SENSORPUSH_USE_SHORT_POLL_UPDATES"),
            default=False,
        )

        sample_limit = _as_int(
            custom.get("sample_limit")
            if "sample_limit" in custom
            else environ.get("SENSORPUSH_SAMPLE_LIMIT"),
            default=1,
            minimum=1,
        )

        sensor_stale_hours = _as_float(
            custom.get("sensor_stale_hours")
            if "sensor_stale_hours" in custom
            else environ.get("SENSOR_STALE_HOURS"),
            default=24.0,
            minimum=0.0,
        )

        ntfy_topic = str(
            custom.get("ntfy_topic")
            or environ.get("NTFY_TOPIC")
            or "sensorpush-alerts"
        ).strip()
        ntfy_server = str(custom.get("ntfy_server") or environ.get("NTFY_SERVER") or "https://ntfy.sh").strip()
        ntfy_token = str(custom.get("ntfy_token") or environ.get("NTFY_TOKEN") or "").strip()
        ntfy_notify_recovery = _as_bool(
            custom.get("ntfy_notify_recovery")
            if "ntfy_notify_recovery" in custom
            else environ.get("NTFY_NOTIFY_RECOVERY"),
            default=True,
        )

        return cls(
            email=email,
            account_token=account_token,
            use_short_poll_updates=use_short,
            sample_limit=sample_limit,
            sensor_stale_hours=sensor_stale_hours,
            ntfy_topic=ntfy_topic,
            ntfy_server=ntfy_server,
            ntfy_token=ntfy_token,
            ntfy_notify_recovery=ntfy_notify_recovery,
        )
