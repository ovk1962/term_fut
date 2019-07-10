#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  graf_fut_pack.py
#
#=======================================================================
import os, sys, math, time
import logging
import smtplib
import sqlite3
import operator
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
        self.arr_pack_archiv = []  # list of [[ind_sec string] ... ]
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

    #///////////////////////////////////////////////////////////////////
    def read_tbl(self):
        rq  = self.obj_table.get_table_db_with('hist_PACK')
        if rq[0] != 0:
            err_msg = 'Can not read TBL hist_PACK ! ' + '  '.join(str(e) for e in rq)
            print(err_msg)
            return [1, err_msg]
        if len(rq[1]) == 0:
            return [1, 'table hist_PACK is empty']

        self.hist_pack_archiv = []
        self.arr_pack_archiv  = []
        self.hist_pack_archiv = rq[1][:]

        str_pack = self.hist_pack_archiv[0][1].split('|')
        ind_pack = ''
        for i_mdl in range(len(str_pack) - 1):
            self.arr_pack_archiv.append([])
            for item in self.hist_pack_archiv:
                str_pack = item[1].replace(',','.').split('|')
                del str_pack[-1]
                str_mdl  = str_pack[0].split(' ')   # dt tm for all packets
                buf_p = Class_PACK()
                buf_p.ind= int(item[0])
                buf_p.dt = str_mdl[0]
                buf_p.tm = str_mdl[1]

                if i_mdl == 0:
                    buf_p.pAsk = float(str_mdl[2])
                    buf_p.pBid = float(str_mdl[3])
                    buf_p.EMAf = float(str_mdl[4])
                    buf_p.EMAf_rnd     = float(str_mdl[5])
                    buf_p.cnt_EMAf_rnd = float(str_mdl[6])

                else:
                    str_mdl  = str_pack[i_mdl].split(' ')
                    buf_p.pAsk = float(str_mdl[0])
                    buf_p.pBid = float(str_mdl[1])
                    buf_p.EMAf = float(str_mdl[2])
                    buf_p.EMAf_rnd     = float(str_mdl[3])
                    buf_p.cnt_EMAf_rnd = float(str_mdl[4])

                self.arr_pack_archiv[i_mdl].append(buf_p)
            ind_pack += str(i_mdl) + ' '
            print(ind_pack, end='\r')
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

        #self.trm_data = Class_TERM_data(self.cfg_soft.path_file_DATA)
        #self.trm_hist = Class_TERM_hist(self.cfg_soft.path_file_HIST)
        self.cfg_pack = Class_TABLE_cfg_pack(path_TERM_FUT_PACK)
        #self.cfg_alarm = Class_TABLE_cfg_alarm(path_TERM_FUT_PACK)
        self.dt_fut   = Class_TABLE_data_fut(path_TERM_FUT_PACK)
        self.h_fut_today  = Class_TABLE_hist_fut_today(path_TERM_FUT_PACK)
        self.h_pack_today = Class_TABLE_hist_pack_today(path_TERM_FUT_PACK)
        self.h_fut_arc    = Class_TABLE_hist_fut(path_TERM_FUT_ARCHIV)
        self.h_pack_arc   = Class_TABLE_hist_pack(path_TERM_FUT_ARCHIV)
        #self.e_mail   = Class_GMAIL('mobile.ovk', '20066002', 'mobile.ovk@gmail.com')

        self.arr_fut        = []    # массив котировок фьючей  60 s
        self.arr_fut_today  = []    # массив котировок фьючей  60 s
        self.arr_pack       = []    # массив котировок packets 60 s
        self.arr_pack_today = []    # массив котировок packets 60 s

        self.tm_wrt_new_data = 0    # minute's counter
