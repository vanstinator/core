"""Tests for the melnor integration."""

from __future__ import annotations

from contextlib import contextmanager
from unittest.mock import AsyncMock, MagicMock, Mock, patch

from melnor_bluetooth.device import Device

from homeassistant.components.melnor.const import CONF_VALVE_COUNT, DOMAIN
from homeassistant.const import CONF_MAC, CONF_NAME
from homeassistant.helpers.typing import HomeAssistantType

from tests.common import MockConfigEntry

FAKE_MAC = "ABCABCABCABC"
FAKE_MODEL = "12345"
FAKE_NAME = "4 Valve Timer"
FAKE_NUM_VALVES = 4
FAKE_SENSOR_EXISTS = False

FAKE_DEVICE = Device(
    mac=FAKE_MAC,
    model=FAKE_MODEL,
    sensor=FAKE_SENSOR_EXISTS,
    valves=FAKE_NUM_VALVES,
)

FAKE_DEVICE_2 = Device(
    mac="ABCABCABCADB",
    model=FAKE_MODEL,
    sensor=FAKE_SENSOR_EXISTS,
    valves=FAKE_NUM_VALVES,
)

TEST_CONNECTION = {CONF_MAC: FAKE_MAC}


async def setup_integration(
    hass: HomeAssistantType,
) -> MockConfigEntry:
    """Mock ConfigEntry in Home Assistant."""

    entry = MockConfigEntry(
        domain=DOMAIN,
        unique_id=FAKE_MAC,
        data={
            CONF_MAC: FAKE_MAC,
            CONF_VALVE_COUNT: FAKE_NUM_VALVES,
            CONF_NAME: FAKE_NAME,
        },
    )

    entry.add_to_hass(hass)

    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    return entry


def _mocked_device(device: Device) -> Device:
    device = MagicMock(auto_spec=Device, name=FAKE_NAME)

    device.connect = AsyncMock()
    device.disconnect = AsyncMock()
    device.is_connected = Mock(return_value=True)
    device.mac = Mock(return_value=FAKE_MAC)
    device.name = Mock(return_value=FAKE_NAME)
    device.valve_count = Mock(return_value=FAKE_NUM_VALVES)

    return device


def _patch_scanner(
    devices: list[Device] = [],
):  # pylint: disable=dangerous-default-value
    @contextmanager
    def _patcher():
        def fake_scanner(callback, scan_timeout_seconds):

            if devices.__len__() > 0:
                for device in devices:
                    callback(device)

        with patch(
            "homeassistant.components.melnor.discovery.scanner",
            side_effect=fake_scanner,
        ):
            yield

    return _patcher()


def _patch_device(fake_device: Device | None = None):
    @contextmanager
    def _patcher():
        if fake_device is not None:
            device = _mocked_device(fake_device)
        else:
            device = _mocked_device(FAKE_DEVICE)

        with patch(
            "homeassistant.components.melnor.Device", return_value=device
        ), patch(
            "homeassistant.components.melnor.config_flow.Device",
            return_value=device,
        ):
            yield

    return _patcher()


# def _patch_discovery():
#     @contextmanager
#     def _patcher():
#         with patch(
#             "homeassistant.components.melnor.discovery.scanner",
#             return_value=[DiscoveredBulb(FAKE_IP, FAKE_MAC)],
#         ):
#             yield

#     return _patcher()


# async def async_setup_integration(
#     hass, wizlight=None, device=None, extended_white_range=None, bulb_type=None
# ):
#     """Set up the integration with a mock device."""
#     entry = MockConfigEntry(
#         domain=DOMAIN,
#         unique_id=FAKE_MAC,
#         data={CONF_HOST: FAKE_IP},
#     )
#     entry.add_to_hass(hass)
#     bulb = wizlight or _mocked_wizlight(device, extended_white_range, bulb_type)
#     with _patch_discovery(), _patch_wizlight(device=bulb):
#         await async_setup_component(hass, DOMAIN, {DOMAIN: {}})
#         await hass.async_block_till_done()
#     return bulb, entry


# async def async_push_update(hass, device, params):
#     """Push an update to the device."""
#     device.state = PilotParser(params)
#     device.status = params.get("state")
#     device.push_callback(device.state)
#     await hass.async_block_till_done()
