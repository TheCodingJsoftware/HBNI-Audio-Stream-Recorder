import firebase_admin
from firebase_admin import credentials, messaging

cred = credentials.Certificate("firebase_web_credentials.json")
firebase_admin.initialize_app(cred)


def send_notification_to_topic(title, body, topic="broadcasts"):
    try:
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            topic=topic,
        )
        response = messaging.send(message)
        print(f"Successfully sent message to topic {topic}: {response}")
    except Exception as e:
        print(f"Failed to send message: {e}")