#=======================================================================
def dbg_prn(cntr, b_clear  = True,
        b_cfg_soft  = False,
        b_cfg_pack  = False,
        b_fut_today = False,
        b_fut_arc   = False,
        b_pack_arc  = False
        ):
    if b_clear:
        os.system('cls')  # on windows

    if b_cfg_soft:
        #hist_in_file = cntr.trm_hist.hist_in_file
        s = cntr.cfg_soft
        rq = s.read_tbl()
        if rq[0] != 0 :
            _err_(cntr, 'cfg_soft ', rq)
            return
        print('.....Class_TABLE_cfg_soft.....')
        print('path_term_fut_pack => ', s.path_term_fut_pack)
        print('titul              => ', s.titul)
        print('path_file_DATA     => ', s.path_file_DATA)
        print('path_file_HIST     => ', s.path_file_HIST)
        print('dt_start           => ', s.dt_start)

    if b_cfg_pack:
        c = cntr.cfg_pack
        rq = c.read_tbl()
        if rq[0] != 0 :
            _err_(cntr, 'cfg_pack ', rq)
            return
        print('.....Class_TABLE_cfg_pack.....')
        print('path_term_fut_pack    => ', c.path_term_fut_pack)
        print('len(nm) => ', len(c.nm))
        if len(c.nm) > 0:
            for i, item in enumerate(c.nm):
                print(item, c.koef[i], c.nul[i], c.ema[i] )

    if b_fut_today:
        h = cntr.h_fut_today
        rq = h.read_tbl()
        if rq[0] != 0 :
            _err_(cntr, 'hist_FUT_today ', rq)
            return
        print('.....Class_TABLE_data_fut.....')
        print('path_term_fut_pack    => ', h.path_term_fut_pack)
        print('len(hist_fut_today)   => ', len(h.hist_fut_today))
        if len(h.hist_fut_today) > 4:
            print('hist_fut_today[0] => ',  h.hist_fut_today[0])
            print('hist_fut_today[1] => ',  h.hist_fut_today[1][1].split('|')[0])
            print('hist_fut_today[2] => ',  h.hist_fut_today[2][1].split('|')[0])
            print('. . . . .')
            print('hist_fut_today[-1] => ', h.hist_fut_today[-1][1].split('|')[0])
            print('___________________________')
        print('len(hist_1_fut_today) => ', len(h.hist_1_fut_today))
        if len(h.hist_1_fut_today) > 4:
            print('hist_1_fut_today[0] => ',  h.hist_1_fut_today[0])
            print('hist_1_fut_today[1] => ',  h.hist_1_fut_today[1][1].split('|')[0])
            print('hist_1_fut_today[2] => ',  h.hist_1_fut_today[2][1].split('|')[0])
            print('. . . . .')
            print('hist_1_fut_today[-1] => ', h.hist_1_fut_today[-1][1].split('|')[0])
            print('___________________________')
        print('len(arr_1_fut_today)  => ', len(h.arr_1_fut_today))
        if len(h.arr_1_fut_today) > 4:
            print('arr_1_fut_today[0] => ',  h.arr_1_fut_today[0])
            print('arr_1_fut_today[1] => ',  h.arr_1_fut_today[1][1].split('|')[0])
            print('arr_1_fut_today[2] => ',  h.arr_1_fut_today[2][1].split('|')[0])
            print('. . . . .')
            print('arr_1_fut_today[-1] => ', h.arr_1_fut_today[-1][1].split('|')[0])

    if b_fut_arc:
        h = cntr.h_fut_arc
        rq = h.read_tbl()
        if rq[0] != 0 :
            _err_(cntr, 'hist_FUT_today ', rq)
            return
        print('.....Class_TABLE_hist_fut(archiv).....')
        print('path_term_fut_archiv    => ', h.path_term_fut_archiv)
        print('len(hist_fut_archiv)   => ', len(h.hist_fut_archiv))
        if len(h.hist_fut_archiv) > 4:
            print('hist_fut_archiv[0] => ',  h.hist_fut_archiv[0])
            print('hist_fut_archiv[1] => ',  h.hist_fut_archiv[1][1].split('|')[0])
            print('hist_fut_archiv[2] => ',  h.hist_fut_archiv[2][1].split('|')[0])
            print('. . . . .')
            print('hist_fut_archiv[-1] => ', h.hist_fut_archiv[-1][1].split('|')[0])
            print('___________________________')
        print('len(arr_fut_archiv)  => ', len(h.arr_fut_archiv))
        if len(h.arr_fut_archiv) > 4:
            print('arr_fut_archiv[0] => ',  h.arr_fut_archiv[0])
            print('arr_fut_archiv[1] => ',  h.arr_fut_archiv[1][1].split('|')[0])
            print('arr_fut_archiv[2] => ',  h.arr_fut_archiv[2][1].split('|')[0])
            print('. . . . .')
            print('arr_fut_archiv[-1] => ', h.arr_fut_archiv[-1][1].split('|')[0])

    if b_pack_arc:
        h = cntr.h_pack_arc
        rq = h.read_tbl()
        if rq[0] != 0 :
            _err_(cntr, 'hist_PACK_today ', rq)
            return
        print('.....Class_TABLE_hist_pack(archiv).....')
        print('path_term_fut_archiv    => ', h.path_term_fut_archiv)
        #rq = h.read_tbl()
        #if rq[0] != 0 :
        #    _err_(cntr, 'hist_PACK ', rq)
        #    return
        print('len(hist_pack_archiv)   => ', len(h.hist_pack_archiv))
        if len(h.hist_pack_archiv) > 4:
            print('hist_pack_archiv[0] => ',  h.hist_pack_archiv[0])
            print('hist_pack_archiv[1] => ',  h.hist_pack_archiv[1][1].split('|')[0])
            print('hist_pack_archiv[2] => ',  h.hist_pack_archiv[2][1].split('|')[0])
            print('. . . . .')
            print('hist_pack_archiv[-1] => ', h.hist_pack_archiv[-1][1].split('|')[0])
            print('___________________________')
        print('len(arr_pack_archiv)   => ', len(h.arr_pack_archiv), ' packets')
        print('len(arr_pack_archiv[0])   => ', len(h.arr_pack_archiv[0]), ' records in pack0')
        if len(h.arr_pack_archiv) > 4:
            print('arr_pack_archiv[0][0].dt => ',  h.arr_pack_archiv[0][0].dt)
            print('arr_pack_archiv[0][1].dt => ',  h.arr_pack_archiv[0][1].dt)
            print('arr_pack_archiv[0][2].dt => ',  h.arr_pack_archiv[0][2].dt)
            print('. . . . .')
            print('arr_pack_archiv[0][-1].dt => ', h.arr_pack_archiv[0][-1].dt)
            print('___________________________')


        print('')
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
def event_menu(cntr, event, values, graph):
    #---------------------------------------------------------------
    if event == 'prn FUT cfg_SOFT'       : dbg_prn(cntr, b_cfg_soft         = True)
    #---------------------------------------------------------------
    if event == 'prn FUT cfg_PACK'       : dbg_prn(cntr, b_cfg_pack         = True)
    #---------------------------------------------------------------
    if event == 'prn FUT hist_FUT_today' : dbg_prn(cntr, b_fut_today        = True)
    #---------------------------------------------------------------
    if event == 'prn FUT hist_FUT_arch'  : dbg_prn(cntr, b_fut_arc          = True)
    #---------------------------------------------------------------
    if event == 'prn PACK hist_PACK_arch': dbg_prn(cntr, b_pack_arc         = True)
    #---------------------------------------------------------------
    if event == 'calc PACK arc'          : debug_calc_PACK_arc(cntr)
    #---------------------------------------------------------------
    if event == 'refresh'   : refresh_graph(cntr, event, values, graph)
