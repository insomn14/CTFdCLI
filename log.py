#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging

FORMAT = '[ %(asctime)s | %(filename)s:%(lineno)s - %(funcName)s() ] %(levelname)s - %(message)s'
# set up logging to file
logging.basicConfig(
	filename='logger.log',
	level= logging.INFO,
	filemode='a',
	format=FORMAT,
	datefmt='%H:%M:%S'
)
# set up logging to console
console = logging.StreamHandler()
console.setLevel(logging.INFO)
# set a format which is simpler for console use
formatter = logging.Formatter(FORMAT)
console.setFormatter(formatter)
# add the handler to the root logger
logging.getLogger('').addHandler(console)
logger = logging.getLogger(__name__)

