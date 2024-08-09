"""Oxygen api."""

import httpx
from .oxygen_ga_parser import parse_ga
from .oxygen_ga_parser import GaData

from homeassistant.exceptions import HomeAssistantError


class OxygenHrvDevice:
    """Oxygen HRV API client."""

    device_connected: bool = False
    timeout_s: int = 3
    ga_data: GaData | None = None
    client = httpx.AsyncClient()
    mac_address: str = "C8:C9:A3:85:8B:8B"

    def __init__(self, host) -> None:
        self.host = "http://" + host.strip("/")

    async def fetch_state(self) -> None:
        try:
            response = await self.client.get(
                self.host + "/cmd?GA", timeout=self.timeout_s
            )
            response.raise_for_status()
        except httpx.exceptions.RequestException as e:
            self.device_connected = False
            raise CannotConnect(
                "Failed to connect to Oxygen HRV at " + self.host
            ) from e
        self.ga_data = parse_ga(response.text)
        self.device_connected = True

    async def set_target_temp(self, target_temp: str | float):
        await self.client.get(
            self.host + "/cmd?sr2=" + str(target_temp), timeout=self.timeout_s
        )

    async def set_target_flow(self, target_flow: str | float):
        await self.client.get(
            self.host + "/cmd?sr1=" + str(target_flow), timeout=self.timeout_s
        )

    async def turn_on(self):
        await self.client.get(self.host + "/cmd?sr0=1", timeout=self.timeout_s)

    async def turn_off(self):
        await self.client.get(self.host + "/cmd?sr0=0", timeout=self.timeout_s)

    async def start_boost(self):
        await self.client.get(self.host + "/cmd?sc73=1", timeout=self.timeout_s)

    async def stop_boost(self):
        await self.client.get(self.host + "/cmd?sc74=1", timeout=self.timeout_s)

    async def set_boost_flow(self, target_flow: str | float):
        await self.client.get(
            self.host + "/cmd?sr12=" + str(target_flow), timeout=self.timeout_s
        )

    async def set_boost_time(self, time_minutes: str | int):
        await self.client.get(
            self.host + "/cmd?sr13=" + str(time_minutes), timeout=self.timeout_s
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""
