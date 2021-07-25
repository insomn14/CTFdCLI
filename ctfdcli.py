#!/usr/bin/python3 

from time import sleep
from ctfdAPI import ctfdapi
from cprint import ok, err, warn, info
from multiprocessing.pool import ThreadPool
from log import logging
import pandas as pd
import argparse
import _thread
import json
import sys
import os

CHECK = lambda fname : os.path.exists(fname)
CURRDIR = os.path.dirname(os.path.realpath('__file__'))
COMMAND = [
    'login','logout','scoreboard','challenges','select',
    'submit','scraping','download','clear','help','close'
]

class tmux:
    def __init__(self, pname, position, size):
        self.pname      = pname
        self.position   = position
        self.size       = size
        logging.info("Initial Class TEMUX")

    def _which(self, program):
        """Locate a command on the filesystem."""
        def is_exe(fpath):
            return os.path.isfile(fpath) and os.access(fpath, os.X_OK)
        fpath = os.path.split(program)[0]
        if fpath:
            if is_exe(program):
                return program
        else:
            for path in os.environ["PATH"].split(os.pathsep):
                path = path.strip('"')
                exe_file = os.path.join(path, program)
                if is_exe(exe_file):
                    return exe_file
        raise FileNotFoundError("Missing file `{:s}`".format(program))

    def setup(self):
        try:
            list_tty = []
            tmux = self._which("tmux")
            print(ok("tmux session found, splitting window..."))

            for pnm, pos, siz in zip(self.pname, self.position, self.size):
                old_ptses = sorted(os.listdir("/dev/pts"))
                if pos == '-v':
                    command = "! {} split-window {} -p {} 'clear ; cat'".format(tmux, pos, siz)
                else:
                    command = "! {} split-window {} -p {} 'clear ; cat'".format(tmux, pos, siz)
                os.system(command)
                new_ptses = set(os.listdir("/dev/pts"))
                pty = list(new_ptses - set(old_ptses))[0]
                pty = "/dev/pts/{}".format(pty)
                print(info("[+] {} panel : {}".format(pnm, pty)))
                list_tty.append(pty)

            _,L = os.get_terminal_size()
            os.system("! {} select-pane -D; {} resize-pane -U {}".format(tmux, tmux, L-2))
            print(ok("[+] Done!"))
            return list_tty
        except Exception as e:
            print(err(e))

