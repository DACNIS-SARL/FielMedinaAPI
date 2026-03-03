"""
Push notification service for sending FCM notifications
when new locations, events, hikings, or tips are created.

Localized notifications are sent based on device language.
To add a new language, simply add entries to NOTIFICATION_TRANSLATIONS.
"""

import logging
import re
from typing import Dict, List, Optional
from django.conf import settings

logger = logging.getLogger(__name__)

try:
    from firebase_admin import messaging
    from fcm_django.models import FCMDevice

    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False
    logger.warning(
        "firebase_admin or fcm_django not available. Push notifications will be disabled."
    )


# ─── Language Configuration ─────────────────────────────────────────────────
# Supported languages for notifications. To add a new language, add its code
# here and add corresponding entries in NOTIFICATION_TRANSLATIONS below.
SUPPORTED_LANGUAGES = {"en", "fr"}
DEFAULT_LANGUAGE = "en"

# ─── Translation Dictionary ─────────────────────────────────────────────────
# Central place for all notification text. Adding a new language only requires
# adding a new key here — no other code changes needed.
NOTIFICATION_TRANSLATIONS = {
    "en": {
        "new_event_title": "🎉 New Event Coming Up!",
        "new_event_body": "{name} in {city} — {date}",
        "new_location_title": "📍 New Place to Explore!",
        "new_location_body": "A new location added in {city}: {name}",
        "new_hiking_title": "🥾 New Hiking Trail!",
        "new_hiking_body": "Explore: {name}",
        "new_tip_title": "💡 New Travel Tip!",
        "new_tip_body": "{preview}",
    },
    "fr": {
        "new_event_title": "🎉 Nouvel événement à venir !",
        "new_event_body": "{name} à {city} — {date}",
        "new_location_title": "📍 Nouveau lieu à explorer !",
        "new_location_body": "Un nouveau lieu ajouté à {city} : {name}",
        "new_hiking_title": "🥾 Nouveau sentier de randonnée !",
        "new_hiking_body": "Explorez : {name}",
        "new_tip_title": "💡 Nouveau conseil de voyage !",
        "new_tip_body": "{preview}",
    },
}


def get_translation(lang: str, key: str) -> str:
    """Get a translated string. Falls back to English if the key is missing."""
    translations = NOTIFICATION_TRANSLATIONS.get(
        lang, NOTIFICATION_TRANSLATIONS[DEFAULT_LANGUAGE]
    )
    return translations.get(
        key, NOTIFICATION_TRANSLATIONS[DEFAULT_LANGUAGE].get(key, "")
    )


def extract_device_language(device_name: str) -> str:
    """
    Extract the language code from the device name field.
    Device names are stored as 'lang:XX|Device Name'.
    Returns DEFAULT_LANGUAGE if parsing fails.
    """
    if device_name and device_name.startswith("lang:"):
        match = re.match(r"^lang:(\w+)\|", device_name)
        if match:
            lang = match.group(1)
            return lang if lang in SUPPORTED_LANGUAGES else DEFAULT_LANGUAGE
    return DEFAULT_LANGUAGE


def group_devices_by_language() -> Dict[str, List[str]]:
    """
    Group all active FCM device tokens by their language.
    Returns a dict like {'en': ['token1', ...], 'fr': ['token2', ...]}.
    """
    if not FIREBASE_AVAILABLE:
        return {}

    devices = FCMDevice.objects.filter(active=True)
    groups: Dict[str, List[str]] = {}

    for device in devices:
        if not device.registration_id:
            continue
        lang = extract_device_language(device.name or "")
        groups.setdefault(lang, []).append(device.registration_id)

    return groups


