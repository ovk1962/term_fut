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
        self.acc_bal  = 0.0
        self.acc_prf  = 0.0
        self.acc_go   = 0.0
        self.acc_depo = 0.0
#=======================================================================
class Class_FUT():
    def __init__(self):
        self.sP_code   = "-"
        self.sRest     = 0
        self.sVar_mrg  = 0.0
        self.sOpen_prc = 0.0
        self.sLast_prc = 0.0
        self.sAsk      = 0.0
        self.sBuy_qty  = 0
        self.sBid      = 0.0
        self.sSell_qty = 0
        self.sFut_go   = 0.0
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
        self.EMAf_r = 0.0
        self.cnt_EMAf_r = 0.0
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
class Class_TERM_data():
    #///////////////////////////////////////////////////////////////////
    def __init__(self, path_trm):
        self.path_trm  = path_trm
        #
        self.dt_file = 0        # curv stamptime data file path_trm
        self.dt_data = 0        # curv stamptime DATA/TIME from TERM
        self.ar_file = []       # list of strings from path_trm
        self.dt_fut  = []       # list of Class_FUT() from trm
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
        self.ar_file = []
        self.ar_file = buf_str[:]
        #print(self.ar_file)
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
        #term_dt = cntr.term.ar_file[0].split('|')[0]
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
        old_data = self.ar_file[2:]
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
        self.ar_file = []
        self.ar_file = buf_str[:]
        #print(self.ar_file)
        #
        req = self.parse_data_in_file()
        if req[0] != 0:
            err_msg = 'parse_data_in_file / ' + str(ex)
            return [9, err_msg]
        return [0, 'OK']
    #///////////////////////////////////////////////////////////////////
    def parse_data_in_file(self):
        try:
            self.dt_fut = []
            self.account  = Class_ACCOUNT()
            # format of list data_fut:
            #   0   => string of DATA / account.acc_date
            #   1   => [account.acc_bal/acc_prf/acc_go/acc_depo]
            #   2 ... 22  => Class_FUT()
            #print(self.ar_file)

            for i, item in enumerate(list(self.ar_file)):
                list_item = ''.join(item).replace(',','.').split('|')
                if   i == 0:
                    self.account.acc_date  = list_item[0]
                    self.dt_fut.append(self.account.acc_date)
                elif i == 1:
                    self.account.acc_bal = float(list_item[0])
                    self.account.acc_prf  = float(list_item[1])
                    self.account.acc_go      = float(list_item[2])
                    self.account.acc_depo    = float(list_item[3])
                    self.dt_fut.append([self.account.acc_bal,
                                            self.account.acc_prf,
                                            self.account.acc_go,
                                            self.account.acc_depo ])
                else:
                    #print(item)
                    b_fut = Class_FUT()
                    b_fut.sP_code      = list_item[0]
                    b_fut.sRest        = int  (list_item[1])
                    b_fut.sVar_mrg  = float(list_item[2])
                    b_fut.sOpen_prc  = float(list_item[3])
                    b_fut.sLast_prc  = float(list_item[4])
                    b_fut.sAsk         = float(list_item[5])
                    b_fut.sBuy_qty     = int  (list_item[6])
                    b_fut.sBid         = float(list_item[7])
                    b_fut.sSell_qty    = int  (list_item[8])
                    b_fut.sFut_go      = float(list_item[9])
                    b_fut.sOpen_pos    = float(list_item[10])
                    self.dt_fut.append(b_fut)
            #print('cntr.dt_fut => \n', cntr.dt_fut)
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
class Class_term_archiv():
    def __init__(self, path_term_archiv):
        self.path_db = path_term_archiv
        self.table_db = []
        self.conn = ''
        self.cur  = ''
        self.buf_arc  = []
        self.hst_fut  = []  # list of [[ind_sec string] ... ]
        self.arr_fut  = []  # list period 1 minute
        self.hst_pack = []  # list of [[ind_sec string] ... ]
        self.arr_pack = []  # list of [[ind_sec string] ... ]

    def op(self,
            rd_hist_FUT = False,
            wr_hist_FUT = False,
            rd_hist_PACK = False,
            wr_hist_PACK = False
            ):
        r_op_archiv = []
        self.conn = sqlite3.connect(self.path_db)
        try:
            with self.conn:
                r_op_archiv = [0, 'ok']
                self.cur = self.conn.cursor()
                if rd_hist_FUT:
                    self.cur.execute('SELECT * from ' + 'hist_FUT')
                    self.hst_fut = []
                    self.arr_fut  = []
                    self.hst_fut = self.cur.fetchall()    # read table name_tbl
                    #
                    for item in self.hst_fut:
                        arr_item = (item[1].replace(',', '.')).split('|')
                        arr_jtem = []
                        arr_jtem.append(item[0])
                        arr_jtem.append(arr_item[0])
                        for jtem in arr_item[1:-1]:
                            arr_jtem.append(float(jtem))
                        self.arr_fut.append(arr_jtem)

                if wr_hist_FUT:
                    self.cur.executemany("INSERT INTO " + 'hist_FUT' + " VALUES(?, ?)", self.buf_arc)
                    self.conn.commit()

                if rd_hist_PACK:
                    self.cur.execute('SELECT * from ' + 'hist_PACK')
                    self.hst_pack = []
                    self.hst_pack = self.cur.fetchall()    # read table name_tbl
                    self.arr_pack  = []
                    str_pack = self.hst_pack[0][1].split('|')
                    ind_pack = ''
                    for i_mdl in range(len(str_pack) - 1):
                        self.arr_pack.append([])
                        for item in self.hst_pack:
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
                                buf_p.EMAf_r     = float(str_mdl[5])
                                buf_p.cnt_EMAf_r = float(str_mdl[6])

                            else:
                                str_mdl  = str_pack[i_mdl].split(' ')
                                buf_p.pAsk = float(str_mdl[0])
                                buf_p.pBid = float(str_mdl[1])
                                buf_p.EMAf = float(str_mdl[2])
                                buf_p.EMAf_r     = float(str_mdl[3])
                                buf_p.cnt_EMAf_r = float(str_mdl[4])

                            self.arr_pack[i_mdl].append(buf_p)
                        ind_pack += str(i_mdl) + ' '
                        print(ind_pack, end='\r')

                if wr_hist_PACK:
                    ''' rewrite data from table ARCHIV_PACK & PACK_TODAY & DATA ----'''
                    self.cur.execute('DELETE FROM ' + 'hist_PACK')
                    self.cur.executemany('INSERT INTO ' + 'hist_PACK' + ' VALUES' + '(?,?)', self.hst_pack)
                    self.conn.commit()

        except Exception as ex:
            r_op_archiv = [1, 'op_archiv / ' + str(ex)]

        return r_op_archiv
