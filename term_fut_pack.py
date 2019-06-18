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
class Class_ACCOUNT():
    def __init__(self):
        self.acc_date = ''
        self.acc_balance = 0.0
        self.acc_profit  = 0.0
        self.acc_go      = 0.0
        self.acc_depo    = 0.0
#=======================================================================
class Class_FUT():
    def __init__(self):
        self.sP_code = "-"
        self.sRest = 0
        self.sVar_margin = 0.0
        self.sOpen_price = 0.0
        self.sLast_price = 0.0
        self.sAsk =  0.0
        self.sBuy_qty = 0
        self.sBid =  0.0
        self.sSell_qty = 0
        self.sFut_go = 0.0
        self.sOpen_pos = 0.0
#=======================================================================
class Class_PACK():
    def __init__(self):
        self.ind= 0
        self.dt = ''
        self.tm = ''
        self.pAsk = 0.0
        self.pBid = 0.0
        self.EMAf = 0.0
        self.EMAf_rnd = 0.0
        self.cnt_EMAf_rnd = 0.0
#=======================================================================
class Class_ALARM():
    def __init__(self):
        self.ena_EMA_cnt= 0
#=======================================================================
class Class_GMAIL():
    def __init__(self, user, pwd, recipient ):
        self.user      = user
        self.pwd       = pwd
        self.recipient = recipient
    #-------------------------------------------------------------------
    def send_email(self, subject, body):
        gmail_user = self.user
        gmail_pwd  = self.pwd
        FROM       = self.user
        TO = self.recipient if type(self.recipient) is list else [self.recipient]
        SUBJECT = subject
        TEXT    = body
        # Prepare actual message
        message = """From: %s\nTo: %s\nSubject: %s\n\n%s
        """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
        try:
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.ehlo()
            server.starttls()
            server.login(gmail_user, gmail_pwd)
            server.sendmail(FROM, TO, message)
            server.close()
        except Exception as ex:
            return [1, str(ex)]

        return [0, 'OK']
#=======================================================================
class Class_SQLite():
    def __init__(self, path_db):
        self.path_db = path_db
        self.table_db = []
        self.conn = ''
        self.cur = ''
    #-------------------------------------------------------------------
    def check_db(self):
        '''  check FILE of DB SQLite    -----------------------------'''
        #    return os.stat: if FILE is and size != 0
        r_check_db = [0, '']
        name_path_db = self.path_db
        if not os.path.isfile(name_path_db):
            r_check_db = [1, 'can not find file']
        else:
            buf_st = os.stat(name_path_db)
            if buf_st.st_size == 0:
                r_check_db = [1, buf_st]
            else:
                r_check_db = [0, buf_st]
        return r_check_db
    #-------------------------------------------------------------------
    def reset_table_db(self, name_tbl):
        ''' reset data in table DB  ---------------------------------'''
        r_reset_tbl = [0, '']
        try:
            self.conn = sqlite3.connect(self.path_db)
            self.cur = self.conn.cursor()
            self.cur.execute("DELETE FROM " + name_tbl)
            self.conn.commit()
            self.conn.execute("VACUUM")
            self.cur.close()
            self.conn.close()
            r_reset_tbl = [0, 'OK']
        except Exception as ex:
            r_reset_tbl = [1, str(ex)]
        return r_reset_tbl
    #-------------------------------------------------------------------
    def rewrite_table(self, name_tbl, name_list, val = '(?, ?)'):
        ''' rewrite data from table ARCHIV_PACK & PACK_TODAY & DATA ----'''
        r_rewrt_tbl = [0, '']
        try:
            self.conn = sqlite3.connect(self.path_db)
            self.cur = self.conn.cursor()
            self.cur.execute("DELETE FROM " + name_tbl)
            self.cur.executemany("INSERT INTO " + name_tbl + " VALUES" + val, name_list)
            self.conn.commit()
            self.cur.close()
            self.conn.close()
            r_rewrt_tbl = [0, 'OK']
        except Exception as ex:
            r_rewrt_tbl = [1, str(ex)]
        return r_rewrt_tbl
    #-------------------------------------------------------------------
    def write_table_db(self, name_tbl, name_list):
        ''' write data string into table DB  ------------------------'''
        r_write_tbl = [0, '']
        try:
            self.conn = sqlite3.connect(self.path_db)
            self.cur = self.conn.cursor()
            self.cur.executemany("INSERT INTO " + name_tbl + " VALUES(?, ?)", name_list)
            self.conn.commit()
            self.cur.close()
            self.conn.close()
            r_write_tbl = [0, 'OK']
        except Exception as ex:
            r_write_tbl = [1, str(ex)]
        return r_write_tbl
    #-------------------------------------------------------------------
    def rwr_tbl_wr_tbl(self, nm_tbl_rwr, nm_lst_rwr, nm_tbl_wr, nm_lst_wr):
        ''' rewrite data from from terminal file  -------------------'''
        '''   write data string into table DB  ----------------------'''
        r_rewrt_tbl = [0, '']
        try:
            self.conn = sqlite3.connect(self.path_db)
            self.cur = self.conn.cursor()
            #
            # rwr_tbl rewrite data from TERM  into table data_FUT
            self.cur.execute("DELETE FROM " + nm_tbl_rwr)
            self.cur.executemany("INSERT INTO " + nm_tbl_rwr + " VALUES(?)", nm_lst_rwr)
            #
            # wr_tbl write last string        into table hist_FUT_today
            self.cur.execute("DELETE FROM " + nm_tbl_wr)
            self.cur.executemany("INSERT INTO " + nm_tbl_wr + " VALUES(?, ?)", nm_lst_wr)
            #
            self.conn.commit()
            self.cur.close()
            self.conn.close()
            r_rewrt_tbl = [0, 'OK']
        except Exception as ex:
            r_rewrt_tbl = [1, str(ex)]
        return r_rewrt_tbl
    #-------------------------------------------------------------------
    def get_table_db_with(self, name_tbl):
        ''' read one table DB  --------------------------------------'''
        r_get_table_db = []
        self.conn = sqlite3.connect(self.path_db)
        try:
            with self.conn:
                self.cur = self.conn.cursor()
                #self.cur.execute("PRAGMA busy_timeout = 3000")   # 3 s
                self.cur.execute("SELECT * from " + name_tbl)
                self.table_db = self.cur.fetchall()    # read table name_tbl
                r_get_table_db = [0, self.table_db]
        except Exception as ex:
            r_get_table_db = [1, name_tbl + str(ex)]

        return r_get_table_db
