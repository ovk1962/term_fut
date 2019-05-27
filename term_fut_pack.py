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
    def __init__(self, path_trm):
        self.path_trm  = path_trm
        #
        self.dt_file = 0        # curv stamptime data file path_trm
        self.dt_data = 0        # curv stamptime DATA/TIME from TERM
        self.data_in_file = []  # list of strings from path_trm
        self.data_fut = []      # list of Class_FUT() from trm
        self.account  = ''      # obj Class_ACCOUNT() from trm
        self.delay_tm = 9       # min period to get data for DB (10 sec)
        #
        self.sec_10_00 = 36000      # seconds from 00:00 to 10:00
        self.sec_14_00 = 50400      # seconds from 00:00 to 14:00
        self.sec_14_05 = 50700      # seconds from 00:00 to 14:05
        self.sec_18_45 = 67500      # seconds from 00:00 to 18:45
        self.sec_19_05 = 68700      # seconds from 00:00 to 19:05
        self.sec_23_45 = 85500      # seconds from 00:00 to 23:45
    #-------------------------------------------------------------------
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
            return [3, 'FILE is not modificated']
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
                err_msg = 'DATA is not updated ' + dt_str
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
    #-------------------------------------------------------------------
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
    def __init__(self, path_hist):
        self.path_hist  = path_hist
        self.hist_in_file = []  # list of strings from path_hist
    #-------------------------------------------------------------------
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
        self.hist_in_file = []
        self.hist_in_file = buf_str[:]
        return [0, 'ok']
#=======================================================================
class Class_TABLE_cfg_pack():
    def __init__(self, path_term_fut_pack):
        self.obj_table = Class_SQLite(path_term_fut_pack)
        self.nm   = []  # list NM   of packets
        self.koef = []  # list KOEF of packets
        self.ema  = []  # list EMA  of packets
    #-------------------------------------------------------------------
    def read_tbl(self):
        rq  = self.obj_table.get_table_db_with('cfg_PACK')
        if rq[0] != 0:
            err_msg = 'Can not read TBL cfg_PACK !'
            print(err_msg)
            sg.PopupError(err_msg)
            return [1, rq[1]]

        for item in rq[1]:
            self.nm.append(item[0])             # just ex ['pckt0']
            self.koef.append(item[1].split(','))# just ex ['0:3:SR','9:-20:MX']
            self.ema.append(item[2].split(':')) # just ex ['1111:15']
        # for test
        #for (item, jtem, ztem) in (self.nm, self.koef, self.ema):
        #    print(item, jtem, ztem)
        return [0, 'ok']
#=======================================================================
class Class_TABLE_cfg_soft():
    def __init__(self, path_term_fut_pack):
        self.obj_table = Class_SQLite(path_term_fut_pack)
        self.titul = self.dt_start = ''
        self.dt_start_sec = 0
        self.path_file_DATA = self.path_file_HIST = ''
        self.path_file_LOG = ''
    #-------------------------------------------------------------------
    def read_tbl(self):
        rq  = self.obj_table.get_table_db_with('cfg_SOFT')
        if rq[0] != 0:
            err_msg = 'Can not read TBL cfg_SOFT !'
            print(err_msg)
            sg.PopupError(err_msg)
            return [1, rq[1]]

        for item in rq[1]:
            if item[0] == 'titul'         : self.titul           = item[1]
            if item[0] == 'path_file_DATA': self.path_file_DATA  = item[1]
            if item[0] == 'path_file_HIST': self.path_file_HIST  = item[1]
            if item[0] == 'dt_start'      : self.dt_start        = item[1]
            if item[0] == 'path_file_LOG' :
                cur_dir = os.path.abspath(os.curdir)
                self.log_path = cur_dir + item[1]

        frm = '%Y-%m-%d %H:%M:%S'
        self.dt_start_sec = \
            int(datetime.strptime(self.dt_start, frm).replace(tzinfo=timezone.utc).timestamp())
        print(self.dt_start, self.dt_start_sec)

        return [0, 'ok']