#=======================================================================
class Class_term_today():
    def __init__(self, path_term_today):
        self.path_db = path_term_today
        self.table_db = []
        self.conn = ''
        self.cur  = ''
        # cfg_alarm
        self.nm_alarm    = []  # list NM             of packets
        self.ena_cnt_ema = []  # list cnt_EMAf_r   of packets
        # cfg_pack
        self.nm   = []  # list NM   of packets
        self.koef = []  # list KOEF of packets
        self.nul  = []  # list NUL  of packets
        self.ema  = []  # list EMA  of packets
        # cfg_soft
        self.titul = self.dt_start = ''
        self.dt_start_sec = 0
        self.path_file_DATA = self.path_file_HIST = ''
        #
        self.buf_file = []
        self.dt_fut   = []                  # list of Class_FUT()
        self.account  = Class_ACCOUNT()     # obj Class_ACCOUNT()
        #
        self.buf_file = []
        self.hst_fut  = []  # list of [[ind_sec string] ... ]
        self.hst_1_fut = []  # list period 1 minute
        self.arr_1_fut = []  # list period 1 minute
        self.sec_10_00 = 36000      # seconds from 00:00 to 10:00
        self.sec_14_00 = 50400      # seconds from 00:00 to 14:00
        self.sec_14_05 = 50700      # seconds from 00:00 to 14:05
        self.sec_18_45 = 67500      # seconds from 00:00 to 18:45
        self.sec_19_05 = 68700      # seconds from 00:00 to 19:05
        self.sec_23_45 = 85500      # seconds from 00:00 to 23:45
        #
        self.hst_pack  = []  # list of [[ind_sec string] ... ]
        self.arr_pack  = []  # list of [[ind_sec string] ... ]

    def op(self,
            rd_cfg_SOFT  = False,
            rd_cfg_PACK  = False,
            rd_cfg_ALARM = False,
            wr_cfg_PACK  = False,
            rd_data_FUT  = False,
            wr_data_FUT  = False,
            rd_data_FUT_in_file = False,
            rd_hist_FUT_today   = False,
            wr_hist_FUT_today   = False,
            clr_hist_FUT_today  = False,
            rd_hist_PACK_today  = False,
            wr_hist_PACK_today  = False,
            ):
        r_op_today = []
        self.conn = sqlite3.connect(self.path_db)
        try:
            with self.conn:
                r_op_today = [0, 'ok']
                self.cur = self.conn.cursor()
                if rd_cfg_SOFT:
                    cfg = []
                    self.cur.execute('SELECT * from ' + 'cfg_SOFT')
                    cfg = self.cur.fetchall()    # read table name_tbl
                    #
                    for item in cfg:
                        if item[0] == 'titul'         : self.titul           = item[1]
                        if item[0] == 'path_file_DATA': self.path_file_DATA  = item[1]
                        if item[0] == 'path_file_HIST': self.path_file_HIST  = item[1]
                        if item[0] == 'dt_start'      : self.dt_start        = item[1]
                    frm = '%Y-%m-%d %H:%M:%S'
                    self.dt_start_sec = \
                        int(datetime.strptime(self.dt_start, frm).replace(tzinfo=timezone.utc).timestamp())

                if rd_cfg_PACK:
                    self.nm, self.koef, self.nul, self.ema = [], [], [], []
                    cfg = []
                    self.cur.execute('SELECT * from ' + 'cfg_PACK')
                    cfg = self.cur.fetchall()    # read table name_tbl
                    #
                    for item in cfg:
                        #print(item)
                        self.nm.append(item[0])             # just ex ['pckt0']
                        self.koef.append(item[1].split(','))# just ex ['0:3:SR','9:-20:MX
                        self.nul.append(item[2])            # just ex [0]
                        self.ema.append(item[3].split(':')) # just ex ['1111:15']

                if rd_cfg_ALARM:
                    self.nm_alarm, self.ena_cnt_ema  = [], []
                    cfg = []
                    self.cur.execute('SELECT * from ' + 'cfg_ALARM')
                    cfg = self.cur.fetchall()    # read table name_tbl
                    #
                    for item in cfg:
                        #print(item)
                        self.nm_alarm.append(item[0])       # just ex ['pckt0']
                        self.ena_cnt_ema.append(item[1])    # just ex [True]

                if wr_cfg_PACK:
                    duf_list = []
                    for j, jtem in enumerate(self.nm):
                        buf = (self.nm[j], ','.join(self.koef[j]), self.nul[j], ':'.join(self.ema[j]))
                        #print(buf)
                        duf_list.append(buf)

                    #rq = self.obj_table.rewrite_table('cfg_PACK', duf_list, val = '(?,?,?,?)')
                    self.cur.execute('DELETE FROM ' + 'cfg_PACK')
                    self.cur.executemany('INSERT INTO ' + 'cfg_PACK' + ' VALUES' + '(?,?,?,?)', duf_list)
                    self.conn.commit()

                if wr_data_FUT:
                    duf_list = []
                    for j, jtem in enumerate(self.buf_file):
                        buf = (jtem,)
                        duf_list.append(buf)
                    #rq = self.obj_table.rewrite_table('data_FUT', duf_list, val = '(?)')
                    self.cur.execute('DELETE FROM ' + 'data_FUT')
                    self.cur.executemany('INSERT INTO ' + 'data_FUT' + ' VALUES' + '(?)', duf_list)
                    self.conn.commit()

                if rd_data_FUT:
                    data = []
                    self.cur.execute('SELECT * from ' + 'data_FUT')
                    data = self.cur.fetchall()    # read table name_tbl
                    #
                    self.dt_fut = []

                    for i, item in enumerate(list(data)):
                        list_item = ''.join(item).replace(',','.').split('|')
                        if   i == 0:
                            self.account.acc_date  = list_item[0]
                        elif i == 1:
                            self.account.acc_bal = float(list_item[0])
                            self.account.acc_prf  = float(list_item[1])
                            self.account.acc_go      = float(list_item[2])
                            self.account.acc_depo    = float(list_item[3])
                        else:
                            b_fut = Class_FUT()
                            b_fut.sP_code      = list_item[0]
                            b_fut.sRest        = int  (list_item[1])
                            b_fut.sVar_mrg  = float(list_item[2])
                            b_fut.sOpen_prc  = float(list_item[3])
                            b_fut.sLast_prc  = float(list_item[4])
                            b_fut.sAsk         = float(list_item[5])
                            b_fut.sBuy_qty     = int  (list_item[6])
                            b_fut.sBid         = float(list_item[7])
                            b_fut.sSell_qty    = int  (list_item[8])
                            b_fut.sFut_go      = float(list_item[9])
                            b_fut.sOpen_pos    = float(list_item[10])
                            self.dt_fut.append(b_fut)

                if rd_data_FUT_in_file:
                    self.dt_fut = []
                    for i, item in enumerate(self.buf_file):
                        list_item = ''.join(item).replace(',','.').split('|')
                        if   i == 0:
                            self.account.acc_date  = list_item[0]
                        elif i == 1:
                            self.account.acc_bal = float(list_item[0])
                            self.account.acc_prf  = float(list_item[1])
                            self.account.acc_go      = float(list_item[2])
                            self.account.acc_depo    = float(list_item[3])
                        else:
                            b_fut = Class_FUT()
                            b_fut.sP_code      = list_item[0]
                            b_fut.sRest        = int  (list_item[1])
                            b_fut.sVar_mrg  = float(list_item[2])
                            b_fut.sOpen_prc  = float(list_item[3])
                            b_fut.sLast_prc  = float(list_item[4])
                            b_fut.sAsk         = float(list_item[5])
                            b_fut.sBuy_qty     = int  (list_item[6])
                            b_fut.sBid         = float(list_item[7])
                            b_fut.sSell_qty    = int  (list_item[8])
                            b_fut.sFut_go      = float(list_item[9])
                            b_fut.sOpen_pos    = float(list_item[10])
                            self.dt_fut.append(b_fut)

                if clr_hist_FUT_today:
                    self.hst_fut   = []
                    self.hst_1_fut = []
                    self.arr_1_fut = []
                    self.hst_pack  = []
                    self.arr_pack  = []
                    for item in self.nm:
                        #self.hst_pack.append([])
                        self.arr_pack.append([])
                    #print('clr_hist_FUT_today / len(arr_pack) = ', len(self.arr_pack))
                    self.cur.execute('DELETE FROM ' + 'hist_FUT_today')
                    self.cur.execute('DELETE FROM ' + 'hist_PACK_today')
                    self.conn.commit()

                if rd_hist_FUT_today:
                    self.hst_fut = []
                    self.cur.execute('SELECT * from ' + 'hist_FUT_today')
                    self.hst_fut = self.cur.fetchall()    # read table name_tbl

                    #print('read hst_fut => ', len(self.hst_fut), ' strings')

                    self.hst_1_fut = []
                    if len(self.hst_fut) != 0:
                        self.hst_1_fut.append(self.hst_fut[0])
                        frm = '%d.%m.%Y %H:%M:%S'
                        dtt = datetime.strptime(str(self.hst_fut[0][1].split('|')[0]), frm)
                        buf_60_sec = dtt.minute
                        for item in self.hst_fut:
                            dtt = datetime.strptime(str(item[1].split('|')[0]), frm)
                            if dtt.minute != buf_60_sec:
                                self.hst_1_fut.append(item)
                                buf_60_sec = dtt.minute
                    #print('parse hst_1_fut => ', len(self.hst_1_fut), ' strings')

                    self.arr_1_fut = []
                    for item in self.hst_1_fut:
                        arr_item = (item[1].replace(',', '.')).split('|')
                        arr_jtem = []
                        arr_jtem.append(item[0])
                        arr_jtem.append(arr_item[0])
                        for jtem in arr_item[1:-1]:
                            arr_jtem.append(float(jtem))
                        self.arr_1_fut.append(arr_jtem)

                if wr_hist_FUT_today:
                    self.hst_fut = []
                    self.hst_1_fut = []

                    buf_60_sec = 666
                    frm = '%d.%m.%Y %H:%M:%S'

                    if self.buf_file != '':
                        for i, item in enumerate(self.buf_file):
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
                                    self.hst_fut.append([ind_sec, item])
                                    if buf_60_sec != dtt.minute :
                                        buf_60_sec = dtt.minute
                                        self.hst_1_fut.append([ind_sec, item])

                        self.arr_1_fut = []
                        for item in self.hst_1_fut:
                            arr_item = (item[1].replace(',', '.')).split('|')
                            arr_jtem = []
                            arr_jtem.append(item[0])
                            arr_jtem.append(arr_item[0])
                            for jtem in arr_item[1:-1]:
                                arr_jtem.append(float(jtem))
                            self.arr_1_fut.append(arr_jtem)

                        #print('self.hst_fut[-1] => ', self.hst_fut[-1])

                        #rq = self.obj_table.rewrite_table('hist_FUT_today', self.hst_fut, val = '(?,?)')
                        self.cur.execute('DELETE FROM ' + 'hist_FUT_today')
                        self.cur.executemany('INSERT INTO ' + 'hist_FUT_today' + ' VALUES' + '(?,?)', self.hst_fut)
                        self.conn.commit()

                if rd_hist_PACK_today:
                    self.hst_pack = []
                    self.arr_pack = []
                    self.cur.execute('SELECT * from ' + 'hist_PACK_today')
                    self.hst_pack = self.cur.fetchall()    # read table name_tbl
                    #
                    if len(self.hst_pack) != 0:
                        str_pack = self.hst_pack[0][1].split('|')
                        ind_pack = ''
                        for i_mdl in range(len(str_pack) - 1):
                            self.arr_pack.append([])
                            for item in self.hst_pack:
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
                                    buf_p.EMAf_r     = float(str_mdl[5])
                                    buf_p.cnt_EMAf_r = float(str_mdl[6])

                                else:
                                    str_mdl  = str_pack[i_mdl].split(' ')
                                    buf_p.pAsk = float(str_mdl[0])
                                    buf_p.pBid = float(str_mdl[1])
                                    buf_p.EMAf = float(str_mdl[2])
                                    buf_p.EMAf_r     = float(str_mdl[3])
                                    buf_p.cnt_EMAf_r = float(str_mdl[4])

                                self.arr_pack[i_mdl].append(buf_p)
                            ind_pack += str(i_mdl) + ' '
                            print(ind_pack, end='\r')
                    else:
                        pass
                    if (len(self.arr_pack) == 0):
                        for item in self.nm:
                            self.arr_pack.append([])
                    #print('rd_hist_PACK_today / len(self.arr_pack) = ', len(self.arr_pack))

                if wr_hist_PACK_today:
                    #rq = self.obj_table.rewrite_table('hist_PACK_today', hist_arc, val = '(?,?)')
                    self.cur.execute('DELETE FROM ' + 'hist_PACK_today')
                    self.cur.executemany('INSERT INTO ' + 'hist_PACK_today' + ' VALUES' + '(?,?)', self.hst_pack)
                    self.conn.commit()

        except Exception as ex:
            r_op_today = [1, 'op_today / ' + str(ex)]

        return r_op_today
