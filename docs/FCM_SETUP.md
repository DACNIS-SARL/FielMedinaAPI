# Firebase Cloud Messaging (FCM) Setup Guide

This guide will help you complete the FCM configuration to send push notifications to your iOS and Android apps.

## ✅ What's Already Configured

1. ✅ `fcm-django` is installed and added to `INSTALLED_APPS`
2. ✅ Firebase Admin SDK initialization code added to `core/__init__.py`
3. ✅ FCM Django settings added to `core/settings.py`
4. ✅ `.gitignore` updated to exclude Firebase service account JSON files

## 🔧 What You Need to Do

### Step 1: Download Firebase Service Account Key

**Important:** The Firebase config you provided is for **client-side** (iOS/Android apps). For Django backend, you need a **server-side service account JSON file**.

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project: **fielmedinasousse**
3. Click on the **⚙️ Settings** (gear icon) → **Project settings**
4. Go to the **"Service accounts"** tab
5. Click **"Generate new private key"**
6. Save the downloaded JSON file as `firebase_service_account.json` in the project root directory (`/backend/`)

**Or** set the path in your `.env` file:
```env
GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/firebase-service-account.json
```

### Step 2: Run Migrations

Apply the FCM Django migrations to create the necessary database tables:

```bash
python manage.py migrate fcm_django
```

### Step 3: (Optional) Add FCM Server Key to .env

If you want to use the legacy FCM server key method instead of (or in addition to) service account credentials, you can get it from:

1. Firebase Console → Project Settings → Cloud Messaging tab
2. Copy the "Server key" (or "Cloud Messaging API (Legacy) server key")
3. Add to your `.env` file:

```env
FCM_SERVER_KEY=your_server_key_here
```

**Note:** Service account credentials (Step 1) are the recommended approach and should be sufficient.

### Step 4: Verify Installation

Start your Django server and check the console. You should see:
- If credentials are found: No errors (Firebase initialized successfully)
- If credentials are missing: A warning message (FCM won't work until configured)

```bash
python manage.py runserver
```

## 📱 Using FCM in Your Code

### Registering Devices

In your mobile apps, after getting the FCM token, you can register it via your API (GraphQL or REST):

```python
from fcm_django.models import FCMDevice

# Register a device
device = FCMDevice.objects.create(
    registration_id='device_fcm_token_from_mobile_app',
    user=user_instance,  # Optional: associate with a user
    type='android',  # or 'ios'
    name='User iPhone',  # Optional: device name
)
```

### Sending Notifications

```python
from fcm_django.models import FCMDevice
from firebase_admin.messaging import Message, Notification

# Send to a single device
device = FCMDevice.objects.get(registration_id='token')
device.send_message(
    Message(
        notification=Notification(
            title="New Event!",
            body="Check out this amazing event happening in your city",
            image="https://example.com/image.jpg"  # Optional
        ),
        data={
            "event_id": "123",
            "type": "event",
            "click_action": "FLUTTER_NOTIFICATION_CLICK"
        }
    )
)

# Send to all active devices
devices = FCMDevice.objects.filter(active=True)
devices.send_message(
    Message(
        notification=Notification(
            title="Broadcast",
            body="This is a broadcast message"
        )
    )
)

# Send to devices of a specific user
user_devices = FCMDevice.objects.filter(user=user, active=True)
user_devices.send_message(message)
```

### GraphQL Integration Example

You might want to add a GraphQL mutation to register devices. Example:

```python
# In api/schema.py
@strawberry.mutation
def register_device(
    self,
    registration_id: str,
    type: str,  # 'android' or 'ios'
    user_id: Optional[int] = None,
) -> bool:
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

## 🔒 Security Notes

1. ✅ `firebase_service_account.json` is already added to `.gitignore` - **DO NOT commit this file**
2. ✅ Use environment variables for production deployments
3. ✅ The service account JSON contains sensitive credentials - keep it secure
4. ✅ Consider using environment variables or secret management services in production

## 📚 Additional Resources

- [fcm-django Documentation](https://fcm-django.readthedocs.io/)
- [Firebase Admin SDK for Python](https://firebase.google.com/docs/admin/setup)
- [FCM Send Messages Documentation](https://firebase.google.com/docs/cloud-messaging/send-message)

## 🐛 Troubleshooting

### Error: "Firebase credentials file not found"
- Make sure `firebase_service_account.json` exists in the project root
- Or set `GOOGLE_APPLICATION_CREDENTIALS` in your `.env` file

### Error: "Firebase Admin SDK initialization failed"
- Check that the JSON file is valid
- Verify the service account has the correct permissions
- Make sure `firebase-admin` package is installed (it should be as a dependency of `fcm-django`)

### Migrations not working
- Make sure you've run `python manage.py migrate` first
- Check that `fcm_django` is in `INSTALLED_APPS`
