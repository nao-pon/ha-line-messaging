"""
Custom component for Home Assistant to enable sending messages via Notify Line API.


Example configuration.yaml entry:

notify:
  - name: line_notification
    platform: line_notify
    
With this custom component loaded, you can send messaged to line Notify.
"""

import json
import requests
import logging
import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant.const import CONF_ACCESS_TOKEN
from homeassistant.components.notify import (
    PLATFORM_SCHEMA,
)
from homeassistant.components.notify.const import (
    ATTR_DATA,
)
from homeassistant.components.notify.legacy import (
    BaseNotificationService,
)

_LOGGER = logging.getLogger(__name__)

BASE_URL = "https://api.line.me/v2/bot/"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_ACCESS_TOKEN): cv.string,
    }
)


def get_service(hass, config, discovery_info=None):
    """Get the Line notification service."""
    conf = discovery_info if discovery_info is not None else config
    return LineMessageingService(conf.get(CONF_ACCESS_TOKEN))


class LineMessageingService(BaseNotificationService):
    """Implementation of a notification service for the Line Messaging service."""

    def __init__(self, access_token):
        """Initialize the service."""
        self.access_token = access_token

    def send_message(self, message="", **kwargs):
        """Send some message."""
        data = kwargs.get(ATTR_DATA)
        if data is None:
            data = {}

        cmd = "message/broadcast"
        payload = {}
        masseges = []
        toUser = data.get("to")

        if (loadingSeconds := data.get("loading")) or message == "loading":
            if toUser:
                cmd = "chat/loading/start"
                payload["chatId"] = toUser
                if loadingSeconds:
                    payload["loadingSeconds"] = loadingSeconds
            else:
                return
        else:
            if toUser:
                payload["to"] = toUser
                cmd = "message/push"

            if replyToken := data.get("reply_token"):
                cmd = "message/reply"
                payload["replyToken"] = replyToken

            type = data.get("type", "text")
            if type in ("text", "textV2"):
                masseges.append(
                    {
                        "type": type,
                        "text": message,
                    }
                )
            elif type == "flex":
                alt_text = data.get("alt_text", "This is a Flex Message")
                masseges.append(
                    {
                        "type": "flex",
                        "altText": alt_text,
                        "contents": json.loads(message),
                    }
                )

            if sticker := data.get("sticker"):
                if isinstance(sticker, dict):
                    packageId = sticker.get("package_id")
                    stickerId = sticker.get("sticker_id")
                    if packageId and stickerId:
                        masseges.append(
                            {
                                "type": "sticker",
                                "packageId": packageId,
                                "stickerId": stickerId,
                            }
                        )

            if imageUrl := data.get("image_url"):
                if imageUrlSmall := data.get("image_url_small"):
                    pass
                else:
                    imageUrlSmall = imageUrl
                masseges.append(
                    {
                        "type": "image",
                        "originalContentUrl": imageUrl,
                        "previewImageUrl": imageUrlSmall,
                    }
                )

            payload["messages"] = masseges

        headers = {
            "AUTHORIZATION": "Bearer " + self.access_token,
        }

        r = requests.Session().post(BASE_URL + cmd, headers=headers, json=payload)
        if r.status_code != 200:
            _LOGGER.error(r.text)
