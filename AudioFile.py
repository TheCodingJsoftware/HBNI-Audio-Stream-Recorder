import mutagen
from mutagen.easyid3 import EasyID3
from pydub import AudioSegment


def getAudioFileLength(pathToFile: str) -> float:
    """
    It takes a path to an audio file, and returns the length of the audio file in minutes

    Args:
      pathToFile (str): The path to the audio file you want to get the length of.

    Returns:
      The length of the audio file in minutes.
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
    """
    It takes a path to a file and an artist name, and sets the artist name in the file's metadata

    Args:
      pathToFile (str): The path to the file you want to edit.
      artist (str): The artist name
    """
    try:
        meta = EasyID3(pathToFile)
    except mutagen.id3.ID3NoHeaderError:
        meta = mutagen.File(parthToFile, easy=True)
        meta.add_tags()
    meta["albumartist"] = artist
    meta["artist"] = artist
    meta.save(pathToFile, v1=2)


def setTitle(pathToFile: str, title: str) -> None:
    """
    It takes a path to a file and a title, and sets the title of the file to the title

    Args:
      pathToFile (str): The path to the file you want to edit.
      title (str): The title of the song
    """
    try:
        meta = EasyID3(pathToFile)
    except mutagen.id3.ID3NoHeaderError:
        meta = mutagen.File(pathToFile, easy=True)
        meta.add_tags()
    meta["title"] = title
    meta.save(pathToFile, v1=2)


def setGenre(pathToFile: str, genre: str) -> None:
    """
    It takes a path to a file and a genre, and sets the genre of the file to the genre

    Args:
      pathToFile (str): The path to the file you want to edit.
      genre (str): The genre of the song.
    """
    try:
        meta = EasyID3(pathToFile)
    except mutagen.id3.ID3NoHeaderError:
        meta = mutagen.File(pathToFile, easy=True)
        meta.add_tags()
    meta["genre"] = genre
    meta.save(pathToFile, v1=2)


def setNumber(pathToFile: str, number: int) -> None:
    """
    It takes a path to a file and a number, and sets the track number and disc number to that number

    Args:
      pathToFile (str): The path to the file you want to change the number of.
      number (int): The number of the track.
    """
    try:
        meta = EasyID3(pathToFile)
    except mutagen.id3.ID3NoHeaderError:
        meta = mutagen.File(pathToFile, easy=True)
        meta.add_tags()
    meta["discnumber"] = str(number)
    meta["tracknumber"] = str(number)
    meta.save(pathToFile, v1=2)
