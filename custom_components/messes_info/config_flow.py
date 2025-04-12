"""Config flow for Messes Info integration."""

import typing as t

import voluptuous as vol
from homeassistant import config_entries

from .const import DOMAIN


class MessesInfoConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Messes Info."""

    async def async_step_user(
        self,
        user_input: t.Dict[str, t.Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Handle the user step of the config flow.

        Args:
            user_input (t.Dict[str, t.Any] | None, optional): The user input. Defaults to None.

        Returns:
            config_entries.ConfigFlowResult: The result of the config flow step.
        """
        if user_input is not None:
            church_name: str = user_input["church_name"]
            postal_code: str = user_input["postal_code"]
            update_interval: int = user_input["update_interval"]
            return self.async_create_entry(
                title=f"{church_name} - {postal_code} [{update_interval}]",
                data=user_input,
            )

        schema: vol.Schema = vol.Schema(
            {
                vol.Required("postal_code"): str,
                vol.Required("church_name"): str,
                vol.Required("update_interval", default=24): int,
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema)

    def is_matching(self, other_flow: config_entries.ConfigFlow) -> bool:
        """Prevent duplicates — called internally by HA when config flow runs.

        Args:
            other_flow (config_entries.ConfigFlow): The other flow.

        Returns:
            bool: True if the entry matches the current user input.
        """
        this_input: t.Any = self.context.get("user_input", {})
        other_input: t.Any = other_flow.context.get("user_input", {})

        return bool(
            this_input.get("postal_code") == other_input.get("postal_code")
            and this_input.get("church_name", "").lower()
            == other_input.get("church_name", "").lower()
            and this_input.get("update_interval", 0)
            == other_input.get("update_interval", 0)
        )
