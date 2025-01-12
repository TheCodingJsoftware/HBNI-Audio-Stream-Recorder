@echo off

:: Get the current date and time for versioning
for /f "tokens=2 delims==" %%I in ('"wmic os get localdatetime /value | findstr LocalDateTime"') do set datetime=%%I

:: Format the version as year.month.day.hour.minute
set VERSION=%datetime:~0,4%.%datetime:~4,2%.%datetime:~6,2%.%datetime:~8,2%.%datetime:~10,2%

:: Build the Docker image with the versioned tag
docker build -t jarebear/hbni-audio-stream-recorder:%VERSION% .

:: Tag the Docker image as "latest"
docker tag jarebear/hbni-audio-stream-recorder:%VERSION% jarebear/hbni-audio-stream-recorder:latest

:: Push both the versioned tag and the "latest" tag
docker push jarebear/hbni-audio-stream-recorder:%VERSION%
docker push jarebear/hbni-audio-stream-recorder:latest