#=======================================================================
class Class_TERM_data():
    #///////////////////////////////////////////////////////////////////
    def __init__(self, path_trm):
        self.path_trm  = path_trm
        #
        self.dt_file = 0        # curv stamptime data file path_trm
        self.dt_data = 0        # curv stamptime DATA/TIME from TERM
        self.data_in_file = []  # list of strings from path_trm
        self.data_fut = []      # list of Class_FUT() from trm
        self.account  = ''      # obj Class_ACCOUNT() from trm
        self.delay_tm = 8       # min period to get data for DB (10 sec)
        #
        self.sec_10_00 = 36000      # seconds from 00:00 to 10:00
        self.sec_14_00 = 50400      # seconds from 00:00 to 14:00
        self.sec_14_05 = 50700      # seconds from 00:00 to 14:05
        self.sec_18_45 = 67500      # seconds from 00:00 to 18:45
        self.sec_19_05 = 68700      # seconds from 00:00 to 19:05
        self.sec_23_45 = 85500      # seconds from 00:00 to 23:45
    #///////////////////////////////////////////////////////////////////
    def rd_term_service(self):
        #--- check file cntr.file_path_DATA ----------------------------
        if not os.path.isfile(self.path_trm):
            err_msg = 'can not find file => ' + self.path_trm
            #cntr.log.wr_log_error(err_msg)
            return [1, err_msg]
        buf_stat = os.stat(self.path_trm)
        #
        #--- check size of file ----------------------------------------
        if buf_stat.st_size == 0:
            err_msg = 'size DATA file is NULL'
            #cntr.log.wr_log_error(err_msg)
            return [2, err_msg]
        #
        #--- read TERM file --------------------------------------------
        buf_str = []
        with open(self.path_trm,"r") as fh:
            buf_str = fh.read().splitlines()
        #
        #--- check size of list/file -----------------------------------
        if len(buf_str) == 0:
            err_msg = ' the size buf_str is NULL'
            #cntr.log.wr_log_error(err_msg)
            return [4, err_msg]
        #
        self.data_in_file = []
        self.data_in_file = buf_str[:]
        #print(self.data_in_file)
        #
        req = self.parse_data_in_file()
        if req[0] != 0:
            err_msg = 'parse_data_in_file / ' + str(ex)
            return [9, err_msg]
        return [0, 'OK']
    #///////////////////////////////////////////////////////////////////
    def rd_term(self):
        #--- check file cntr.file_path_DATA ----------------------------
        if not os.path.isfile(self.path_trm):
            err_msg = 'can not find file => ' + self.path_trm
            #cntr.log.wr_log_error(err_msg)
            return [1, err_msg]
        buf_stat = os.stat(self.path_trm)
        #
        #--- check size of file ----------------------------------------
        if buf_stat.st_size == 0:
            err_msg = 'size DATA file is NULL'
            #cntr.log.wr_log_error(err_msg)
            return [2, err_msg]
        #
        #--- check time modificated of file ----------------------------
        if int(buf_stat.st_mtime) == self.dt_file:
            #str_dt_file = datetime.fromtimestamp(self.dt_file).strftime('%H:%M:%S')
            return [3, 'FILE is not modificated ' + time.strftime("%M:%S", time.gmtime())]
        else:
            #self.dt_file_prev = self.dt_file
            self.dt_file = int(buf_stat.st_mtime)
            #print(self.dt_file)
        #
        #--- read TERM file --------------------------------------------
        buf_str = []
        with open(self.path_trm,"r") as fh:
            buf_str = fh.read().splitlines()
        #
        #--- check size of list/file -----------------------------------
        if len(buf_str) == 0:
            err_msg = ' the size buf_str is NULL'
            #cntr.log.wr_log_error(err_msg)
            return [4, err_msg]
        #
        #--- check modificated DATE/TIME of term ! ---------------------
        #--- It's should be more then 10 sec ---------------------------
        try:
            dt_str = buf_str[0].split('|')[0]
            dt_datetime = datetime.strptime(dt_str, '%d.%m.%Y %H:%M:%S')
            dt_sec = dt_datetime.replace(tzinfo=timezone.utc).timestamp()      # real UTC
            if (dt_sec - self.dt_data) > self.delay_tm:
                self.dt_data = int(dt_sec)
            else:
                str_dt_data = datetime.fromtimestamp(self.dt_data).strftime('%H:%M:%S')
                err_msg = str_dt_data + '  DATA is not updated  ' + dt_str
                #cntr.log.wr_log_error(err_msg)
                return [5, err_msg]
        except Exception as ex:
            err_msg = dt_str + ' => ' + str(ex)
            cntr.log.wr_log_error(err_msg)
            return [6, err_msg]
        #
        #--- check MARKET time from 10:00 to 23:45 ---------------------
        #term_dt = cntr.term.data_in_file[0].split('|')[0]
        term_dt = buf_str[0].split('|')[0]
        dtt = datetime.strptime(str(term_dt), "%d.%m.%Y %H:%M:%S")
        cur_time = dtt.second + 60 * dtt.minute + 60 * 60 * dtt.hour
        if not (
            (cur_time > self.sec_10_00  and # from 10:00 to 14:00
            cur_time < self.sec_14_00) or
            (cur_time > self.sec_14_05  and # from 14:05 to 18:45
            cur_time < self.sec_18_45) or
            (cur_time > self.sec_19_05  and # from 19:05 to 23:45
            cur_time < self.sec_23_45)):
                err_msg = 'it is not MARKET time now'
                #cntr.log.wr_log_error(err_msg)
                return [7, err_msg]
        #
        #--- compare new DATA with old ---------------------------------
        new_data = buf_str[2:]
        old_data = self.data_in_file[2:]
        buf_len = len(list(set(new_data) - set(old_data)))
        if  buf_len == 0:
            err_msg = 'ASK/BID did not change'
            #cntr.log.wr_log_error(err_msg)
            return [8, err_msg]
        #---  you will do more checks in the future!!!  ----------------
        #--- check ASK != 0  -------------------------------------------
        #--- check BID != 0  -------------------------------------------
        #--- check ASK < BID -------------------------------------------
        #
        self.data_in_file = []
        self.data_in_file = buf_str[:]
        #print(self.data_in_file)
        #
        req = self.parse_data_in_file()
        if req[0] != 0:
            err_msg = 'parse_data_in_file / ' + str(ex)
            return [9, err_msg]
        return [0, 'OK']
    #///////////////////////////////////////////////////////////////////
    def parse_data_in_file(self):
        try:
            self.data_fut = []
            self.account  = Class_ACCOUNT()
            # format of list data_fut:
            #   0   => string of DATA / account.acc_date
            #   1   => [account.acc_balance/acc_profit/acc_go/acc_depo]
            #   2 ... 22  => Class_FUT()
            #print(self.data_in_file)

            for i, item in enumerate(list(self.data_in_file)):
                list_item = ''.join(item).replace(',','.').split('|')
                if   i == 0:
                    self.account.acc_date  = list_item[0]
                    self.data_fut.append(self.account.acc_date)
                elif i == 1:
                    self.account.acc_balance = float(list_item[0])
                    self.account.acc_profit  = float(list_item[1])
                    self.account.acc_go      = float(list_item[2])
                    self.account.acc_depo    = float(list_item[3])
                    self.data_fut.append([self.account.acc_balance,
                                            self.account.acc_profit,
                                            self.account.acc_go,
                                            self.account.acc_depo ])
                else:
                    #print(item)
                    b_fut = Class_FUT()
                    b_fut.sP_code      = list_item[0]
                    b_fut.sRest        = int  (list_item[1])
                    b_fut.sVar_margin  = float(list_item[2])
                    b_fut.sOpen_price  = float(list_item[3])
                    b_fut.sLast_price  = float(list_item[4])
                    b_fut.sAsk         = float(list_item[5])
                    b_fut.sBuy_qty     = int  (list_item[6])
                    b_fut.sBid         = float(list_item[7])
                    b_fut.sSell_qty    = int  (list_item[8])
                    b_fut.sFut_go      = float(list_item[9])
                    b_fut.sOpen_pos    = float(list_item[10])
                    self.data_fut.append(b_fut)
            #print('cntr.data_fut => \n', cntr.data_fut)
        except Exception as ex:
            err_msg = 'parse_data_in_file / ' + str(ex)
            print(err_msg)
            cntr.log.wr_log_error(err_msg)
            return [1, err_msg]
        return [0, 'ok']
#=======================================================================
class Class_TERM_hist():
    #///////////////////////////////////////////////////////////////////
    def __init__(self, path_hist):
        self.path_hist  = path_hist
        self.hist_in_file = []  # list of strings from path_hist
        #
        self.sec_10_00 = 36000      # seconds from 00:00 to 10:00
        self.sec_14_00 = 50400      # seconds from 00:00 to 14:00
        self.sec_14_05 = 50700      # seconds from 00:00 to 14:05
        self.sec_18_45 = 67500      # seconds from 00:00 to 18:45
        self.sec_19_05 = 68700      # seconds from 00:00 to 19:05
        self.sec_23_45 = 85500      # seconds from 00:00 to 23:45
    #///////////////////////////////////////////////////////////////////
    def rd_hist(self):
        #--- check file cntr.file_path_DATA ----------------------------
        if not os.path.isfile(self.path_hist):
            err_msg = 'can not find file => ' + self.path_hist
            #cntr.log.wr_log_error(err_msg)
            return [1, err_msg]
        buf_stat = os.stat(self.path_hist)
        #
        #--- check size of file ----------------------------------------
        if buf_stat.st_size == 0:
            err_msg = 'size HIST file is NULL'
            return [2, err_msg]
        #
        #--- read HIST file --------------------------------------------
        buf_str = []
        with open(self.path_hist,"r") as fh:
            buf_str = fh.read().splitlines()
        #
        #--- check size of list/file -----------------------------------
        if len(buf_str) == 0:
            err_msg = 'the size buf_str(HIST) is NULL '
            return [3, err_msg]
        #
        #--- check MARKET time from 10:00 to 23:45 ---------------------
        self.hist_in_file = []
        for item in buf_str:
            term_dt = item.split('|')[0]
            dtt = datetime.strptime(str(term_dt), "%d.%m.%Y %H:%M:%S")
            cur_time = dtt.second + 60 * dtt.minute + 60 * 60 * dtt.hour
            #if not (
            if (
                (cur_time > self.sec_10_00  and # from 10:00 to 14:00
                cur_time < self.sec_14_00) or
                (cur_time > self.sec_14_05  and # from 14:05 to 18:45
                cur_time < self.sec_18_45) or
                (cur_time > self.sec_19_05  and # from 19:05 to 23:45
                cur_time < self.sec_23_45)):
                    self.hist_in_file.append(item)
        #
        return [0, 'ok']
#=======================================================================
class Class_TABLE_cfg_alarm():
    #///////////////////////////////////////////////////////////////////
    def __init__(self, path_term_fut_pack):
        self.obj_table = Class_SQLite(path_term_fut_pack)
        self.path_term_fut_pack = path_term_fut_pack
        self.nm            = []  # list NM             of packets
        self.ena_cnt_ema   = []  # list cnt_EMAf_rnd   of packets
    #///////////////////////////////////////////////////////////////////
    def read_tbl(self):
        self.nm, self.ena_cnt_ema  = [], []
        rq  = self.obj_table.get_table_db_with('cfg_ALARM')
        if rq[0] != 0:
            err_msg = 'Can not read TBL cfg_ALARM !' + '  '.join(str(e) for e in rq)
            print(err_msg)
            #sg.PopupError(err_msg)
            return [1, rq[1]]

        for item in rq[1]:
            #print(item)
            self.nm.append(item[0])             # just ex ['pckt0']
            self.ena_cnt_ema.append(item[1])    # just ex [True]

        return [0, 'ok']
    #///////////////////////////////////////////////////////////////////
    def rewrite_tbl(self):
        # rewrite table cfg_ALARM
        duf_list = []
        for j, jtem in enumerate(self.nm):
            buf = (self.nm[j], self.ena_cnt_ema[j])
            #print(buf)
            duf_list.append(buf)
        rq = self.obj_table.rewrite_table('cfg_ALARM', duf_list, val = '(?,?)')
        if rq[0] != 0:
            err_msg = 'rewrite_tbl cfg_ALARM ' + '  '.join(str(e) for e in rq)
            return [1, err_msg]
        return [0, 'ok']
