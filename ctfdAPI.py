#!/usr/bin/python3

from bs4 import BeautifulSoup
from pathlib import Path
from cprint import ok, err, warn, info
from mega import Mega
import pandas as pd
import requests
import gdown
import wget
import json
import re
import os

class ctfdapi:
    def __init__(self, args):
        self.lstatus    = False
        self.url        = args.url
        self.auth       = dict(name=args.user, password=args.passwd)
        self.session    = requests.Session()
        self.__setup()

    def __setup(self):
        self.check      = lambda fname : os.path.exists(fname)
        self.CURRDIR   = os.path.dirname(os.path.realpath('__file__'))

        self.login_url  = self.url + '/login'
        self.logout_url = self.url + '/logout'
        self.hint_url   = self.url + '/api/v1/hints'
        self.sboard_url = self.url + '/api/v1/scoreboard'
        self.chall_url  = self.url + '/api/v1/challenges'
        self.submit_url = self.chall_url + '/attempt'
        self.headers    = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        if (not self.check(self.CURRDIR + '/.hide')):
            os.mkdir(self.CURRDIR + '/.hide')
        if (not self.check(self.CURRDIR + '/.hide/scoreboard.csv')):
            Path(self.CURRDIR + '/.hide/scoreboard.csv').touch()
        if (not self.check(self.CURRDIR + '/.hide/challenges.csv')):
            Path(self.CURRDIR + '/.hide/challenges.csv').touch()

    def submit_flag(self, flag, cate, chal, chal_id):
        filename = os.path.join(self.CURRDIR,cate,chal,'flag.txt')
        new_headers = {
            'Accept': 'application/json',
            'CSRF-Token': self.nonce,
            'Content-Type': 'application/json'
        }
        if (not all(k in self.headers.keys() for k in new_headers.keys())):
            self.headers.update(new_headers)
        submit = json.dumps({'challenge_id': chal_id, 'submission': flag})
        recv = self.session.post(self.submit_url, data=submit, headers=self.headers)
        status = json.loads(recv.content)
        with open(filename, 'w') as f:
            f.write(flag)
            f.close()
        return ok(f'[+] Message : {status["data"]["message"]}')

    def login(self):
        if (not self.lstatus):
            data = self.session.get(self.login_url, headers=self.headers)
            soup = BeautifulSoup(data.text, 'lxml')
            self.auth['nonce'] = soup.find('input', {'name':'nonce'}).get('value')
            self.auth['_submit'] = 'Submit'
            data = self.session.post(self.login_url, data=self.auth)
            if (data.status_code.__ne__(200)):
                # Check 403 Forbidden still login
                check = soup.find("div", {"class":"collapse navbar-collapse"})
                if ('Logout' not in re.findall(r'Logout',check.text)):
                    return warn('[!] Login failed')

            self.lstatus = True
            soup = BeautifulSoup(data.text, 'lxml')
            self.nonce = re.findall(r'\'csrfNonce\': "(\w+)', str(soup.find('script')))[0]
            return ok('[*] Login Successfuly')
        return warn('[!] Your already login')

    def logout(self):
        if (self.lstatus):
            if ('CSRF-Token' in self.headers): self.headers.pop('CSRF-Token')
            new_headers = { 'Content-Type': 'application/x-www-form-urlencoded' }
            self.headers.update(new_headers)
            recv = self.session.get(self.logout_url)
            if (recv.status_code.__eq__(200)):
                self.lstatus = False
            return ok('[*] Logout Successfuly')
        return warn('[!] Your already logout')

    def __get_id(self, link):
        data = pd.read_json(self.session.get(link).content)
        id = [ch['id'] for ch in data.data]
        return id

    def __get_hints(self, hints_id):
        recv = pd.read_json(self.session.get(f'{self.hint_url}/{hints_id}').text).data
        if ('content' in recv.keys()):
            return recv.content
        return f'Need cost point atleast : {recv.cost}'

    def get_challenges(self):
        if (self.lstatus):
            if ('CSRF-Token' in self.headers): self.headers.pop('CSRF-Token')
            filename = f'{self.CURRDIR}/.hide/challenges.csv'
            id_chals = self.__get_id(self.chall_url)
            key = ['attempts', 'category', 'description', 'files',
                    'hints', 'id', 'name', 'solves', 'value']
            challenges = pd.DataFrame(columns=key)
            for ids in id_chals:
                recv = pd.read_json(self.session.get(f'{self.chall_url}/{ids}').content)['data']
                if (len(recv.hints) != 0):
                    hdata = []
                    for hid in recv.hints:
                        hdata.append(self.__get_hints(hid['id']))
                    recv.hints = '\n'.join(hdata)
                challenges = challenges.append({k:recv[k] for k in key}, ignore_index=True)
            self._write_to_csv(challenges, filename)
            return ok('[*] Successfully scraping challenges')

    def get_scoreboard(self):
        filename = f'{self.CURRDIR}/.hide/scoreboard.csv'
        if ('CSRF-Token' in self.headers): self.headers.pop('CSRF-Token')
        key = ['pos', 'name', 'score']
        scoreboard = pd.DataFrame(columns=key)
        recv = pd.read_json(self.session.get(self.sboard_url).content)
        for pos in recv.data:
            scoreboard = scoreboard.append({k:pos[k] for k in key}, ignore_index=True)
        self._write_to_csv(scoreboard, filename)
        return ok('[*] Successfully scraping scoreboard')

    def _write_to_csv(self, new_dataframe, filename):
        new_dataframe.to_csv(filename, index=False)

    def download(self, num, name, category, links=None):
        platform = ['CTFd','GDRIVE','MEGA']
        outfile = f'{self.CURRDIR}/{category}/{name}/'
        if (platform[int(num)]):
            link = self.url + links
            if (not self.check(f'{outfile}{wget.filename_from_url(link)}')):
                filedown = wget.download(link, outfile)
                return ok(f'\n[!] Status {filedown}')
        elif (platform[int(num)]):
            tmp = re.findall(r'/[a-z0-9A-Z-_\+]+', links)[3][1:]
            url = f'https://drive.google.com/uc?id={tmp}'
            gdown.download(url, outfile, quiet=True)
            return warn('[*] Done')
        elif (platform[int(num)]):
            mega = Mega()
            m = mega.login()
            m.download_url(links, dest_path=outfile)
            return warn('[*] Done')
        else:
            return warn('[!] Choose one of these: [1]CTFd,[2]GDRIVE,[3]MEGA') 