# HBNI Audio Stream Recorder

Records HBNI streams as the show up.

## Requirements:

[ffmpeg download](https://www.filehorse.com/download-ffmpeg/)

Add to **PATH** environment variables.

**PYTHON 3.8+**

```
pip install flask natsort mega.py gitpython pydub colorama
```

## Server setup (Windows)

Create Batch file:

`StreamRecorder.bat`

With the following contents:
```bat
/path/to/python.exe /path/to/StreamRecorder.py %*
```

Example:

```bat
C:\Users\user\AppData\Local\Programs\Python\Python38\python.exe C:\Users\user\Desktop\HBNI-Audio-Stream-Recorder\StreamRecorder.py %*
```

Create a shortcut and paste it into the `Startup` directory:

Directory Example:
```
C:\Users\user\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup
```

## Server setup (Raspberry Pi)

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
