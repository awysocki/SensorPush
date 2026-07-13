from __future__ import annotations

from typing import Any

from udi_interface import Node


class SensorPushSensorNode(Node):
    id = "sensor"

    drivers = [
        {"driver": "ST", "value": 0, "uom": 25},
        {"driver": "GV0", "value": 0, "uom": 17},
        {"driver": "GV1", "value": 0, "uom": 22},
        {"driver": "GV2", "value": 0, "uom": 72},
        {"driver": "GV3", "value": 0, "uom": 17},
        {"driver": "GV4", "value": 0, "uom": 56},
        {"driver": "GV5", "value": 0, "uom": 56},
        {"driver": "GV6", "value": 0, "uom": 56},
        {"driver": "GV7", "value": 0, "uom": 17},
        {"driver": "GV8", "value": 0, "uom": 25},
    ]

    commands = {}

    def __init__(self, polyglot: Any, address: str, name: str, primary: str) -> None:
        super().__init__(polyglot, primary, address, name)

    def set_metrics(
        self,
        *,
        connected: bool,
        temperature_f: float | None,
        humidity_pct: float | None,
        battery_v: float | None,
        dew_point_f: float | None,
        vpd_kpa: float | None,
        signal_dbm: float | None,
        barometric: float | None,
        heat_index_f: float | None,
        sensor_type_index: int,
    ) -> None:
        self.setDriver("ST", 1 if connected else 0)

        if temperature_f is not None:
            self.setDriver("GV0", round(float(temperature_f), 1))
        if humidity_pct is not None:
            self.setDriver("GV1", round(float(humidity_pct), 1))
        if battery_v is not None:
            self.setDriver("GV2", round(float(battery_v), 3))
        if dew_point_f is not None:
            self.setDriver("GV3", round(float(dew_point_f), 1))
        if vpd_kpa is not None:
            self.setDriver("GV4", round(float(vpd_kpa), 2))
        if signal_dbm is not None:
            self.setDriver("GV5", round(float(signal_dbm)))
        if barometric is not None:
            self.setDriver("GV6", round(float(barometric), 2))
        if heat_index_f is not None:
            self.setDriver("GV7", round(float(heat_index_f), 1))
        self.setDriver("GV8", int(sensor_type_index))

        self.reportDrivers()