class challenges:
    def __init__(self, mpty, pty):
        self.mpty       = mpty
        self.pty        = pty
        self.task       = set()
        self.filename   = os.path.join(CURRDIR,'.hide/challenges.csv')
        logging.info("Initial Class Challenges")

    def _readme(self, chall):
        logging.info("Call Method challenges._readme")
        name   = chall.name.values[0]
        cate   = chall.category.values[0]
        points = chall.value.values[0]
        solves = chall.solves.values[0]
        desc   = chall.description.values[0]
        hints  = chall.hints.values[0]
        files  = chall.files.values[0]
        fname = os.path.join(CURRDIR,cate,name,'README.md')
        if CHECK(fname): return
        cont  = '# {} [{} pts]\n\n'.format(name, points)
        cont += '**Category:** {}\n\n'.format(cate)
        cont += '**Solves:** {}\n\n'.format(solves)
        cont += '## Description\n>{}\n\n'.format(desc)
        cont += '**Hint**\n* {}\n\n'.format(hints)
        cont += '## File\n {}\n\n'.format(files)
        cont += '## Solution\n\n'
        cont += '### Flag\n\n'
        with open(fname, 'w') as f:
            f.write(cont)
            f.close()

    def _ptask(self, chall):
        logging.info("Call Method challenges._ptask")
        keys = ['id','name','value','description','hints','files']
        cont = ''.join(f'\r[{k.upper()}]: {info(chall[k].values[0])}\n' for k in keys).replace('`', '')
        command = 'clear > {}; echo "{}" > {}'.format(self.pty, cont, self.pty)
        os.system(command)

    def select(self, cate, chal):
        logging.info("Call Method challenges.select")
        if self.task != set():
            if cate in self.task.keys() and chal < len(self.task[cate]):
                challs = self.dataset.loc[ self.dataset.name == self.task[cate][chal] ]
                _thread.start_new_thread( self._ptask, (challs,) )
                _thread.start_new_thread( self._readme, (challs,) )
                return challs.category.values[0], challs.name.values[0], int(challs.id)
            else:
                logger(err('[!] Enter the correct category/challenges number'), self.pty)
        else:
            logger(err('[!] Enter command \'challenges\' first'), self.pty)

    def _pchall(self, cate):
        logging.info("Call Method challenges._pchall")
        cont = ''
        for ct in cate.keys():
            cont += '\n[{}] {}'.format(ct+1, warn(cate[ct]))
            tmp = os.path.join(CURRDIR,cate[ct])
            if not CHECK(f'{tmp}'): os.mkdir(f'{tmp}')
            for i, nm in enumerate(self.task[ct]):
                tmp = os.path.join(CURRDIR,cate[ct],nm)
                solved = CHECK(os.path.join(tmp,'flag.txt'))
                if not CHECK(f'{tmp}'): os.mkdir(f'{tmp}')
                cont += '\n    [{}] {}'.format(i+1, (err(nm),ok(nm))[solved])
        command = 'clear > {}; echo "{}" > {}'.format(self.mpty, cont, self.mpty)
        os.system(command)

    def show(self):
        try:
            logging.info("Call Method challenges.show")
            self.dataset = pd.read_csv(self.filename)
            lcate = self.dataset.category.unique()
            cate = {i:ct for i,ct in enumerate(lcate)}
            self.task = {i:list(self.dataset.loc[self.dataset.category == lc].name) for i,lc in enumerate(lcate)}
            self._pchall(cate)
        except Exception as e:
            logger(err(e), self.pty)

class scoreboard:
    def __init__(self, pty):
        self.pty        = pty
        self.filename   = os.path.join(CURRDIR,'.hide/scoreboard.csv')
        logging.info('Initial Class Scoreboard')

    def show(self, num=20):
        try:
            logging.info("Call Method scoreboard.show")
            self.dataset = pd.read_csv(self.filename).drop(columns='pos')
            cont = '\n'.join(f'{n},{s}' for n,s in zip( list(self.dataset.name[:num]), list(self.dataset.score[:num]) ))
            command = '''
                clear > {}; echo "{}" | termgraph --color red --width 20 --title "Scoreboard" > {}
            '''.format(self.pty, cont, self.pty)
            os.system(command)
        except Exception as e:
            logger(err(e), self.pty)

def logger(msg, pty):
    command = 'clear > {} ; echo "{}" > {}'.format(pty, msg, pty)
    os.system(command)

def help(pty):
    logging.info(f"Initial HELP!!!")
    cont = '''Command :
    - login         : login to ctfd platform
    - logout        : logout to ctfd platform
    - scoreboard    : Show Top 20 team on scoreboard.
    - challenges    : Show all of the challenges.
        + select    : Select a challenges. select:[num_cate]:[num_chall]
                      ( example -> select:2:1 )
        + submit    : Submit Flag. select:[num_cate]:[num_chall]:submit
                      ( example -> select:2:1:submit )
    - scraping      : Start scraping scoreboard & challenges
    - download      : Download chal. [1] CTFd, [2] GDRIVE, [3] MEGA
                      ( example -> download:<num>:<link> )
    - clear         : Clear all panel
    - close         : Exit program
    - help          : Help'''
    return logger(ok(cont), pty)

def _close(pty):
    command = [
        'pkill -9 -t {}'.format(p.replace('/dev/', '')) for p in pty
    ]
    for cmd in command:
        os.system(cmd)
    return 1

