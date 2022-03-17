from pydub import AudioSegment


def getAudioFileLength(pathToFile: str) -> float:
    """Get the length of the audio file in minutes

    Args:
        pathToFile (str): path to the audio file you want the length for

    Returns:
        float: the length of the audio file as minutes
    """
    audioFile = AudioSegment.from_file(pathToFile)
    return len(audioFile) / 60000  # Convert ms to min


def convertDeltatime(duration) -> str:
    """Converts minutes to a pretty format

    Args:
        duration (deltatime): file length

    Returns:
        output (str): final format
    """
    days, seconds = duration.days, duration.seconds
    hours = days * 24 + seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60

    return f"{minutes}m {seconds}s" if hours == 0 else f"{hours}h {minutes}m {seconds}s"
