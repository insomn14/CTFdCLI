#!/usr/bin/python3

class colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def warn(msg):  return "{}{}{}".format(colors.WARNING,msg,colors.ENDC)
def err(msg):   return "{}{}{}".format(colors.FAIL, msg, colors.ENDC)
def ok(msg):    return "{}{}{}".format(colors.OKGREEN, msg, colors.ENDC)
def info(msg):  return "{}{}{}".format(colors.OKCYAN, msg, colors.ENDC)