#=======================================================================
def calc_hist_PACK(cntr, i_pack):
    cntr.arr_pack[i_pack] = []
    arr_HIST = cntr.h_fut_arc.arr_fut_archiv    # archiv of FUT 60 sec
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
    cntr.cfg_pack.read_tbl()
    print('writing hist_PACK . . . . . .')
    wr_hist_PACK(cntr)
    print('ok. . . . . . . . . . . . . .')
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

#=======================================================================
def refresh_graph(cntr, event, values, graph):
    graph.Erase()
    y_pack, y_gr_1, y_gr_2, y_gr_12 , y_gr_22 = [], [], [], [], []
    x_up, x_down   = [], []
    f_mode = [1, 5, 15, 30, 60, 120]

    if   values['TF'][0] == ' 1 min':   TF_mode = 0
    elif values['TF'][0] == ' 5 min':   TF_mode = 1
    elif values['TF'][0] == '15 min':   TF_mode = 2
    elif values['TF'][0] == '30 min':   TF_mode = 3
    elif values['TF'][0] == '60 min':   TF_mode = 4
    elif values['TF'][0] == '120 min':  TF_mode = 5
    else:                               TF_mode = 0

    print('len = ', len(cntr.h_fut_arc.arr_fut_archiv))

    for i_pack, item in enumerate(cntr.h_pack_arc.arr_pack_archiv):
        y_pack.append([])
        y_pack[i_pack] = [x for x in cntr.h_pack_arc.arr_pack_archiv[i_pack]]
    #if len(cntr.hist_pack_today) != 0:
    #    for i_pack, item in enumerate(cntr.hist_pack_today):
    #        y_pack[i_pack] += [x for x in cntr.hist_pack_today[i_pack]]

    x_dt = [x.dt for x in y_pack[0]]
    x_tm = [x.tm for x in y_pack[0]]

    y_pack_1  = [int((y.pAsk+y.pBid)/2) for y in y_pack[0]]
    y_emaf_1  = [y.EMAf_rnd             for y in y_pack[0]]
    nom_PACK = int(values['PACK'].split(' ')[0])
    y_pack_2  = [int((y.pAsk+y.pBid)/2) for y in y_pack[nom_PACK]]
    y_emaf_2  = [y.EMAf_rnd             for y in y_pack[nom_PACK]]

    len_y = len(y_pack_1)
    sz_L, sz_W = graph.TopRight[0]-5, graph.TopRight[1]-5

    x_scale = f_mode[TF_mode]
    if len_y > x_scale * sz_L:   i_start = len_y - x_scale * sz_L
    else:                        i_start = 0

    for x in range(i_start, len_y-1, x_scale):
        if x < len_y:
            x_up.append(x_dt[x])
            x_down.append(x_tm[x])
            y_gr_1.append (y_pack_1[x])
            y_gr_2.append (y_emaf_1[x])
            y_gr_12.append(y_pack_2[x])
            y_gr_22.append(y_emaf_2[x])

    k_max = [max(y_gr_1), max(y_gr_2)]
    index, value = max(enumerate(k_max), key=operator.itemgetter(1))
    if   index == 0: k_max = 100 + max(y_gr_1)
    elif index == 1: k_max = 100 + max(y_gr_2)

    k_min = [min(y_gr_1), min(y_gr_2)]
    index, value = min(enumerate(k_min), key=operator.itemgetter(1))
    if   index == 0: k_min = min(y_gr_1) - 100
    elif index == 1: k_min = min(y_gr_2) - 100

    k_max = 100 * math.ceil(k_max/100)
    k_min = 100 * int(k_min/100)
    k_gr = sz_W / (k_max - k_min)

    k_max_2 = [max(y_gr_12), max(y_gr_22)]
    index, value = max(enumerate(k_max_2), key=operator.itemgetter(1))
    if   index == 0: k_max_2 = 100 + max(y_gr_12)
    elif index == 1: k_max_2 = 100 + max(y_gr_22)

    k_min_2 = [min(y_gr_12), min(y_gr_22)]
    index, value = min(enumerate(k_min_2), key=operator.itemgetter(1))
    if   index == 0: k_min_2 = min(y_gr_12) - 100
    elif index == 1: k_min_2 = min(y_gr_22) - 100

    k_max_2 = 100 * math.ceil(k_max_2/100)
    k_min_2 = 100 * int(k_min_2/100)
    k_gr_2 = sz_W / (k_max_2 - k_min_2)

    # Draw axis X
    for x in range(104, len(x_up), 104):
        graph.DrawLine((x,25), (x,sz_W-0), color='lightgrey')
        graph.DrawText( x_up[x], (x,3), color='black')
        graph.DrawText( x_down[x], (x,18), color='black')

    # Draw axis Y
    for y in range(50, sz_W , 50):
        graph.DrawLine((25, y), (sz_L, y), color='lightgrey')
        k_text = int(k_min + y / k_gr)
        graph.DrawText(k_text , (15, y), color='green')

    graph.DrawText('Delta Y = ' + str(k_max - k_min) ,
        (35, sz_W - 5),
        color='green')
    graph.DrawText('Delta Y2 = ' + str(k_max_2 - k_min_2) ,
        (sz_L - 55, sz_W - 5),
        color='blue')

    # Draw Graph Y1 (Left)
    for i, item in enumerate(y_gr_1):
        if i != 0:
            prev = int((pr_item - k_min) * k_gr)
            cur  = int((item - k_min) * k_gr)
            graph.DrawLine((i-1, prev), (i, cur), color='green')
        pr_item = item
    for i, item in enumerate(y_gr_2):
        cur  = int((item - k_min) * k_gr)
        graph.DrawCircle((i, cur), 2, line_color='red', fill_color='red')

    # Draw Graph Y2 (Right)
    for i, item in enumerate(y_gr_12):
        if i != 0:
            prev = int((pr_item - k_min_2) * k_gr_2)
            cur  = int((item - k_min_2) * k_gr_2)
            graph.DrawLine((i-1, prev), (i, cur), color='blue')
        pr_item = item
    for i, item in enumerate(y_gr_22):
        cur  = int((item - k_min_2) * k_gr_2)
        graph.DrawCircle((i, cur), 2, line_color='lightblue', fill_color='lightblue')