#=======================================================================
class Class_TABLE_cfg_pack():
    #///////////////////////////////////////////////////////////////////
    def __init__(self, path_term_fut_pack):
        self.obj_table = Class_SQLite(path_term_fut_pack)
        self.path_term_fut_pack = path_term_fut_pack
        self.nm   = []  # list NM   of packets
        self.koef = []  # list KOEF of packets
        self.nul  = []  # list NUL  of packets
        self.ema  = []  # list EMA  of packets
    #///////////////////////////////////////////////////////////////////
    def read_tbl(self):
        self.nm, self.koef, self.nul, self.ema = [], [], [], []
        rq  = self.obj_table.get_table_db_with('cfg_PACK')
        if rq[0] != 0:
            err_msg = 'Can not read TBL cfg_PACK !' + '  '.join(str(e) for e in rq)
            print(err_msg)
            sg.PopupError(err_msg)
            return [1, rq[1]]

        for item in rq[1]:
            #print(item)
            self.nm.append(item[0])             # just ex ['pckt0']
            self.koef.append(item[1].split(','))# just ex ['0:3:SR','9:-20:MX
            self.nul.append(item[2])            # just ex [0]
            self.ema.append(item[3].split(':')) # just ex ['1111:15']

        return [0, 'ok']
    #///////////////////////////////////////////////////////////////////
    def rewrite_tbl(self):
        # rewrite table cfg_PACK
        duf_list = []
        for j, jtem in enumerate(self.nm):
            buf = (self.nm[j], ','.join(self.koef[j]), self.nul[j], ':'.join(self.ema[j]))
            #print(buf)
            duf_list.append(buf)
        rq = self.obj_table.rewrite_table('cfg_PACK', duf_list, val = '(?,?,?,?)')
        if rq[0] != 0:
            err_msg = 'rewrite_tbl cfg_PACK ' + '  '.join(str(e) for e in rq)
            return [1, err_msg]
        return [0, 'ok']
#=======================================================================
class Class_TABLE_cfg_soft():
    #///////////////////////////////////////////////////////////////////
    def __init__(self, path_term_fut_pack):
        self.obj_table = Class_SQLite(path_term_fut_pack)
        self.path_term_fut_pack  = path_term_fut_pack
        self.titul = self.dt_start = ''
        self.dt_start_sec = 0
        self.path_file_DATA = self.path_file_HIST = ''
    #///////////////////////////////////////////////////////////////////
    def read_tbl(self):
        rq  = self.obj_table.get_table_db_with('cfg_SOFT')
        if rq[0] != 0:
            err_msg = 'Can not read TBL cfg_SOFT !' + '  '.join(str(e) for e in rq)
            print(err_msg)
            sg.PopupError(err_msg)
            return [1, rq[1]]

        for item in rq[1]:
            if item[0] == 'titul'         : self.titul           = item[1]
            if item[0] == 'path_file_DATA': self.path_file_DATA  = item[1]
            if item[0] == 'path_file_HIST': self.path_file_HIST  = item[1]
            if item[0] == 'dt_start'      : self.dt_start        = item[1]

        frm = '%Y-%m-%d %H:%M:%S'
        self.dt_start_sec = \
            int(datetime.strptime(self.dt_start, frm).replace(tzinfo=timezone.utc).timestamp())

        return [0, 'ok']
#=======================================================================
class Class_TABLE_data_fut():
    #///////////////////////////////////////////////////////////////////
    def __init__(self, path_term_fut_pack):
        self.obj_table = Class_SQLite(path_term_fut_pack)
        self.path_term_fut_pack = path_term_fut_pack
        self.data_fut = []                  # list of Class_FUT()
        self.account  = Class_ACCOUNT()     # obj Class_ACCOUNT()
    #///////////////////////////////////////////////////////////////////
    def rewrite_tbl(self, buf_tbl):
        # rewrite table DATA
        duf_list = []
        for j, jtem in enumerate(buf_tbl):
            buf = (jtem,)
            duf_list.append(buf)
        rq = self.obj_table.rewrite_table('data_FUT', duf_list, val = '(?)')
        if rq[0] != 0:
            err_msg = 'rewrite_tbl data_FUT ' + '  '.join(str(e) for e in rq)
            return [1, err_msg]
        return [0, 'ok']
    #///////////////////////////////////////////////////////////////////
    def read_tbl(self):
        rq  = self.obj_table.get_table_db_with('data_FUT')
        if rq[0] != 0:
            err_msg = 'Can not read TBL data_FUT ! ' + '  '.join(str(e) for e in rq)
            print(err_msg)
            #sg.PopupError(err_msg)
            return [1, err_msg]

        try:
            self.data_fut = []

            for i, item in enumerate(list(rq[1])):
                list_item = ''.join(item).replace(',','.').split('|')
                if   i == 0:
                    self.account.acc_date  = list_item[0]
                elif i == 1:
                    self.account.acc_balance = float(list_item[0])
                    self.account.acc_profit  = float(list_item[1])
                    self.account.acc_go      = float(list_item[2])
                    self.account.acc_depo    = float(list_item[3])
                else:
                    b_fut = Class_FUT()
                    b_fut.sP_code      = list_item[0]
                    b_fut.sRest        = int  (list_item[1])
                    b_fut.sVar_margin  = float(list_item[2])
                    b_fut.sOpen_price  = float(list_item[3])
                    b_fut.sLast_price  = float(list_item[4])
                    b_fut.sAsk         = float(list_item[5])
                    b_fut.sBuy_qty     = int  (list_item[6])
                    b_fut.sBid         = float(list_item[7])
                    b_fut.sSell_qty    = int  (list_item[8])
                    b_fut.sFut_go      = float(list_item[9])
                    b_fut.sOpen_pos    = float(list_item[10])
                    self.data_fut.append(b_fut)
        except Exception as ex:
            err_msg = 'parse_data_in_file / ' + str(ex)
            return [1, err_msg]

        return [0, 'ok']
    #///////////////////////////////////////////////////////////////////
    def read_data_in_file(self, arr_strings):
        try:
            self.data_fut = []
            for i, item in enumerate(arr_strings):
                list_item = ''.join(item).replace(',','.').split('|')
                if   i == 0:
                    self.account.acc_date  = list_item[0]
                elif i == 1:
                    self.account.acc_balance = float(list_item[0])
                    self.account.acc_profit  = float(list_item[1])
                    self.account.acc_go      = float(list_item[2])
                    self.account.acc_depo    = float(list_item[3])
                else:
                    b_fut = Class_FUT()
                    b_fut.sP_code      = list_item[0]
                    b_fut.sRest        = int  (list_item[1])
                    b_fut.sVar_margin  = float(list_item[2])
                    b_fut.sOpen_price  = float(list_item[3])
                    b_fut.sLast_price  = float(list_item[4])
                    b_fut.sAsk         = float(list_item[5])
                    b_fut.sBuy_qty     = int  (list_item[6])
                    b_fut.sBid         = float(list_item[7])
                    b_fut.sSell_qty    = int  (list_item[8])
                    b_fut.sFut_go      = float(list_item[9])
                    b_fut.sOpen_pos    = float(list_item[10])
                    self.data_fut.append(b_fut)
        except Exception as ex:
            err_msg = 'read_data_in_file / ' + str(ex)
            return [1, err_msg]

        return [0, 'ok']
#=======================================================================
class Class_TABLE_hist_fut_today():
    #///////////////////////////////////////////////////////////////////
    def __init__(self, path_term_fut_pack):
        self.obj_table = Class_SQLite(path_term_fut_pack)
        self.path_term_fut_pack = path_term_fut_pack
        self.hist_fut_today   = []  # list of [[ind_sec string] ... ]
        self.hist_1_fut_today = []  # list period 1 minute
        self.arr_1_fut_today  = []  # list period 1 minute

        self.sec_10_00 = 36000      # seconds from 00:00 to 10:00
        self.sec_14_00 = 50400      # seconds from 00:00 to 14:00
        self.sec_14_05 = 50700      # seconds from 00:00 to 14:05
        self.sec_18_45 = 67500      # seconds from 00:00 to 18:45
        self.sec_19_05 = 68700      # seconds from 00:00 to 19:05
        self.sec_23_45 = 85500      # seconds from 00:00 to 23:45
    #///////////////////////////////////////////////////////////////////
    def read_tbl(self):
        rq  = self.obj_table.get_table_db_with('hist_FUT_today')
        if rq[0] != 0:
            err_msg = 'Can not read TBL hist_FUT_today ! ' + '  '.join(str(e) for e in rq)
            print(err_msg)
            return [1, err_msg]

        self.hist_fut_today = []
        self.hist_fut_today = rq[1][:]
        #print('read hist_fut_today => ', len(self.hist_fut_today), ' strings')

        self.hist_1_fut_today = []
        if len(self.hist_fut_today) != 0:
            self.hist_1_fut_today.append(self.hist_fut_today[0])
            frm = '%d.%m.%Y %H:%M:%S'
            dtt = datetime.strptime(str(self.hist_fut_today[0][1].split('|')[0]), frm)
            buf_60_sec = dtt.minute
            for item in self.hist_fut_today:
                dtt = datetime.strptime(str(item[1].split('|')[0]), frm)
                if dtt.minute != buf_60_sec:
                    self.hist_1_fut_today.append(item)
                    buf_60_sec = dtt.minute
        #print('parse hist_1_fut_today => ', len(self.hist_1_fut_today), ' strings')

        self.arr_1_fut_today = []
        for item in self.hist_1_fut_today:
            arr_item = (item[1].replace(',', '.')).split('|')
            arr_jtem = []
            arr_jtem.append(item[0])
            arr_jtem.append(arr_item[0])
            for jtem in arr_item[1:-1]:
                arr_jtem.append(float(jtem))
            self.arr_1_fut_today.append(arr_jtem)

        #print(self.arr_1_fut_today[-1])
        #print('arr_1_fut_today[-1] => ', self.arr_1_fut_today[-1])

        return [0, 'ok']
    #///////////////////////////////////////////////////////////////////
    def rewrite_tbl(self, term_hist):
        #print('term_hist[-1] => ', term_hist[-1])
        self.hist_fut_today = []
        self.hist_1_fut_today = []

        buf_60_sec = 666
        frm = '%d.%m.%Y %H:%M:%S'
        try:
            if term_hist != '':
                for i, item in enumerate(term_hist):
                    list_item = item.split('|')
                    dtt = datetime.strptime(list_item[0], frm)
                    ind_sec  = int(dtt.replace(tzinfo=timezone.utc).timestamp())
                    cur_time = dtt.second + 60 * dtt.minute + 60 * 60 * dtt.hour
                    if (
                        (cur_time > self.sec_10_00  and # from 10:00 to 14:00
                        cur_time < self.sec_14_00) or
                        (cur_time > self.sec_14_05  and # from 14:05 to 18:45
                        cur_time < self.sec_18_45) or
                        (cur_time > self.sec_19_05  and # from 19:05 to 23:45
                        cur_time < self.sec_23_45)):
                            self.hist_fut_today.append([ind_sec, item])
                            if buf_60_sec != dtt.minute :
                                buf_60_sec = dtt.minute
                                self.hist_1_fut_today.append([ind_sec, item])

            else:
                return [1, 'hist_in_file is empty! ']
        except Exception as ex:
            err_msg = 'rewrite_tbl => ' + str(ex)
            return [1, err_msg]

        #print('self.hist_1_fut_today[-1] => ', self.hist_1_fut_today[-1])

        self.arr_1_fut_today = []
        for item in self.hist_1_fut_today:
            arr_item = (item[1].replace(',', '.')).split('|')
            arr_jtem = []
            arr_jtem.append(item[0])
            arr_jtem.append(arr_item[0])
            for jtem in arr_item[1:-1]:
                arr_jtem.append(float(jtem))
            self.arr_1_fut_today.append(arr_jtem)

        #print('self.hist_fut_today[-1] => ', self.hist_fut_today[-1])

        rq = self.obj_table.rewrite_table('hist_FUT_today', self.hist_fut_today, val = '(?,?)')
        if rq[0] != 0:
            err_msg = 'rewrite_table(hist_FUT_today) ' + '  '.join(str(e) for e in rq)
            return [1, err_msg]

        return [0, 'ok']
