import os
from pathlib import Path

# Initialize Firebase Admin SDK
BASE_DIR = Path(__file__).resolve().parent.parent

# Get the service account key path from environment variable
# This should point to your Firebase service account JSON file
FIREBASE_CREDENTIALS_PATH = os.environ.get(
    "GOOGLE_APPLICATION_CREDENTIALS",
    str(BASE_DIR / "fielmedinasousse-firebase-adminsdk-fbsvc-8f2da79831.json")
)

# Initialize Firebase Admin SDK only if not already initialized
try:
    import firebase_admin
    from firebase_admin import credentials
    
    # Only initialize if credentials file exists and Firebase is not already initialized
    if not firebase_admin._apps and os.path.exists(FIREBASE_CREDENTIALS_PATH):
        try:
            cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
            firebase_admin.initialize_app(cred)
        except ValueError:
            # Firebase app already initialized (can happen during Django reload)
            pass
        except Exception as e:
            # Log error but don't crash the app if Firebase isn't configured yet
            print(f"Warning: Firebase Admin SDK initialization failed: {e}")
            print("FCM notifications will not work until Firebase credentials are configured.")
    elif not os.path.exists(FIREBASE_CREDENTIALS_PATH):
        print(f"Warning: Firebase credentials file not found at {FIREBASE_CREDENTIALS_PATH}")
        print("FCM notifications will not work until Firebase service account JSON is configured.")
except ImportError:
    print("Warning: firebase-admin package not installed. Install it with: pip install firebase-admin")