#=======================================================================
def main():
    cntr = Class_CONTROLER()
    while True: # init   -----------------------------------------------
        rq = cntr.cfg_pack.read_tbl()
        if rq[0] != 0 : _err_(cntr, 'INIT cfg_PACK ', rq)
        else:
            print('cfg_pack  = > ', rq)
            if len(cntr.cfg_pack.nm) == 0:
                _err_(cntr, 'cfg_pack.nm = 0  ', [' ', 'It can not be EMPTY !'] )
                break
            for item in cntr.cfg_pack.nm:
                cntr.arr_pack.append([])
                cntr.arr_pack_today.append([])
        #---------------------------------------------------------------
        rq = cntr.dt_fut.read_tbl()
        if rq[0] != 0:  _err_(cntr, 'INIT data_FUT ', rq)
        else:           print('data_fut        = > ', rq)
        #---------------------------------------------------------------
        rq = cntr.h_fut_today.read_tbl()
        if rq[0] != 0 : _err_(cntr, 'INIT h_fut_today ', rq)
        else:           print('hist_FUT today  = > ', rq)
        #---------------------------------------------------------------
        rq = cntr.h_fut_arc.read_tbl()
        if rq[0] != 0 : _err_(cntr, 'INIT hist_fut_archiv ', rq)
        else:           print('hist_FUT archiv = > ', rq)
        #---------------------------------------------------------------
        rq = cntr.h_pack_arc.read_tbl()
        if rq[0] != 0 : _err_(cntr, 'INIT hist_pack_archiv ', rq)
        else:           print('hist_PACK archiv = > ', rq)
        #---------------------------------------------------------------
        # init Graph
        sz_W, sz_L = 500, 1040
        sg.SetOptions(element_padding=(0,0))

        grafic = sg.Graph(canvas_size=(sz_L, sz_W),
                        graph_bottom_left=(  -5,     -5),
                        graph_top_right=(sz_L+5, sz_W+5),
                        background_color= 'lightyellow', #'white',
                        key='graph')

        sg_pack=[
                '0 all FUT vs -320:MX',
                '1 1:SR,-10:MX',
                '2 1:GZ,-10:MX',
                '3 6:VB,-10:MX',
                '4 5:HR,-10:MX',
                '5 1:SP,-10:MX',
                '6 1:FS,-10:MX',
                '7 3:AL,-10:MX',
                '8 1:MT,-10:MX',
                '9 1:LK,-20:MX',
                '10 1:RS,-20:MX',
                '11 pack_6  vs -120:MX',
                '12 pack_10 vs -120:MX'
                ]

        # init MENU
        menu_def = [
            ['Mode',
                ['auto', 'manual', ],
                ],
            ['Print',
                [
                 'prn FUT cfg_SOFT',       'prn FUT cfg_PACK',
                 'prn FUT hist_FUT_today', 'prn FUT hist_FUT_arch', 'prn PACK hist_PACK_arch'],
                ],
            ['Debug',
                ['calc PACK today', 'calc PACK arc'],
                ],
            ['Grafic',
                ['refresh', '-------'],
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
                    [
                     sg.InputOptionMenu(sg_pack, key='PACK', default_value='12 special vs -120:MX'),
                     sg.T(' ' * 22),
                     sg.Listbox(values=(' 1 min', ' 5 min', '15 min', '30 min', '60 min', '120 min'),
                             size=(10, 2), default_values=' 1 min' , key='TF', bind_return_key=True),
                    ],
                    [grafic],
                    [sg.T('',size=(165,2), font='Helvetica 8', key='txt_status'),
                     sg.Quit(auto_size_button=True)],
                 ]
        sg.SetOptions(element_padding=(0,0))
        window = sg.Window(cntr.cfg_soft.titul, grab_anywhere=True).Layout(layout).Finalize()

        break

    mode = 'manual'
    tm_out = 360000
    frm = '%d.%m.%Y %H:%M:%S'
    stts  = time.strftime(frm, time.localtime()) + '\n' + 'event = manual'
    window.FindElement('txt_status').Update(stts)

    while True:
        stroki = []
        event, values = window.Read(timeout=tm_out )
        print('event = ', event, ' ..... values = ', values)
        #---------------------------------------------------------------
        if event == 'auto'   :
            tm_out = 1550
            mode = 'auto'
        #---------------------------------------------------------------
        if event == 'manual' :
            tm_out = 240000
            mode = 'manual'
        #---------------------------------------------------------------
        event_menu(cntr, event, values, grafic)
        #---------------------------------------------------------------
        if event is None or event == 'Quit' or event == 'Exit': break
        #---------------------------------------------------------------

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
