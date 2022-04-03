# HBNI Audio Stream Recorder
![image](https://img.shields.io/badge/Heroku-430098?style=for-the-badge&logo=heroku&logoColor=white)
![image](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![image](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)
![image](https://img.shields.io/badge/json-5E5C5C?style=for-the-badge&logo=json&logoColor=white)
![image](https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue)

Records HBNI streams as the show up.

## Requirements:

[ffmpeg download](https://www.filehorse.com/download-ffmpeg/)

Add to **PATH** environment variables.

**PYTHON 3.8+**

```
pip install flask natsort mega.py gitpython pydub colorama pyqt5 pyqtdarktheme
```

## JsonEditor.py

Demo:

![image](https://user-images.githubusercontent.com/25397800/157153928-06c7fecd-d541-42f6-ac73-f24a88136f69.png)

Run with:

```
python JsonEditor.py
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

Possible Github TLS/SSL error [fix](https://www.youtube.com/watch?v=LK7-YNpxEhA&ab_channel=AccuWebHosting):

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
+-- UI/
|   +-- add_json_dialog.ui
|   +-- json_editor.ui
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
+-- JsonEditor.py
+-- MegaGetFileList.py
+-- MegaUploader.py
+-- README.md
+-- RecordingStatus.py
+-- recordingStatus.txt
+-- RemoveSilence.py
+-- StreamRecorder.py
+-- Website.py
+-- Zip.py
```

Create a `credentials.json` file with the following:
```
{
    "username": "",
    "password": ""
}
```
Make sure you fill these out with your mega login credetials.
