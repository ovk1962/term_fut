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
class Class_TERM():
    def __init__(self, path_trm, path_hist):
        self.nm = ''
        self.path_trm  = path_trm
        self.path_hist = path_hist
        #self.dt_file_size = 0
        self.dt_file = 0        # curv stamptime data file path_trm
        self.dt_data = 0        # curv stamptime DATA/TIME from TERM
        self.data_in_file = []  # list of strings from path_trm
        self.dt_hist = 0        # curv stamptime data file path_hist
        self.hist_in_file = []  # list of strings from path_hist
        self.data_fut = []      # list of Class_FUT() from trm

        self.account  = ''      # obj Class_ACCOUNT() from trm
        self.str_for_hist = ''  # str for hist table
        self.delay_tm = 10      # min period to get data for DB (10 sec)
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
            err_msg = 'can not find file'
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
                self.dt_data = dt_sec
            else:
                str_dt_data = datetime.fromtimestamp(self.dt_data).strftime('%H:%M:%S')
                err_msg = 'DATA is not updated ' + dt_str
                #cntr.log.wr_log_error(err_msg)
                return [5, err_msg]
        except Exception as ex:
            err_msg = dt_str + ' => ' + str(ex)
            #cntr.log.wr_log_error(err_msg)
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
        #
        return [0, 'OK']
    #-------------------------------------------------------------------
    def rd_hist(self):
        #--- check file cntr.file_path_HIST ----------------------------
        if not os.path.isfile(self.path_hist):
            err_msg = 'can not find file'
            #cntr.log.wr_log_error(err_msg)
            return [1, err_msg]
        buf_stat = os.stat(self.path_hist)
        #
        #--- check size of file ----------------------------------------
        if buf_stat.st_size == 0:
            err_msg = 'size DATA file is NULL'
            #cntr.log.wr_log_error(err_msg)
            return [2, err_msg]
        #
        #--- check time modificated of file ----------------------------
        if int(buf_stat.st_mtime) == self.dt_hist:
            #str_dt_file = datetime.fromtimestamp(self.dt_hist).strftime('%H:%M:%S')
            return [3, 'FILE is not modificated']
        else:
            #self.dt_file_prev = self.dt_file
            self.dt_hist = int(buf_stat.st_mtime)
            #print(self.dt_file)
        #
        #--- read TERM file --------------------------------------------
        buf_str = []
        with open(self.path_hist,"r") as fh:
            buf_str = fh.read().splitlines()
        #
        #--- check size of list/file -----------------------------------
        if len(buf_str) == 0:
            err_msg = ' the size path_hist is NULL'
            #cntr.log.wr_log_error(err_msg)
            return [4, err_msg]
        #
        self.hist_in_file = []
        self.hist_in_file = buf_str[:]
        #
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
            #cntr.log.wr_log_error(err_msg)
            return [1, err_msg]
        return [0, 'ok']
    #-------------------------------------------------------------------
    def prpr_str_hist(self):
        try:
            if self.data_in_file != '':
                for i, item in enumerate(self.data_in_file):
                    list_item = ''.join(item).replace(',','.').split('|')
                    if   i == 0:
                        str_hist = item.split('|')[0] + '|'
                    elif i == 1:
                        pass
                    else:
                        b_str = item.split('|')
                        str_hist += b_str[5] + '|' + b_str[7] + '|'
                self.str_for_hist = str_hist
            else:
                return [0, 'data_in_file is empty!']
        except Exception as ex:
            err_msg = 'prepare_str_hist => ' + str(ex)
            #cntr.log.wr_log_error(err_msg)
            return [1, err_msg]
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
class Class_CONTR():
    ''' There are 2 history tables of FUT -
    file_path_DATA  - file data from terminal QUIK
    file_path_HIST  - file hist(today) from terminal QUIK
    db_path_FUT     - TABLE s_hist_1, ask/bid from TERMINAL 1 today (TF = 15 sec)
    '''
    def __init__(self, file_path_DATA, file_path_HIST, db_path_FUT, log_path):
        self.name_trm = ''
        #
        self.file_path_DATA  = file_path_DATA    # path file DATA
        self.file_path_HIST  = file_path_HIST    # path file HIST
        self.term            = Class_TERM(self.file_path_DATA, self.file_path_HIST)
        #
        self.db_path_FUT  = db_path_FUT       # path DB data & hist
        self.db_FUT_data  = Class_SQLite(self.db_path_FUT)
        #
        self.hist_fut        = []   # массив котировок фьючей  60 s (archiv)
        self.hist_fut_today  = []   # массив котировок фьючей  60 s (today)
        self.hist_pack       = []   # массив котировок packets 60 s (archiv)
        self.hist_pack_today = []   # массив котировок packets 60 s (today)
        #
        self.data_fut = []    # list of Class_FUT()
        self.account  = ''    # obj Class_ACCOUNT()
        #
        self.koef_pack  = []  # массив списков-характеристик packets
        #
        # init LOGger
        self.log  = Class_LOGGER(log_path)
        self.log.wr_log_info('*** START ***')
