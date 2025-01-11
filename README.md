# HBNI Audio Stream Recorder

Records broadcasts from the HBNI Audio Streaming Service and send notifications.

## Features

- Records audio from the HBNI Audio Streaming Service.
- Sends notifications via email and firebase.
- Stores recordings in a Synology NAS.

## Installation

1. Clone the repository.
2. Create a `.env` file in the root directory of the project with the following variables:

```bash
STATIC_RECORDINGS_PATH="/app/static/Recordings"
RECORDING_STATUS_FILE_PATH="/app/static/recording_status.json"
MINIMUM_RECORDING_LENGTH="10"
LOG_SERVER_HOST="0.0.0.0"
LOG_SERVER_PORT="5054"
NOTIFICATION_DELAY="2"
POSTGRES_USER=""
POSTGRES_PASSWORD=""
POSTGRES_DB=""
POSTGRES_HOST=""
POSTGRES_PORT=""
SMTP_USERNAME=""
SMTP_PASSWORD=""
EMAIL_FROM=""
EMAIL_TO=""
```

## Docker & Synology NAS

- Make sure you set port to 5053.
- Under Volume Settings you need to add a **folder**, you need to set it to this path: `/web/HBNI Audio Stream Recorder/static/Recordings` and call the mount point `/app/static/Recordings` (It should be the same as the `STATIC_RECORDINGS_PATH` environment variable).
- Under Volume Settings you need to add a **file**, you need to set it to this path: `/web/HBNI Audio Stream Recorder/static/recording_status.json` and call the mount point `/app/static/recording_status.json` (It should be the same as the `RECORDINGS_STATUS_PATH` environment variable).

## Contributing

Contributions are welcome! If you have any suggestions or improvements, please send an email.

## License

This project is licensed under the MIT License.
