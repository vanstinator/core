"""Test the melnor config flow."""
from unittest.mock import patch

from homeassistant import config_entries
from homeassistant.components.melnor.const import CONF_VALVE_COUNT, DOMAIN
from homeassistant.const import CONF_MAC, CONF_NAME
from homeassistant.core import HomeAssistant

from . import (
    FAKE_DEVICE,
    FAKE_DEVICE_2,
    FAKE_MAC,
    FAKE_NAME,
    FAKE_NUM_VALVES,
    _patch_device,
    _patch_scanner,
)

INTEGRATION_DISCOVERY = {
    CONF_MAC: FAKE_MAC,
    CONF_NAME: FAKE_NAME,
    CONF_VALVE_COUNT: FAKE_NUM_VALVES,
}


async def test_single_discovered(hass):
    """Test we short circuit to config entry creation."""

    with _patch_scanner(devices=[FAKE_DEVICE]), _patch_device(), patch(
        "homeassistant.components.melnor.async_setup_entry",
        return_value=True,
    ) as mock_setup_entry, patch(
        "homeassistant.components.melnor.async_setup", return_value=True
    ) as mock_setup:

        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )

        assert result["type"] == "create_entry"
        assert result["title"] == "4 Valve Timer ABCABCABCABC"
        assert result["data"] == {
            CONF_MAC: FAKE_MAC,
            CONF_NAME: "4 Valve Timer",
            CONF_VALVE_COUNT: 4,
        }

    assert len(mock_setup.mock_calls) == 1
    assert len(mock_setup_entry.mock_calls) == 1


async def test_multiple_discovered(hass: HomeAssistant):
    """Test we get the device picker."""

    with _patch_scanner([FAKE_DEVICE, FAKE_DEVICE_2]), _patch_device(), patch(
        "homeassistant.components.melnor.async_setup_entry",
        return_value=True,
    ) as mock_setup_entry, patch(
        "homeassistant.components.melnor.async_setup", return_value=True
    ) as mock_setup:

        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )

        assert result["type"] == "form"
        assert result["step_id"] == "pick_device"
        assert result["data_schema"] is not None

    assert len(mock_setup.mock_calls) == 0
    assert len(mock_setup_entry.mock_calls) == 0


# @pytest.mark.parametrize(
#     "source, data",
#     [
#         (config_entries.SOURCE_DHCP, DHCP_DISCOVERY),
#         (config_entries.SOURCE_INTEGRATION_DISCOVERY, INTEGRATION_DISCOVERY),
#     ],
# )
# async def test_discovered_by_dhcp_connection_fails(hass, source, data):
#     """Test we abort on connection failure."""
#     with patch(
#         "homeassistant.components.wiz.wizlight.getBulbConfig",
#         side_effect=WizLightTimeOutError,
#     ):
#         result = await hass.config_entries.flow.async_init(
#             DOMAIN, context={"source": source}, data=data
#         )
#         await hass.async_block_till_done()

#     assert result["type"] == RESULT_TYPE_ABORT
#     assert result["reason"] == "cannot_connect"


# @pytest.mark.parametrize(
#     "source, data, bulb_type, extended_white_range, name",
#     [
#         (
#             config_entries.SOURCE_DHCP,
#             DHCP_DISCOVERY,
#             FAKE_DIMMABLE_BULB,
#             FAKE_EXTENDED_WHITE_RANGE,
#             "WiZ Dimmable White ABCABC",
#         ),
#         (
#             config_entries.SOURCE_INTEGRATION_DISCOVERY,
#             INTEGRATION_DISCOVERY,
#             FAKE_DIMMABLE_BULB,
#             FAKE_EXTENDED_WHITE_RANGE,
#             "WiZ Dimmable White ABCABC",
#         ),
#         (
#             config_entries.SOURCE_DHCP,
#             DHCP_DISCOVERY,
#             FAKE_RGBW_BULB,
#             FAKE_EXTENDED_WHITE_RANGE,
#             "WiZ RGBW Tunable ABCABC",
#         ),
#         (
#             config_entries.SOURCE_INTEGRATION_DISCOVERY,
#             INTEGRATION_DISCOVERY,
#             FAKE_RGBW_BULB,
#             FAKE_EXTENDED_WHITE_RANGE,
#             "WiZ RGBW Tunable ABCABC",
#         ),
#         (
#             config_entries.SOURCE_DHCP,
#             DHCP_DISCOVERY,
#             FAKE_RGBWW_BULB,
#             FAKE_EXTENDED_WHITE_RANGE,
#             "WiZ RGBWW Tunable ABCABC",
#         ),
#         (
#             config_entries.SOURCE_INTEGRATION_DISCOVERY,
#             INTEGRATION_DISCOVERY,
#             FAKE_RGBWW_BULB,
#             FAKE_EXTENDED_WHITE_RANGE,
#             "WiZ RGBWW Tunable ABCABC",
#         ),
#         (
#             config_entries.SOURCE_DHCP,
#             DHCP_DISCOVERY,
#             FAKE_SOCKET,
#             None,
#             "WiZ Socket ABCABC",
#         ),
#         (
#             config_entries.SOURCE_INTEGRATION_DISCOVERY,
#             INTEGRATION_DISCOVERY,
#             FAKE_SOCKET,
#             None,
#             "WiZ Socket ABCABC",
#         ),
#     ],
# )
# async def test_discovered_by_dhcp_or_integration_discovery(
#     hass, source, data, bulb_type, extended_white_range, name
# ):
#     """Test we can configure when discovered from dhcp or discovery."""
#     with _patch_wizlight(
#         device=None, extended_white_range=extended_white_range, bulb_type=bulb_type
#     ):
#         result = await hass.config_entries.flow.async_init(
#             DOMAIN, context={"source": source}, data=data
#         )
#         await hass.async_block_till_done()

