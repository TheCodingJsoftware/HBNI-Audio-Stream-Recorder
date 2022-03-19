from pydub import AudioSegment


def __findSilence(
    sound: AudioSegment, silenceThreshold: int = -30.0, chunkSize: int = 10
) -> int:
    """iterate over chunks until you find the first one with sound

    Args:
        sound (AudioSegment): is a pydub.AudioSegment
        silenceThreshold (int): in dB
        chunkSize (int): in ms

    Returns:
        int: what time chunk the sound was first detected
    """
    trimMilliSeconds: int = 0  # ms

    assert chunkSize > 0  # to avoid infinite loop
    while sound[
        trimMilliSeconds : trimMilliSeconds + chunkSize
    ].dBFS < silenceThreshold and trimMilliSeconds < len(sound):
        trimMilliSeconds += chunkSize

    return trimMilliSeconds


def removeSilence(filePath: str) -> None:
    """removes silence from beggining and the end of the audio file

    Args:
        filePath (str): full path to the audio file.
    """
    sound = AudioSegment.from_file(filePath, format="mp3")

    startTrim: int = __findSilence(sound)
    endTrim: int = __findSilence(sound.reverse())

    duration: float = len(sound)
    trimmedSound = sound[startTrim : duration - endTrim]

    trimmedSound.export(filePath, format="mp3")
