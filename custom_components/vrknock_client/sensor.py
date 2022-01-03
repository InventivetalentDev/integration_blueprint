"""Sensor platform for integration_blueprint."""
from .const import DEFAULT_NAME, DOMAIN, ICON, SENSOR
from .entity import IntegrationBlueprintEntity


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_devices(
        [StatusSensor(coordinator, entry), GameSensor(coordinator, entry)]
    )
    print("sensor")
    print(coordinator.data)


class StatusSensor(IntegrationBlueprintEntity):
    """integration_blueprint Sensor class."""

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{DEFAULT_NAME}_{SENSOR}_status"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get(
            "status_message"
        )  # todo: should probably be a code

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return ICON


class GameSensor(IntegrationBlueprintEntity):
    """integration_blueprint Sensor class."""

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{DEFAULT_NAME}_{SENSOR}_game"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get("game")  # todo: should probably be a code

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return ICON