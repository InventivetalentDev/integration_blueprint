"""
Custom integration to integrate integration_blueprint with Home Assistant.

For more details about this integration, please refer to
https://github.com/custom-components/integration_blueprint
"""
import asyncio
from datetime import datetime, timedelta
import logging
import time

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import Config, HomeAssistant, ServiceCall
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers import entity_platform

from .client import VRKnockClient

from .api import IntegrationBlueprintApiClient

from .const import (
    CONF_HOST,
    CONF_CODE,
    CONF_PASSWORD,
    CONF_USERNAME,
    DOMAIN,
    PLATFORMS,
    SCHEMA_SERVICE_TRIGGER_KNOCK,
    SERVICE_TRIGGER_KNOCK,
    STARTUP_MESSAGE,
)

SCAN_INTERVAL = timedelta(seconds=30)

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup(hass: HomeAssistant, config: Config):
    """Set up this integration using YAML is not supported."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up this integration using UI."""
    if hass.data.get(DOMAIN) is None:
        hass.data.setdefault(DOMAIN, {})
        _LOGGER.info(STARTUP_MESSAGE)

    host = entry.data.get(CONF_HOST)
    code = entry.data.get(CONF_CODE)

    # session = async_get_clientsession(hass)
    # client = IntegrationBlueprintApiClient(username, password, session)
    client = VRKnockClient(host, code)
    # client.start()

    coordinator = BlueprintDataUpdateCoordinator(hass, client=client)
    await coordinator.async_refresh()

    if not coordinator.last_update_success:
        raise ConfigEntryNotReady

    hass.data[DOMAIN][entry.entry_id] = coordinator

    for platform in PLATFORMS:
        if entry.options.get(platform, True):
            coordinator.platforms.append(platform)
            hass.async_add_job(
                hass.config_entries.async_forward_entry_setup(entry, platform)
            )

    hass.services.async_register(
        DOMAIN,
        SERVICE_TRIGGER_KNOCK,
        coordinator.trigger_knock,
        schema=SCHEMA_SERVICE_TRIGGER_KNOCK,
    )
    # platform.async_register_entity_service(SERVICE_TRIGGER_KNOCK, SCHEMA_SERVICE_TRIGGER_KNOCK,"trigger_knock")

    entry.add_update_listener(async_reload_entry)
    return True


class BlueprintDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(self, hass: HomeAssistant, client: VRKnockClient) -> None:
        """Initialize."""
        self.api = client
        self.platforms = []

        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=SCAN_INTERVAL)

    async def _async_update_data(self):
        """Update data via library."""
        try:
            # status = self.api.get_latest_status()
            # if status is not None and time.time() - status["_time"] < 1000 * 60:
            #    return status
            status = await self.api.get_status()

            data = {
                "status_data": status,
                "online": status is not None and status["status"] == 0,
                "status_message": "offline" if status is None else status["msg"],
                "status_time": 0 if status is None else status["_time"],
                "game": "unknown" if status is None else status["game"] or "none",
            }
            print(data)
            return data
        except Exception as exception:
            print(exception)
            raise UpdateFailed() from exception

    async def trigger_knock(self, data: ServiceCall):
        print("coordinator trigger_knock")
        print(data)
        await self.api.trigger_knock(data.data.get("message"))


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Handle removal of an entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    unloaded = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, platform)
                for platform in PLATFORMS
                if platform in coordinator.platforms
            ]
        )
    )
    if unloaded:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unloaded


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