#=======================================================================
class Class_TABLE_hist_pack_today():
    #///////////////////////////////////////////////////////////////////
    def __init__(self, path_term_fut_pack):
        self.path_term_fut_pack  = path_term_fut_pack
        self.obj_table = Class_SQLite(path_term_fut_pack)
        self.hist_pack_today = []  # list of [[ind_sec string] ... ]
    #///////////////////////////////////////////////////////////////////
    def rewrite_tbl(self, hist_arc):
        self.hist_pack_today = []
        rq = self.obj_table.rewrite_table('hist_PACK_today', hist_arc, val = '(?,?)')
        if rq[0] != 0:
            err_msg = 'rewrite_table hist_PACK_today ' + '  '.join(str(e) for e in rq)
            #cntr.log.wr_log_error(err_msg)
            #sg.Popup('Error !', err_msg)
            return [1, err_msg]

        return [0, 'OK']
#=======================================================================
class Class_TABLE_hist_fut():
    def __init__(self, path_term_fut_archiv):
        self.path_term_fut_archiv  = path_term_fut_archiv
        self.obj_table = Class_SQLite(path_term_fut_archiv)
        self.hist_fut_archiv = []  # list of [[ind_sec string] ... ]
        self.arr_fut_archiv  = []  # list period 1 minute
    #///////////////////////////////////////////////////////////////////
    def read_tbl(self):
        rq  = self.obj_table.get_table_db_with('hist_FUT')
        if rq[0] != 0:
            err_msg = 'Can not read TBL hist_FUT ! ' + '  '.join(str(e) for e in rq)
            print(err_msg)
            return [1, err_msg]

        self.hist_fut_archiv = []
        self.hist_fut_archiv = rq[1][:]
        #print('read hist_FUT => ', len(self.hist_fut_archiv), ' strings')

        self.arr_fut_archiv = []
        for item in self.hist_fut_archiv:
            arr_item = (item[1].replace(',', '.')).split('|')
            arr_jtem = []
            arr_jtem.append(item[0])
            arr_jtem.append(arr_item[0])
            for jtem in arr_item[1:-1]:
                arr_jtem.append(float(jtem))
            self.arr_fut_archiv.append(arr_jtem)

        #print('arr_fut_archiv[-1] => ', self.arr_fut_archiv[-1])

        return [0, 'ok']
#=======================================================================
class Class_TABLE_hist_pack():
    #///////////////////////////////////////////////////////////////////
    def __init__(self, path_term_fut_archiv):
        self.path_term_fut_archiv  = path_term_fut_archiv
        self.obj_table = Class_SQLite(path_term_fut_archiv)
        self.hist_pack_archiv = []  # list of [[ind_sec string] ... ]
    #///////////////////////////////////////////////////////////////////
    def rewrite_tbl(self, hist_arc):
        self.hist_pack_archiv = []
        rq = self.obj_table.rewrite_table('hist_PACK', hist_arc, val = '(?,?)')
        if rq[0] != 0:
            err_msg = 'rewrite_table hist_PACK ' + '  '.join(str(e) for e in rq)
            #cntr.log.wr_log_error(err_msg)
            #sg.Popup('Error !', err_msg)
            return [1, err_msg]

        return [0, 'OK']
#=======================================================================
class Class_CONTROLER():
    #///////////////////////////////////////////////////////////////////
    def __init__(self):
        c_dir = os.path.abspath(os.curdir)
        self.log = Class_LOGGER(c_dir + '\\LOG\\term_fut_pack_logger.log')
        path_TERM_FUT_PACK    = c_dir + '\\DB\\term_fut_pack.sqlite'
        path_TERM_FUT_ARCHIV  = c_dir + '\\DB\\term_fut_archiv.sqlite'

        self.cfg_soft = Class_TABLE_cfg_soft(path_TERM_FUT_PACK)
        rq = self.cfg_soft.read_tbl()
        if rq[0] != 0:
            err_msg = 'Can not init TBL cfg_SOFT !' + '  '.join(str(e) for e in rq)
            sg.PopupError('Error !', err_msg)
            print(err_msg)
            return [1, err_msg]
        else:
            print('cfg_SOFT = > ', rq)

        self.trm_data = Class_TERM_data(self.cfg_soft.path_file_DATA)
        self.trm_hist = Class_TERM_hist(self.cfg_soft.path_file_HIST)
        self.cfg_pack = Class_TABLE_cfg_pack(path_TERM_FUT_PACK)
        self.cfg_alarm = Class_TABLE_cfg_alarm(path_TERM_FUT_PACK)
        self.dt_fut   = Class_TABLE_data_fut(path_TERM_FUT_PACK)
        self.h_fut_today  = Class_TABLE_hist_fut_today(path_TERM_FUT_PACK)
        self.h_pack_today = Class_TABLE_hist_pack_today(path_TERM_FUT_PACK)
        self.h_fut_arc    = Class_TABLE_hist_fut(path_TERM_FUT_ARCHIV)
        self.h_pack_arc   = Class_TABLE_hist_pack(path_TERM_FUT_ARCHIV)
        self.e_mail   = Class_GMAIL('mobile.ovk', '20066002', 'mobile.ovk@gmail.com')

        self.arr_fut        = []    # массив котировок фьючей  60 s
        self.arr_fut_today  = []    # массив котировок фьючей  60 s
        self.arr_pack       = []    # массив котировок packets 60 s
        self.arr_pack_today = []    # массив котировок packets 60 s

        self.tm_wrt_new_data = 0    # minute's counter
#=======================================================================
def read_term(cntr):
    rq = cntr.trm_data.rd_term()
    if rq[0] != 0 :
        err_msg = 'rd_term => ' + '  '.join(str(e) for e in rq)
        if 'FILE is not modificated' in err_msg:
            pass
        else:
            if 'not MARKET time' in err_msg:
                pass
            else:
                cntr.log.wr_log_error(err_msg)
        return [1, err_msg]

    rq = cntr.trm_hist.rd_hist()
    if rq[0] != 0:
        _err_(cntr, 'rd_hist => ', rq, PopUp = False )
        return [1, 'rd_hist => _err_']

    return [0, 'ok']

