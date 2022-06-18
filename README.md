**Downloader for ecchi.iwara.tv**

COMMAND: python3 main.py [option] [value]

OPTIONS:
* --url                      - get a video by url
* --uid                      - get a video by uid ([ecchi.iwara.tv/videos/](https://ecchi.iwara.tv/videos/)**UID**)
* --saveDir DIRECTORY        - change default save directory for session to DIRECTORY
* --save-dir-force DIRECTORY - change default save directory for session to DIRECTORY and creating them if they doesn't exist
* --groupBy                  - group downloaded videos by *value*
    * VALUES: author, day, fulldate
* --all                      - download with no looking at UID of last saved video from the last time you downloaded **all** videos