def posinput(msg='Command'):
    # _,L = os.get_terminal_size()
    # for _ in range(L):
    #     print()
    return str(input(ok('[?] {} : '.format(msg))))

def arghandler():
    parser = argparse.ArgumentParser(description='CTFd-cli', prog='ctfdcli', usage='%(prog)s -h [options]')
    parser.add_argument('url',  metavar='url', type=str, help='example: http://ctf.chall.com')
    parser.add_argument('user', metavar='user', type=str, help='Username/email')
    parser.add_argument('passwd', metavar='passwd', type=str, help='Password')
    parser.add_argument('-n', '--interval', type=int, nargs='?', default=1000, help='Scraping every N seconds. default=1000')   
    return parser.parse_args()

def main(ctfd, list_tty):
    mty, lty, cty = list_tty # main_pty, log_pty, chal_pty
    scoreb, chall = scoreboard(mty), challenges(mty, cty)
    while (True):
        try:
            stdin = posinput()
            if (stdin == COMMAND[0]):
                pool = ThreadPool(processes=1)
                async_result = pool.apply_async(ctfd.login, ())
                _thread.start_new_thread( logger, (async_result.get(), lty) )
            elif (stdin == COMMAND[1]):
                pool = ThreadPool(processes=1)
                async_result = pool.apply_async(ctfd.logout, ())
                _thread.start_new_thread( logger, (async_result.get(), lty) )
            elif (COMMAND[2] in stdin):
                _thread.start_new_thread( scoreb.show, () )
            elif (stdin == COMMAND[3]):
                _thread.start_new_thread( chall.show, () )
            elif (COMMAND[4] in stdin):
                cate, chal = [int(i)-1 for i in stdin.split(':') if i.isdigit()]
                cate, chal, chal_id = chall.select(cate, chal)
                if (COMMAND[5] in stdin):
                    if (ctfd.lstatus):
                        flag = posinput('Enter the flag')
                        _thread.start_new_thread( logger, (ctfd.submit_flag(flag, cate, chal, chal_id), cty, ) ) 
                    else:
                        _thread.start_new_thread( logger, (warn('[!] Your not login yet'), cty) )
            elif (COMMAND[6] in stdin):
                pool = ThreadPool(processes=1)
                for call in ['ctfd.get_scoreboard','ctfd.get_challenges']:
                    async_result = pool.apply_async(eval(call), ())
                    _thread.start_new_thread( logger, (async_result.get(), lty) )
            elif (stdin == COMMAND[7]):
                logger(warn('[-] TODO : Add download functional'), lty)
                # _, num, link = stdin.split(':')
                # pool = ThreadPool(processes=1)
                # async_result = pool.apply_async(ctfd.download, (num, name, category, link) )
                # _thread.start_new_thread( logger, (async_result.get(), lty) )
            elif (stdin == COMMAND[8]):
                for ty in list_tty:
                    _thread.start_new_thread( logger, ("", ty, ) )
            elif (stdin == COMMAND[9]):
                _thread.start_new_thread( eval(stdin), (lty, ) )
            elif (stdin == COMMAND[10]):
                exit(_close(list_tty))
            else:
                print(err('[!] Command "{}" not found'.format(stdin)))
        except (ValueError, Exception) as e:
            print(err('[!] {}'.format(e)))


if __name__ == '__main__':
    try:
        if (os.getenv('TMUX')):
            wpane = {
                'panel': ['main','challenges','logging'],
                'split': ['-v','-h','-v'],
                'size': [50,50,55]
            }
            list_tty = tmux(wpane['panel'], wpane['split'], wpane['size'])
            ctfd, list_tty = ctfdapi(arghandler()), list_tty.setup()
            main(ctfd, list_tty)
        else:
            logging.info(warn('[!] tmux session not found...'))
    except Exception as e:
        print(err(e))
        exit(_close(list_tty))