#=======================================================================
def dbg_prn(cntr, b_clear  = True,
        b_trm_data_in_file = False,
        b_trm_hist_in_file = False,
        b_trm_data_fut = False,
        b_trm_account  = False,
        b_cfg_alarm = False,
        b_cfg_soft  = False,
        b_cfg_pack  = False,
        b_dt_fut    = False,
        b_fut_today = False,
        b_fut_arc   = False
        ):
    if b_clear:
        os.system('cls')  # on windows

    if b_trm_data_in_file:
        data_in_file = cntr.trm_data.data_in_file
        print('.....Class_TERM_data.....')
        #print('cntr.trm_data.data_in_file => cntr.trm_data.data_fut => list of Class_FUT() from trm')
        print('path_trm   => ', cntr.trm_data.path_trm)
        print('dt_file    => ', cntr.trm_data.dt_file)
        print('dt_data    => ', cntr.trm_data.dt_data)
        print('len(data_in_file) => ', len(data_in_file))
        for i, item in enumerate(data_in_file): print('[',i,'] => ', item)

    if b_trm_data_fut:
        print('.....Class_TERM_data.....')
        #print('cntr.trm_data.data_in_file => cntr.trm_data.data_fut => list of Class_FUT() from trm')
        print('path_trm   => ', cntr.trm_data.path_trm)
        data_fut = cntr.trm_data.data_fut
        print('len(data_fut)     => ', len(data_fut))
        if len(data_fut) > 0:
            for i, item in enumerate(data_fut):
                print('[',i,'] => ', item)
            print('. . . . .')
            print('data_fut[-1] =>')
            print('     sP_code     ', data_fut[-1].sP_code)
            print('     sRest       ', data_fut[-1].sRest)
            print('     sVar_margin ', data_fut[-1].sVar_margin)
            print('     sOpen_price ', data_fut[-1].sOpen_price)
            print('     sLast_price ', data_fut[-1].sLast_price)
            print('     sAsk        ', data_fut[-1].sAsk)
            print('     sBuy_qty    ', data_fut[-1].sBuy_qty)
            print('     sBid        ', data_fut[-1].sBid)
            print('     sSell_qty   ', data_fut[-1].sSell_qty)
            print('     sFut_go     ', data_fut[-1].sFut_go)
            print('     sOpen_pos   ', data_fut[-1].sOpen_pos)
            print('. . . . .')
            print('cntr.trm_data.data_in_file[-1]  =>  \n', cntr.trm_data.data_in_file[-1])

    if b_trm_account:
        print('.....Class_TERM_data.....')
        print('path_trm   => ', cntr.trm_data.path_trm)
        acnt = cntr.trm_data.account
        if acnt != '':
            print('. . . . .')
            print('.....Class_ACCOUNT.....')
            print('acc_date    => ', acnt.acc_date)
            print('acc_balance => ', acnt.acc_balance)
            print('acc_profit  => ', acnt.acc_profit)
            print('acc_go      => ', acnt.acc_go)
            print('acc_depo    => ', acnt.acc_depo)
        else:
            print('account     => _')

    if b_trm_hist_in_file:
        hist_in_file = cntr.trm_hist.hist_in_file
        print('.....Class_TERM_hist.....')
        print('path_hist    => ', cntr.trm_hist.path_hist)
        print('len(hist_in_file) => ', len(hist_in_file))
        if len(hist_in_file) > 0:
            #for i, item in enumerate(hist_in_file):
                #if i == 0 or i == 1        :  print('[',i,'] => ', item)
                #if i == len(hist_in_file)-2:  print('. . . . .')
                #if i == len(hist_in_file)-1:  print('[',i,'] => ', item)
            print('trm_hist.hist_in_file[0] => ',  hist_in_file[0])
            print('trm_hist.hist_in_file[1] => ',  hist_in_file[1].split('|')[0])
            print('trm_hist.hist_in_file[2] => ',  hist_in_file[2].split('|')[0])
            print('. . . . .')
            print('trm_hist.hist_in_file[-1] => ', hist_in_file[-1].split('|')[0])

    if b_cfg_soft:
        #hist_in_file = cntr.trm_hist.hist_in_file
        s = cntr.cfg_soft
        print('.....Class_TABLE_cfg_soft.....')
        print('path_term_fut_pack => ', s.path_term_fut_pack)
        print('titul              => ', s.titul)
        print('path_file_DATA     => ', s.path_file_DATA)
        print('path_file_HIST     => ', s.path_file_HIST)
        print('dt_start           => ', s.dt_start)

    if b_cfg_alarm:
        a = cntr.cfg_alarm
        print('.....Class_TABLE_cfg_alarm.....')
        print('path_term_fut_pack    => ', a.path_term_fut_pack)
        print('len(nm) => ', len(a.nm))
        if len(a.nm) > 0:
            for i, item in enumerate(a.nm):
                print(item, a.ena_cnt_ema[i])

    if b_cfg_pack:
        cfg_pack = cntr.cfg_pack
        print('.....Class_TABLE_cfg_pack.....')
        print('path_term_fut_pack    => ', cfg_pack.path_term_fut_pack)
        print('len(nm) => ', len(cfg_pack.nm))
        if len(cfg_pack.nm) > 0:
            for i, item in enumerate(cfg_pack.nm):
                print(item, cfg_pack.koef[i], cfg_pack.nul[i], cfg_pack.ema[i] )

    if b_dt_fut:
        print('.....Class_TABLE_data_fut.....')
        print('path_term_fut_pack    => ', cntr.dt_fut.path_term_fut_pack)
        dt_acc = cntr.dt_fut.account
        print('.....Class_ACCOUNT.....')
        print('acc_date    => ', dt_acc.acc_date)
        print('acc_balance => ', dt_acc.acc_balance)
        print('acc_profit  => ', dt_acc.acc_profit)
        print('acc_go      => ', dt_acc.acc_go)
        print('acc_depo    => ', dt_acc.acc_depo)
        print('. . . . .')
        dt_fut = cntr.dt_fut.data_fut
        print('len(data_fut)     => ', len(dt_fut))
        if len(dt_fut) > 0:
            for i, item in enumerate(dt_fut):
                print('[',i,'] => ', item)
            print('. . . . .')
            print('dt_fut[-1] =>')
            print('     sP_code     ', dt_fut[-1].sP_code)
            print('     sRest       ', dt_fut[-1].sRest)
            print('     sVar_margin ', dt_fut[-1].sVar_margin)
            print('     sOpen_price ', dt_fut[-1].sOpen_price)
            print('     sLast_price ', dt_fut[-1].sLast_price)
            print('     sAsk        ', dt_fut[-1].sAsk)
            print('     sBuy_qty    ', dt_fut[-1].sBuy_qty)
            print('     sBid        ', dt_fut[-1].sBid)
            print('     sSell_qty   ', dt_fut[-1].sSell_qty)
            print('     sFut_go     ', dt_fut[-1].sFut_go)
            print('     sOpen_pos   ', dt_fut[-1].sOpen_pos)
            #print('. . . . .')
            #print('cntr.trm_data.data_in_file[-1]  =>  \n', cntr.trm_data.data_in_file[-1])

    if b_fut_today:
        print('.....Class_TABLE_data_fut.....')
        print('path_term_fut_pack    => ', cntr.h_fut_today.path_term_fut_pack)
        hist = cntr.h_fut_today
        print('len(hist_fut_today)   => ', len(hist.hist_fut_today))
        if len(hist.hist_fut_today) > 4:
            print('hist_fut_today[0] => ',  hist.hist_fut_today[0])
            print('hist_fut_today[1] => ',  hist.hist_fut_today[1][1].split('|')[0])
            print('hist_fut_today[2] => ',  hist.hist_fut_today[2][1].split('|')[0])
            print('. . . . .')
            print('hist_fut_today[-1] => ', hist.hist_fut_today[-1][1].split('|')[0])
            print('___________________________')
        print('len(hist_1_fut_today) => ', len(hist.hist_1_fut_today))
        if len(hist.hist_1_fut_today) > 4:
            print('hist_1_fut_today[0] => ',  hist.hist_1_fut_today[0])
            print('hist_1_fut_today[1] => ',  hist.hist_1_fut_today[1][1].split('|')[0])
            print('hist_1_fut_today[2] => ',  hist.hist_1_fut_today[2][1].split('|')[0])
            print('. . . . .')
            print('hist_1_fut_today[-1] => ', hist.hist_1_fut_today[-1][1].split('|')[0])
            print('___________________________')
        print('len(arr_1_fut_today)  => ', len(hist.arr_1_fut_today))
        if len(hist.arr_1_fut_today) > 4:
            print('arr_1_fut_today[0] => ',  hist.arr_1_fut_today[0])
            print('arr_1_fut_today[1] => ',  hist.arr_1_fut_today[1][1].split('|')[0])
            print('arr_1_fut_today[2] => ',  hist.arr_1_fut_today[2][1].split('|')[0])
            print('. . . . .')
            print('arr_1_fut_today[-1] => ', hist.arr_1_fut_today[-1][1].split('|')[0])

    if b_fut_arc:
        print('.....Class_TABLE_hist_fut(archiv).....')
        print('path_term_fut_archiv    => ', cntr.h_fut_arc.path_term_fut_archiv)
        hist = cntr.h_fut_arc
        print('len(hist_fut_archiv)   => ', len(hist.hist_fut_archiv))
        if len(hist.hist_fut_archiv) > 4:
            print('hist_fut_archiv[0] => ',  hist.hist_fut_archiv[0])
            print('hist_fut_archiv[1] => ',  hist.hist_fut_archiv[1][1].split('|')[0])
            print('hist_fut_archiv[2] => ',  hist.hist_fut_archiv[2][1].split('|')[0])
            print('. . . . .')
            print('hist_fut_archiv[-1] => ', hist.hist_fut_archiv[-1][1].split('|')[0])
            print('___________________________')
        print('len(arr_fut_archiv)  => ', len(hist.arr_fut_archiv))
        if len(hist.arr_fut_archiv) > 4:
            print('arr_fut_today[0] => ',  hist.arr_fut_archiv[0])
            print('arr_fut_today[1] => ',  hist.arr_fut_archiv[1][1].split('|')[0])
            print('arr_fut_today[2] => ',  hist.arr_fut_archiv[2][1].split('|')[0])
            print('. . . . .')
            print('arr_fut_today[-1] => ', hist.arr_fut_archiv[-1][1].split('|')[0])


        print('')
#=======================================================================
def dbg_srv(cntr,
        b_trm_data   = False,
        b_trm_hist   = False,
        b_cfg_alarm  = False,
        b_cfg_pack   = False,
        b_cfg_soft   = False,
        b_data_fut   = False,
        b_hist_fut_t = False,
        b_hist_fut_a = False,
        b_send_mail  = False
        ):
    if b_trm_data:
        c = cntr.trm_data
        c.dt_file, c.dt_data, c.data_in_file = 0, 0, []
        rq = c.rd_term_service()
        if rq[0] != 0 : _err_(cntr, 'trm_data.rd_term_service ', rq)
        else:           dbg_prn(cntr,  b_trm_data_in_file = True)

    elif b_trm_hist:
        rq = cntr.trm_hist.rd_hist()
        if rq[0] != 0:  _err_(cntr, 'trm_hist.rd_term_service ', rq)
        else:           dbg_prn(cntr, b_clear  = False, b_trm_hist_in_file = True)

    elif b_cfg_alarm:
        rq = cntr.cfg_alarm.read_tbl()
        if rq[0] != 0 : _err_(cntr, 'cfg_alarm ', rq)
        else:           dbg_prn(cntr,  b_cfg_alarm = True)

    elif b_cfg_pack:
        rq = cntr.cfg_pack.read_tbl()
        if rq[0] != 0 : _err_(cntr, 'cfg_pack ', rq)
        else:           dbg_prn(cntr,  b_cfg_pack = True)

    elif b_cfg_soft:
        rq = cntr.cfg_soft.read_tbl()
        if rq[0] != 0 : _err_(cntr, 'cfg_soft ', rq)
        else:           dbg_prn(cntr,  b_cfg_soft = True)

    elif b_data_fut:
        rq = cntr.dt_fut.read_tbl()
        if rq[0] != 0 : _err_(cntr, 'dt_fut ', rq)
        else:           dbg_prn(cntr,  b_dt_fut = True)

    elif b_hist_fut_t:
        rq = cntr.h_fut_today.read_tbl()
        if rq[0] != 0 : _err_(cntr, 'h_fut_today ', rq)
        else:           dbg_prn(cntr,  b_fut_today = True)

    elif b_hist_fut_a:
        rq = cntr.h_fut_arc.read_tbl()
        if rq[0] != 0 : _err_(cntr, 'h_fut_arc ', rq)
        else:           dbg_prn(cntr,  b_fut_arc = True)

    elif b_send_mail:
        print( 'Start TEST e-mail (it is about 20 s) => ' + datetime.today().strftime('%H:%M:%S') )
        rq = cntr.e_mail.send_email('test  subj','test  body')
        if rq[0] != 0 :
            _err_(cntr, 'send_email ', rq)
        else:
            print('TEST sent e-mail OK . . . . .')
        print( 'Finish TEST e-mail => ' +  datetime.today().strftime('%H:%M:%S') )

    else:
        print('TEST NOTHING')

