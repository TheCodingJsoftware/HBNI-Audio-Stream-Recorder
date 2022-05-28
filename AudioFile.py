import mutagen
from mutagen.easyid3 import EasyID3
from pydub import AudioSegment


def getAudioFileLength(pathToFile: str) -> float:
    """Get the length of the audio file in minutes

    Args:
        pathToFile (str): path to the audio file you want the length for

    Returns:
        float: the length of the audio file as minutes
    """
    return len(AudioSegment.from_file(pathToFile)) / 60000  # Convert ms to min


def convertDeltatime(duration) -> str:
    """Converts minutes to a pretty format

    Args:
        duration (deltatime): file length

    Returns:
        output (str): final format
    """
    days: int = duration.days
    seconds: int = duration.seconds
    hours: int = days * 24 + seconds // 3600
    minutes: int = (seconds % 3600) // 60
    seconds %= 60

    return f"{minutes}m {seconds}s" if hours == 0 else f"{hours}h {minutes}m {seconds}s"


def setArtist(pathToFile: str, artist: str) -> None:
    try:
        meta = EasyID3(pathToFile)
    except mutagen.id3.ID3NoHeaderError:
        meta = mutagen.File(parthToFile, easy=True)
        meta.add_tags()
    meta["albumartist"] = artist
    meta["artist"] = artist
    meta.save(pathToFile, v1=2)


def setTitle(pathToFile: str, title: str) -> None:
    try:
        meta = EasyID3(pathToFile)
    except mutagen.id3.ID3NoHeaderError:
        meta = mutagen.File(pathToFile, easy=True)
        meta.add_tags()
    meta["title"] = title
    meta.save(pathToFile, v1=2)


def setGenre(pathToFile: str, genre: str) -> None:
    try:
        meta = EasyID3(pathToFile)
    except mutagen.id3.ID3NoHeaderError:
        meta = mutagen.File(pathToFile, easy=True)
        meta.add_tags()
    meta["genre"] = genre
    meta.save(pathToFile, v1=2)


def setNumber(pathToFile: str, number: int) -> None:
    try:
        meta = EasyID3(pathToFile)
    except mutagen.id3.ID3NoHeaderError:
        meta = mutagen.File(pathToFile, easy=True)
        meta.add_tags()
    meta["discnumber"] = str(number)
    meta["tracknumber"] = str(number)
    meta.save(pathToFile, v1=2)
