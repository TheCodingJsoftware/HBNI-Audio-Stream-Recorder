import zipfile


def zip_file(pathToFile: str) -> None:
    fileName: str = pathToFile.split("/")[-1]
    pathToZipFile: str = pathToFile.replace(".mp3", ".zip")
    zf = zipfile.ZipFile(pathToZipFile, mode="w")
    zf.write(pathToFile, fileName, compress_type=zipfile.ZIP_DEFLATED)
    zf.close()
