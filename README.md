# HBNI Audio Stream Recorder

Records HBNI streams as the show up.

[ffmpeg download](https://www.filehorse.com/download-ffmpeg/)

Requirements:

**PYTHON 3.9**

```
pip install flask natsort mega.py gitpython
```

**STARTING WEBSERVER PRODUCTION**
```
gunicorn -w 4 -b 10.0.0.150:5000 StreamRecorder:app
```

Tree Directory
```
+-- logs
+-- Recordings
+-- static
|   +-- favicon.png
|   +-- hbni_logo_dark.png
|   +-- icon.png
+-- templates
|   +-- index.html
+-- .gitignore
+-- archived_page.html
+-- ffmpeg.exe
+-- ffplay.exe
+-- ffprobe.exe
+-- README.md
+-- StreamRecorder.py
+-- Website.py
```
