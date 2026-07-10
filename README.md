# SensorPush Polyglot for eISY / PG3

Starter PG3 Polyglot node server for polling SensorPush Gateway Cloud API.

## Current Scope

- Poll SensorPush cloud API endpoints.
- Default production behavior: update on PG3 long poll (5 minutes).
- Optional test behavior: update on PG3 short poll (1 minute).
- Auto-manage per-sensor child nodes (add new sensors, remove missing sensors).
- BLE support can be added later.

## Per-Sensor Node Lifecycle

Each SensorPush sensor is represented as a PG3 child node under the controller.

- New sensor appears in SensorPush: a new child node is created automatically.
- Existing sensor remains: child node values are updated.
- Sensor removed from SensorPush: corresponding child node is deleted automatically.

Child node metrics currently include:

- Temperature (F)
- Humidity (%)
- Battery voltage (V)
- Dew point (F)
- VPD (kPa)
- Signal (dBm, when provided by API)

Controller metrics include:

- Sensor Count
- Sample Count
- Stale Sensor Count

## Polling Strategy

SensorPush API documentation notes requests should not exceed once per minute.

This project supports two update modes:

- `long` (default): updates during PG3 `longPoll`.
- `short`: updates during PG3 `shortPoll`.

PG3 defaults used in `server.json`:

- `shortPoll`: 60 seconds
- `longPoll`: 300 seconds

## Configuration

Set credentials and behavior using PG3 custom parameters (or environment variables).

### Custom Parameters

- `sensorpush_email` (required)
- `sensorpush_password` (required)
- `use_short_poll_updates` (`true`/`false`, default: `false`)
- `sample_limit` (default: `1`)
- `sensor_stale_hours` (default: `24`)
- `ntfy_topic` (default: `sensorpush-alerts`)
- `ntfy_server` (optional, default: `https://ntfy.sh`)
- `ntfy_token` (optional bearer token for private ntfy topics)
- `ntfy_notify_recovery` (`true`/`false`, default: `true`)

In PG3 Admin, these are also published as typed fields on the configuration page.

Authentication mode:

- Email + password: set `sensorpush_email` and `sensorpush_password`.
- The node server exchanges credentials for OAuth access token before API calls.
- Backward compatibility: legacy `sensorpush_account_token` is still accepted.

### Environment Variables

- `SENSORPUSH_EMAIL`
- `SENSORPUSH_PASSWORD`
- `SENSORPUSH_USE_SHORT_POLL_UPDATES`
- `SENSORPUSH_SAMPLE_LIMIT`
- `SENSOR_STALE_HOURS`
- `NTFY_TOPIC`
- `NTFY_SERVER`
- `NTFY_TOKEN`
- `NTFY_NOTIFY_RECOVERY`

Backward compatibility: legacy `SENSORPUSH_ACCOUNT_TOKEN` is still accepted.

Custom parameters take precedence over environment variables.

## Stale Sensor Alerts

This node server can alert when a sensor appears to have stopped reporting.

- A sensor is considered stale when its latest sample time is older than `sensor_stale_hours`.
- If the sample payload has no timestamp field, receipt of a sample during a poll is treated as fresh.
- `ST` for that sensor is set to `Disconnected` while stale.
- `GV2` on the controller reports total stale sensors.
- ntfy notifications are sent once when stale is detected, and optionally once on recovery.

Example custom params for a 24-hour stale alert to ntfy:

- `sensor_stale_hours=24`
- `ntfy_topic=my-home-sensors`
- `ntfy_server=https://ntfy.sh`
- `ntfy_notify_recovery=true`

## Local Development

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python main.py
```

## Repo

Planned GitHub remote:

- https://github.com/awysocki/SensorPushPolyglot.git

## Next Steps

- Add robust token refresh handling using refresh token endpoint.
- Add BLE mode integration.
