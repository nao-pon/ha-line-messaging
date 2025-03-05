"""Config flow for NFAndroidTV integration."""
from __future__ import annotations

import logging
from typing import Any

"""from notifications_android_tv.notifications import ConnectError, Notifications"""
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_NAME, CONF_ACCESS_TOKEN
from homeassistant.config_entries import ConfigFlowResult

from .const import DEFAULT_NAME, DOMAIN


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Line Messaging."""

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle a flow initiated by the user."""
        errors = {}

        if user_input is not None:
            self._async_abort_entries_match({CONF_NAME: user_input[CONF_NAME]})
            return self.async_create_entry(
                title=user_input[CONF_NAME],
                data={
                    CONF_NAME: user_input[CONF_NAME],
                    CONF_ACCESS_TOKEN: user_input[CONF_ACCESS_TOKEN],
                },
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_NAME, default=DEFAULT_NAME): str,
                    vol.Required(CONF_ACCESS_TOKEN, default=""): str,
                }
            ),
            errors=errors,
        )
