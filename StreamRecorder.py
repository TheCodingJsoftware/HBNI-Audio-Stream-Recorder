import subprocess
import time
import sched
import os
import re
import logging
import threading
from logging.handlers import RotatingFileHandler
from datetime import datetime
from urllib.request import urlopen
from urllib.error import HTTPError, URLError
import MegaUploader

os.system('cls')
s = sched.scheduler(time.time, time.sleep)
titles: list = []
bodies: list = []
host_addresses: list = []

log_formatter = logging.Formatter('%(message)s')
file_name = datetime.today().strftime('%Y-%m-%d')
logFile = f'logs/{file_name}.log'

my_handler = RotatingFileHandler(
    logFile,
    mode='a',
    maxBytes=1024 ** 2 * 1024, # 1 gb
    backupCount=2,
    encoding=None,
    delay=0,
)

my_handler.setFormatter(log_formatter)
my_handler.setLevel(logging.INFO)

app_log = logging.getLogger('root')
app_log.setLevel(logging.INFO)

app_log.addHandler(my_handler)


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class Changes:
    def __init__(self, url: str, archive: str = 'archived_page.html'):
        self.url = url
        self.new_html = []
        self.old_html = []
        self.change_list: list[str] = []
        self.archive = archive

    def update(self):

        try:
            with urlopen(self.url) as byt:
                self.new_html = [x.decode('latin-1') for x in byt.readlines()]
        except HTTPError as e:
            self.new_html = [x.decode('latin-1') for x in e.readlines()]
            print('HTTPError 500; continuing listenting process.')
        except (URLError, ConnectionResetError):
            print('URL ERROR')
            return False


        open(self.archive, 'a').close()

        with open(self.archive, 'rb+') as old:
            self.old_html = [x.decode('latin-1') for x in old.readlines()]
            old.seek(0)
            old.truncate()
            old.writelines(x.encode('latin-1') for x in self.new_html)
            return True

    def diff(self) -> "list[str]":
        self.change_list.clear()
        #print(self.old_html)
        #print(self.new_html)
        for a, b in zip(self.old_html, self.new_html):
            # if any(streams in a for streams in current_streams): continue
            # if any(streams in a for streams in current_streams): continue
            if a != b:
                self.change_list.append(b)

        return self.change_list

    def email(self):
        message = f'{len(self.change_list)} changes in {self.url}:\n'
        message += ''.join(self.change_list)
        email_alert.send(message)

    def check_for_streams(self):
        with open(self.archive, 'r') as f_archive:
            file = f_archive.read()
            if 'SSLLOGIN' in file:
                # email_alert.send('SSLLOGIN Required')
                #push_notify.send_notification_to_dev('SSLLOGIN', 'Raspberry pi needs SSLLOGIN')
                print('Raspberry pi needs SSLLOGIN')
                return
            return 'No streams currently online.' not in file
            # return 'No streams currently online.' not in file


def regex_finder(tag: str, html: str, replace_text: bool = True) -> 'list[str]':
    '''
    regex_finder finds strings after a tag using regex matching
    Args:
        tag (str): a tag in the html such as "data-mnt" or "data-streams"
        html (str): the html string to parserTest
    Returns:
        str: the string attached to the tag.
    '''
    regex = r"{}=([\"'])((?:(?=(?:\\)*)\\.|.)*?)\1".format(tag)
    matches = re.finditer(regex, html, re.MULTILINE)

    list_matches: list[str] = []

    for match in matches:
        m = match.group()
        m = m.replace(tag, '').replace('=','').replace('\'','')
        if replace_text:
            m = m.replace('/','').title()
        list_matches.append(m)
    return list_matches


