from __future__ import annotations

from typing import Any

from udi_interface import Node


class SensorPushGatewayNode(Node):
    id = "sp_gateway"

    drivers = [
        {"driver": "ST", "value": 0, "uom": 25},
    ]

    commands = {}

    def __init__(self, polyglot: Any, address: str, name: str, primary: str) -> None:
        super().__init__(polyglot, primary, address, name)

    def set_online(self, online: bool) -> None:
        self.setDriver("ST", 1 if online else 0)
        self.reportDrivers()