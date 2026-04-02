# Device Registration Guide

## 📱 How Device Registration Works

Devices are **not automatically registered**. Your mobile apps (iOS/Android) need to:

1. **Get FCM token** from Firebase (when app starts)
2. **Call the GraphQL API** to register the token with your Django backend
3. **Backend stores the token** in the database
4. **Notifications are sent** to all registered devices when events/locations/hikings are created

## 🔧 GraphQL Mutation

I've created a `registerFcmDevice` mutation in your GraphQL API.

### Mutation Definition

```graphql
mutation RegisterFcmDevice(
  $registrationId: String!
  $type: String!
  $name: String
  $userUid: UUID
) {
  registerFcmDevice(
    registrationId: $registrationId
    type: $type
    name: $name
    userUid: $userUid
  ) {
    ok
    message
  }
}
```

### Parameters

- **`registrationId`** (required): The FCM token from the mobile device
- **`type`** (required): Device type - `"android"`, `"ios"`, or `"web"`
- **`name`** (optional): Device name/identifier (e.g., "John's iPhone")
- **`userUid`** (optional): User UUID if you want to associate device with a user

### Example Request

```graphql
mutation {
  registerFcmDevice(
    registrationId: "dK3jH8fK9L2mN5pQ7rS9tU1vW3xY5zA7bC9dE1fG3hI5jK7lM9nO1pQ3rS5tU7vW9xY1zA3bC5dE7fG9hI1jK3lM5nO7pQ9rS1tU3vW5xY7zA9bC1dE3fG5hI7jK9lM1nO3pQ5rS7tU9vW1xY3zA5bC7dE9fG1hI3jK5lM7nO9pQ1rS3tU5vW7xY9zA1bC3dE5fG7hI9jK1lM3nO5pQ7rS9tU1vW3xY5"
    type: "ios"
    name: "iPhone 14 Pro"
  ) {
    ok
    message
  }
}
```

### Example Response

```json
{
  "data": {
    "registerFcmDevice": {
      "ok": true,
      "message": "Device registered successfully"
    }
  }
}
```

## 📲 Mobile App Implementation

### For Flutter Apps

```dart
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:graphql_flutter/graphql_flutter.dart';

class NotificationService {
  final FirebaseMessaging _firebaseMessaging = FirebaseMessaging.instance;
  final GraphQLClient _graphQLClient;

  NotificationService(this._graphQLClient);

  Future<void> registerDevice() async {
    // Request permission
    NotificationSettings settings = await _firebaseMessaging.requestPermission(
      alert: true,
      badge: true,
      sound: true,
    );

    if (settings.authorizationStatus == AuthorizationStatus.authorized) {
      // Get FCM token
      String? token = await _firebaseMessaging.getToken();
      
      if (token != null) {
        // Determine device type
        String deviceType = Platform.isIOS ? 'ios' : 'android';
        
        // Register with backend
        await _registerToken(token, deviceType);
      }
    }
  }

  Future<void> _registerToken(String token, String deviceType) async {
    const String mutation = '''
      mutation RegisterFcmDevice(\$registrationId: String!, \$type: String!) {
        registerFcmDevice(
          registrationId: \$registrationId
          type: \$type
        ) {
          ok
          message
        }
      }
    ''';

    await _graphQLClient.mutate(
      MutationOptions(
        document: gql(mutation),
        variables: {
          'registrationId': token,
          'type': deviceType,
        },
      ),
    );
  }

  // Listen for token refresh
  void setupTokenRefresh() {
    _firebaseMessaging.onTokenRefresh.listen((newToken) {
      String deviceType = Platform.isIOS ? 'ios' : 'android';
      _registerToken(newToken, deviceType);
    });
  }
}
```

### For React Native Apps

