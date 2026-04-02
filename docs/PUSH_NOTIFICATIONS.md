# Push Notifications Setup

This document explains the automatic push notification system for new Locations, Events, and Hikings.

## 📋 Overview

When a new **Location**, **Event**, or **Hiking** is created via the Django admin or API, the system automatically sends push notifications to all registered mobile devices (iOS and Android).

## 🏗️ Architecture

### Files Created/Modified

1. **`guard/notifications.py`** - Notification service with methods for sending FCM notifications
2. **`guard/signals.py`** - Django signals that trigger notifications on model creation
3. **`core/settings.py`** - Added `SITE_URL` configuration for building absolute image URLs

### How It Works

1. **Django Signals**: When a `Location`, `Event`, or `Hiking` is saved for the first time (`created=True`), the signal handlers fire
2. **Notification Service**: The signal handlers call the `NotificationService` methods
3. **FCM Devices**: The service fetches all active FCM device tokens from the database
4. **Send Notifications**: Firebase Cloud Messaging sends notifications to all registered devices

## 📱 Notification Structure

Each notification includes:

- **Title**: Emoji + descriptive text (e.g., "🎉 New Event Coming Up!")
- **Body**: Entity name and relevant details (e.g., event name + date)
- **Image**: First image from the entity (if available)
- **Data Payload**: Contains navigation information:
  - `type`: Entity type (`new_event`, `new_location`, `new_hiking`)
  - `screen`: Screen to open (`event_detail`, `location_detail`, `hiking_detail`)
  - Entity ID (e.g., `event_id`, `location_id`, `hiking_id`)
  - Related IDs (e.g., `city_id`, `category_id`)
  - `click_action`: Action identifier for mobile apps

### iOS Configuration (APNS)

- Sound: `default`
- Badge: `1`
- Mutable content: `true` (allows notification extensions)

### Android Configuration

- Sound: `default`
- Channel ID: `events`, `locations`, or `hikings`
- Priority: `high`

## 🔧 Configuration

### Required Settings

In your `.env` file, you can optionally set:

```env
# Site URL for building absolute image URLs in notifications
SITE_URL=https://mystory.fielmedina.com  # Production
# or
SITE_URL=http://localhost:8000  # Development
```

If not set, it defaults to:
- Development: `http://localhost:8000`
- Production: `https://mystory.fielmedina.com`

### Image URLs

Image URLs in notifications are built as:
```
{SITE_URL}/{MEDIA_URL}{image_path}
```

Example: `https://mystory.fielmedina.com/upload/locations/123/image.jpg`

## 📝 Usage

### Automatic (Recommended)

Notifications are sent automatically when you create entities through:
- Django Admin
- Django Forms/Views
- API endpoints (REST/GraphQL)

**No additional code needed!** Just create the entity and notifications are sent.

### Manual Usage

If you need to send notifications manually:

```python
from guard.notifications import NotificationService
from guard.models import Location, Event, Hiking

# Send location notification
location = Location.objects.get(id=1)
NotificationService.send_new_location_notification(location)

# Send event notification
event = Event.objects.get(id=1)
NotificationService.send_new_event_notification(event)

# Send hiking notification
hiking = Hiking.objects.get(id=1)
NotificationService.send_new_hiking_notification(hiking)
```

## 📱 Mobile App Integration

Your mobile apps need to:

1. **Register FCM Tokens**: When the app starts, get the FCM token and send it to your backend via API
2. **Handle Notifications**: Handle notification clicks using the data payload:
   - Check `type` field to determine entity type
   - Navigate to the appropriate screen using the ID fields
   - Example: `OPEN_EVENT` → Navigate to EventDetailScreen with `event_id`

### Example Notification Payload

```json
{
  "type": "new_event",
  "screen": "event_detail",
  "event_id": "123",
  "location_id": "45",
  "city_id": "7",
  "click_action": "OPEN_EVENT"
}
```

### Device Registration

You'll need to create an API endpoint (GraphQL mutation or REST endpoint) for mobile apps to register their FCM tokens:

```python
# Example GraphQL mutation (add to api/schema.py)
@strawberry.mutation
def register_fcm_device(
    self,
    registration_id: str,
    type: str,  # 'android' or 'ios'
    user_id: Optional[int] = None,
) -> bool:
    from fcm_django.models import FCMDevice
    device, created = FCMDevice.objects.get_or_create(
        registration_id=registration_id,
        defaults={
            'type': type,
            'user_id': user_id,
        }
    )
    if not created:
        device.type = type
        device.active = True
        device.save()
    return True
```

## 🐛 Troubleshooting

### Notifications Not Sending

1. **Check Logs**: Look for error messages in Django logs
2. **Verify Firebase**: Ensure Firebase Admin SDK is initialized (check server startup logs)
3. **Check Devices**: Verify there are active FCM devices in the database:
   ```python
   from fcm_django.models import FCMDevice
   active_devices = FCMDevice.objects.filter(active=True)
   print(f"Active devices: {active_devices.count()}")
   ```
4. **Check Images**: If image URLs are wrong, check `SITE_URL` and `MEDIA_URL` settings

### Common Issues

- **No devices registered**: Notifications won't send if no devices are registered
- **Invalid image URLs**: Check `SITE_URL` configuration
- **Firebase not initialized**: Check that service account JSON file exists and is valid
- **Signals not firing**: Ensure `guard.signals` is imported in `guard/apps.py` (it should be)

## 📊 Monitoring

Notifications are logged with:
- Success/failure counts
- Entity IDs
- Error messages (if any)

Check Django logs to monitor notification delivery.

## 🔒 Security Notes

- Only active devices receive notifications
- Device tokens are stored securely in the database
- Image URLs use absolute URLs based on `SITE_URL` setting
- Notifications are sent to ALL active devices (consider filtering by user preferences in the future)

## 🚀 Future Enhancements

Consider adding:
- User preference filtering (only notify users interested in specific cities/categories)
- Notification preferences per user
- Scheduled notifications (e.g., reminders for upcoming events)
- Notification history/logging
- A/B testing for notification content