#=======================================================================
class Class_CONTROLER():
    #///////////////////////////////////////////////////////////////////
    def __init__(self):
        c_dir = os.path.abspath(os.curdir)
        self.log = Class_LOGGER(c_dir + '\\LOG\\term_fut_pack_logger.log')
        path_TERM_TODAY   = c_dir + '\\DB\\term_today.sqlite'
        path_TERM_ARCHIV  = c_dir + '\\DB\\term_archiv.sqlite'

        self.db_TODAY = Class_term_today(path_TERM_TODAY)
        self.db_ARCHIV = Class_term_archiv(path_TERM_ARCHIV)
        rq = self.db_TODAY.op(rd_cfg_SOFT = True)

        if rq[0] != 0:
            err_msg = 'Can not init TBL cfg_SOFT !' + '  '.join(str(e) for e in rq)
            sg.PopupError('Error !', err_msg)
            print(err_msg)
            return [1, err_msg]
        else:
            print('cfg_SOFT = > ', rq)

        self.trm_data = Class_TERM_data(self.db_TODAY.path_file_DATA)
        self.trm_hist = Class_TERM_hist(self.db_TODAY.path_file_HIST)

        self.e_mail     = Class_GMAIL('mobile.ovk', '20066002', 'mobile.ovk@gmail.com')

        #self.arr_fut        = []    # массив котировок фьючей  60 s
        #self.arr_fut_today  = []    # массив котировок фьючей  60 s
        #self.arr_pack       = []    # массив котировок packets 60 s
        #self.arr_pack = []    # массив котировок packets 60 s

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
        b_trm_data_file = False,
        b_trm_hist_file = False,
        b_trm_data_fut = False,
        b_trm_account  = False,
        b_cfg_alarm = False,
        b_cfg_soft  = False,
        b_cfg_pack  = False,
        b_dt_fut    = False,
        b_fut_today = False,
        b_pack_today = False,
        b_fut_arc   = False,
        b_pack_arc  = False
        ):
    if b_clear:
        os.system('cls')  # on windows

    if b_trm_data_file:
        data_in_file = cntr.trm_data.ar_file
        print('.....Class_TERM_data.....')
        print('path_trm   => ', cntr.trm_data.path_trm)
        print('dt_file    => ', cntr.trm_data.dt_file)
        print('dt_data    => ', cntr.trm_data.dt_data)
        print('len(data_in_file) => ', len(data_in_file))
        for i, item in enumerate(data_in_file): print('[',i,'] => ', item)

    if b_trm_data_fut:
        print('.....Class_TERM_data.....')
        print('path_trm   => ', cntr.trm_data.path_trm)
        data_fut = cntr.trm_data.dt_fut
        print('len(data_fut)     => ', len(data_fut))
        if len(data_fut) > 0:
            for i, item in enumerate(data_fut):
                print('[',i,'] => ', item)
            print('. . . . .')
            print('data_fut[-1] =>')
            print('     sP_code     ', data_fut[-1].sP_code)
            print('     sRest       ', data_fut[-1].sRest)
            print('     sVar_mrg ', data_fut[-1].sVar_mrg)
            print('     sOpen_prc ', data_fut[-1].sOpen_prc)
            print('     sLast_prc ', data_fut[-1].sLast_prc)
            print('     sAsk        ', data_fut[-1].sAsk)
            print('     sBuy_qty    ', data_fut[-1].sBuy_qty)
            print('     sBid        ', data_fut[-1].sBid)
            print('     sSell_qty   ', data_fut[-1].sSell_qty)
            print('     sFut_go     ', data_fut[-1].sFut_go)
            print('     sOpen_pos   ', data_fut[-1].sOpen_pos)
            print('. . . . .')
            print('cntr.trm_data.ar_file[-1]  =>  \n', cntr.trm_data.ar_file[-1])

    if b_trm_account:
        print('.....Class_TERM_data.....')
        print('path_trm   => ', cntr.trm_data.path_trm)
        acnt = cntr.trm_data.account
        if acnt != '':
            print('. . . . .')
            print('.....Class_ACCOUNT.....')
            print('acc_date    => ', acnt.acc_date)
            print('acc_bal => ', acnt.acc_bal)
            print('acc_prf  => ', acnt.acc_prf)
            print('acc_go      => ', acnt.acc_go)
            print('acc_depo    => ', acnt.acc_depo)
        else:
            print('account     => _')

    if b_trm_hist_file:
        print('.....Class_TERM_hist.....')
        print('path_hist    => ', cntr.trm_hist.path_hist)
        hist_in_file = cntr.trm_hist.hist_in_file
        print('len(hist_in_file) => ', len(hist_in_file))
        if len(hist_in_file) > 0:
            print('trm_hist.hist_in_file[0] => ',  hist_in_file[0])
            print('trm_hist.hist_in_file[1] => ',  hist_in_file[1].split('|')[0])
            print('trm_hist.hist_in_file[2] => ',  hist_in_file[2].split('|')[0])
            print('. . . . .')
            print('trm_hist.hist_in_file[-1] => ', hist_in_file[-1].split('|')[0])

    if b_cfg_soft:
        s = cntr.db_TODAY
        print('..... cfg_SOFT .....')
        print('path_term_today => ', s.path_db)
        print('titul              => ', s.titul)
        print('path_file_DATA     => ', s.path_file_DATA)
        print('path_file_HIST     => ', s.path_file_HIST)
        print('dt_start           => ', s.dt_start)

    if b_cfg_alarm:
        a = cntr.db_TODAY
        print('..... cfg_ALARM .....')
        print('path_term_today    => ', a.path_db)
        print('len(nm) => ', len(a.nm_alarm))
        if len(a.nm_alarm) > 0:
            for i, item in enumerate(a.nm_alarm):
                print(item, a.ena_cnt_ema[i])

    if b_cfg_pack:
        cfg_pack = cntr.db_TODAY
        print('..... cfg_PACK .....')
        print('path_term_today    => ', cfg_pack.path_db)
        print('len(nm) => ', len(cfg_pack.nm))
        if len(cfg_pack.nm) > 0:
            for i, item in enumerate(cfg_pack.nm):
                print(item, cfg_pack.koef[i], cfg_pack.nul[i], cfg_pack.ema[i] )

    if b_dt_fut:
        print('..... data_FUT .....')
        print('path_term_today    => ', cntr.db_TODAY.path_db)
        dt_acc = cntr.db_TODAY.account
        print('.....Class_ACCOUNT.....')
        print('acc_date    => ', dt_acc.acc_date)
        print('acc_bal => ', dt_acc.acc_bal)
        print('acc_prf  => ', dt_acc.acc_prf)
        print('acc_go      => ', dt_acc.acc_go)
        print('acc_depo    => ', dt_acc.acc_depo)
        print('. . . . .')
        dt_fut = cntr.db_TODAY.dt_fut
        print('len(data_fut)     => ', len(dt_fut))
        if len(dt_fut) > 0:
            for i, item in enumerate(dt_fut):
                print('[',i,'] => ', item)
            print('. . . . .')
            print('dt_fut[-1] =>')
            print('     sP_code     ', dt_fut[-1].sP_code)
            print('     sRest       ', dt_fut[-1].sRest)
            print('     sVar_mrg ', dt_fut[-1].sVar_mrg)
            print('     sOpen_prc ', dt_fut[-1].sOpen_prc)
            print('     sLast_prc ', dt_fut[-1].sLast_prc)
            print('     sAsk        ', dt_fut[-1].sAsk)
            print('     sBuy_qty    ', dt_fut[-1].sBuy_qty)
            print('     sBid        ', dt_fut[-1].sBid)
            print('     sSell_qty   ', dt_fut[-1].sSell_qty)
            print('     sFut_go     ', dt_fut[-1].sFut_go)
            print('     sOpen_pos   ', dt_fut[-1].sOpen_pos)

    if b_fut_today:
        print('..... hist_FUT_today .....')
        print('path_term_today    => ', cntr.db_TODAY.path_db)
        hist = cntr.db_TODAY.hst_fut
        print('len(hst_fut)   => ', len(hist))
        if len(hist) > 4:
            print('hst_fut[0] => ',  hist[0])
            print('hst_fut[1] => ',  hist[1][1].split('|')[0])
            print('hst_fut[2] => ',  hist[2][1].split('|')[0])
            print('. . . . .')
            print('hst_fut[-1] => ', hist[-1][1].split('|')[0])
            print('___________________________')
        hist = cntr.db_TODAY.hst_1_fut
        print('len(hst_1_fut) => ', len(hist))
        if len(hist) > 4:
            print('hst_1_fut[0] => ',  hist[0])
            print('hst_1_fut[1] => ',  hist[1][1].split('|')[0])
            print('hst_1_fut[2] => ',  hist[2][1].split('|')[0])
            print('. . . . .')
            print('hst_1_fut[-1] => ', hist[-1][1].split('|')[0])
            print('___________________________')
        hist = cntr.db_TODAY.arr_1_fut
        print('len(arr_1_fut)  => ', len(hist))
        if len(hist) > 4:
            print('arr_1_fut[0] => ',  hist[0])
            print('arr_1_fut[1] => ',  hist[1][1].split('|')[0])
            print('arr_1_fut[2] => ',  hist[2][1].split('|')[0])
            print('. . . . .')
            print('arr_1_fut[-1] => ', hist[-1][1].split('|')[0])

    if b_pack_today:
        print('..... hist_PACK_today .....')
        print('path_term_today    => ', cntr.db_TODAY.path_db)
        hist = cntr.db_TODAY.hst_pack
        print('len(hst_pack)   => ', len(hist))
        if len(hist) != 0:
            print('len(hst_pack[0])   => ', len(hist[0]))
        hist = cntr.db_TODAY.arr_pack
        print('len(arr_pack)   => ', len(hist))
        if len(hist) != 0:
            print('len(arr_pack[0])   => ', len(hist[0]))

    if b_fut_arc:
        print('..... hist_FUT_archiv .....')
        print('path_term_archiv    => ', cntr.db_ARCHIV.path_db)
        hist = cntr.db_ARCHIV.hst_fut
        print('len(hst_fut_arc)   => ', len(hist))
        if len(hist) > 4:
            print('hst_fut_arc[0] => ',  hist[0])
            print('hst_fut_arc[1] => ',  hist[1][1].split('|')[0])
            print('hst_fut_arc[2] => ',  hist[2][1].split('|')[0])
            print('. . . . .')
            print('hst_fut_arc[-1] => ', hist[-1][1].split('|')[0])
            print('___________________________')
        hist = cntr.db_ARCHIV.arr_fut
        print('len(arr_fut_arc)  => ', len(hist))
        if len(hist) > 4:
            print('arr_fut_today[0] => ',  hist[0])
            print('arr_fut_today[1] => ',  hist[1][1].split('|')[0])
            print('arr_fut_today[2] => ',  hist[2][1].split('|')[0])
            print('. . . . .')
            print('arr_fut_today[-1] => ', hist[-1][1].split('|')[0])

    if b_pack_arc:
        print('..... hist_PACK_archiv .....')
        print('path_term_archiv    => ', cntr.db_ARCHIV.path_db)
        hist = cntr.db_ARCHIV.hst_pack
        print('len(hst_pack_arc)   => ', len(hist))
        if len(hist) > 4:
            print('hst_pack_arc[0] => ',  hist[0])
            print('hst_pack_arc[1] => ',  hist[1][1].split('|')[0])
            print('hst_pack_arc[2] => ',  hist[2][1].split('|')[0])
            print('. . . . .')
            print('hst_pack_arc[-1] => ', hist[-1][1].split('|')[0])
            print('___________________________')
        hist = cntr.db_ARCHIV.arr_pack[0]
        print('PACK_0 :     ')
        print('len(arr_pack_arc[0])  => ', len(hist))
        if len(hist) > 4:
            print('arr_pack_arc[0][-1].ind => ' ,  hist[-1].ind)
            print('arr_pack_arc[0][-1].dt  => ' ,  hist[-1].dt)
            print('arr_pack_arc[0][-1].tm  => ' ,  hist[-1].tm)
            print('arr_pack_arc[0][-1].pAsk => ',  hist[-1].pAsk)
            print('arr_pack_arc[0][-1].pBid => ',  hist[-1].pBid)
            print('arr_pack_arc[0][-1].EMAf => ',  hist[-1].EMAf)
            print('arr_pack_arc[0][-1].EMAf_r     => ',  hist[-1].EMAf_r)
            print('arr_pack_arc[0][-1].cnt_EMAf_r => ',  hist[-1].cnt_EMAf_r)
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
        b_hist_pack_t= False,
        b_clr_hist_fut_t = False,
        #b_hist_fut_a = False,
        t_hist_fut_a  = False,
        t_hist_pack_a = False,
        b_send_mail   = False,
        t_calc_PACK_arc   = False,
        t_calc_PACK_today = False,

        ):
    if b_trm_data:
        c = cntr.trm_data
        c.dt_file, c.dt_data, c.ar_file = 0, 0, []
        rq = c.rd_term_service()
        if rq[0] != 0 : _err_(cntr, 'trm_data.rd_term_service ', rq)
        else:           dbg_prn(cntr,  b_trm_data_file = True)

    elif b_trm_hist:
        rq = cntr.trm_hist.rd_hist()
        if rq[0] != 0:  _err_(cntr, 'trm_hist.rd_term_service ', rq)
        else:           dbg_prn(cntr, b_clear  = False, b_trm_hist_file = True)

    elif b_cfg_alarm:
        rq = cntr.db_TODAY.op(rd_cfg_ALARM = True)
        if rq[0] != 0 : _err_(cntr, 'cfg_alarm ', rq)
        else:           dbg_prn(cntr,  b_cfg_alarm = True)

    elif b_cfg_pack:
        rq = cntr.db_TODAY.op(rd_cfg_PACK = True)
        if rq[0] != 0 : _err_(cntr, 'cfg_pack ', rq)
        else:           dbg_prn(cntr,  b_cfg_pack = True)

    elif b_cfg_soft:
        rq = cntr.db_TODAY.op(rd_cfg_SOFT = True)
        if rq[0] != 0 : _err_(cntr, 'cfg_soft ', rq)
        else:           dbg_prn(cntr,  b_cfg_soft = True)

    elif b_data_fut:
        rq = cntr.db_TODAY.op(rd_data_FUT = True)
        if rq[0] != 0 : _err_(cntr, 'dt_fut ', rq)
        else:           dbg_prn(cntr,  b_dt_fut = True)

    elif b_hist_fut_t:
        rq = cntr.db_TODAY.op(rd_hist_FUT_today = True)
        if rq[0] != 0 : _err_(cntr, 'h_fut_today ', rq)
        else:           dbg_prn(cntr,  b_fut_today = True)

    elif b_hist_pack_t:
        rq = cntr.db_TODAY.op(rd_hist_PACK_today = True)
        if rq[0] != 0 : _err_(cntr, 'h_pack_today ', rq)
        else:           dbg_prn(cntr,  b_pack_today = True)

    elif b_clr_hist_fut_t:
        rq = cntr.db_TODAY.op(clr_hist_FUT_today = True)
        if rq[0] != 0 : _err_(cntr, 'h_fut_today ', rq)
        else:           dbg_prn(cntr,  b_fut_today = True)

    elif t_hist_fut_a:
        rq = cntr.db_ARCHIV.op(rd_hist_FUT = True)
        if rq[0] != 0 : _err_(cntr, 'rd_hist_FUT ', rq)
        else:           dbg_prn(cntr,  b_fut_arc = True)

    elif t_hist_pack_a:
        rq = cntr.db_ARCHIV.op(rd_hist_PACK = True)
        if rq[0] != 0 : _err_(cntr, 'rd_hist_PACK ', rq)
        else:           dbg_prn(cntr,  b_pack_arc = True)

    elif b_send_mail:
        print( 'Start TEST e-mail (it is about 20 s) => ' + datetime.today().strftime('%H:%M:%S') )
        rq = cntr.e_mail.send_email('test  subj','test  body')
        if rq[0] != 0 :
            _err_(cntr, 'send_email ', rq)
        else:
            print('TEST sent e-mail OK . . . . .')
        print( 'Finish TEST e-mail => ' +  datetime.today().strftime('%H:%M:%S') )

    elif t_calc_PACK_arc:
        print('calc PACK arc')
        rq = cntr.db_ARCHIV.op(rd_hist_FUT = True)
        if rq[0] != 0 :   _err_(cntr, 'debug_calc_PACK_arc ', rq)
        else:             arr = cntr.db_ARCHIV.hst_fut
        for i_pack, item in enumerate(cntr.db_TODAY.nm):
            calc_hist_PACK(cntr, i_pack)
            sg.OneLineProgressMeter('calc_hist_PACK',
                                    i_pack+1,
                                    len(cntr.db_TODAY.nm),
                                    'key', orientation='h')
        rq = cntr.db_TODAY.op(wr_cfg_PACK = True)
        print('writing hist_PACK . . . . . .')
        wr_hist_PACK(cntr)
        print('ok. . . . . . . . . . . . . .')

    elif t_calc_PACK_today:
        print('calc PACK today')
        rq = cntr.db_TODAY.op(rd_hist_FUT_today = True)
        if rq[0] != 0 :
            _err_(cntr, 'debug_calc_PACK_today ', rq)
        else:
            arr   = cntr.db_TODAY.hst_fut
            arr1   = cntr.db_TODAY.hst_1_fut
        if len(arr) > 0:
            ind_pack = 'debug_calc_PACK_today => '
            for i_pack, item in enumerate(cntr.db_TODAY.nm):
                calc_hist_PACK_today(cntr, i_pack)
                ind_pack += str(i_pack) + ' '
                print(ind_pack, end='\r')
            wr_hist_PACK_today(cntr)
            print('ok . . .' + 60*' ')

    else:
        print('TEST NOTHING')