#=======================================================================
def calc_hist_PACK(cntr, i_pack):
    cntr.arr_pack[i_pack] = []
    arr_HIST = cntr.h_fut_arc.arr_fut_archiv    # archiv of FUT 60 sec
    #const_UP, const_DW = +50, -50
    #print('ema =  ', cntr.cfg_pack.ema[i_pack])
    k_EMA     = int(cntr.cfg_pack.ema[i_pack][0])
    k_EMA_rnd = int(cntr.cfg_pack.ema[i_pack][1])
    koef_EMA = round(2/(1+k_EMA),5)
    ind = []
    kf  = []
    #print('koef =  ', cntr.cfg_pack.koef[i_pack])
    for elem in cntr.cfg_pack.koef[i_pack]:
        ind.append(int(elem.split(':')[0]))
        kf.append(int(elem.split(':')[1]))
    #koef_AMA = cntr.koef_pack[i_pack][3]
    #fSC       = float(koef_AMA.split(':')[0])
    #sSC       = float(koef_AMA.split(':')[1])
    #nn        = int(koef_AMA.split(':')[2])
    #k_ama_rnd = int(koef_AMA.split(':')[3])

    #print('arr_HIST[-1] => ', arr_HIST[-1])
    for idx, item in enumerate(arr_HIST):
        ask_p, bid_p = 0, 0
        buf_c_pack = Class_PACK()
        buf_c_pack.ind = item[0]
        #item = (item_HIST[1].replace(',', '.')).split('|')
        #print(item)
        buf_c_pack.dt, buf_c_pack.tm  = item[1].split(' ')
        for jdx, jtem in enumerate(kf):
            ask_j = float(item[2 + 2*ind[jdx]])
            bid_j = float(item[2 + 2*ind[jdx] + 1])
            if jtem > 0 :
                ask_p = ask_p + jtem * ask_j
                bid_p = bid_p + jtem * bid_j
            if jtem < 0 :
                ask_p = ask_p + jtem * bid_j
                bid_p = bid_p + jtem * ask_j

        ask_bid_AVR = 0
        if idx == 0:
            null_prc = int((ask_p + bid_p)/2)
            cntr.cfg_pack.nul[i_pack] = null_prc
            buf_c_pack.pAsk, buf_c_pack.pBid = 0, 0
            buf_c_pack.EMAf, buf_c_pack.EMAf_rnd = 0, 0
            buf_c_pack.cnt_EMAf_rnd = 0
            #buf_c_pack.AMA, buf_c_pack.AMA_rnd = 0, 0
            #buf_c_pack.cnt_AMA_rnd = 0

        else:
            ask_p = int(ask_p - null_prc)
            bid_p = int(bid_p - null_prc)
            buf_c_pack.pAsk = ask_p
            buf_c_pack.pBid = bid_p
            ask_bid_AVR = int((ask_p + bid_p)/2)

            prev_EMAf = cntr.arr_pack[i_pack][idx-1].EMAf
            buf_c_pack.EMAf = round(prev_EMAf + (ask_bid_AVR - prev_EMAf) * koef_EMA, 1)
            buf_c_pack.EMAf_rnd = k_EMA_rnd * math.ceil(buf_c_pack.EMAf / k_EMA_rnd )

            prev_EMAf_rnd = cntr.arr_pack[i_pack][idx-1].EMAf_rnd
            i_cnt = cntr.arr_pack[i_pack][idx-1].cnt_EMAf_rnd
            if prev_EMAf_rnd > buf_c_pack.EMAf_rnd:
                buf_c_pack.cnt_EMAf_rnd = 0 if i_cnt > 0 else i_cnt-1
            elif prev_EMAf_rnd < buf_c_pack.EMAf_rnd:
                buf_c_pack.cnt_EMAf_rnd = 0 if i_cnt < 0 else i_cnt+1
            else:
                buf_c_pack.cnt_EMAf_rnd = i_cnt

        cntr.arr_pack[i_pack].append(buf_c_pack)
#=======================================================================
def calc_hist_PACK_today(cntr, i_pack):
    cntr.arr_pack_today[i_pack] = []
    arr_HIST = cntr.h_fut_today.arr_1_fut_today    # today of FUT 60 sec
    k_EMA     = int(cntr.cfg_pack.ema[i_pack][0])
    k_EMA_rnd = int(cntr.cfg_pack.ema[i_pack][1])
    koef_EMA = round(2/(1+k_EMA),5)
    ind = []
    kf  = []
    #print('koef =  ', cntr.cfg_pack.koef[i_pack])
    for elem in cntr.cfg_pack.koef[i_pack]:
        ind.append(int(elem.split(':')[0]))
        kf.append(int(elem.split(':')[1]))

    #print('arr_HIST[-1] => ', arr_HIST[-1])
    for idx, item in enumerate(arr_HIST):
        ask_p, bid_p = 0, 0
        buf_c_pack = Class_PACK()
        buf_c_pack.ind = item[0]
        #item = (item_HIST[1].replace(',', '.')).split('|')
        #print(item)
        buf_c_pack.dt, buf_c_pack.tm  = item[1].split(' ')
        for jdx, jtem in enumerate(kf):
            ask_j = float(item[2 + 2*ind[jdx]])
            bid_j = float(item[2 + 2*ind[jdx] + 1])
            if jtem > 0 :
                ask_p = ask_p + jtem * ask_j
                bid_p = bid_p + jtem * bid_j
            if jtem < 0 :
                ask_p = ask_p + jtem * bid_j
                bid_p = bid_p + jtem * ask_j

        ask_bid_AVR = 0
        if idx == 0:
            null_prc = cntr.cfg_pack.nul[i_pack]
            ask_p = int(ask_p - null_prc)
            bid_p = int(bid_p - null_prc)
            buf_c_pack.pAsk = ask_p
            buf_c_pack.pBid = bid_p
            ask_bid_AVR = int((ask_p + bid_p)/2)

            prev_EMAf = cntr.arr_pack[i_pack][idx-1].EMAf
            buf_c_pack.EMAf = round(prev_EMAf + (ask_bid_AVR - prev_EMAf) * koef_EMA, 1)
            buf_c_pack.EMAf_rnd = k_EMA_rnd * math.ceil(buf_c_pack.EMAf / k_EMA_rnd )

            prev_EMAf_rnd = cntr.arr_pack[i_pack][idx-1].EMAf_rnd
            i_cnt = cntr.arr_pack[i_pack][idx-1].cnt_EMAf_rnd
            if prev_EMAf_rnd > buf_c_pack.EMAf_rnd:
                buf_c_pack.cnt_EMAf_rnd = 0 if i_cnt > 0 else i_cnt-1
            elif prev_EMAf_rnd < buf_c_pack.EMAf_rnd:
                buf_c_pack.cnt_EMAf_rnd = 0 if i_cnt < 0 else i_cnt+1
            else:
                buf_c_pack.cnt_EMAf_rnd = i_cnt

        else:
            ask_p = int(ask_p - null_prc)
            bid_p = int(bid_p - null_prc)
            buf_c_pack.pAsk = ask_p
            buf_c_pack.pBid = bid_p
            ask_bid_AVR = int((ask_p + bid_p)/2)

            prev_EMAf = cntr.arr_pack_today[i_pack][idx-1].EMAf
            buf_c_pack.EMAf = round(prev_EMAf + (ask_bid_AVR - prev_EMAf) * koef_EMA, 1)
            buf_c_pack.EMAf_rnd = k_EMA_rnd * math.ceil(buf_c_pack.EMAf / k_EMA_rnd )

            prev_EMAf_rnd = cntr.arr_pack_today[i_pack][idx-1].EMAf_rnd
            i_cnt = cntr.arr_pack_today[i_pack][idx-1].cnt_EMAf_rnd
            if prev_EMAf_rnd > buf_c_pack.EMAf_rnd:
                buf_c_pack.cnt_EMAf_rnd = 0 if i_cnt > 0 else i_cnt-1
            elif prev_EMAf_rnd < buf_c_pack.EMAf_rnd:
                buf_c_pack.cnt_EMAf_rnd = 0 if i_cnt < 0 else i_cnt+1
            else:
                buf_c_pack.cnt_EMAf_rnd = i_cnt

        cntr.arr_pack_today[i_pack].append(buf_c_pack)
