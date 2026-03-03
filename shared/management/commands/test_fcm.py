from django.core.management.base import BaseCommand
from fcm_django.models import FCMDevice
from firebase_admin import messaging
import firebase_admin


class Command(BaseCommand):
    help = "Test FCM notifications"

    def handle(self, *args, **options):
        self.stdout.write("Checking Firebase configuration...")
        self.stdout.write(f"Apps initialized: {list(firebase_admin._apps.keys())}")

        device = FCMDevice.objects.first()
        if not device:
            self.stdout.write(self.style.ERROR("No FCM devices found in database."))
            return

        self.stdout.write(
            f"Testing notification for device: {device.registration_id[:10]}..."
        )

        message = messaging.Message(
            notification=messaging.Notification(
                title="Test Notification",
                body="This is a test notification from management command.",
            ),
            token=device.registration_id,
        )

        try:
            # Try sending via raw firebase_admin
            response = messaging.send(message, dry_run=True)
            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully sent test message (dry run): {response}"
                )
            )

            # Now try via fcm_django
            response = device.send_message(
                messaging.Message(
                    notification=messaging.Notification(
                        title="FCM Django Test",
                        body="Testing fcm-django integration.",
                    )
                ),
                dry_run=True,
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully sent fcm-django test message (dry run): {response}"
                )
            )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {e}"))
            import traceback

            self.stdout.write(traceback.format_exc())
