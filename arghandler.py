#!/usr/bin/python3

import json
import os
import argparse        

def arghandler(currdir):
    parser = argparse.ArgumentParser(description='CTFd-CLI scraping API', prog='ctfdcli', usage='%(prog)s -h [options]')
    parser.add_argument('user', nargs='?', metavar='user', type=str, help='Username/email')
    parser.add_argument('passwd', nargs='?', metavar='passwd', type=str, help='Password')
    parser.add_argument('url', nargs='?',  metavar='url', type=str, default='', help='example: http://ctf.chall.com')
    parser.add_argument('-n', '--interval', type=int, nargs='?', default=1000, help='Scraping every N seconds. default=1000')   

    args = parser.parse_args()
    if not os.path.exists(os.path.join(currdir,args.userdb)):
        __generateJS(args)
        return args
    elif (args.load):
        if (data := open(args.load, 'r')):
            return __loadJS(data, args)
    else:
        exit(parser.print_help())
