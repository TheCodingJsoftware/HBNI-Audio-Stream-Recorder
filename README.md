# HBNI Audio Stream Recorder

Records HBNI streams as the show up.

## Requirements:

[ffmpeg download](https://www.filehorse.com/download-ffmpeg/)

Add to **PATH** environment variables.

**PYTHON 3.10+**

```
pip install --upgrade flask natsort pydub colorama pyqt5 qt_material themepy 
```

## Editing Archived Streams Data

Demo:

![image](https://github.com/TheCodingJsoftware/HBNI-Audio-Stream-Recorder/assets/25397800/e25a2d75-f644-4725-a057-405173aaf522)

Run with:

```
python json_editor.py
```

## Server setup (Windows)

Create a shortcut of [StreamRecorder.bat](https://github.com/TheCodingJsoftware/HBNI-Audio-Stream-Recorder/blob/master/StreamRecorder.bat) and paste it into the `Startup` directory:

Directory Example:
```
C:\Users\user\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup
```

## Mega Setup

Create a `mega_credentials.json` file with the following:
```
{
    "username": "",
    "password": ""
}
```
Make sure you fill these out with your mega login credetials.

## GoogleDrive Setup

`pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib`

Follow instructions here to setup: https://developers.google.com/drive/api/quickstart/python

You need only to run `python GoogleDriveSetup.py` to upload files to GoogleDrive account.
