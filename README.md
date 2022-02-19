# HBNI Audio Stream Recorder

Records HBNI streams as the show up.

## Stream Recorder

[ffmpeg download](https://www.filehorse.com/download-ffmpeg/)
 ### Requirements:

**PYTHON 3.9**

```
pip install flask natsort mega.py gitpython pydub
```


## Server setup

### Autoreboot

Run this:

```
sudo crontab -e
```

Choose nano [1]

Add this line at the end

```
30 4 * * * /sbin/shutdown -r now
```

```Ctrl+S```

```Ctrl+X```


### Starting server

Go into this file:

```
sudo nano /etc/xdg/lxsession/LXDE-pi/autostart
```

Add this line before ```@xscreensaver -no-splash```

```
@lxterminal --working-directory="/home/pi/HBNI-Audio-Stream-Recorder" -e gunicorn -w 1 -b 10.0.0.198:5000 Website:app
```

```Ctrl+S```

```Ctrl+X```

## Tree Directory
```
+-- logs/
+-- CURRENTLY_RECORDING/
+-- Recordings/
+-- static/
|   +-- favicon.png
|   +-- hbni_logo_dark.png
|   +-- icon.png
|   +-- main.css
+-- templates/
|   +-- index.html
+-- .gitignore
+-- archived_page.html
+-- AudioFile.py
+-- credentials.json
+-- downloadLinks.json
+-- DownloadLinks.py
+-- ffmpeg.exe
+-- ffplay.exe
+-- ffprobe.exe
+-- GlobalVariables.py
+-- MegaGetFileList.py
+-- MegaUploader.py
+-- README.md
+-- RemoveSilence.py
+-- StreamRecorder.py
+-- Website.py
+-- Zip.py
```
