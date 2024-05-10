"""Oxygen api."""

import httpx

from homeassistant.exceptions import HomeAssistantError


class OxygenHrvDevice:
    """Oxygen HRV API client."""

    power_on: bool = False
    real_temp: float | None
    target_temp: float | None
    target_flow: float | None
    device_connected: bool = False
    timeout_s: int = 3
    client = httpx.AsyncClient()
    mac_address: str = "C8:C9:A3:85:8B:8B"

    def __init__(self, host) -> None:
        self.host = "http://" + host.strip("/")

    async def fetch_state(self) -> None:
        try:
            response = await self.client.get(
                self.host + "/status", timeout=self.timeout_s
            )
            response.raise_for_status()
        except httpx.exceptions.RequestException as e:
            self.device_connected = False
            raise CannotConnect(
                "Failed to connect to Oxygen HRV at " + self.host
            ) from e
        parts = response.text.split("<br>")

        for part in parts:
            match part:
                case s if s.startswith("Power"):
                    power_on_str = s.split(" ")[1]
                    self.power_on = power_on_str == "ON"
                case s if s.startswith("Real Temp"):
                    real_temp_str = s.split(":")[1].strip()
                    self.real_temp = float(real_temp_str)
                case s if s.startswith("Set Temp"):
                    target_temp_str = s.split(":")[1].strip()
                    self.target_temp = float(target_temp_str)
                case s if s.startswith("Flow"):
                    target_flow_str = s.split(":")[1].strip()
                    self.target_flow = float(target_flow_str)
        self.device_connected = True

    async def set_target_temp(self, target_temp: str | float):
        await self.client.get(
            self.host + "/cmd?tempset=" + str(target_temp), timeout=self.timeout_s
        )

    async def set_target_flow(self, target_flow: str | float):
        await self.client.get(
            self.host + "/cmd?flowset=" + str(target_flow), timeout=self.timeout_s
        )

    async def turn_on(self):
        await self.client.get(self.host + "/cmd?on=1", timeout=self.timeout_s)

    async def turn_off(self):
        await self.client.get(self.host + "/cmd?off=1", timeout=self.timeout_s)


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""
