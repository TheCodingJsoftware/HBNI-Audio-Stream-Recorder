import json

import requests
from oauth2client.service_account import ServiceAccountCredentials

# pip install oauth2client google-api-python-client requests

PROJECT_ID: str = "hutterite-church-80812"
BASE_URL: str = "https://fcm.googleapis.com"
FCM_ENDPOINT: str = "v1/projects/" + PROJECT_ID + "/messages:send"
FCM_URL: str = BASE_URL + "/" + FCM_ENDPOINT
SCOPES = ["https://www.googleapis.com/auth/firebase.messaging"]


def _get_access_token():
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        "firebase_android_credentials.json",
        SCOPES,
    )
    access_token_info = credentials.get_access_token()
    return access_token_info.access_token


def _send_fcm_message(fcm_message):
    headers: dict[str, str] = {
        "Authorization": "Bearer " + _get_access_token(),
        "Content-Type": "application/json; UTF-8",
    }
    resp = requests.post(FCM_URL, data=json.dumps(fcm_message), headers=headers)

    if resp.status_code == 200:
        print("Message sent to Firebase for delivery, response:")
    else:
        print("Unable to send message to Firebase")
    print(resp.text)


def _build_common_message(
    title: str,
    body: str,
    topic: str = "news",
    link: str = "https://broadcasting.hbni.net/events",
):
    return {
        "message": {
            "topic": topic,
            "notification": {
                "title": title,
                "body": body,
            },
            "webpush": {
                "notification": {
                    "title": title,
                    "body": body,
                    "icon": "/favicon.ico",  # optional: your logo icon
                },
                "fcm_options": {
                    "link": link,
                },
            },
            "data": {
                "link": link,
            },
        }
    }



def _build_override_message(
    title: str,
    body: str,
    topic: str = "news",
    link: str = "https://broadcasting.hbni.net/events",
):
    fcm_message = _build_common_message(title=title, body=body, topic=topic, link=link)

    apns_override = {
        "payload": {"aps": {"badge": 1}},
        "headers": {"apns-priority": "10"},
    }

    android_override = {"notification": {"click_action": "android.intent.action.MAIN"}}

    fcm_message["message"]["android"] = android_override
    fcm_message["message"]["apns"] = apns_override

    return fcm_message


def send_notification(title: str, body: str, link: str):
    override_message = _build_override_message(
        title=title, body=body, topic="news", link=link
    )
    _send_fcm_message(override_message)
    send_notification_to_dev(title=title, body=body, link=link)


def send_notification_to_dev(
    title: str, body: str, link: str = "https://broadcasting.hbni.net/events"
):
    override_message = _build_override_message(
        title=title, body=body, topic="developer", link=link
    )
    _send_fcm_message(override_message)
