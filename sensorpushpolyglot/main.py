from __future__ import annotations

import udi_interface

from sensorpushpolyglot.nodes.controller import SensorPushController

LOGGER = udi_interface.LOGGER


def _register_admin_params(polyglot: udi_interface.Interface) -> None:
    typed_params = udi_interface.Custom(polyglot, "customtypedparams")
    typed_params.load(
        [
            {
                "name": "sensorpush_email",
                "title": "SensorPush Email",
                "desc": "Email used to sign in to SensorPush Cloud API.",
                "isRequired": True,
            },
            {
                "name": "sensorpush_password",
                "title": "SensorPush Password",
                "desc": "Password used to sign in to SensorPush Cloud API.",
                "isRequired": True,
            },
            {
                "name": "use_short_poll_updates",
                "title": "Use Short Poll Updates",
                "desc": "Set true for 1-minute test updates; false for 5-minute production updates.",
                "isRequired": False,
            },
            {
                "name": "sample_limit",
                "title": "Sample Limit",
                "desc": "Number of samples to request per sensor each poll (1-100).",
                "isRequired": False,
            },
        ],
        True,
    )


def main() -> None:
    polyglot = udi_interface.Interface([])
    polyglot.start()
    _register_admin_params(polyglot)
    polyglot.setCustomParamsDoc()

    controller = SensorPushController(polyglot)
    polyglot.subscribe(polyglot.START, controller.start)
    polyglot.subscribe(polyglot.CUSTOMPARAMS, controller.custom_params_changed)
    custom_typed_data_event = getattr(polyglot, "CUSTOMTYPEDDATA", None)
    if custom_typed_data_event is not None:
        polyglot.subscribe(custom_typed_data_event, controller.custom_typed_data_changed)
    polyglot.addNode(controller, conn_status=True)

    polyglot.ready()
    polyglot.runForever()


if __name__ == "__main__":
    main()
