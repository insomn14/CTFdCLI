#!/usr/bin/python3

from cprint import ok, err, warn, info
from mega import Mega
import gdown
import wget
import re
import os

check = lambda fname : os.path.exists(fname)

def download_file(ctfd, choice, name, category, links=None):
    try:
        outfile = f'{ctfd.CURR_DIR}/{category}/{name}/'
        if (choice.__eq__('CTF event')):
            for lk in links:
                link = ctfd.url + lk
                if (not check(f'{outfile}/{wget.filename_from_url(link)}')):
                    ok(f'[!] Downloading : {link}')
                    filedown = wget.download(link, outfile)
                    ok(f'\n[!] Status {filedown}')
        else:
            if (choice.__eq__('Google drive')):
                child = re.findall(r'/[a-z0-9A-Z-_\+]+', links)[3][1:]
                url = f'https://drive.google.com/uc?id={child}'
                ok(f'[!] Downloading : {url}')
                gdown.download(url, outfile, quiet=False)
            elif (choice.__eq__('Mega.nz')):
                mega = Mega()
                m = mega.login()
                m.download_url(links, dest_path=outfile)
    except Exception as exp:
        err(f"[!] {exp}")