#     assert result["type"] == RESULT_TYPE_FORM
#     assert result["step_id"] == "discovery_confirm"

#     with _patch_wizlight(
#         device=None, extended_white_range=extended_white_range, bulb_type=bulb_type
#     ), patch(
#         "homeassistant.components.wiz.async_setup_entry",
#         return_value=True,
#     ) as mock_setup_entry, patch(
#         "homeassistant.components.wiz.async_setup", return_value=True
#     ) as mock_setup:
#         result2 = await hass.config_entries.flow.async_configure(
#             result["flow_id"],
#             {},
#         )
#         await hass.async_block_till_done()

#     assert result2["type"] == "create_entry"
#     assert result2["title"] == name
#     assert result2["data"] == {
#         CONF_HOST: "1.1.1.1",
#     }
#     assert len(mock_setup.mock_calls) == 1
#     assert len(mock_setup_entry.mock_calls) == 1


# @pytest.mark.parametrize(
#     "source, data",
#     [
#         (config_entries.SOURCE_DHCP, DHCP_DISCOVERY),
#         (config_entries.SOURCE_INTEGRATION_DISCOVERY, INTEGRATION_DISCOVERY),
#     ],
# )
# async def test_discovered_by_dhcp_or_integration_discovery_updates_host(
#     hass, source, data
# ):
#     """Test dhcp or discovery updates existing host."""
#     entry = MockConfigEntry(
#         domain=DOMAIN,
#         unique_id=TEST_SYSTEM_INFO["id"],
#         data={CONF_HOST: "dummy"},
#     )
#     entry.add_to_hass(hass)

#     with _patch_wizlight():
#         result = await hass.config_entries.flow.async_init(
#             DOMAIN, context={"source": source}, data=data
#         )
#         await hass.async_block_till_done()

#     assert result["type"] == RESULT_TYPE_ABORT
#     assert result["reason"] == "already_configured"
#     assert entry.data[CONF_HOST] == FAKE_IP


# async def test_setup_via_discovery(hass):
#     """Test setting up via discovery."""
#     result = await hass.config_entries.flow.async_init(
#         DOMAIN, context={"source": config_entries.SOURCE_USER}
#     )
#     await hass.async_block_till_done()
#     assert result["type"] == "form"
#     assert result["step_id"] == "user"
#     assert not result["errors"]

#     with _patch_discovery():
#         result2 = await hass.config_entries.flow.async_configure(result["flow_id"], {})
#         await hass.async_block_till_done()

#     assert result2["type"] == "form"
#     assert result2["step_id"] == "pick_device"
#     assert not result2["errors"]

#     # test we can try again
#     result = await hass.config_entries.flow.async_init(
#         DOMAIN, context={"source": config_entries.SOURCE_USER}
#     )
#     assert result["type"] == "form"
#     assert result["step_id"] == "user"
#     assert not result["errors"]

#     with _patch_discovery():
#         result2 = await hass.config_entries.flow.async_configure(result["flow_id"], {})
#         await hass.async_block_till_done()

#     assert result2["type"] == "form"
#     assert result2["step_id"] == "pick_device"
#     assert not result2["errors"]

#     with _patch_wizlight(), patch(
#         "homeassistant.components.wiz.async_setup", return_value=True
#     ) as mock_setup, patch(
#         "homeassistant.components.wiz.async_setup_entry", return_value=True
#     ) as mock_setup_entry:
#         result3 = await hass.config_entries.flow.async_configure(
#             result["flow_id"],
#             {CONF_DEVICE: FAKE_MAC},
#         )
#         await hass.async_block_till_done()