#=======================================================================
def calc_hist_PACK(cntr, i_pack):
    cntr.db_ARCHIV.arr_pack[i_pack] = []
    arr_PACK = cntr.db_ARCHIV.arr_pack[i_pack]
    arr_HIST = cntr.db_ARCHIV.arr_fut   # archiv of FUT 60 sec
    #print('ema =  ', cntr.cfg_pack.ema[i_pack])
    k_EMA     = int(cntr.db_TODAY.ema[i_pack][0])
    k_EMA_rnd = int(cntr.db_TODAY.ema[i_pack][1])
    koef_EMA = round(2/(1+k_EMA),5)
    ind, kf = [], []
    #print('koef =  ', cntr.cfg_pack.koef[i_pack])
    for elem in cntr.db_TODAY.koef[i_pack]:
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
            null_prc = int((ask_p + bid_p)/2)
            cntr.db_TODAY.nul[i_pack] = null_prc
            buf_c_pack.pAsk, buf_c_pack.pBid = 0, 0
            buf_c_pack.EMAf, buf_c_pack.EMAf_r = 0, 0
            buf_c_pack.cnt_EMAf_r = 0

        else:
            ask_p = int(ask_p - null_prc)
            bid_p = int(bid_p - null_prc)
            buf_c_pack.pAsk = ask_p
            buf_c_pack.pBid = bid_p
            ask_bid_AVR = int((ask_p + bid_p)/2)

            prev_EMAf = arr_PACK[idx-1].EMAf
            buf_c_pack.EMAf = round(prev_EMAf + (ask_bid_AVR - prev_EMAf) * koef_EMA, 1)
            buf_c_pack.EMAf_r = k_EMA_rnd * math.ceil(buf_c_pack.EMAf / k_EMA_rnd )

            prev_EMAf_r = arr_PACK[idx-1].EMAf_r
            i_cnt = arr_PACK[idx-1].cnt_EMAf_r
            if prev_EMAf_r > buf_c_pack.EMAf_r:
                buf_c_pack.cnt_EMAf_r = 0 if i_cnt > 0 else i_cnt-1
            elif prev_EMAf_r < buf_c_pack.EMAf_r:
                buf_c_pack.cnt_EMAf_r = 0 if i_cnt < 0 else i_cnt+1
            else:
                buf_c_pack.cnt_EMAf_r = i_cnt

        arr_PACK.append(buf_c_pack)