#=======================================================================
def debug_calc_PACK_arc(cntr):   # 'Service\Debug\calc PACK arc'
    print('calc PACK arc')
    s_term = []
    s_term.append('___ calc PACK arc ___')

    rq = cntr.h_fut_arc.read_tbl()
    if rq[0] != 0 :
        _err_(cntr, 'debug_calc_PACK_arc ', rq)
        s_term.append('debug_calc_PACK_arc ')
    else:
        arr   = cntr.h_fut_arc.hist_fut_archiv

    for i_pack, item in enumerate(cntr.cfg_pack.nm):
        calc_hist_PACK(cntr, i_pack)
        sg.OneLineProgressMeter('calc_hist_PACK',
                                i_pack+1,
                                len(cntr.cfg_pack.nm),
                                'key', orientation='h')

    print('NOTE - must update null_price every time after calc_hist_PACK !!!')
    cntr.cfg_pack.rewrite_tbl()
    print('writing hist_PACK . . . . . .')
    wr_hist_PACK(cntr)
    print('ok. . . . . . . . . . . . . .')
#=======================================================================
def debug_calc_PACK_today(cntr): # 'Service\Debug\calc PACK today'
    print('calc PACK today')
    s_term = []
    s_term.append('___ calc PACK today ___')

    rq = cntr.h_fut_today.read_tbl()
    if rq[0] != 0 :
        _err_(cntr, 'debug_calc_PACK_today ', rq)
        s_term.append('debug_calc_PACK_today ')
    else:
        arr   = cntr.h_fut_today.hist_fut_today
        arr1   = cntr.h_fut_today.hist_1_fut_today
        s_term.append('\n hist_fut_today   => ' + str(len(arr))  + ' strings\n ')
        s_term.append('\n hist_1_fut_today => ' + str(len(arr1)) + ' strings\n ')

    if len(arr) > 0:
        ind_pack = 'debug_calc_PACK_today => '
        for i_pack, item in enumerate(cntr.cfg_pack.nm):
            calc_hist_PACK_today(cntr, i_pack)
            #print(i_pack, cntr.arr_pack_today[i_pack][-1])
            ind_pack += str(i_pack) + ' '
            print(ind_pack, end='\r')
        wr_hist_PACK_today(cntr)

    s_term.append(' ')
    sg.Popup( 'hist_fut_today', '\n'.join(s_term))
#=======================================================================
def TODAY_copy_ARCHIV(cntr):
    os.system('cls')  # on windows
    print('Copy fut TODAY in ARCHIV .  .  .  .  .')
    hist = cntr.h_fut_today
    print('len(hist_1_fut_today) => ', len(hist.hist_1_fut_today))
    if len(hist.hist_1_fut_today) > 4:
        print('hist_1_fut_today[0] => ',  hist.hist_1_fut_today[0])
        print('hist_1_fut_today[1] => ',  hist.hist_1_fut_today[1][1].split('|')[0])
        print('hist_1_fut_today[2] => ',  hist.hist_1_fut_today[2][1].split('|')[0])
        print('. . . . .')
        print('hist_1_fut_today[-2] => ', hist.hist_1_fut_today[-2][1].split('|')[0])
        print('hist_1_fut_today[-1] => ', hist.hist_1_fut_today[-1][1].split('|')[0])
    print('. . . . .')
    print('Status BEFORE')
    hist = cntr.h_fut_arc
    print('len(hist_fut_archiv)   => ', len(hist.hist_fut_archiv))
    if len(hist.hist_fut_archiv) > 4:
        print('hist_fut_archiv[0] => ',  hist.hist_fut_archiv[0])
        print('hist_fut_archiv[1] => ',  hist.hist_fut_archiv[1][1].split('|')[0])
        print('hist_fut_archiv[2] => ',  hist.hist_fut_archiv[2][1].split('|')[0])
        print('. . . . .')
        print('hist_fut_archiv[-2] => ', hist.hist_fut_archiv[-2][1].split('|')[0])
        print('hist_fut_archiv[-1] => ', hist.hist_fut_archiv[-1][1].split('|')[0])
    print('. . . . .')
    buf_list = []
    if len(cntr.h_fut_today.hist_1_fut_today) < 520:
        rq = cntr.h_fut_arc.obj_table.write_table_db('hist_FUT', cntr.h_fut_today.hist_1_fut_today)
        if rq[0] != 0: _err_(cntr, 'TODAY_copy_ARCHIV ', rq)
    else:
        rq = cntr.h_fut_arc.obj_table.write_table_db('hist_FUT', cntr.h_fut_today.hist_1_fut_today[:520])
        if rq[0] != 0: _err_(cntr, 'TODAY_copy_ARCHIV ', rq)
    print('. . . . .')
    print('Press Test & Print for STATUS')
#=======================================================================
def convert_tbl_TODAY(cntr):
    def wr_file(path_file, hist_out, mes, cntr):
        if os.path.exists(path_file):
            os.remove(path_file)
        f = open(path_file,'w')
        for item in hist_out:
            f.writelines(item + '\n')
        f.close()
        cntr.log.wr_log_info(mes + path_file)
        print(mes + path_file)
    #
    #service_hist_FUT_TODAY(cntr)    #read & print
    dbg_srv(cntr,  b_hist_fut_t = False)
    #
    arr_hist = cntr.h_fut_today.hist_fut_today
    term_dt = arr_hist[-1][1].split('|')[0]
    dtt = datetime.strptime(str(term_dt), "%d.%m.%Y %H:%M:%S")
    #
    str_month = str(dtt.month) if dtt.month > 9 else '0' + str(dtt.month)
    str_day   = str(dtt.day)   if dtt.day   > 9 else '0' + str(dtt.day)
    str_dt    = str(dtt.year) + '-' + str_month + '-' + str_day
    # write in file HISTORY  10 sec ------------------------------------
    hist_out = []           # convert TUPLE in LIST & delete last '|'
    for item in arr_hist: hist_out.append(''.join(list(item[1])[0:-1]))
    path_file = str_dt + '_hist_' + cntr.cfg_soft.titul + '.txt'
    wr_file(path_file, hist_out, 'Hist export for ', cntr)
    #
    arr_hist = cntr.h_fut_today.hist_1_fut_today
    term_dt = arr_hist[-1][1].split('|')[0]
    dtt = datetime.strptime(str(term_dt), "%d.%m.%Y %H:%M:%S")
    # write in file HISTORY  60 sec ------------------------------------
    hist_out = []           # convert TUPLE in LIST & delete last '|'
    for item in arr_hist:
        dt_buf = datetime.strptime(str(item[1].split('|')[0]), "%d.%m.%Y %H:%M:%S")
        if dt_buf.hour < 19:
            hist_out.append(str(int(item[0])) + ';' + ''.join(list(item[1])[0:-1]))
    path_file = cntr.cfg_soft.titul + '_' + str_dt + '_hist_FUT' + '.csv'
    wr_file(path_file, hist_out, 'Archiv for ', cntr)
    #
    print('.  .  .  .  .')
    print('start  => ', hist_out[0].split(';')[1].split('|')[0])
    print('finish => ', hist_out[-1].split(';')[1].split('|')[0])
    print('lench  => ', len(hist_out))
    print('.  .  .  .  .')
#=======================================================================
def prepair_hist_PACK(cntr, b_today = False):
    name_list =[]
    if b_today :
        arr_hist_pack = cntr.arr_pack_today
    else:
        arr_hist_pack = cntr.arr_pack

    if len(arr_hist_pack) > 0:
        for i_hist, item_hist in enumerate(arr_hist_pack[0]):
            buf_dt = item_hist.dt + ' ' + item_hist.tm + ' '
            buf_s = ''
            for i_mdl, item_mdl in enumerate(arr_hist_pack):
                buf = arr_hist_pack[i_mdl][i_hist]
                buf_s += str(buf.pAsk) + ' ' + str(buf.pBid)     + ' '
                buf_s += str(buf.EMAf) + ' ' + str(buf.EMAf_rnd) + ' ' + str(buf.cnt_EMAf_rnd) + '|'
                #buf_s += str(buf.AMA)  + ' ' + str(buf.AMA_rnd)  + ' ' + str(buf.cnt_AMA_rnd) + '|'
            name_list.append((item_hist.ind, buf_dt + buf_s.replace('.', ',')))

    return name_list
#=======================================================================
def wr_hist_PACK(cntr):
    name_list = []
    name_list = prepair_hist_PACK(cntr)
    rq = cntr.h_pack_arc.rewrite_tbl(name_list)
    if rq[0] != 0:
        _err_(cntr, 'hist_PACK ', rq, PopUp = False)
        return [1, 'wr_hist_PACK']

    return [0, 'OK']
#=======================================================================
def wr_hist_PACK_today(cntr):
    name_list = []
    name_list = prepair_hist_PACK(cntr, b_today = True)
    rq = cntr.h_pack_today.rewrite_tbl(name_list)
    if rq[0] != 0:
        _err_(cntr, 'hist_PACK_today ', rq, PopUp = False)
        return [1, 'wr_hist_PACK_today']

    return [0, 'OK']
#=======================================================================
def _err_(cntr, msg, rq, Log = True, Prn = True, PopUp = True):
    err_msg  = msg
    err_msg += '  '.join(str(e) for e in rq)
    if Log  :  cntr.log.wr_log_error(err_msg)
    if PopUp:  sg.PopupError('Error !', err_msg)
    if Prn  :
        os.system('cls')  # on windows
        print(err_msg)
