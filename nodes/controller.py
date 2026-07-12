from __future__ import annotations

import hashlib
import json
import math
import os
from datetime import datetime, timezone
from typing import Any, Dict, Iterable

import requests
import udi_interface
from udi_interface import Node

from config import RuntimeConfig
from nodes.gateway import SensorPushGatewayNode
from nodes.sensor import SensorPushSensorNode
from sensorpush_api import SensorPushApiError, SensorPushClient

LOGGER = udi_interface.LOGGER

class SensorPushController(Node):
    id = "controller"
    SENSOR_ADDR_PREFIX = "sp_"
    GATEWAY_ADDR_PREFIX = "gw_"
    PARAM_NOTICE_KEY = "sensorpush_required_params"

    drivers = [
        {"driver": "ST", "value": 0, "uom": 25},
        {"driver": "GV0", "value": 0, "uom": 56},
        {"driver": "GV1", "value": 0, "uom": 56},
        {"driver": "GV2", "value": 0, "uom": 56},
    ]

    commands = {
        "QUERY": "query",
    }

    def __init__(self, polyglot: Any) -> None:
        super().__init__(polyglot, "controller", "controller", "SensorPush Controller")
        self.poly = polyglot
        self._runtime_config = RuntimeConfig()
        self._client: SensorPushClient | None = None
        self._last_poll_utc: datetime | None = None
        self._sensor_last_seen_utc: Dict[str, datetime] = {}
        self._sensor_stale_alerted: set[str] = set()
        self._gateway_defs_refreshed = False
        self._customparams_bootstrapped = False
        self._reload_config()

    def _set_notice(self, message: str) -> None:
        adder = getattr(self.poly, "addNotice", None)
        if callable(adder):
            adder(message, self.PARAM_NOTICE_KEY)

    def _clear_notice(self) -> None:
        remover = getattr(self.poly, "removeNotice", None)
        if callable(remover):
            remover(self.PARAM_NOTICE_KEY)

    def _ensure_required_params(self) -> bool:
        params = self._get_custom_params()
        email = str(params.get("sensorpush_email") or "").strip()
        account_token = str(params.get("sensorpush_password") or "").strip()

        if not email or not account_token:
            message = "Set required custom params: sensorpush_email, sensorpush_password."
            self._set_notice(message)
            self.setDriver("ST", 0)
            return False

        self._clear_notice()
        return True

    @classmethod
    def _sensor_address(cls, sensor_id: str) -> str:
        digest = hashlib.md5(sensor_id.encode("utf-8")).hexdigest()[:10]
        return f"{cls.SENSOR_ADDR_PREFIX}{digest}"

    @classmethod
    def _gateway_address(cls, gateway_id: str) -> str:
        digest = hashlib.md5(gateway_id.encode("utf-8")).hexdigest()[:10]
        return f"{cls.GATEWAY_ADDR_PREFIX}{digest}"

    def _get_existing_nodes(self) -> Dict[str, Any]:
        return getattr(self.poly, "nodes", {})

    def _get_node(self, address: str) -> Any | None:
        return self._get_existing_nodes().get(address)

    def _delete_node(self, address: str) -> None:
        self.poly.delNode(address)

    def _get_custom_params(self) -> Dict[str, str]:
        """Fetch current customParams from PG3."""
        config = getattr(self.poly, "polyConfig", {})
        params = config.get("customParams", {})
        return {str(k): str(v) for k, v in params.items()}

    def _reload_config(self, custom_params: Dict[str, str] | None = None) -> None:
        if custom_params is None:
            custom_params = self._get_custom_params()
        self._runtime_config = RuntimeConfig.from_sources(custom_params, os.environ)

        if self._runtime_config.email and self._runtime_config.account_token:
            self._client = SensorPushClient(
                email=self._runtime_config.email,
                account_token=self._runtime_config.account_token,
            )
        else:
            self._client = None

    def start(self, command: Dict[str, Any] | None = None) -> None:
        if not self._ensure_required_params():
            return
        self._run_poll_cycle("startup")

    def custom_params_changed(self, params: Dict[str, Any] | None = None) -> None:
        """Handles updates from the Configuration page."""
        self._reload_config()
        self._ensure_required_params()
        self.poly.updateProfile()
        LOGGER.info("Custom params updated.")
        self._run_poll_cycle("config_update")

    def _run_poll_cycle(self, reason: str) -> None:
        if not self._client:
            self.setDriver("ST", 0)
            return
        
        # ... (rest of your existing polling logic remains the same) ...
        try:
            sensors = self._client.list_sensors() or {}
            gateways = self._client.list_gateways() or {}
            
            self._sync_gateway_nodes(gateways)
            # ... sync sensors ...
            
            self.setDriver("ST", 1)
            self.reportDrivers()
        except Exception:
            self.setDriver("ST", 0)
            LOGGER.exception("Error during poll cycle")

    def poll(self, command: Dict[str, Any] | None = None) -> None:
        if self._runtime_config.use_short_poll_updates:
            self.shortPoll(command)
        else:
            self.longPoll(command)

    def shortPoll(self, command: Dict[str, Any] | None = None) -> None:
        if self._runtime_config.use_short_poll_updates:
            self._run_poll_cycle("shortPoll")

    def longPoll(self, command: Dict[str, Any] | None = None) -> None:
        if not self._runtime_config.use_short_poll_updates:
            self._run_poll_cycle("longPoll")

    def query(self, command: Dict[str, Any] | None = None) -> bool:
        self._run_poll_cycle("query")
        return True