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
gunicorn -w 4 -b 10.0.0.150:5000 Website:app
```

Tree Directory
```
+-- logs
+-- CURRENTLY_RECORDING
+-- Recordings
+-- static
|   +-- favicon.png
|   +-- hbni_logo_dark.png
|   +-- icon.png
+-- templates
|   +-- index.html
+-- .gitignore
+-- archived_page.html
+-- credentials.json
+-- downloadLinks.json
+-- ffmpeg.exe
+-- ffplay.exe
+-- ffprobe.exe
+-- GlobalVariables.py
+-- LinksJson.py
+-- MegaGetFileList.py
+-- MegaUploader.py
+-- README.md
+-- RemoveSilence.py
+-- StreamRecorder.py
+-- Website.py
```