#=======================================================================
def error_msg_popup(cntr, msg_log, msg_rq_1, PopUp = True):
    err_msg = msg_log + msg_rq_1
    cntr.log.wr_log_error(err_msg)
    if PopUp:  sg.PopupError('Error !', err_msg)
#=======================================================================
def get_table_data(cntr):
    # read table DATA / init cntr.data_fut & cntr.account
    rq  = cntr.db_FUT_data.get_table_db_with('data_FUT')
    if rq[0] == 0:
        cntr.term.data_in_file = rq[1]
        #print('db_FUT_data.get_table_db_with(data) \n', rq[1])
        rq  = cntr.term.parse_data_in_file()
        if rq[0] != 0:
            err_msg = 'get_table_data...parse_str_data_fut => ' + rq[1]
            return [1, err_msg]
    else:
        err_msg = 'get_table_db_with(data) ' + rq[1]
        return [1, err_msg]
    return [0, 'ok']
#=======================================================================
def get_cfg_PACK(cntr):
    # read table cfg_PACK from DB cntr.db_PACK
    # init cntr.koef_pack
    rq  = cntr.db_FUT_data.get_table_db_with('cfg_PACK')
    if rq[0] != 0:
        sg.Popup('Error cfg_PACK!',  rq[1])
        return [1, rq[1]]
    else:
        for i_mdl, item in enumerate(rq[1]):
            cntr.koef_pack.append([])
            #   ['pckt0', ['0:2:SR, 9:-20:MX'], '222:100', '0.1:0.01:22:100']
            cntr.koef_pack[i_mdl].append(rq[1][i_mdl][0])
            cntr.koef_pack[i_mdl].append(rq[1][i_mdl][1].split(','))
            cntr.koef_pack[i_mdl].append(rq[1][i_mdl][2])
            #cntr.koef_pack[i_mdl].append(rq[1][i_mdl][3])
            cntr.koef_pack[i_mdl].append(0) # NULL price for PACK
            print(cntr.koef_pack[i_mdl])
        print('___ Totally PACKETs ___ ', len(cntr.koef_pack))
        for item in cntr.koef_pack:
            cntr.hist_pack.append([])
            cntr.hist_pack_today.append([])
        return [0, 'OK']
#=======================================================================
def service_cfg_PACK(cntr): # 'Service\Test SQL\cfg_PACK'
    s_koef = []
    cntr.koef_pack = []
    rq  = get_cfg_PACK(cntr)
    if rq[0] != 0:
        error_msg_popup(cntr, 'service_cfg_PACK => ', str(rq[1]), PopUp = True)
        return

    for item in cntr.koef_pack :
        s_jtem = ''
        for jtem in item:
            if type(jtem) is list:  s_jtem += ' ; '.join(jtem) + '  '
            else:                   s_jtem += str(jtem) + '  '
        s_koef.append(s_jtem)
    sg.Popup(
             'cfg_PACK',
             '\n'.join(s_koef)
            )
#=======================================================================
def service_data_FUT(cntr): # 'Service\Test SQL\data_FUT'
    print('data_FUT')
    rq  = cntr.db_FUT_data.get_table_db_with('data_FUT')
    if rq[0] == 0:
        for item in rq[1]:  print(item)
    else:
        err_msg = 'get_table_db_with(data_FUT) ' + rq[1]
        sg.PopupError('Error !', err_msg)
#=======================================================================
def service_hist_FUT_TODAY(cntr): # 'Service\Test SQL\data_FUT'
    print('hist_FUT_TODAY')
    rq  = cntr.db_FUT_data.get_table_db_with('hist_FUT_today')
    if rq[0] == 0:
        if len(rq[1]) == 0:  print('hist_FUT_today is EMPTY')
        for item in rq[1] :  print(item)
    else:
        err_msg = 'get_table_db_with(hist_FUT_today) ' + rq[1]
        sg.PopupError('Error !', err_msg)
#=======================================================================
def service_term_DATA(cntr): # 'Service\Test TERM\term DATA'
    print('term DATA')
    # read DATA file
    rq = cntr.term.rd_term()
    if rq[0] > 4 :
        # there is not new DATA
        err_msg = 'service_cfg_PACK => ' + str(rq[1])
        error_msg_popup(cntr, err_msg, rq[1], PopUp = False)
        return [1, 'rd_term => '+rq[1]]
    else:
        for item in cntr.term.data_in_file: print(item)
    return [0, 'ok']
#=======================================================================
def service_term_HIST(cntr): # 'Service\Test TERM\term HIST'
    print('term HIST')
    # read HIST file
    rq = cntr.term.rd_hist()
    if rq[0] != 0:
        # there is not new HIST
        return [1, 'rd_hist => '+rq[1]]
    else:
        print('There are strings = ', len(cntr.term.hist_in_file))
        print(cntr.term.hist_in_file[0])
        print(cntr.term.hist_in_file[1])
        print('...')
        print(cntr.term.hist_in_file[-2])
        print(cntr.term.hist_in_file[-1])
    return [0, 'ok']
#=======================================================================