#     assert result3["type"] == "create_entry"
#     assert result3["title"] == "WiZ Dimmable White ABCABC"
#     assert result3["data"] == {
#         CONF_HOST: "1.1.1.1",
#     }
#     assert len(mock_setup.mock_calls) == 1
#     assert len(mock_setup_entry.mock_calls) == 1

#     # ignore configured devices
#     result = await hass.config_entries.flow.async_init(
#         DOMAIN, context={"source": config_entries.SOURCE_USER}
#     )
#     assert result["type"] == "form"
#     assert result["step_id"] == "user"
#     assert not result["errors"]

#     with _patch_discovery():
#         result2 = await hass.config_entries.flow.async_configure(result["flow_id"], {})
#         await hass.async_block_till_done()

#     assert result2["type"] == "abort"
#     assert result2["reason"] == "no_devices_found"


# async def test_setup_via_discovery_cannot_connect(hass):
#     """Test setting up via discovery and we fail to connect to the discovered device."""
#     result = await hass.config_entries.flow.async_init(
#         DOMAIN, context={"source": config_entries.SOURCE_USER}
#     )
#     await hass.async_block_till_done()
#     assert result["type"] == "form"
#     assert result["step_id"] == "user"
#     assert not result["errors"]

#     with _patch_discovery():
#         result2 = await hass.config_entries.flow.async_configure(result["flow_id"], {})
#         await hass.async_block_till_done()

#     assert result2["type"] == "form"
#     assert result2["step_id"] == "pick_device"
#     assert not result2["errors"]

#     with patch(
#         "homeassistant.components.wiz.wizlight.getBulbConfig",
#         side_effect=WizLightTimeOutError,
#     ), _patch_discovery():
#         result3 = await hass.config_entries.flow.async_configure(
#             result["flow_id"],
#             {CONF_DEVICE: FAKE_MAC},
#         )
#         await hass.async_block_till_done()

#     assert result3["type"] == "abort"
#     assert result3["reason"] == "cannot_connect"


# async def test_setup_via_discovery_exception_finds_nothing(hass):
#     """Test we do not find anything if discovery throws."""
#     result = await hass.config_entries.flow.async_init(
#         DOMAIN, context={"source": config_entries.SOURCE_USER}
#     )
#     await hass.async_block_till_done()
#     assert result["type"] == "form"
#     assert result["step_id"] == "user"
#     assert not result["errors"]

#     with patch(
#         "homeassistant.components.wiz.discovery.find_wizlights",
#         side_effect=OSError,
#     ):
#         result2 = await hass.config_entries.flow.async_configure(result["flow_id"], {})
#         await hass.async_block_till_done()

#     assert result2["type"] == RESULT_TYPE_ABORT
#     assert result2["reason"] == "no_devices_found"


# async def test_discovery_with_firmware_update(hass):
#     """Test we check the device again between first discovery and config entry creation."""
#     with _patch_wizlight(
#         device=None,
#         extended_white_range=FAKE_EXTENDED_WHITE_RANGE,
#         bulb_type=FAKE_RGBW_BULB,
#     ):
#         result = await hass.config_entries.flow.async_init(
#             DOMAIN,
#             context={"source": config_entries.SOURCE_INTEGRATION_DISCOVERY},
#             data=INTEGRATION_DISCOVERY,
#         )
#         await hass.async_block_till_done()

#     assert result["type"] == RESULT_TYPE_FORM
#     assert result["step_id"] == "discovery_confirm"

#     # In between discovery and when the user clicks to set it up the firmware
#     # updates and we now can see its really RGBWW not RGBW since the older
#     # firmwares did not tell us how many white channels exist

#     with patch(
#         "homeassistant.components.wiz.async_setup_entry",
#         return_value=True,
#     ) as mock_setup_entry, patch(
#         "homeassistant.components.wiz.async_setup", return_value=True
#     ) as mock_setup, _patch_wizlight(
#         device=None,
#         extended_white_range=FAKE_EXTENDED_WHITE_RANGE,
#         bulb_type=FAKE_RGBWW_BULB,
#     ):
#         result2 = await hass.config_entries.flow.async_configure(
#             result["flow_id"],
#             {},
#         )
#         await hass.async_block_till_done()

#     assert result2["type"] == "create_entry"
#     assert result2["title"] == "WiZ RGBWW Tunable ABCABC"
#     assert result2["data"] == {
#         CONF_HOST: "1.1.1.1",
#     }
#     assert len(mock_setup.mock_calls) == 1
#     assert len(mock_setup_entry.mock_calls) == 1