#=======================================================================
def calc_hist_PACK_today(cntr, i_pack):
    cntr.db_TODAY.arr_pack[i_pack] = []
    arr_PACK = cntr.db_TODAY.arr_pack[i_pack]
    arr_PACK_arc = cntr.db_ARCHIV.arr_pack[i_pack]
    arr_HIST = cntr.db_TODAY.arr_1_fut   # today of FUT 60 sec
    k_EMA     = int(cntr.db_TODAY.ema[i_pack][0])
    k_EMA_rnd = int(cntr.db_TODAY.ema[i_pack][1])
    koef_EMA = round(2/(1+k_EMA),5)
    ind, kf = [], []
    #print('koef =  ', cntr.cfg_pack.koef[i_pack])
    for elem in cntr.db_TODAY.koef[i_pack]:
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
            null_prc = cntr.db_TODAY.nul[i_pack]
            ask_p = int(ask_p - null_prc)
            bid_p = int(bid_p - null_prc)
            buf_c_pack.pAsk = ask_p
            buf_c_pack.pBid = bid_p
            ask_bid_AVR = int((ask_p + bid_p)/2)

            prev_EMAf = arr_PACK_arc[idx-1].EMAf
            buf_c_pack.EMAf = round(prev_EMAf + (ask_bid_AVR - prev_EMAf) * koef_EMA, 1)
            buf_c_pack.EMAf_r = k_EMA_rnd * math.ceil(buf_c_pack.EMAf / k_EMA_rnd )

            prev_EMAf_r = arr_PACK_arc[idx-1].EMAf_r
            i_cnt = arr_PACK_arc[idx-1].cnt_EMAf_r
            if prev_EMAf_r > buf_c_pack.EMAf_r:
                buf_c_pack.cnt_EMAf_r = 0 if i_cnt > 0 else i_cnt-1
            elif prev_EMAf_r < buf_c_pack.EMAf_r:
                buf_c_pack.cnt_EMAf_r = 0 if i_cnt < 0 else i_cnt+1
            else:
                buf_c_pack.cnt_EMAf_r = i_cnt

        else:
            ask_p = int(ask_p - null_prc)
            bid_p = int(bid_p - null_prc)
            buf_c_pack.pAsk = ask_p
            buf_c_pack.pBid = bid_p
            ask_bid_AVR = int((ask_p + bid_p)/2)

            prev_EMAf = arr_PACK[idx-1].EMAf
            buf_c_pack.EMAf = round(prev_EMAf + (ask_bid_AVR - prev_EMAf) * koef_EMA, 1)
            buf_c_pack.EMAf_r = k_EMA_rnd * math.ceil(buf_c_pack.EMAf / k_EMA_rnd )

            prev_EMAf_r = arr_PACK[idx-1].EMAf_r
            i_cnt = arr_PACK[idx-1].cnt_EMAf_r
            if prev_EMAf_r > buf_c_pack.EMAf_r:
                buf_c_pack.cnt_EMAf_r = 0 if i_cnt > 0 else i_cnt-1
            elif prev_EMAf_r < buf_c_pack.EMAf_r:
                buf_c_pack.cnt_EMAf_r = 0 if i_cnt < 0 else i_cnt+1
            else:
                buf_c_pack.cnt_EMAf_r = i_cnt

        arr_PACK.append(buf_c_pack)
