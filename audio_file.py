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