#=======================================================================
class Class_TABLE_data_fut():
    def __init__(self, path_term_fut_pack):
        self.obj_table = Class_SQLite(path_term_fut_pack)
        self.data_fut = []                  # list of Class_FUT()
        self.account  = Class_ACCOUNT()     # obj Class_ACCOUNT()
    #-------------------------------------------------------------------
    def rewrite_tbl(self, buf_tbl):
        # rewrite table DATA
        duf_list = []
        for j, jtem in enumerate(buf_tbl):
            buf = (jtem,)
            duf_list.append(buf)
        rq = self.obj_table.rewrite_table('data_FUT', duf_list, val = '(?)')
        if rq[0] != 0:
            err_msg = 'rewrite_tbl data_FUT ' + rq[1]
            return [1, err_msg]
        return [0, 'ok']
    #-------------------------------------------------------------------
    def read_tbl(self):
        rq  = self.obj_table.get_table_db_with('data_FUT')
        if rq[0] != 0:
            err_msg = 'Can not read TBL data_FUT ! ' + rq[1]
            print(err_msg)
            #sg.PopupError(err_msg)
            return [1, err_msg]

        try:
            self.data_fut = []

            for i, item in enumerate(list(rq[1])):
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
                    self.data_fut.append(b_fut)
        except Exception as ex:
            err_msg = 'parse_data_in_file / ' + str(ex)
            return [1, err_msg]

        return [0, 'ok']
#=======================================================================
class Class_TABLE_hist_fut_today():
    def __init__(self, path_term_fut_pack):
        self.obj_table = Class_SQLite(path_term_fut_pack)
        self.hist_fut_today = []      # list of [[ind_sec string] ... ]

        self.sec_10_00 = 36000      # seconds from 00:00 to 10:00
        self.sec_14_00 = 50400      # seconds from 00:00 to 14:00
        self.sec_14_05 = 50700      # seconds from 00:00 to 14:05
        self.sec_18_45 = 67500      # seconds from 00:00 to 18:45
        self.sec_19_05 = 68700      # seconds from 00:00 to 19:05
        self.sec_23_45 = 85500      # seconds from 00:00 to 23:45
    #-------------------------------------------------------------------
    def read_tbl(self):
        rq  = self.obj_table.get_table_db_with('hist_FUT_today')
        if rq[0] != 0:
            err_msg = 'Can not read TBL hist_FUT_today ! ' + rq[1]
            print(err_msg)
            return [1, err_msg]

        self.hist_fut_today = []
        self.hist_fut_today = rq[1][:]
        print('read hist_fut_today => ', len(self.hist_fut_today), ' strings')
        return [0, 'ok']
    #-------------------------------------------------------------------
    def rewrite_tbl(self, term_hist):
        self.hist_fut_today = []
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
                            if buf_60_sec != dtt.minute :
                                buf_60_sec = dtt.minute
                                self.hist_fut_today.append([ind_sec, item])
            else:
                return [1, 'hist_in_file is empty! ']
        except Exception as ex:
            err_msg = 'rewrite_tbl => ' + str(ex)
            return [1, err_msg]

        rq = self.obj_table.rewrite_table('hist_FUT_today', self.hist_fut_today, val = '(?,?)')
        if rq[0] != 0:
            err_msg = 'rewrite_table(hist_FUT_today) ' + rq[1]
            return [1, err_msg]

        return [0, 'ok']
#=======================================================================
class Class_TABLE_hist_pack_today():
    def __init__(self, path_term_fut_pack):
        self.path_term_fut_pack  = path_term_fut_pack
#=======================================================================
class Class_TABLE_hist_fut():
    def __init__(self, path_term_fut_archiv):
        self.path_term_fut_archiv  = path_term_fut_archiv
#=======================================================================
class Class_TABLE_hist_pack():
    def __init__(self, path_term_fut_archiv):
        self.path_term_fut_archiv  = path_term_fut_archiv
