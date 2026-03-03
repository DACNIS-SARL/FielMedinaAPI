import os
from pathlib import Path

# Initialize Firebase Admin SDK
BASE_DIR = Path(__file__).resolve().parent.parent

# Get the service account key path from environment variable
# This should point to your Firebase service account JSON file
FIREBASE_CREDENTIALS_PATH = os.environ.get(
    "GOOGLE_APPLICATION_CREDENTIALS",
    str(BASE_DIR / "fielmedinasousse-firebase-adminsdk-fbsvc-8f2da79831.json"),
)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = FIREBASE_CREDENTIALS_PATH


# Initialize Firebase Admin SDK only if not already initialized
try:
    import firebase_admin
    from firebase_admin import credentials

    # Only initialize if Firebase is not already initialized
    if not firebase_admin._apps:
        if os.path.exists(FIREBASE_CREDENTIALS_PATH):
            try:
                cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
                firebase_admin.initialize_app(cred)
                print(
                    f"Successfully initialized Firebase Admin SDK with {FIREBASE_CREDENTIALS_PATH}"
                )
            except Exception as e:
                print(f"Error: Firebase Admin SDK initialization failed: {e}")
        else:
            print(
                f"Warning: Firebase credentials file not found at {FIREBASE_CREDENTIALS_PATH}"
            )
            print(
                "FCM notifications will not work until Firebase service account JSON is configured."
            )
except ImportError:
    print(
        "Warning: firebase-admin package not installed. Install it with: pip install firebase-admin"
    )
