"""Config flow for Messes Info integration."""

import typing as t

import voluptuous as vol
from homeassistant import config_entries

from .const import (
    CONF_CHURCH_CITY,
    CONF_CHURCH_NAME,
    CONF_CHURCH_POSTAL_CODE,
    CONF_DAYS_AHEAD,
    DOMAIN,
)


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
                title=f"Messes infos for {user_input[CONF_CHURCH_NAME]} ({user_input[CONF_CHURCH_POSTAL_CODE]}, {user_input[CONF_CHURCH_CITY]})",  # pylint: disable=line-too-long
                data=user_input,
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_DAYS_AHEAD, default=7): int,
                    vol.Required(CONF_CHURCH_CITY, default="Paris"): str,
                    vol.Required(CONF_CHURCH_POSTAL_CODE, default="75004"): str,
                    vol.Required(
                        CONF_CHURCH_NAME, default="Notre-Dame de Paris (Cathédrale)"
                    ): str,
                },
                extra=vol.PREVENT_EXTRA,
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
            this_input.get(CONF_DAYS_AHEAD) == other_input.get(CONF_DAYS_AHEAD)
            and this_input.get(CONF_CHURCH_CITY) == other_input.get(CONF_CHURCH_CITY)
            and this_input.get(CONF_CHURCH_POSTAL_CODE)
            == other_input.get(CONF_CHURCH_POSTAL_CODE)
            and this_input.get(CONF_CHURCH_NAME) == other_input.get(CONF_CHURCH_NAME)
        )
