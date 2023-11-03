"""Handle delivery of notifications to FCM"""

import json
import logging
import os
from typing import List

from firebase_admin import messaging, credentials, initialize_app

logger = logging.getLogger(__name__)


def init():
    """Initialize firebase admin."""

    # Containerized environment
    firebase_config = os.environ.get("FIREBASE_CONFIG_FILE", None)
    if firebase_config is None:
        firebase_config = os.environ.get("FIREBASE_CONFIG", None)
        if not firebase_config is None:
            firebase_config = json.loads(firebase_config)

    logger.debug(firebase_config)
    creds = credentials.Certificate(cert=firebase_config)
    initialize_app(credential=creds)


def send(
    msg: str, title: str, body: str, tokens: List[str]
) -> messaging.BatchResponse:
    """Dispatch message through firebase cloud message"""
    notification = messaging.Notification(title=title, body=body)

    message = messaging.MulticastMessage(
        data={"message": msg}, tokens=tokens, notification=notification
    )

    try:
        br = messaging.send_multicast(message)

        logger.debug(
            f"Sent message to {br.success_count} device(s)"  # pylint: disable=logging-fstring-interpolation
        )
    except Exception as exc:  # pylint: disable=broad-exception-caught
        logger.exception(
            "An error occured while sending message using firebase. {}" % exc
        )
