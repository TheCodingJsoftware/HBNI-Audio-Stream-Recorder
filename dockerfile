FROM python:3.12.5-slim

WORKDIR /app

COPY . /app

RUN apt-get update && apt-get install -y \
    ffmpeg \
    && apt-get clean && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5054

ENV PORT=5054
ENV TZ="America/Guatemala"
ENV PYTHONUNBUFFERED=1
ENV STATIC_RECORDINGS_PATH="/app/static/Recordings"
ENV RECORDING_STATUS_FILE_PATH="/app/static/recording_status.json"
ENV MINIMUM_RECORDING_LENGTH="10"
ENV LOG_SERVER_HOST="0.0.0.0"
ENV LOG_SERVER_PORT="5054"
ENV NOTIFICATION_DELAY="2"
ENV POSTGRES_USER="admin"
ENV POSTGRES_PASSWORD=""
ENV POSTGRES_DB="hbni"
ENV POSTGRES_HOST="172.17.0.1"
ENV POSTGRES_PORT="5434"
ENV FILEBROWSER_URL="http://10.0.1.209:8080"
ENV FILEBROWSER_USERNAME="admin"
ENV FILEBROWSER_PASSWORD=""
ENV FILEBROWSER_UPLOAD_PATH="HBNI-Audio/Recordings"
ENV SMTP_USERNAME="jaredgrozz@gmail.com"
ENV SMTP_PASSWORD=""
ENV EMAIL_FROM="jaredgrozz@gmail.com"
ENV EMAIL_TO="jared@pinelandfarms.ca"

RUN mkdir -p /app/logs /app/CURRENTLY_RECORDING

CMD ["python", "main.py"]