def init_cntr(cntr):
    # init cntr.koef_pack
    rq  = get_cfg_PACK(cntr)
    if rq[0] != 0:
        error_msg_popup(cntr, 'get_cfg_PACK => ', str(rq[1]), PopUp = True)
        return [1, 'get_cfg_PACK => ' + str(rq[1])]

    #--- init FUT cntr.data_fut & cntr.account -------------
    rq  = get_table_data(cntr)
    if rq[0] != 0:
        error_msg_popup(cntr, 'init_cntr => get_table_data => ', str(rq[1]), PopUp = True)
        return [1, err_msg]

    print('init_cntr - OK')
    return [0, 'OK']
#=======================================================================
def read_data_hist_files(cntr):
    # read DATA file
    rq = cntr.term.rd_term()
    if rq[0] != 0:
        return [1, 'read_data_hist_files...rd_term => '+rq[1]]
    rq  = cntr.term.parse_data_in_file()
    if rq[0] != 0:
        return [1, 'read_data_hist_files...parse_str_data_fut => ' + rq[1]]
    # read HIST file
    rq = cntr.term.rd_hist()
    if rq[0] != 0:
        return [1, 'read_data_hist_files...rd_hist => '+rq[1]]

    return [0, 'ok']
#=======================================================================
def main():
    # init program config
    dirr, sub_dirr = os.path.abspath(os.curdir), '\\DB\\'
    path_FUT_PACK = 'term_fut_pack.sqlite'
    path_FUT_ARCH = 'term_fut_archiv.sqlite'
    db_path_FUT_PACK  = dirr + sub_dirr + path_FUT_PACK
    nm_trm, file_path_DATA, file_path_HIST, log_path = '', '', '', ''

    path_DB  = Class_SQLite(db_path_FUT_PACK)
    rq  = path_DB.get_table_db_with('cfg_SOFT')
    if rq[0] != 0:
        print('Can not read DB => term_today.sqlite !')
        sg.PopupError('Can not read DB => term_today.sqlite !')
        return
    for item in rq[1]:
        print(item)
        if item[0] == 'titul'         : nm_trm          = item[1]
        if item[0] == 'path_file_DATA': file_path_DATA  = item[1]
        if item[0] == 'path_file_HIST': file_path_HIST  = item[1]
        if item[0] == 'path_file_LOG' : log_path        = dirr + item[1]

    # init CONTR
    cntr = Class_CONTR(file_path_DATA, file_path_HIST, db_path_FUT_PACK, log_path)
    cntr.name_trm = nm_trm
    init_cntr(cntr)

    # init MENU
    menu_def = [
                ['Mode',    ['auto', 'manual', ],],
                ['Service',
                    [
                        ['Test TERM',     ['term DATA', 'term HIST'],
                         'Test SQL',      ['data_FUT', 'hist_FUT', 'hist_FUT_TODAY', 'cfg_PACK'],
                         'Hist FUT today',['Convert tbl TODAY', 'VACUUM tbl TODAY'],],
                    ],
                ],
                ['Help', 'About...'],
                ['Exit', 'Exit']
                ]

    tab_BALANCE =  [
                    [sg.T('{: ^12}'.format(str(cntr.term.account.acc_profit)), font='Helvetica 48', key='txt_bal')],
                   ]

    def_txt, frm = [], '{: <15}  => {: ^15}\n'
    def_txt.append(frm.format('path_db_FUT'   , path_FUT_PACK))
    def_txt.append(frm.format('path_db_ARC'   , path_FUT_ARCH))
    def_txt.append(frm.format('path_file_DATA', file_path_DATA))
    def_txt.append(frm.format('path_file_HIST', file_path_HIST))

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

    window = sg.Window(nm_trm, grab_anywhere=True).Layout(layout).Finalize()

    mode = 'auto'
    frm_str = '{: <15}{: ^15}'
    # main cycle   -----------------------------------------------------
    while True:
        stroki = []
        if mode == 'auto':
            event, values = window.Read(timeout=3500 )  # period 2,4 sec
        else:
            event, values = window.Read(timeout=240000) # period 4 min
        #print('event = ', event, ' ..... values = ', values)

        if event is None        : break
        if event == 'Quit'      : break
        if event == 'Exit'      : break
        if event == 'auto'      : mode = 'auto'
        if event == 'manual'    : mode = 'manual'

        if event == 'term DATA'     : service_term_DATA(cntr)
        if event == 'term HIST'     : service_term_HIST(cntr)
        if event == 'cfg_PACK'      : service_cfg_PACK(cntr)
        if event == 'data_FUT'      : service_data_FUT(cntr)
        if event == 'hist_FUT_TODAY': service_hist_FUT_TODAY(cntr)

        if event == '__TIMEOUT__':
            rq = read_data_hist_files(cntr)
            if rq[0] == 0:
                stroki.append('Time DATA:  ' + cntr.term.data_in_file[0].split('|')[0])
                stroki.append('Time HIST:  ' + cntr.term.hist_in_file[-1].split('|')[0])
                stroki.append('Have got new data/hist')
            else:
                stroki.append(rq[1])

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
