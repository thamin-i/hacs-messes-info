"""Config flow for Messes Info integration."""

import typing as t

import voluptuous as vol
from homeassistant import config_entries

from .const import CONF_CHURCH_NAME, CONF_POSTAL_CODE, DOMAIN


class MessesInfoConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Messes Info."""

    VERSION: int = 1

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
            return self.async_create_entry(
                title=user_input[CONF_CHURCH_NAME], data=user_input
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_POSTAL_CODE): str,
                    vol.Required(CONF_CHURCH_NAME): str,
                }
            ),
        )

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
        )
