from __future__ import annotations

import logging

import udi_interface
from nodes.controller import SensorPushController

LOGGER = udi_interface.LOGGER


def _dedupe_logger_handlers(logger: logging.Logger) -> None:
    seen: set[tuple[str, str]] = set()
    for handler in list(logger.handlers):
        destination = ""
        if hasattr(handler, "baseFilename"):
            destination = str(getattr(handler, "baseFilename", ""))
        elif hasattr(handler, "stream"):
            destination = repr(getattr(handler, "stream", ""))

        key = (handler.__class__.__name__, destination)
        if key in seen:
            logger.removeHandler(handler)
        else:
            seen.add(key)

    # If this logger has its own handlers, avoid duplicate emission via parents.
    if logger.handlers:
        logger.propagate = False


def _dedupe_all_loggers() -> None:
    _dedupe_logger_handlers(logging.getLogger())
    _dedupe_logger_handlers(logging.getLogger("udi_interface"))
    _dedupe_logger_handlers(LOGGER)

    # udi_interface defines multiple child loggers; de-dupe each one explicitly.
    manager = logging.root.manager
    for name, obj in manager.loggerDict.items():
        if name.startswith("udi_interface") and isinstance(obj, logging.Logger):
            _dedupe_logger_handlers(obj)


def _set_mqtt_logger_silent() -> None:
    """Keep MQTT driver update messages suppressed by default."""
    logging.getLogger("udi_interface.interface").setLevel(logging.WARNING)


def main() -> None:
    polyglot = udi_interface.Interface([])
    polyglot.start()
    _dedupe_all_loggers()
    _set_mqtt_logger_silent()

    controller = SensorPushController(polyglot)
    polyglot.subscribe(polyglot.START, controller.start)
    polyglot.subscribe(polyglot.POLL, controller.poll)
    stop_event = getattr(polyglot, "STOP", None)
    if stop_event is not None:
        polyglot.subscribe(stop_event, controller.stop)
    polyglot.subscribe(polyglot.CUSTOMPARAMS, controller.custom_params_changed)
    polyglot.addNode(controller, conn_status=True)

    polyglot.ready()
    polyglot.runForever()


if __name__ == "__main__":
    main()