#=======================================================================
class Class_CONTROLER():
    def __init__(self):
        c_dir = os.path.abspath(os.curdir)
        self.log = Class_LOGGER(c_dir + '\\LOG\\term_fut_pack_logger.log')
        path_TERM_FUT_PACK    = c_dir + '\\DB\\term_fut_pack.sqlite'
        path_TERM_FUT_ARCHIV  = c_dir + '\\DB\\term_fut_archiv.sqlite'

        self.cfg_soft = Class_TABLE_cfg_soft(path_TERM_FUT_PACK)
        rq = self.cfg_soft.read_tbl()
        if rq[0] != 0:
            err_msg = 'Can not init TBL cfg_SOFT !' + rq[1]
            sg.PopupError('Error !', err_msg)
            print(err_msg)
            return [1, err_msg]
        else:
            print('cfg_SOFT = > ', rq)


        self.trm_data = Class_TERM_data(self.cfg_soft.path_file_DATA)
        self.trm_hist = Class_TERM_hist(self.cfg_soft.path_file_HIST)
        self.cfg_pack = Class_TABLE_cfg_pack(path_TERM_FUT_PACK)
        self.data_fut = Class_TABLE_data_fut(path_TERM_FUT_PACK)
        self.hist_fut_today  = Class_TABLE_hist_fut_today(path_TERM_FUT_PACK)
        self.hist_pack_today = Class_TABLE_hist_pack_today(path_TERM_FUT_PACK)
#=======================================================================
def service_term_TERM(cntr): # 'Service\Test TERM\term TERM'
    print('term TERM')
    cntr.trm_data.dt_file = 0
    cntr.trm_data.dt_data = 0
    cntr.trm_data.data_in_file = []
    s_term = []
    s_term.append('___ read DATA file ___')
    rq = cntr.trm_data.rd_term()
    if rq[0] != 0 :
        err_msg = 'rd_term => ' + '  '.join(str(e) for e in rq)
        cntr.log.wr_log_error(err_msg)
        s_term.append(err_msg)
    else:
        for item in cntr.trm_data.data_in_file:
            s_term.append(item)
    s_term.append(' ')

    s_term.append('___ read HIST file ___')
    rq = cntr.trm_hist.rd_hist()
    if rq[0] != 0:
        err_msg = 'rd_hist => ' + '  '.join(str(e) for e in rq)
        cntr.log.wr_log_error(err_msg)
        s_term.append(err_msg)
    else:
        arr = cntr.trm_hist.hist_in_file
        if len (cntr.trm_hist.hist_in_file) > 5:
            s_term.append(arr[0].split('|')[0])
            s_term.append(arr[1].split('|')[0])
            s_term.append(arr[2].split('|')[0])
            s_term.append('...')
            s_term.append(arr[-2].split('|')[0])
            s_term.append(arr[-1].split('|')[0])
        else:
            s_term.append('hist_in_file is EMPTY')
    s_term.append(' ')

    sg.Popup( 'term TERM', '\n'.join(s_term) )
#=======================================================================
def error_msg_popup(cntr, msg_log, msg_rq_1, PopUp = True):
    err_msg = msg_log + msg_rq_1
    cntr.log.wr_log_error(err_msg)
    if PopUp:  sg.PopupError('Error !', err_msg)