#=======================================================================
def TODAY_copy_ARCHIV(cntr):
    os.system('cls')  # on windows
    print('Copy fut TODAY in ARCHIV .  .  .  .  .')
    hist = cntr.db_TODAY.hst_1_fut
    print('len(hst_1_fut) => ', len(hist))
    if len(hist) > 4:
        print('hst_1_fut[0] => ',  hist[0][1].split('|')[0])
        print('. . .')
        print('hst_1_fut[-1] => ', hist[-1][1].split('|')[0])
    print('___________________________________')
    if len(hist) > 10:
        last_1_fut_today = hist[-1][1].split('|')[0].split(' ')[0]

        hist = cntr.db_ARCHIV.hst_fut
        print('len(hst_fut_arc)   => ', len(hist))
        if len(hist) > 4:
            print('hst_fut_arc[0] => ',  hist[0][1].split('|')[0])
            print('. . .')
            print('hst_fut_arc[-1] => ', hist[-1][1].split('|')[0])
        print('___________________________________')
        last_fut_archiv = hist[-1][1].split('|')[0].split(' ')[0]
        if last_1_fut_today != last_fut_archiv:
            cntr.db_ARCHIV.buf_arc = []
            cntr.db_ARCHIV.buf_arc = cntr.db_TODAY.hst_1_fut[:520]
            rq = cntr.db_ARCHIV.op(wr_hist_FUT = True)
            if rq[0] != 0: _err_(cntr, 'TODAY_copy_ARCHIV ', rq)
            print('ok . . .')
        else:
            print('\n' + str (last_1_fut_today) + ' have copy already. Check it \n')
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
    dbg_srv(cntr,  b_hist_fut_t = True) #read & print
    #
    arr_hist = cntr.db_TODAY.hst_fut
    if len(arr_hist) > 10:
        term_dt = arr_hist[-1][1].split('|')[0]
        dtt = datetime.strptime(str(term_dt), "%d.%m.%Y %H:%M:%S")
        #
        str_month = str(dtt.month) if dtt.month > 9 else '0' + str(dtt.month)
        str_day   = str(dtt.day)   if dtt.day   > 9 else '0' + str(dtt.day)
        str_dt    = str(dtt.year) + '-' + str_month + '-' + str_day
        # write in file HISTORY  10 sec ------------------------------------
        hist_out = []           # convert TUPLE in LIST & delete last '|'
        for item in arr_hist: hist_out.append(''.join(list(item[1])[0:-1]))
        path_file = str_dt + '_hist_' + cntr.db_TODAY.titul + '.txt'
        wr_file(path_file, hist_out, 'Hist export for ', cntr)
        #
        arr_hist = cntr.db_TODAY.hst_1_fut
        term_dt = arr_hist[-1][1].split('|')[0]
        dtt = datetime.strptime(str(term_dt), "%d.%m.%Y %H:%M:%S")
        # write in file HISTORY  60 sec ------------------------------------
        hist_out = []           # convert TUPLE in LIST & delete last '|'
        for item in arr_hist:
            dt_buf = datetime.strptime(str(item[1].split('|')[0]), "%d.%m.%Y %H:%M:%S")
            if dt_buf.hour < 19:
                hist_out.append(str(int(item[0])) + ';' + ''.join(list(item[1])[0:-1]))
        path_file = cntr.db_TODAY.titul + '_' + str_dt + '_hist_FUT' + '.csv'
        wr_file(path_file, hist_out, 'Archiv for ', cntr)
        #
        print('.  .  .  .  .')
        cnt_tm = lambda x: datetime.strptime(str(x.split(';')[1].split('|')[0]), "%d.%m.%Y %H:%M:%S")
        nmb_ms = lambda h, m: 60 * h + m
        dtm    = lambda t: t.split(';')[1].split('|')[0]
        print('start  => ', dtm(hist_out[0]))
        for i, item in enumerate(hist_out[1:]):
            c = cnt_tm(hist_out[i+1])
            p = cnt_tm(hist_out[i])
            if nmb_ms(c.hour, c.minute) - nmb_ms(p.hour, p.minute) != 1:
                print('delay  => ', dtm(hist_out[i]), ' ... ', dtm(hist_out[i+1]))
        print('finish => ', dtm(hist_out[-1]))
        print('lench  => ', len(hist_out))
        print('.  .  .  .  .')
