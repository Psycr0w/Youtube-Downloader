import os
import yt_dlp
from datetime import datetime
import re

if os.name == 'nt': # type: ignore
    import ctypes
    from ctypes import windll, wintypes
    from uuid import UUID

    # ctypes GUID copied from MSDN sample code
    class GUID(ctypes.Structure):
        _fields_ = [
            ("Data1", wintypes.DWORD),
            ("Data2", wintypes.WORD),
            ("Data3", wintypes.WORD),
            ("Data4", wintypes.BYTE * 8)
        ]

        def __init__(self, uuidstr):
            uuid = UUID(uuidstr)
            ctypes.Structure.__init__(self)
            self.Data1, self.Data2, self.Data3, \
            self.Data4[0], self.Data4[1], rest = uuid.fields
            for i in range(2, 8):
                self.Data4[i] = rest >> (8 - i - 1) * 8 & 0xff

    SHGetKnownFolderPath = windll.shell32.SHGetKnownFolderPath
    SHGetKnownFolderPath.argtypes = [
        ctypes.POINTER(GUID), wintypes.DWORD,
        wintypes.HANDLE, ctypes.POINTER(ctypes.c_wchar_p)
    ]

    def _get_known_folder_path(uuidstr):
        pathptr = ctypes.c_wchar_p()
        guid = GUID(uuidstr)
        if SHGetKnownFolderPath(ctypes.byref(guid), 0, 0, ctypes.byref(pathptr)):
            raise ctypes.WinError()
        return pathptr.value

    FOLDERID_Download = '{374DE290-123F-4565-9164-39C4925E467B}'

    def get_download_folder():
        return _get_known_folder_path(FOLDERID_Download)
else:
    def get_download_folder():
        home = os.path.expanduser("~")
        return os.path.join(home, "Downloads")

URL = str(input("URL: "))


def download_mp3(uri):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': os.path.join(get_download_folder(), '%(title)s.%(ext)s'),
        'clean_infojson': False
    }

    ydl = yt_dlp.YoutubeDL(ydl_opts)
    info = ydl.extract_info(uri, download=False)
    file_path = ydl.prepare_filename(info).replace(".webm",".mp3")
    ydl.download([uri])

    # Update LastWriteTime of the file
    current_time = datetime.now()
    os.utime(file_path, (os.path.getatime(file_path), int(current_time.timestamp())))



if re.match(r'.*&?\??list=.*', URL):
    playlist = yt_dlp.YoutubeDL().extract_info(URL, download=False)
    for item in playlist['entries']:
        download_mp3(item['webpage_url'])
    print("Done")
else:
    download_mp3(URL)
    print("Done")