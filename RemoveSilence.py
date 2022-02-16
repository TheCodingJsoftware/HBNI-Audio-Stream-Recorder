from pydub import AudioSegment


def __findSilence(
    sound: AudioSegment, silenceThreshold: int = -30.0, chunkSize: int = 10
):
    """iterate over chunks until you find the first one with sound

    Args:
        sound (AudioSegment): is a pydub.AudioSegment
        silenceThreshold (int): in dB
        chunkSize (int): in ms
    """
    trimMilliSecond = 0  # ms

    assert chunkSize > 0  # to avoid infinite loop
    while sound[
        trimMilliSecond : trimMilliSecond + chunkSize
    ].dBFS < silenceThreshold and trimMilliSecond < len(sound):
        trimMilliSecond += chunkSize

    return trimMilliSecond


def removeSilence(filePath: str):
    """removes silence from beggining and the end of the audio file

    Args:
        filePath (str): full path to the audio file.
    """
    sound = AudioSegment.from_file(filePath, format="mp3")

    startTrim = __findSilence(sound)
    endTrim = __findSilence(sound.reverse())

    duration = len(sound)
    trimmedSound = sound[startTrim : duration - endTrim]

    trimmedSound.export(filePath, format="mp3")