#=======================================================================
def event_menu(event, cntr):
    #-------------------------------------------------------------------
    if event == 'srv data TERM'      : dbg_srv(cntr, b_trm_data   = True)
    #-------------------------------------------------------------------
    if event == 'srv hist TERM'      : dbg_srv(cntr, b_trm_hist   = True)
    #-------------------------------------------------------------------
    if event == 'srv config ALARM'   : dbg_srv(cntr, b_cfg_alarm  = True)
    #-------------------------------------------------------------------
    if event == 'srv config PACK'    : dbg_srv(cntr, b_cfg_pack   = True)
    #-------------------------------------------------------------------
    if event == 'srv config SOFT'    : dbg_srv(cntr, b_cfg_soft   = True)
    #-------------------------------------------------------------------
    if event == 'srv data FUT'       : dbg_srv(cntr, b_data_fut   = True)
    #-------------------------------------------------------------------
    if event == 'srv hist FUT today' : dbg_srv(cntr, b_hist_fut_t = True)
    #-------------------------------------------------------------------
    if event == 'srv hist FUT arch'  : dbg_srv(cntr, b_hist_fut_a = True)
    #-------------------------------------------------------------------
    if event == 'srv send E-MAIL'    : dbg_srv(cntr, b_send_mail  = True)
    #-------------------------------------------------------------------
    if event == 'prn TERM data_in_file'  : dbg_prn(cntr, b_trm_data_in_file = True)
    #---------------------------------------------------------------
    if event == 'prn TERM data_fut'      : dbg_prn(cntr, b_trm_data_fut     = True)
    #---------------------------------------------------------------
    if event == 'prn TERM account'       : dbg_prn(cntr, b_trm_account      = True)
    #---------------------------------------------------------------
    if event == 'prn TERM hist_in_file'  : dbg_prn(cntr, b_trm_hist_in_file = True)
    #---------------------------------------------------------------
    if event == 'prn FUT cfg_ALARM'      : dbg_prn(cntr, b_cfg_alarm        = True)
    #---------------------------------------------------------------
    if event == 'prn FUT cfg_SOFT'       : dbg_prn(cntr, b_cfg_soft         = True)
    #---------------------------------------------------------------
    if event == 'prn FUT cfg_PACK'       : dbg_prn(cntr, b_cfg_pack         = True)
    #---------------------------------------------------------------
    if event == 'prn FUT data_FUT'       : dbg_prn(cntr, b_dt_fut           = True)
    #---------------------------------------------------------------
    if event == 'prn FUT hist_FUT_today' : dbg_prn(cntr, b_fut_today        = True)
    #---------------------------------------------------------------
    if event == 'prn FUT hist_FUT_arch'  : dbg_prn(cntr, b_fut_arc          = True)
    #---------------------------------------------------------------
    if event == 'calc PACK arc'   : debug_calc_PACK_arc(cntr)
    #---------------------------------------------------------------
    if event == 'calc PACK today' : debug_calc_PACK_today(cntr)
    #---------------------------------------------------------------
    if event == 'Convert tbl TODAY' : convert_tbl_TODAY(cntr)
    #---------------------------------------------------------------
    if event == 'TODAY to ARCHIV'   : TODAY_copy_ARCHIV(cntr)
#=======================================================================
def main():
    # init
    cntr = Class_CONTROLER()
    while True:
        #---------------------------------------------------------------
        rq = cntr.trm_data.rd_term()
        if rq[0] != 0:  _err_(cntr, 'INIT data_in_file ', rq)
        else:           print('trm_data = > ', rq)
        #---------------------------------------------------------------
        rq = cntr.trm_hist.rd_hist()
        if rq[0] != 0:  _err_(cntr, 'INIT hist_in_file ', rq)
        else:           print('trm_hist = > ', rq)
        #---------------------------------------------------------------
        rq = cntr.dt_fut.read_tbl()
        if rq[0] != 0:  _err_(cntr, 'INIT data_FUT ', rq)
        else:           print('data_fut = > ', rq)
        #---------------------------------------------------------------
        rq = cntr.cfg_alarm.read_tbl()
        if rq[0] != 0 : _err_(cntr, 'INIT cfg_ALARM ', rq)
        else:           print('cfg_alarm = > ', rq)
        #---------------------------------------------------------------
        rq = cntr.cfg_pack.read_tbl()
        if rq[0] != 0 : _err_(cntr, 'INIT cfg_PACK ', rq)
        else:
            print('cfg_pack = > ', rq)
            if len(cntr.cfg_pack.nm) == 0:
                _err_(cntr, 'cfg_pack.nm = 0  ', [' ', 'It can not be EMPTY !'] )
                break
            for item in cntr.cfg_pack.nm:
                cntr.arr_pack.append([])
                cntr.arr_pack_today.append([])
        #---------------------------------------------------------------
        rq = cntr.h_fut_arc.read_tbl()
        if rq[0] != 0 : _err_(cntr, 'INIT hist_fut_archiv ', rq)
        else:
            print('hist_FUT archiv = > ', rq)
        #---------------------------------------------------------------
        print('calculating hist_PACK . . . .')
        for i_pack, item in enumerate(cntr.cfg_pack.nm):
            calc_hist_PACK(cntr, i_pack)
            sg.OneLineProgressMeter('calc_hist_PACK',
                                    i_pack+1,
                                    len(cntr.cfg_pack.nm),
                                    'key', orientation='h')
        cntr.cfg_pack.rewrite_tbl()
        print('writing hist_PACK . . . . . .')
        wr_hist_PACK(cntr)
        #---------------------------------------------------------------
        # init MENU
        menu_def = [
            ['Mode',
                ['auto', 'manual', ],
                ],
            ['Service',
                ['srv send E-MAIL',
                 'srv data TERM',    'srv hist TERM',
                 'srv config ALARM', 'srv config PACK',    'srv config SOFT',
                 'srv data FUT',     'srv hist FUT today', 'srv hist FUT arch' ],
                ],
            ['Print',
                ['prn TERM data_in_file', 'prn TERM hist_in_file',
                 'prn TERM data_fut',     'prn TERM account',
                 'prn FUT cfg_ALARM',     'prn FUT cfg_SOFT',       'prn FUT cfg_PACK',
                 'prn FUT data_FUT',      'prn FUT hist_FUT_today', 'prn FUT hist_FUT_arch'],
                ],
            ['Debug',
                ['calc PACK today', 'calc PACK arc'],
                ],
            ['Hist FUT',
                ['Convert tbl TODAY', 'TODAY to ARCHIV', 'VACUUM tbl TODAY'],
                ],
            ['Help', 'About...'],
            ['Exit', 'Exit']
            ]

        def_txt = []
        frm = '{: <15}  => {: ^15}\n'
        def_txt.append(frm.format('TODAY' , '\\DB\\term_fut_pack.sqlite'))
        def_txt.append(frm.format('ARCHV' , '\\DB\\term_fut_archiv.sqlite'))

        # Display data
        layout = [
                    [sg.Menu(menu_def, tearoff=False, key='menu_def')],
                    [sg.Multiline( default_text=''.join(def_txt),
                        size=(50, 5), key='txt_data', autoscroll=False, focus=False),],
                    [sg.T('',size=(60,2), font='Helvetica 8', key='txt_status'), sg.Quit(auto_size_button=True)],
                 ]
        sg.SetOptions(element_padding=(0,0))
        window = sg.Window(cntr.cfg_soft.titul, grab_anywhere=True).Layout(layout).Finalize()
        break

    mode = 'manual'
    tm_out = 360000
    frm = '%d.%m.%Y %H:%M:%S'
    stts  = time.strftime(frm, time.localtime()) + '\n' + 'event = manual'
    window.FindElement('txt_status').Update(stts)

    # main cycle   -----------------------------------------------------
    # 1. read TERM files DATA & HIST today
    # 2. if have not new data :  BREAK
    # 3. else :
    #       calc new price & indicators
    #       write new data in DB file
    #       check ALARMs
    #       send in WWW/FTP/SMTP

    while True:
        stroki = []
        event, values = window.Read(timeout=tm_out )
        #---------------------------------------------------------------
        if event == 'auto'   :
            tm_out = 1550
            mode = 'auto'
        #---------------------------------------------------------------
        if event == 'manual' :
            tm_out = 240000
            mode = 'manual'
        #---------------------------------------------------------------
        event_menu(event, cntr)
        #---------------------------------------------------------------
        if event is None or event == 'Quit' or event == 'Exit': break
        #---------------------------------------------------------------
        if event == '__TIMEOUT__':
            rq = read_term(cntr)
            if rq[0] != 0:
                tm_out = 1550
                stroki.append(rq[1])
            else:
                tm_out = 7550
                stroki.append('Time DATA:  ' + cntr.trm_data.data_in_file[0].split('|')[0])
                stroki.append('Have got new data/hist')
                tmr = cntr.trm_data.account.acc_date
                dt_minute = datetime.strptime(str(tmr.split('|')[0]), frm).minute
                if cntr.tm_wrt_new_data == dt_minute:
                    req = cntr.dt_fut.rewrite_tbl(cntr.trm_data.data_in_file)
                    if req[0] != 0: _err_(cntr, 'dt_fut.rewrite_tbl => ', req, PopUp = False)
                    else:
                        rq = cntr.dt_fut.read_data_in_file( cntr.trm_data.data_in_file )
                        if rq[0] != 0 : _err_(cntr, 'dt_fut.read_data_in_file => ', rq, PopUp = False)
                        else:           print(60*' ', end='\r')
                else:
                    cntr.tm_wrt_new_data = dt_minute
                    req = cntr.h_fut_today.rewrite_tbl(cntr.trm_hist.hist_in_file)
                    if req[0] != 0: _err_(cntr, 'h_fut_today.rewrite_tbl => ', req, PopUp = False)
                    else:
                        ind_pack = 'calc_hist_PACK_today => '
                        for i_pack, item in enumerate(cntr.cfg_pack.nm):
                            calc_hist_PACK_today(cntr, i_pack)
                            ind_pack += str(i_pack) + ' '
                            print(ind_pack, end='\r')
                        wr_hist_PACK_today(cntr)
        #---------------------------------------------------------------
        window.FindElement('txt_data').Update('\n'.join(stroki))
        stts  = time.strftime(frm, time.localtime()) + '\n'
        stts += 'event = ' + event
        window.FindElement('txt_status').Update(stts)

    return

#=======================================================================
if __name__ == '__main__':
    import sys
    sys.exit(main())