#=======================================================================
def prepair_hist_PACK(cntr, b_today = False):
    name_list =[]
    if b_today :
        arr_hist_pack = cntr.db_TODAY.arr_pack
        #print()
        #print('len(arr_hist_pack) = ',len(arr_hist_pack ))
        #print('len(arr_hist_pack[0]) = ',len(arr_hist_pack[0]))
    else:
        arr_hist_pack = cntr.db_ARCHIV.arr_pack

    if len(arr_hist_pack) > 0:
        for i_hist, item_hist in enumerate(arr_hist_pack[0]):
            buf_dt = item_hist.dt + ' ' + item_hist.tm + ' '
            buf_s = ''
            for i_mdl, item_mdl in enumerate(arr_hist_pack):
                buf = arr_hist_pack[i_mdl][i_hist]
                buf_s += str(buf.pAsk) + ' ' + str(buf.pBid)     + ' '
                buf_s += str(buf.EMAf) + ' ' + str(buf.EMAf_r) + ' ' + str(buf.cnt_EMAf_r) + '|'
                #buf_s += str(buf.AMA)  + ' ' + str(buf.AMA_rnd)  + ' ' + str(buf.cnt_AMA_rnd) + '|'
            name_list.append((item_hist.ind, buf_dt + buf_s.replace('.', ',')))

    return name_list
#=======================================================================
def wr_hist_PACK(cntr):
    cntr.db_ARCHIV.hst_pack = []
    cntr.db_ARCHIV.hst_pack = prepair_hist_PACK(cntr)
    rq = cntr.db_ARCHIV.op(wr_hist_PACK = True)

    if rq[0] != 0:
        _err_(cntr, 'hist_PACK ', rq, PopUp = False)
        return [1, 'wr_hist_PACK']

    return [0, 'OK']
#=======================================================================
def wr_hist_PACK_today(cntr):
    name_list = []
    name_list = prepair_hist_PACK(cntr, b_today = True)

    cntr.db_TODAY.hst_pack = []
    cntr.db_TODAY.hst_pack = name_list[:]
    rq = cntr.db_TODAY.op(wr_hist_PACK_today = True)
    if rq[0] != 0:
        _err_(cntr, 'hist_PACK_today ', rq, PopUp = True)
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
    print(event)
    #-------------------------------------------------------------------
    if event == 'srv data TERM'       : dbg_srv(cntr, b_trm_data   = True)
    #-------------------------------------------------------------------
    if event == 'srv hist TERM'       : dbg_srv(cntr, b_trm_hist   = True)
    #-------------------------------------------------------------------
    if event == 'srv config ALARM'    : dbg_srv(cntr, b_cfg_alarm  = True)
    #-------------------------------------------------------------------
    if event == 'srv config PACK'     : dbg_srv(cntr, b_cfg_pack   = True)
    #-------------------------------------------------------------------
    if event == 'srv config SOFT'     : dbg_srv(cntr, b_cfg_soft   = True)
    #-------------------------------------------------------------------
    if event == 'srv data FUT'        : dbg_srv(cntr, b_data_fut   = True)
    #-------------------------------------------------------------------
    if event == 'srv hist FUT today'  : dbg_srv(cntr, b_hist_fut_t = True)
    #-------------------------------------------------------------------
    if event == 'srv hist PACK today' : dbg_srv(cntr, b_hist_pack_t= True)
    #-------------------------------------------------------------------
    if event == 'clear hist FUT today': dbg_srv(cntr, b_clr_hist_fut_t = True)
    #-------------------------------------------------------------------
    #if event == 'srv hist FUT arch'  : dbg_srv(cntr, b_hist_fut_a = True)
    #-------------------------------------------------------------------
    if event == 'test hist FUT arch'   : dbg_srv(cntr, t_hist_fut_a  = True)
    #-------------------------------------------------------------------
    if event == 'test hist PACK arch'  : dbg_srv(cntr, t_hist_pack_a = True)
    #-------------------------------------------------------------------
    if event == 'srv send E-MAIL'    : dbg_srv(cntr, b_send_mail     = True)
    #-------------------------------------------------------------------
    if event == 'prn TERM data_in_file'  : dbg_prn(cntr, b_trm_data_file = True)
    #---------------------------------------------------------------
    if event == 'prn TERM data_fut'      : dbg_prn(cntr, b_trm_data_fut     = True)
    #---------------------------------------------------------------
    if event == 'prn TERM account'       : dbg_prn(cntr, b_trm_account      = True)
    #---------------------------------------------------------------
    if event == 'prn TERM hist_in_file'  : dbg_prn(cntr, b_trm_hist_file = True)
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
    if event == 'prn FUT hist_PACK_today': dbg_prn(cntr, b_pack_today        = True)

    #---------------------------------------------------------------
    if event == 'prn FUT hist_FUT_arch'  : dbg_prn(cntr, b_fut_arc          = True)
    #---------------------------------------------------------------
    if event == 'calc PACK arc'   : dbg_srv(cntr, t_calc_PACK_arc    = True)
    #---------------------------------------------------------------
    if event == 'calc PACK today' : dbg_srv(cntr, t_calc_PACK_today  = True)
    #---------------------------------------------------------------
    if event == 'Convert tbl TODAY' : convert_tbl_TODAY(cntr)
    #---------------------------------------------------------------
    if event == 'TODAY to ARCHIV'   : TODAY_copy_ARCHIV(cntr)