#=======================================================================
def main():
    # init
    cntr = Class_CONTROLER()

    rq = cntr.trm_data.rd_term()
    if rq[0] != 0:  print('Could not parse_data_in_file !')
    else:           print('trm_data = > ', rq)

    rq = cntr.data_fut.read_tbl()
    if rq[0] != 0:  print('Could not data_fut read !')
    else:           print('data_fut = > ', rq)

    #print('TEST 000 --------------------------------------')

    # init MENU
    menu_def = [
                ['Mode',    ['auto', 'manual', ],],
                ['Service',
                    [
                        ['Test TERM',     ['term TERM', 'reserv'],
                         'Test SQL',      ['data_FUT', 'hist_FUT', 'hist_FUT_TODAY', 'cfg_PACK _ SOFT'],
                         'Hist FUT today',['Convert tbl TODAY', 'VACUUM tbl TODAY'],],
                    ],
                ],
                ['Help', 'About...'],
                ['Exit', 'Exit']
                ]

    tab_BALANCE =  [
                    [sg.T('{: ^12}'.format(str(cntr.data_fut.account.acc_profit)), font='Helvetica 48', key='txt_bal')],
                   ]

    def_txt, frm = [], '{: <15}  => {: ^15}\n'
    #def_txt.append(frm.format('path_db_FUT'   , path_TERM_FUT_PACK))

    tab_DATA    =  [
                    [sg.Multiline( default_text=''.join(def_txt),
                        size=(50, 5), key='txt_data', autoscroll=False, focus=False),],
                   ]

    # Display data
    sg.SetOptions(element_padding=(0,0))

    layout = [
                [sg.Menu(menu_def, tearoff=False, key='menu_def')],
                [sg.TabGroup([[sg.Tab('DATA', tab_DATA), sg.Tab('BALANCE', tab_BALANCE)]], key='tab_group')],
                [sg.T('',size=(60,2), font='Helvetica 8', key='txt_status'), sg.Quit(auto_size_button=True)],
             ]

    window = sg.Window(cntr.cfg_soft.titul, grab_anywhere=True).Layout(layout).Finalize()

    mode = 'manual'
    frm_str = '{: <15}{: ^15}'
    # main cycle   -----------------------------------------------------
    while True:
        stroki = []
        if mode == 'auto':
            event, values = window.Read(timeout=3500 )  # period 2,4 sec
        else:
            event, values = window.Read(timeout=240000) # period 4 min
        #print('event = ', event, ' ..... values = ', values)
        #---------------------------------------------------------------
        if event is None        : break
        if event == 'Quit'      : break
        if event == 'Exit'      : break
        if event == 'auto'      : mode = 'auto'
        if event == 'manual'    : mode = 'manual'
        #---------------------------------------------------------------
        if event == 'term TERM' : service_term_TERM(cntr)
        #---------------------------------------------------------------
        if event == 'cfg_PACK _ SOFT' :
            get_cfg_PACK_obj(cntr)
            get_cfg_SOFT_obj(cntr)
        #---------------------------------------------------------------
        if event == 'reserv' :
            #rq = cntr.hist_fut_today.rewrite_tbl([])                           # Empty table
            rq = cntr.hist_fut_today.rewrite_tbl(cntr.trm_hist.hist_in_file)   # Rewrite table
            print('hist_fut_today.rewrite_tbl => ', rq)
            rq = cntr.hist_fut_today.read_tbl()                                # Read table
            print('hist_fut_today.read_tbl => ', rq)

        #---------------------------------------------------------------
        if event == 'data_FUT'      :
            rq = service_data_FUT(cntr)
            if rq[0] == 0:
                stroki.append('data_FUT - it is OK')
            else:
                stroki.append('ERORR => ' + rq[1])
        #---------------------------------------------------------------
        if event == 'hist_FUT_TODAY':
            rq = service_hist_FUT_TODAY(cntr)
            if rq[0] == 0:
                stroki.append('hist_FUT_TODAY  = ' + str(rq[1]) + ' strings' )
            else:
                stroki.append('ERORR => ' + rq[1])
        #---------------------------------------------------------------
        if event == 'hist_FUT':
            rq = service_hist_FUT(cntr)
            if rq[0] == 0:
                stroki.append('hist_FUT  = ' + str(rq[1]) + ' strings' )
            else:
                stroki.append('ERORR => ' + rq[1])
        #---------------------------------------------------------------
        if event == '__TIMEOUT__':
            rq = read_data_hist_files(cntr)
            if rq[0] == 0:
                stroki.append('Time DATA:  ' + cntr.term.data_in_file[0].split('|')[0])
                stroki.append('Time HIST:  ' + cntr.term.hist_in_file[-1].split('|')[0])
                stroki.append('Have got new data/hist')
            else:
                stroki.append(rq[1])
        #---------------------------------------------------------------
        window.FindElement('txt_data').Update('\n'.join(stroki))
        txt_frmt = '%Y.%m.%d  %H:%M:%S'
        stts  = time.strftime(txt_frmt, time.localtime()) + '\n'
        stts += 'event = ' + event
        window.FindElement('txt_status').Update(stts)

    return
#=======================================================================
if __name__ == '__main__':
    import sys
    sys.exit(main())