class NotificationService:
    """Service for sending push notifications via FCM"""

    @staticmethod
    def build_absolute_image_url(image_field) -> Optional[str]:
        """Build absolute URL for an image field"""
        if not image_field:
            return None
        try:
            if not image_field.name:
                return None

            base_url = getattr(settings, "SITE_URL", "http://localhost:8000").rstrip(
                "/"
            )
            media_url = settings.MEDIA_URL.lstrip("/")

            return f"{base_url}/{media_url}{image_field.name}"
        except Exception as e:
            logger.error(f"Error building image URL: {e}")
            return None

    @staticmethod
    def _send_multicast_by_language(
        lang: str,
        tokens: List[str],
        title: str,
        body: str,
        image_url: Optional[str],
        data: dict,
        channel_id: str,
    ) -> Optional[messaging.BatchResponse]:
        """Send a multicast FCM message to a list of tokens."""
        if not tokens:
            return None

        message = messaging.MulticastMessage(
            notification=messaging.Notification(
                title=title,
                body=body,
                image=image_url,
            ),
            data=data,
            tokens=tokens,
            apns=messaging.APNSConfig(
                payload=messaging.APNSPayload(
                    aps=messaging.Aps(
                        sound="default",
                        badge=1,
                        mutable_content=True,
                        alert=messaging.ApsAlert(
                            title=title,
                            body=body,
                        ),
                    )
                )
            ),
            android=messaging.AndroidConfig(
                notification=messaging.AndroidNotification(
                    sound="default",
                    channel_id=channel_id,
                    priority="high",
                )
            ),
        )

        response = messaging.send_each_for_multicast(message)
        logger.info(
            f"Notification [{lang}] sent: {response.success_count} successful, "
            f"{response.failure_count} failed"
        )

        return response

    @staticmethod
    def send_new_event_notification(event) -> None:
        """Send notification when a new event is added"""
        if not FIREBASE_AVAILABLE:
            logger.warning("Firebase not available, skipping notification")
            return

        try:
            device_groups = group_devices_by_language()
            if not device_groups:
                logger.info("No active FCM devices found, skipping notification")
                return

            # Get first image URL if available
            image_url = None
            first_image = event.images.first()
            if first_image and first_image.image:
                image_url = NotificationService.build_absolute_image_url(
                    first_image.image
                )

            # Format event date
            start_date_str = (
                event.startDate.strftime("%B %d, %Y") if event.startDate else ""
            )

            # Get city name (use English name for payload, localized for body)
            city_name = ""
            if event.city:
                city_name = event.city.name or ""

            # Build data payload (same for all languages)
            data = {
                "type": "new_event",
                "screen": "event_detail",
                "event_id": str(event.id),
                "location_id": str(event.location.id) if event.location else "",
                "city_id": str(event.city.id) if event.city else "",
                "city_name": city_name,
                "click_action": "OPEN_EVENT",
            }

            # Send per language group
            for lang, tokens in device_groups.items():
                # Use translated name if available
                event_name = getattr(event, f"name_{lang}", None) or event.name
                event_city = city_name

                title = get_translation(lang, "new_event_title")
                body = get_translation(lang, "new_event_body").format(
                    name=event_name, city=event_city, date=start_date_str
                )

                NotificationService._send_multicast_by_language(
                    lang, tokens, title, body, image_url, data, "events"
                )

            logger.info(f"Event notification dispatched for event {event.id}")

        except Exception as e:
            logger.error(f"Error sending event notification: {e}", exc_info=True)

    @staticmethod
    def send_new_location_notification(location) -> None:
        """Send notification when a new location is added"""
        if not FIREBASE_AVAILABLE:
            logger.warning("Firebase not available, skipping notification")
            return

        try:
            device_groups = group_devices_by_language()
            if not device_groups:
                logger.info("No active FCM devices found, skipping notification")
                return

            # Get first image URL if available
            image_url = None
            first_image = location.images.first()
            if first_image and first_image.image:
                image_url = NotificationService.build_absolute_image_url(
                    first_image.image
                )

            # Get city name
            city_name = ""
            if location.city:
                city_name = location.city.name or ""

            # Build data payload
            data = {
                "type": "new_location",
                "screen": "location_detail",
                "location_id": str(location.id),
                "category_id": str(location.category.id) if location.category else "",
                "city_id": str(location.city.id) if location.city else "",
                "city_name": city_name,
                "click_action": "OPEN_LOCATION",
            }

            # Send per language group
            for lang, tokens in device_groups.items():
                location_name = getattr(location, f"name_{lang}", None) or location.name
                loc_city = city_name

                title = get_translation(lang, "new_location_title")
                body = get_translation(lang, "new_location_body").format(
                    name=location_name, city=loc_city
                )

                NotificationService._send_multicast_by_language(
                    lang, tokens, title, body, image_url, data, "locations"
                )

            logger.info(f"Location notification dispatched for location {location.id}")

        except Exception as e:
            logger.error(f"Error sending location notification: {e}", exc_info=True)

    @staticmethod
    def send_new_hiking_notification(hiking) -> None:
        """Send notification when a new hiking trail is added"""
        if not FIREBASE_AVAILABLE:
            logger.warning("Firebase not available, skipping notification")
            return

        try:
            device_groups = group_devices_by_language()
            if not device_groups:
                logger.info("No active FCM devices found, skipping notification")
                return

            # Get first image URL if available
            image_url = None
            first_image = hiking.images.first()
            if first_image and first_image.image:
                image_url = NotificationService.build_absolute_image_url(
                    first_image.image
                )

            data = {
                "type": "new_hiking",
                "screen": "hiking_detail",
                "hiking_id": str(hiking.id),
                "city_id": str(hiking.city.id) if hiking.city else "",
                "click_action": "OPEN_HIKING",
            }

            for lang, tokens in device_groups.items():
                hiking_name = getattr(hiking, f"name_{lang}", None) or hiking.name

                title = get_translation(lang, "new_hiking_title")
                body = get_translation(lang, "new_hiking_body").format(name=hiking_name)

                NotificationService._send_multicast_by_language(
                    lang, tokens, title, body, image_url, data, "hikings"
                )

            logger.info(f"Hiking notification dispatched for hiking {hiking.id}")

        except Exception as e:
            logger.error(f"Error sending hiking notification: {e}", exc_info=True)

    @staticmethod
    def send_new_tip_notification(tip) -> None:
        """Send notification when a new tip is created"""
        if not FIREBASE_AVAILABLE:
            logger.warning("Firebase not available, skipping notification")
            return

        try:
            device_groups = group_devices_by_language()
            if not device_groups:
                logger.info("No active FCM devices found, skipping notification")
                return

            data = {
                "type": "new_tip",
                "screen": "home",
                "tip_id": str(tip.id),
                "city_id": str(tip.city.id) if tip.city else "",
                "click_action": "OPEN_HOME",
            }

            for lang, tokens in device_groups.items():
                # Get the localized description or fallback
                description = (
                    getattr(tip, f"description_{lang}", None) or tip.description or ""
                )
                # Strip HTML tags for the preview
                clean_text = re.sub(r"<[^>]+>", "", description)
                # Truncate to 100 chars for preview
                preview = clean_text[:100].strip()
                if len(clean_text) > 100:
                    preview += "..."

                title = get_translation(lang, "new_tip_title")
                body = get_translation(lang, "new_tip_body").format(preview=preview)

                NotificationService._send_multicast_by_language(
                    lang, tokens, title, body, None, data, "tips"
                )

            logger.info(f"Tip notification dispatched for tip {tip.id}")

        except Exception as e:
            logger.error(f"Error sending tip notification: {e}", exc_info=True)
