import zipfile

from GlobalVariables import FOLDER_LOCATION


def zipFile(pathToFile: str) -> None:
    """Puts the audio file into a compressed zip folder

    Args:
        pathToFile (str): the path to the file you want to zip
    """
    fileName: str = pathToFile.split("/")[-1]
    pathToZipFile: str = pathToFile.replace(".mp3", ".zip")
    zf = zipfile.ZipFile(pathToZipFile, mode="w")
    zf.write(pathToFile, fileName, compress_type=zipfile.ZIP_DEFLATED)
    zf.close()