def run(sc: sched.scheduler):
    global titles, bodies, host_addresses
    url = 'http://hbniaudio.hbni.net/'
    lister = Changes(url)
    lister.update()
    dt = datetime.now()
    if not lister.check_for_streams():
        print(f'{bcolors.BOLD}{dt}{bcolors.ENDC} - {bcolors.OKBLUE}No streams currently online{bcolors.ENDC}')
        titles.clear()
        bodies.clear()
        host_addresses.clear()
        IS_DELAYED = 'NULL'
        s.enter(15, 1, run, (sc,))
        return

    if not lister.diff():
        print(f'{bcolors.BOLD}{dt}{bcolors.ENDC} - {bcolors.OKCYAN}No differences found{bcolors.ENDC}')
        s.enter(15, 1, run, (sc,))
        return

    changes = lister.diff()

    try:
        for change in changes:
            print(f'{bcolors.BOLD}{dt}{bcolors.ENDC} - {bcolors.OKGREEN}Changes: {change}{bcolors.ENDC}')
            app_log.info(f'{dt} - Changes: {change}')
            titles = regex_finder(tag='data-mnt', html=change)
            bodies = regex_finder(tag='data-stream', html=change)
            host_addresses = regex_finder(tag='data-mnt', html=change, replace_text=False)
            print(f'{bcolors.BOLD}{dt}{bcolors.ENDC} - {bcolors.OKGREEN}Titles: {titles}{bcolors.ENDC}')
            app_log.info(f'{dt} - Titles: {titles}')
            print(f'{bcolors.BOLD}{dt}{bcolors.ENDC} - {bcolors.OKGREEN}Bodies: {bodies}{bcolors.ENDC}')
            app_log.info(f'{dt} - Bodies: {bodies}')
            print(f'{bcolors.BOLD}{dt}{bcolors.ENDC} - {bcolors.OKGREEN}Host Addresses: {host_addresses}{bcolors.ENDC}')
            app_log.info(f'{dt} - Host Addresses: {host_addresses}')
            if len(titles) != 0:
                break
        if (len(titles) == 0 or len(bodies) == 0 or len(host_addresses) == 0):
            print(f'{bcolors.BOLD}{dt}{bcolors.ENDC} - {bcolors.FAIL}No data could be found in changes{bcolors.ENDC}')
            print(f'{bcolors.BOLD}{dt}{bcolors.ENDC} - {bcolors.OKBLUE}Starting next cylce{bcolors.ENDC}')
            s.enter(15, 1, run, (sc,))
            return
    except Exception as e: # IndexError
        print(f'{bcolors.BOLD}{dt}{bcolors.ENDC} - {bcolors.FAIL}Error: {e}{bcolors.ENDC}')
        app_log.info(f'{dt} - Error: {e}')
        print(f'{bcolors.BOLD}{dt}{bcolors.ENDC} - {bcolors.FAIL}No data could be found for active streams{bcolors.ENDC}')
        app_log.info(f'{dt} - No data could be found for active streams')
        print(f'{bcolors.BOLD}{dt}{bcolors.ENDC} - {bcolors.FAIL}Starting next cylce{bcolors.ENDC}')
        app_log.info(f'{dt} - Starting next cycle')
        s.enter(15, 1, run, (sc,))
        return

    for title, body, address in zip(titles, bodies, host_addresses):
        print(f"{bcolors.ENDC}{bcolors.BOLD}{dt}{bcolors.ENDC} - {bcolors.OKGREEN}Host: {title} Description: {body}{bcolors.ENDC}")
        app_log.info(f"{dt} - Host: {title} Description: {body} - Recording starting")
        fileName = f'{title} - {body}'
        threading.Thread(target=download, args=(fileName, address,)).start()

    s.enter(15, 1, run, (sc,))


def download(fileName: str, hostAddress: str):
    dt = datetime.now()
    print(f"{bcolors.ENDC}{bcolors.BOLD}{dt}{bcolors.ENDC} - {bcolors.OKGREEN}Started recording thread{bcolors.ENDC}")
    timestr = datetime.now().strftime('%B %d %A %Y')
    recordingstr = time.strftime("%Y%m%d%H%M%S")
    p = subprocess.Popen(
        [
            'ffmpeg',
            '-y',
            '-i',
            f'http://hbniaudio.hbni.net:8000{hostAddress}',
            f'CURRENTLY_RECORDING/{recordingstr}.mp3'
        ]
    )
    p.communicate()
    print(f"{bcolors.ENDC}{bcolors.BOLD}{dt}{bcolors.ENDC} - {bcolors.OKGREEN}Recording stopped{bcolors.ENDC}")
    os.rename(
            f'CURRENTLY_RECORDING/{recordingstr}.mp3',
            f'Recordings/{fileName} - {timestr}.mp3'
        )
    print(f"{bcolors.ENDC}{bcolors.BOLD}{dt}{bcolors.ENDC} - {bcolors.OKGREEN}Starting upload to Mega{bcolors.ENDC}")
    app_log.info(f"{dt} - Starting upload to Mega")
    MegaUploader.upload(file_path=f'Recordings/{fileName} - {timestr}.mp3')
    app_log.info(f"{dt} - Done uploading")
    print(f"{bcolors.ENDC}{bcolors.BOLD}{dt}{bcolors.ENDC} - {bcolors.OKGREEN}Done uploading{bcolors.ENDC}")


def main():
    s.enter(0, 0, run, (s,))
    print(f'{bcolors.BOLD}{datetime.now()}{bcolors.ENDC} - {bcolors.HEADER}Starting stream listener{bcolors.ENDC}')
    app_log.info(f'{datetime.now()} - Starting stream listener')
    s.run()


if __name__ == '__main__':
    main()
