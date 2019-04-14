#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  term_fut_pack.py
#
#=======================================================================
import os, sys, math, time
import logging
import smtplib
import sqlite3
from datetime import datetime, timezone
if sys.version_info[0] >= 3:
    import PySimpleGUI as sg
else:
    import PySimpleGUI27 as sg
#=======================================================================
class Class_LOGGER():
    def __init__(self, path_log):
        #self.logger = logging.getLogger(__name__)
        self.logger = logging.getLogger('__main__')
        self.logger.setLevel(logging.INFO)
        # create a file handler
        self.handler = logging.FileHandler(path_log)
        self.handler.setLevel(logging.INFO)
        # create a logging format
        #self.formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        self.handler.setFormatter(self.formatter)

        # add the handlers to the logger
        self.logger.addHandler(self.handler)
    #-------------------------------------------------------------------
    def wr_log_info(self, msg):
        self.logger.info(msg)
    #-------------------------------------------------------------------
    def wr_log_error(self, msg):
        self.logger.error(msg)
#=======================================================================


#=======================================================================
def main():
    # init program config
    dirr, sub_dirr = os.path.abspath(os.curdir), '\\DB\\'
    path_FUT = 'term_fut_pack.sqlite'
    db_path_FUT  = dirr + sub_dirr + path_FUT
    nm_trm, file_path_DATA, log_path = dirr + '\\DB\\term_fut_pack.sqlite', '', ''

    return
#=======================================================================
if __name__ == '__main__':
    import sys
    sys.exit(main())
