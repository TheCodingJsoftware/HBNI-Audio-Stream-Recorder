import mutagen
from mutagen.easyid3 import EasyID3
from pydub import AudioSegment
from pydub.utils import which

AudioSegment.converter = which("ffmpeg")

def get_audio_file_length(pathToFile: str) -> float:
    return len(AudioSegment.from_file(pathToFile)) / 60000  # Convert ms to min


def convert_delta_time(duration) -> str:
    days: int = duration.days
    seconds: int = duration.seconds
    hours: int = days * 24 + seconds // 3600
    minutes: int = (seconds % 3600) // 60
    seconds %= 60

    return f"{minutes}m {seconds}s" if hours == 0 else f"{hours}h {minutes}m {seconds}s"


def set_artist(pathToFile: str, artist: str) -> None:
    try:
        meta = EasyID3(pathToFile)
    except mutagen.id3.ID3NoHeaderError:
        meta = mutagen.File(pathToFile, easy=True)
        meta.add_tags()
    meta["albumartist"] = artist
    meta["artist"] = artist
    meta.save(pathToFile, v1=2)


def set_title(pathToFile: str, title: str) -> None:
    try:
        meta = EasyID3(pathToFile)
    except mutagen.id3.ID3NoHeaderError:
        meta = mutagen.File(pathToFile, easy=True)
        meta.add_tags()
    meta["title"] = title
    meta.save(pathToFile, v1=2)


def set_genre(pathToFile: str, genre: str) -> None:
    try:
        meta = EasyID3(pathToFile)
    except mutagen.id3.ID3NoHeaderError:
        meta = mutagen.File(pathToFile, easy=True)
        meta.add_tags()
    meta["genre"] = genre
    meta.save(pathToFile, v1=2)


def set_track_number(pathToFile: str, number: int) -> None:
    try:
        meta = EasyID3(pathToFile)
    except mutagen.id3.ID3NoHeaderError:
        meta = mutagen.File(pathToFile, easy=True)
        meta.add_tags()
    meta["discnumber"] = str(number)
    meta["tracknumber"] = str(number)
    meta.save(pathToFile, v1=2)