#=======================================================================
def main():
    # init
    cntr = Class_CONTROLER()
    while True:  # init tables -----------------------------------------
        rq = cntr.trm_data.rd_term()
        if rq[0] != 0:  _err_(cntr, 'INIT data_in_file ', rq)
        else:           print('trm_data  = > ', rq)
        #---------------------------------------------------------------
        rq = cntr.trm_hist.rd_hist()
        if rq[0] != 0:  _err_(cntr, 'INIT hist_in_file ', rq)
        else:           print('trm_hist  = > ', rq)
        #---------------------------------------------------------------
        rq = cntr.db_TODAY.op(
                                    rd_cfg_ALARM = True,
                                    rd_cfg_PACK  = True,
                                    rd_data_FUT  = True,
                                    rd_hist_FUT_today = True,
                                    rd_hist_PACK_today = True,
                                    )
        if rq[0] != 0 : _err_(cntr, 'INIT cfg_data_hist TODAY', rq)
        else:
            print('INIT cfg_data_hist TODAY = > ', rq)
            if len(cntr.db_TODAY.nm) == 0:
                _err_(cntr, 'cfg_pack.nm = 0  ', [' ', 'It can not be EMPTY !'] )
                break
            if (len(cntr.db_TODAY.arr_pack) == 0):
                for item in cntr.db_TODAY.nm:
                    cntr.db_TODAY.arr_pack.append([])
            for item in cntr.db_TODAY.nm:
                cntr.db_ARCHIV.arr_pack.append([])
            #print('init tables / len arr_pack  = ', len(cntr.db_TODAY.arr_pack))
            #print('init tables / len arr_pack_arc = ', len(cntr.db_ARCHIV.arr_pack))
        #---------------------------------------------------------------
        rq = cntr.db_ARCHIV.op(rd_hist_FUT = True)
        if rq[0] != 0 : _err_(cntr, 'INIT hst_fut_arc ', rq)
        else:           print('hist_FUT archiv = > ', rq)
        print('calculating hist_PACK . . . .')
        for i_pack, item in enumerate(cntr.db_TODAY.nm):
            calc_hist_PACK(cntr, i_pack)
            sg.OneLineProgressMeter('calc_hist_PACK',
                                    i_pack+1,
                                    len(cntr.db_TODAY.nm),
                                    'key', orientation='h')
        rq = cntr.db_TODAY.op(wr_cfg_PACK = True) #rewrite NUL price
        print('writing hist_PACK . . . . . .')
        wr_hist_PACK(cntr)
        break
    while True:  # init MENU -------------------------------------------
        menu_def = [
            ['Mode',
                ['auto', 'manual', ],
                ],
            ['Service',
                [
                 'srv data TERM',    'srv hist TERM',        '---',
                 'srv config ALARM', 'srv config PACK',      'srv config SOFT',
                 'srv data FUT',     'srv hist FUT today',   'srv hist PACK today', '---',
                 'clear hist FUT today',   '---',
                 'test hist FUT arch', 'test hist PACK arch','---',
                 'calc PACK arc',    'calc PACK today',      '---',
                 'srv send E-MAIL',
                 ],
                ],
            ['Print',
                ['prn TERM data_in_file', 'prn TERM hist_in_file', 'prn TERM data_fut', 'prn TERM account', '---',
                 'prn FUT cfg_ALARM',     'prn FUT cfg_SOFT',       'prn FUT cfg_PACK',
                 'prn FUT data_FUT',      'prn FUT hist_FUT_today', 'prn FUT hist_PACK_today', '---',
                 'prn FUT hist_FUT_arch'],
                ],
            ['Hist FUT',
                ['Convert tbl TODAY', 'TODAY to ARCHIV'],
                ],
            ['Help', 'About...'],
            ['Exit', 'Exit']
            ]

        def_txt = []
        frm = '{: <15}  => {: ^15}\n'
        def_txt.append(frm.format('TODAY' , '\\DB\\term_today.sqlite'))
        def_txt.append(frm.format('ARCHV' , '\\DB\\term_archiv.sqlite'))

        # Display data
        layout = [
                    [sg.Menu(menu_def, tearoff=False, key='menu_def')],
                    [sg.Multiline( default_text=''.join(def_txt),
                        size=(50, 5), key='txt_data', autoscroll=False, focus=False),],
                    [sg.T('',size=(60,2), font='Helvetica 8', key='txt_status'), sg.Quit(auto_size_button=True)],
                 ]
        sg.SetOptions(element_padding=(0,0))
        window = sg.Window(cntr.db_TODAY.titul, grab_anywhere=True).Layout(layout).Finalize()
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

    while True:  # MAIN cycle ------------------------------------------
        stroki = []
        event, values = window.Read(timeout=tm_out )
        #---------------------------------------------------------------
        event_menu(event, cntr)
        #---------------------------------------------------------------
        if event is None or event == 'Quit' or event == 'Exit': break
        #---------------------------------------------------------------
        if event == 'auto'   :    tm_out, mode = 1550,   'auto'
        #---------------------------------------------------------------
        if event == 'manual' :    tm_out, mode = 240000, 'manual'
        #---------------------------------------------------------------
        if event == '__TIMEOUT__':
            rq = read_term(cntr)
            #stroki.append('Profit = ' + str(cntr.trm_data.account.acc_prf))
            if rq[0] != 0:
                dbg_prn(cntr)
                tm_out = 1550
                stroki.append(rq[1])
            else:
                tm_out = 7550
                print('Time new DATA:  ' + cntr.trm_data.ar_file[0].split('|')[0])
                stroki.append('Time DATA:  ' + cntr.trm_data.ar_file[0].split('|')[0])
                stroki.append('Have got new data/hist')
                tmr = cntr.trm_data.account.acc_date
                dt_minute = datetime.strptime(str(tmr.split('|')[0]), frm).minute
                if cntr.tm_wrt_new_data == dt_minute:
                    cntr.db_TODAY.buf_file = cntr.trm_data.ar_file
                    req = cntr.db_TODAY.op(wr_data_FUT = True)
                    if req[0] != 0: _err_(cntr, 'rewrite_tbl => ', req, PopUp = False)
                    else:
                        rq = cntr.db_TODAY.op(rd_data_FUT_in_file = True)
                        if rq[0] != 0 : _err_(cntr, 'read_data_in_file => ', rq, PopUp = False)
                        else:           print(60*' ', end='\r')
                else:
                    cntr.tm_wrt_new_data = dt_minute
                    cntr.db_TODAY.buf_file = cntr.trm_hist.hist_in_file
                    req = cntr.db_TODAY.op(wr_hist_FUT_today = True)
                    if req[0] != 0: _err_(cntr, 'h_fut_today.rewrite_tbl => ', req, PopUp = False)
                    else:
                        ind_pack = 'calc_hist_PACK_today => '
                        for i_pack, item in enumerate(cntr.db_TODAY.nm):
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