```javascript
import messaging from '@react-native-firebase/messaging';
import { Platform } from 'react-native';

async function registerDevice(graphQLClient) {
  // Request permission
  const authStatus = await messaging().requestPermission();
  const enabled =
    authStatus === messaging.AuthorizationStatus.AUTHORIZED ||
    authStatus === messaging.AuthorizationStatus.PROVISIONAL;

  if (enabled) {
    // Get FCM token
    const token = await messaging().getToken();
    
    // Determine device type
    const deviceType = Platform.OS === 'ios' ? 'ios' : 'android';
    
    // Register with backend
    await registerToken(graphQLClient, token, deviceType);
  }
}

async function registerToken(graphQLClient, token, deviceType) {
  const mutation = `
    mutation RegisterFcmDevice($registrationId: String!, $type: String!) {
      registerFcmDevice(
        registrationId: $registrationId
        type: $type
      ) {
        ok
        message
      }
    }
  `;

  await graphQLClient.mutate({
    mutation: gql(mutation),
    variables: {
      registrationId: token,
      type: deviceType,
    },
  });
}

// Listen for token refresh
messaging().onTokenRefresh(async (token) => {
  const deviceType = Platform.OS === 'ios' ? 'ios' : 'android';
  await registerToken(graphQLClient, token, deviceType);
});
```

### For Native iOS (Swift)

```swift
import Firebase
import FirebaseMessaging

class NotificationManager {
    func registerDevice() {
        // Request permission
        UNUserNotificationCenter.current().requestAuthorization(options: [.alert, .badge, .sound]) { granted, error in
            if granted {
                DispatchQueue.main.async {
                    UIApplication.shared.registerForRemoteNotifications()
                }
            }
        }
    }
    
    func didRegisterForRemoteNotifications(withDeviceToken deviceToken: Data) {
        Messaging.messaging().apnsToken = deviceToken
        Messaging.messaging().token { token, error in
            if let token = token {
                self.sendTokenToBackend(token: token)
            }
        }
    }
    
    func sendTokenToBackend(token: String) {
        // Use your GraphQL client to call registerFcmDevice mutation
        let mutation = """
            mutation RegisterFcmDevice($registrationId: String!, $type: String!) {
                registerFcmDevice(
                    registrationId: $registrationId
                    type: $type
                ) {
                    ok
                    message
                }
            }
        """
        
        // Call your GraphQL API
        // graphQLClient.mutate(mutation: mutation, variables: ["registrationId": token, "type": "ios"])
    }
}
```

### For Native Android (Kotlin)

```kotlin
import com.google.firebase.messaging.FirebaseMessaging

class NotificationManager {
    fun registerDevice() {
        FirebaseMessaging.getInstance().token.addOnCompleteListener { task ->
            if (!task.isSuccessful) {
                return@addOnCompleteListener
            }
            
            val token = task.result
            sendTokenToBackend(token)
        }
    }
    
    private fun sendTokenToBackend(token: String) {
        // Use your GraphQL client to call registerFcmDevice mutation
        val mutation = """
            mutation RegisterFcmDevice(\$registrationId: String!, \$type: String!) {
                registerFcmDevice(
                    registrationId: \$registrationId
                    type: \$type
                ) {
                    ok
                    message
                }
            }
        """
        
        // Call your GraphQL API
        // graphQLClient.mutate(mutation, mapOf("registrationId" to token, "type" to "android"))
    }
}
```

## 🔄 When to Register

1. **App Launch**: Register when the app starts (after user grants permissions)
2. **Token Refresh**: Firebase tokens can refresh - listen for token refresh events and re-register
3. **User Login**: Optionally re-register when user logs in (to associate device with user)

## ✅ Testing

1. **Check registered devices**:
   ```bash
   python manage.py shell -c "from fcm_django.models import FCMDevice; print(FCMDevice.objects.all())"
   ```

2. **Test registration via GraphQL** (using GraphiQL at `/graphql/`):
   ```graphql
   mutation {
     registerFcmDevice(
       registrationId: "test_token_123"
       type: "ios"
       name: "Test Device"
     ) {
       ok
       message
     }
   }
   ```

3. **Create a test event** and verify notifications are sent to all registered devices

## 🎯 Summary

- ✅ GraphQL mutation created: `registerFcmDevice`
- ✅ Mobile apps need to call this API when they get FCM tokens
- ✅ Devices are stored in the database automatically
- ✅ Notifications are sent to ALL registered devices when events/locations/hikings are created
- ✅ Works for both iOS and Android devices

**Next Steps**: Implement the device registration in your mobile app code (examples above), then test by creating a new event/location/hiking!
