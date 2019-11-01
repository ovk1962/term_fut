#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  db_graph.py
#
#=======================================================================
import os, sys, math, time, sqlite3, logging
from datetime import datetime, timezone
#import matplotlib.pyplot as plt
#import matplotlib.ticker as ticker
from ipdb import set_trace as bp    # to set breakpoints just -> bp()
if sys.version_info[0] >= 3:
    import PySimpleGUI as sg
else:
    import PySimpleGUI27 as sg
#=======================================================================
menu_def = [
['Mode',        ['auto','manual','auto_TEST', ], ],
['READ  today', ['rd_term_FUT',  'rd_term_HST',   '---',
                'rd_cfg_PACK',   'rd_data_FUT',   '---',
                'rd_hst_FUT_t',  'rd_hst_PCK_t',  '---',
                'rd_hst_FUT',    'rd_hst_PCK'],],
['CALC',        ['ASK_BID', 'EMA_f', '---', 'ASK_BID_t', 'EMA_f_t', '---', 'cnt'] ,],
['PRINT today', ['prn_cfg_SOFT', 'prn_cfg_PACK', 'prn_cfg_ALARM',   '---',
                'prn_ar_FILE',   'prn_hist_in_FILE', '---',
                'prn_data_FUT',  '---',
                'prn_hst_FUT_t', 'prn_arr_FUT_t', 'prn_arr_PK_t',   '---',
                'prn_arr_FUT',   'prn_arr_PK'],
                ],
['Plot', 'win2_active'],
['Exit', 'Exit']
]

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
class Class_str_PCK():
    pAsk, pBid, EMAf, EMAf_r, cnt_EMAf_r = range(5)
    def __init__(self):
        self.ind_s, self.dt, self.arr  = 0, '', []
    def __retr__(self):
        return 'ind_s = {}, dt = {}{} arr={}'.format(self.ind_s, self.dt, '\n', str(self.arr))
    def __str__(self):
        return 'ind_s = {}, dt = {}{} arr={}'.format(self.ind_s, self.dt, '\n', str(self.arr))
#=======================================================================
class Class_str_FUT():
    fAsk, fBid = range(2)
    def __init__(self):
        self.ind_s, self.dt, self.arr  = 0, '', []
    def __retr__(self):
        return 'ind_s = {}, dt = {}{} arr={}'.format(self.ind_s, self.dt, '\n', str(self.arr))
    def __str__(self):
        return 'ind_s = {}, dt = {}{} arr={}'.format(self.ind_s, self.dt, '\n', str(self.arr))
#=======================================================================
class Class_ACCOUNT():
    bal, prf, go, dep = range(4)
    def __init__(self):
        self.ss = '        bal,      prf,      go,       dep'
        self.dt, self.arr  = '', []
    def __retr__(self):
        return 'dt = {}\n{}\narr={}\n'.format(self.dt, self.ss, str(self.arr))
    def __str__(self):
        return 'dt = {}\n{}\narr={}\n'.format(self.dt, self.ss, str(self.arr))
#=======================================================================
class Class_FUT():
    sP_code, sRest, sVar_mrg, sOpen_prc, sLast_prc, sAsk, sBuy_qty, sBid, sSell_qty, sFut_go, sOpen_pos  = range(11)
    def __init__(self):
        self.sP_code, self.arr = '', []
    def __retr__(self):
        return  '{} {}'.format(self.sP_code,  str([int(k) for k in self.arr]))
    def __str__(self):
        return  '{} {}'.format(self.sP_code,  str([int(k) for k in self.arr]))
#=======================================================================
class Class_term_TODAY():
    def __init__(self, path_db_today):
        self.path_db = path_db_today
        self.table_db = []
        self.conn = ''
        self.cur  = ''
        # cfg_alarm
        self.nm_alarm    = []  # list NM           of packets
        self.ena_cnt_ema = []  # list cnt_EMAf_r   of packets
        # cfg_pack
        self.nm   = []  # list NM   of packets
        self.koef = []  # list KOEF of packets
        self.nul  = []  # list NUL  of packets
        self.ema  = []  # list EMA  of packets
        # cfg_soft
        self.titul          = ''    # term ALFA
        self.path_file_DATA = ''    # D:\\str_log_ad_A7.txt
        self.path_file_HIST = ''    # D:\\hist_log_ad_A7.txt
        self.dt_start_sec   = 0     # 2017-01-01 00:00:00
        #
        self.dt_file = 0        # curv stamptime data file path_file_DATA
        self.dt_data = 0        # curv stamptime DATA/TIME from TERM
        self.ar_file = []       # list of strings from path_file_DATA
        self.hist_in_file = []  # list of strings from path_file_HIST
        #
        self.buf_file    = []               # data FUT from TXT file
        self.dt_fut_file = []               # list of Class_FUT()
        self.ac_fut_file = Class_ACCOUNT()  # obj Class_ACCOUNT()
        self.delay_tm = 8       # min period to get data for DB (10 sec)
        #
        self.dt_fut   = []               # list of Class_FUT()
        self.account  = Class_ACCOUNT()  # obj Class_ACCOUNT()
        #

        self.hst_fut_t = []  # list of [[ind_sec string] ... ]
        self.arr_fut_t = []  # list period 1 minute
        self.arr_pk_t  = []  # list of [[ind_sec string] ... ]
        # hist_FUT
        self.arr_fut = []  # list period 1 minute
        # hist_PACK
        self.buf_arc = []
        self.arr_pk  = []  # list of obj [Class_STR_PACK ... ]
        #
        self.sec_10_00 = 36000      # seconds from 00:00 to 10:00
        self.sec_14_00 = 50400      # seconds from 00:00 to 14:00
        self.sec_14_05 = 50700      # seconds from 00:00 to 14:05
        self.sec_18_45 = 67500      # seconds from 00:00 to 18:45
        self.sec_19_05 = 68700      # seconds from 00:00 to 19:05
        self.sec_23_45 = 85500      # seconds from 00:00 to 23:45
        #
        #self.path_trm  = path_trm # path_file_DATA
        #

    def prn_arr(self, name_arr, arr):
        print('len(' + name_arr + ')   => ' + str(len(arr)) + '\n' )
        if len(arr) > 4:
            for i in [0,1,2]: print(arr[i],'\n')
            print('+++++++++++++++++++++++++\n')
            for i in [-2,-1]: print(arr[i],'\n')
        else:
            for item in arr: print(item, '\n')

    def prn(self,
            p_cfg_PACK  = False,
            p_cfg_SOFT  = False,
            p_cfg_ALARM = False,
            p_ar_FILE   = False,
            p_hist_in_file = False,
            p_data_FUT  = False,
            p_hst_FUT_t  = False,
            p_arr_FUT_t  = False,
            p_arr_PK_t  = False,
            p_arr_fut   = False,
            p_arr_pk    = False
            ):
        s = ''
        try:
            if p_cfg_PACK:
                if len(self.nm) > 0:
                    frm = '{: ^5}{: ^15}{}{}{}'
                    print(frm.format('nm','nul','ema[]','        ','koef[]'))
                    for i, item in enumerate(self.nm):
                        print(frm.format(self.nm[i], str(self.nul[i]), self.ema[i], '   ', self.koef[i]))

            if p_cfg_SOFT:
                frm = '{: <18}{: <55}'
                print(frm.format('titul',          self.titul))
                print(frm.format('dt_start',       self.dt_start))
                print(frm.format('dt_start_sec',   str(self.dt_start_sec)))
                print(frm.format('path_file_DATA', self.path_file_DATA))
                print(frm.format('path_file_HIST', self.path_file_HIST))
                print(frm.format('path_db_today',  self.path_db))

            if p_cfg_ALARM:
                if len(self.nm) > 0:
                    frm = '{: ^8}{: ^5}'
                    print(frm.format('nm','ena_cnt_ema'))
                    for i, item in enumerate(self.nm_alarm):
                        print(frm.format(self.nm_alarm[i], str(self.ena_cnt_ema[i])))

            if p_ar_FILE:
                for i in self.ar_file:   print(i)

            if p_data_FUT:
                print(self.account)
                for i in self.dt_fut:   print(i)

            if p_hist_in_file:
                self.prn_arr('hist_in_file', self.hist_in_file)

            if p_hst_FUT_t:
                self.prn_arr('hst_fut_t', self.hst_fut_t)

            if p_arr_FUT_t:
                self.prn_arr('arr_fut_t', self.arr_fut_t)

            if p_arr_PK_t:
                self.prn_arr('arr_pk_t', self.arr_pk_t)

            if p_arr_fut:
                self.prn_arr('arr_fut', self.arr_fut)

            if p_arr_pk:
                self.prn_arr('arr_pk', self.arr_pk)

        except Exception as ex:
            r_prn = [1, 'op_archiv / ' + str(ex)]

        return [0, s]

    def op(self,
            rd_cfg_SOFT  = False,
            rd_cfg_PACK  = False,
            rd_cfg_ALARM = False,

            rd_term_FUT  = False,
            rd_term_HST  = False,

            wr_data_FUT  = False,
            rd_data_FUT  = False,

            rd_hst_FUT   = False,
            clc_ASK_BID   = False,
            clc_EMA       = False,
            wr_hst_PCK  = False,
            rd_hst_PCK  = False,

            wr_hist_FUT_t = False,
            rd_hst_FUT_t  = False,
            clc_ASK_BID_t = False,
            clc_EMA_t     = False,
            wr_hst_PCK_t  = False,
            rd_hst_PCK_t  = False,

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
                    print('packets => ', len(cfg))
                    #
                    for item in cfg:
                        self.nm.append(item[0])          # ['pckt0']
                        arr_k    = item[1].split(',')
                        arr_koef = []
                        for item_k in arr_k:             # '0:2:SR' => [0, 32, 'SR']
                            buf_k = [int(f) if f.replace('-','').isdigit() else f for f in item_k.split(':')]
                            arr_koef.append(buf_k)
                        self.koef.append(arr_koef)       #  [[0, 2, 'SR'],[9, -20, 'MX'], ...
                        self.nul.append(int(item[2]))    #  [0]
                        self.ema.append([int(e) for e in item[3].split(':')]) # [1111, 15]

                if rd_cfg_ALARM:
                    self.nm_alarm, self.ena_cnt_ema  = [], []
                    cfg = []
                    self.cur.execute('SELECT * from ' + 'cfg_ALARM')
                    cfg = self.cur.fetchall()    # read table name_tbl
                    #
                    for item in cfg:
                        self.nm_alarm.append(item[0])       # just ex ['pckt0']
                        self.ena_cnt_ema.append(item[1])    # just ex [True]

                if rd_term_FUT:
                    #--- check file cntr.file_path_DATA ----------------------------
                    if not os.path.isfile(self.path_file_DATA):
                        err_msg = 'can not find file => ' + self.path_file_DATA
                        #cntr.log.wr_log_error(err_msg)
                        return [1, err_msg]
                    buf_stat = os.stat(self.path_file_DATA)
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
                        self.dt_file = int(buf_stat.st_mtime)
                    #--- read TERM file --------------------------------------------
                    buf_str = []
                    with open(self.path_file_DATA,"r") as fh:
                        buf_str = fh.read().splitlines()
                    #
                    #--- check size of list/file -----------------------------------
                    print('len(buf_str) = ', len(buf_str))
                    if len(buf_str) == 0:
                        err_msg = ' the size buf_str is NULL'
                        #cntr.log.wr_log_error(err_msg)
                        return [4, err_msg]
                    #
                    self.ar_file = []
                    self.ar_file = buf_str[:]
                    #
                    #--- update table 'data_FUT' -----------------------------------
                    self.cur.execute('DELETE FROM ' + 'data_FUT')
                    self.cur.executemany('INSERT INTO ' + 'data_FUT' + ' VALUES' + '(?)', ((j,) for j in buf_str))
                    self.conn.commit()

                if rd_term_HST:
                    print('start rd_term_HST!  => ', str(len(self.hist_in_file)))
                    #--- check file cntr.file_path_DATA ----------------------------
                    if not os.path.isfile(self.path_file_HIST):
                        err_msg = 'can not find file => ' + self.path_file_HIST
                        #cntr.log.wr_log_error(err_msg)
                        return [1, err_msg]
                    buf_stat = os.stat(self.path_file_HIST)
                    #
                    #--- check size of file ----------------------------------------
                    if buf_stat.st_size == 0:
                        err_msg = 'size HIST file is NULL'
                        return [2, err_msg]
                    #
                    #--- read HIST file --------------------------------------------
                    buf_str = []
                    with open(self.path_file_HIST,"r") as fh:
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
                        if (
                            (cur_time > self.sec_10_00  and # from 10:00 to 14:00
                            cur_time < self.sec_14_00) or
                            (cur_time > self.sec_14_05  and # from 14:05 to 18:45
                            cur_time < self.sec_18_45) or
                            (cur_time > self.sec_19_05  and # from 19:05 to 23:45
                            cur_time < self.sec_23_45)):
                                self.hist_in_file.append(item)
                    print('finish rd_term_HST!  => ', str(len(self.hist_in_file)))

                if wr_data_FUT:
                    print('start wr_data_FUT! ')
                    self.dt_fut = []
                    acc = self.account
                    for i, item in enumerate(list(self.ar_file)):
                        lst = ''.join(item).replace(',','.').split('|')
                        del lst[-1]
                        if   i == 0:
                            acc.dt  = lst[0]
                        elif i == 1:
                            acc.arr = [float(j) for j in lst]
                        else:
                            b_fut = Class_FUT()
                            b_fut.sP_code = lst[0]
                            b_fut.arr     = [float(k) for k in lst[1:]]
                            self.dt_fut.append(b_fut)
                    self.cur.execute('DELETE FROM ' + 'data_FUT')
                    self.cur.executemany('INSERT INTO ' + 'data_FUT' + ' VALUES' + '(?)', ((jtem,) for jtem in self.ar_file))
                    self.conn.commit()
                    print('finish wr_data_FUT!  => ', str(len(self.ar_file)))

                if rd_data_FUT:
                    print('start rd_data_FUT! ')
                    data = []
                    self.cur.execute('SELECT * from ' + 'data_FUT')
                    data = self.cur.fetchall()    # read table name_tbl
                    #
                    self.dt_fut = []
                    acc = self.account
                    for i, item in enumerate(list(data)):
                        lst = ''.join(item).replace(',','.').split('|')
                        del lst[-1]
                        if   i == 0:
                            acc.dt  = lst[0]
                        elif i == 1:
                            acc.arr = [float(j) for j in lst]
                        else:
                            b_fut = Class_FUT()
                            b_fut.sP_code = lst[0]
                            b_fut.arr     = [float(k) for k in lst[1:]]
                            self.dt_fut.append(b_fut)
                    print('finish rd_data_FUT! => ', str(len(self.dt_fut)))

                if rd_hst_FUT:
                    print('start rd_hst_FUT! ')
                    self.cur.execute('SELECT * from ' + 'hist_FUT')
                    arr_buf = []    #self.hst_fut = []
                    arr_buf = self.cur.fetchall()    # read table name_tbl
                    print('len(hist_FUT) = ', len(arr_buf))
                    self.arr_fut  = []
                    for cnt, i_str in enumerate(arr_buf):
                        #arr_item = (i_str[1].replace(',', '.')).split('|')
                        s = Class_str_FUT()
                        s.ind_s = i_str[0]
                        s.dt    = i_str[1].split('|')[0].split(' ')
                        arr_buf = i_str[1].replace(',', '.').split('|')[1:-1]
                        fAsk, fBid = range(2)
                        for item in (zip(arr_buf[::2], arr_buf[1::2])):
                            s.arr.append([float(item[fAsk]), float(item[fBid])])
                        self.arr_fut.append(s)
                        if len(self.arr_fut) % 1000 == 0:  print(len(self.arr_fut), end='\r')
                    print('finish rd_hst_FUT! => ', str(len(self.arr_fut)))

                if clc_ASK_BID:
                    print('start clc_ASK_BID! ')
                    ''' init  table ARCHIV_PACK  --------------------'''
                    self.arr_pk  = []  # Class_str_PCK()
                    fAsk, fBid = range(2)
                    for idx, item in enumerate(self.arr_fut): # change STRINGs
                        if idx % 1000 == 0:  print(idx, end='\r')
                        arr_bb = Class_str_PCK()
                        arr_bb.ind_s, arr_bb.dt  = item.ind_s, item.dt
                        for p, ptem in enumerate(self.nm):    # change PACKETs
                            ask_p, bid_p, arr_pp = 0, 0, [0, 0, 0, 0, 0]
                            for jdx, jtem in enumerate(self.koef[p]): # calc PACK
                                i_koef, k_koef = jtem[0], jtem[1]
                                if k_koef > 0 :
                                    ask_p +=  k_koef * item.arr[i_koef][fAsk]
                                    bid_p +=  k_koef * item.arr[i_koef][fBid]
                                if k_koef < 0 :
                                    ask_p +=  k_koef * item.arr[i_koef][fBid]
                                    bid_p +=  k_koef * item.arr[i_koef][fAsk]
                            if idx == 0:
                                self.nul[p] = int((ask_p + bid_p)/2)
                            else:
                                arr_pp = [int(ask_p - self.nul[p]), int(bid_p - self.nul[p]), 0, 0, 0]
                            arr_bb.arr.append(arr_pp)
                        self.arr_pk.append(arr_bb)

                    # update self.nul[i_pack] in table cfg_PACK ----
                    duf_list = []
                    for j, jtem in enumerate(self.nm):
                        arr_koef = ''
                        for ktem in self.koef[j]:
                            str_koef = ':'.join([str(f) for f in ktem])
                            arr_koef += str_koef + ','
                        buf = (self.nm[j], arr_koef[:-1], str(self.nul[j]), ':'.join([str(f) for f in self.ema[j]]))
                        duf_list.append(buf)
                    self.cur.execute('DELETE FROM ' + 'cfg_PACK')
                    self.cur.executemany('INSERT INTO ' + 'cfg_PACK' + ' VALUES' + '(?,?,?,?)', duf_list)
                    self.conn.commit()
                    print('finish clc_ASK_BID! => ', str(len(self.arr_pk)))

                if clc_EMA:
                    print('start clc_EMA! ')
                    koef_EMA, k_EMA_rnd = [], []
                    for kdx, ktem in enumerate(self.nm):
                        koef_EMA.append(round(2/(1+int(self.ema[kdx][0])),5))
                        k_EMA_rnd.append(int(self.ema[kdx][1]))
                    for idx, item in enumerate(self.arr_pk):
                        if idx % 1000 == 0:  print(idx, end='\r')
                        for pdx, ptem in enumerate(item.arr):
                            pAsk, pBid, EMAf, EMAf_r, cnt_EMAf_r = range(5)
                            if idx > 0:
                                cr = self.arr_pk[idx].arr[pdx]
                                pr = self.arr_pk[idx-1].arr[pdx]
                                cr[EMAf]  = round(pr[EMAf] + (int((ptem[pAsk] + ptem[pBid])/2) - pr[EMAf]) * koef_EMA[pdx], 1)
                                cr[EMAf_r]= k_EMA_rnd[pdx] * math.ceil(cr[EMAf] / k_EMA_rnd[pdx] )
                                if pr[EMAf_r] > cr[EMAf_r]:
                                    cr[cnt_EMAf_r] = 0 if pr[cnt_EMAf_r] > 0 else pr[cnt_EMAf_r]-1
                                elif pr[EMAf_r] < cr[EMAf_r]:
                                    cr[cnt_EMAf_r] = 0 if pr[cnt_EMAf_r] < 0 else pr[cnt_EMAf_r]+1
                                else:
                                    cr[cnt_EMAf_r] = pr[cnt_EMAf_r]
                    print('finish clc_EMA! => ', str(len(self.arr_pk)))

                if wr_hst_PCK:
                    print('start wr_hst_PCK! ')
                    buf_list =[]
                    pAsk, pBid, EMAf, EMAf_r, cnt_EMAf_r = range(5)
                    if len(self.arr_pk) > 0:
                        print('len(self.arr_pk) = ', len(self.arr_pk))
                        for i_hist, item_hist in enumerate(self.arr_pk):
                            if i_hist % 1000 == 0:  print(str(i_hist), end='\r')
                            #bp()
                            buf_dt = item_hist.dt[0] + ' ' + item_hist.dt[1] + ' '
                            buf_s = ''
                            for i_pack, item_pack in enumerate(item_hist.arr):
                                buf_s += str(item_pack[pAsk]) + ' ' + str(item_pack[pBid])   + ' '
                                buf_s += str(item_pack[EMAf]) + ' ' + str(item_pack[EMAf_r]) + ' '
                                buf_s += str(item_pack[cnt_EMAf_r]) + '|'
                            buf_list.append((item_hist.ind_s, buf_dt + buf_s.replace('.', ',')))

                    ''' rewrite data from table ARCHIV_PACK & PACK_TODAY & DATA ----'''
                    self.cur.execute('DELETE FROM ' + 'hist_PACK')
                    self.cur.executemany('INSERT INTO ' + 'hist_PACK' + ' VALUES' + '(?,?)', buf_list)
                    self.conn.commit()
                    print('finish wr_hst_PCK! => ', str(len(buf_list)))

                if rd_hst_PCK:
                    print('start rd_hst_PCK! ')
                    self.cur.execute('SELECT * from ' + 'hist_PACK')
                    arr_buf = []
                    arr_buf = self.cur.fetchall()    # read table name_tbl
                    print('len(hist_PACK) = ', len(arr_buf))
                    self.arr_pk  = []
                    for cnt, i_str in enumerate(arr_buf):
                        buf = i_str[1].replace(',','.').split('|')
                        del buf[-1]
                        s = Class_str_PCK()
                        s.ind_s = i_str[0]
                        for cn, item in enumerate(buf):
                            if cn == 0 : s.dt = item.split(' ')[0:2]
                            ind_0 = 0 if cn != 0 else 2
                            s.arr.append([int(float(f)) for f in item.split(' ')[ind_0:]])
                        self.arr_pk.append(s)
                        if len(self.arr_pk) % 1000 == 0:  print(len(self.arr_pk), end='\r')
                    print('finish rd_hst_PCK! => ', str(len(self.arr_pk)))

                if wr_hist_FUT_t:
                    print('start wr_hist_FUT_t! ')
                    #--- update table 'hist_FUT_today' ------------------------------
                    buf_list =[]
                    pAsk, pBid = range(2)
                    if len(self.hist_in_file) > 0:
                        for it in self.hist_in_file:
                            dtt = datetime.strptime(it.split('|')[0], '%d.%m.%Y %H:%M:%S')
                            ind_sec  = int(dtt.replace(tzinfo=timezone.utc).timestamp())
                            buf_list.append([ind_sec, it])

                    ''' rewrite data from table hist_FUT_today ------'''
                    self.cur.execute('DELETE FROM ' + 'hist_FUT_today')
                    self.cur.executemany('INSERT INTO ' + 'hist_FUT_today' + ' VALUES' + '(?,?)', buf_list)
                    self.conn.commit()
                    print('finish wr_hist_FUT_t!  => ', str(len(buf_list)))

                if rd_hst_FUT_t:
                    print('start rd_hst_FUT_t! ')
                    self.cur.execute('SELECT * from ' + 'hist_FUT_today')
                    self.hst_fut_t = []
                    self.hst_fut_t = self.cur.fetchall()    # read table name_tbl
                    print('len(hist_FUT_today) = ', len(self.hst_fut_t))
                    self.arr_fut_t  = []
                    for cnt, i_str in enumerate(self.hst_fut_t):
                        mn_pr, mn_cr = '', ''
                        if cnt == 0 :
                            mn_pr, mn_cr = '', '00'
                        else:
                            mn_pr = self.hst_fut_t[cnt-1][1][14:16]
                            mn_cr = self.hst_fut_t[cnt-0][1][14:16]
                        if mn_pr != mn_cr:
                            s = Class_str_FUT()
                            s.ind_s = i_str[0]
                            s.dt    = i_str[1].split('|')[0].split(' ')
                            arr_buf = i_str[1].replace(',', '.').split('|')[1:-1]
                            fAsk, fBid = range(2)
                            for item in (zip(arr_buf[::2], arr_buf[1::2])):
                                s.arr.append([float(item[fAsk]), float(item[fBid])])
                            self.arr_fut_t.append(s)
                        if len(self.arr_fut_t) % 100 == 0:  print(len(self.arr_fut_t), end='\r')
                    print('finish rd_hst_FUT_t => !', str(len(self.arr_fut_t)))

                if clc_ASK_BID_t:
                    print('start clc_ASK_BID_t! ')
                    ''' init  table ARCHIV_PACK  --------------------'''
                    self.arr_pk_t  = []  # Class_str_PCK()
                    fAsk, fBid = range(2)
                    for idx, item in enumerate(self.arr_fut_t): # change STRINGs
                        if idx % 100 == 0:  print(idx, end='\r')
                        arr_bb = Class_str_PCK()
                        arr_bb.ind_s, arr_bb.dt  = item.ind_s, item.dt
                        for p, ptem in enumerate(self.nm):    # change PACKETs
                            ask_p, bid_p, arr_pp = 0, 0, [0, 0, 0, 0, 0]
                            for jdx, jtem in enumerate(self.koef[p]): # calc PACK
                                i_koef, k_koef = jtem[0], jtem[1]
                                if k_koef > 0 :
                                    ask_p +=  k_koef * item.arr[i_koef][fAsk]
                                    bid_p +=  k_koef * item.arr[i_koef][fBid]
                                if k_koef < 0 :
                                    ask_p +=  k_koef * item.arr[i_koef][fBid]
                                    bid_p +=  k_koef * item.arr[i_koef][fAsk]
                            arr_pp = [int(ask_p - self.nul[p]), int(bid_p - self.nul[p]), 0, 0, 0]
                            arr_bb.arr.append(arr_pp)
                        self.arr_pk_t.append(arr_bb)
                    print('finish clc_ASK_BID_t => !', str(len(self.arr_pk_t)))

                if clc_EMA_t:
                    print('start clc_EMA_t! ')
                    koef_EMA, k_EMA_rnd = [], []
                    for kdx, ktem in enumerate(self.nm):
                        koef_EMA.append(round(2/(1+int(self.ema[kdx][0])),5))
                        k_EMA_rnd.append(int(self.ema[kdx][1]))
                    for idx, item in enumerate(self.arr_pk_t):
                        if idx % 1000 == 0:  print(idx, end='\r')
                        for pdx, ptem in enumerate(item.arr):
                            pAsk, pBid, EMAf, EMAf_r, cnt_EMAf_r = range(5)
                            if idx == 0:
                                cr = self.arr_pk_t[idx].arr[pdx]
                                pr = self.arr_pk[idx-1].arr[pdx]
                                cr[EMAf]  = round(pr[EMAf] + (int((ptem[pAsk] + ptem[pBid])/2) - pr[EMAf]) * koef_EMA[pdx], 1)
                                cr[EMAf_r]= k_EMA_rnd[pdx] * math.ceil(cr[EMAf] / k_EMA_rnd[pdx] )
                                if pr[EMAf_r] > cr[EMAf_r]:
                                    cr[cnt_EMAf_r] = 0 if pr[cnt_EMAf_r] > 0 else pr[cnt_EMAf_r]-1
                                elif pr[EMAf_r] < cr[EMAf_r]:
                                    cr[cnt_EMAf_r] = 0 if pr[cnt_EMAf_r] < 0 else pr[cnt_EMAf_r]+1
                                else:
                                    cr[cnt_EMAf_r] = pr[cnt_EMAf_r]
                            else:
                                cr = self.arr_pk_t[idx].arr[pdx]
                                pr = self.arr_pk_t[idx-1].arr[pdx]
                                cr[EMAf]  = round(pr[EMAf] + (int((ptem[pAsk] + ptem[pBid])/2) - pr[EMAf]) * koef_EMA[pdx], 1)
                                cr[EMAf_r]= k_EMA_rnd[pdx] * math.ceil(cr[EMAf] / k_EMA_rnd[pdx] )
                                if pr[EMAf_r] > cr[EMAf_r]:
                                    cr[cnt_EMAf_r] = 0 if pr[cnt_EMAf_r] > 0 else pr[cnt_EMAf_r]-1
                                elif pr[EMAf_r] < cr[EMAf_r]:
                                    cr[cnt_EMAf_r] = 0 if pr[cnt_EMAf_r] < 0 else pr[cnt_EMAf_r]+1
                                else:
                                    cr[cnt_EMAf_r] = pr[cnt_EMAf_r]
                    print('finish clc_EMA_t => !', str(len(self.arr_pk_t)))

                if wr_hst_PCK_t:
                    print('start wr_hst_PCK_t! ')
                    buf_list =[]
                    pAsk, pBid, EMAf, EMAf_r, cnt_EMAf_r = range(5)
                    if len(self.arr_pk_t) > 0:
                        print('len(self.arr_pk_t) = ', len(self.arr_pk_t))
                        for i_hist, item_hist in enumerate(self.arr_pk_t):
                            if i_hist % 1000 == 0:  print(str(i_hist), end='\r')
                            #bp()
                            buf_dt = item_hist.dt[0] + ' ' + item_hist.dt[1] + ' '
                            buf_s = ''
                            for i_pack, item_pack in enumerate(item_hist.arr):
                                buf_s += str(item_pack[pAsk]) + ' ' + str(item_pack[pBid])   + ' '
                                buf_s += str(item_pack[EMAf]) + ' ' + str(item_pack[EMAf_r]) + ' '
                                buf_s += str(item_pack[cnt_EMAf_r]) + '|'
                            buf_list.append((item_hist.ind_s, buf_dt + buf_s.replace('.', ',')))

                    ''' rewrite data from table ARCHIV_PACK & PACK_TODAY & DATA ----'''
                    self.cur.execute('DELETE FROM ' + 'hist_PACK_today')
                    self.cur.executemany('INSERT INTO ' + 'hist_PACK_today' + ' VALUES' + '(?,?)', buf_list)
                    self.conn.commit()
                    print('finish wr_hst_PCK_t => !', str(len(buf_list)))

                if rd_hst_PCK_t:
                    print('start rd_hst_PCK_t! ')
                    arr_buf = []
                    self.cur.execute('SELECT * from ' + 'hist_PACK_today')
                    arr_buf = self.cur.fetchall()    # read table name_tbl
                    print('len(hist_PACK_today) = ', len(arr_buf))
                    if len(arr_buf) != 0:
                        self.arr_pk_t  = []
                        for cnt, i_str in enumerate(arr_buf):
                            buf = i_str[1].replace(',','.').split('|')
                            del buf[-1]
                            s = Class_str_PCK()
                            s.ind_s = i_str[0]
                            for cn, item in enumerate(buf):
                                if cn == 0 : s.dt = item.split(' ')[0:2]
                                ind_0 = 0 if cn != 0 else 2
                                s.arr.append([int(float(f)) for f in item.split(' ')[ind_0:]])
                            self.arr_pk_t.append(s)
                            if len(self.arr_pk_t) % 100 == 0:  print(len(self.arr_pk_t), end='\r')
                            else:
                                pass
                            if (len(self.arr_pk_t) == 0):
                                for item in self.nm:
                                    self.arr_pk_t.append([])
                    print('finish rd_hst_PCK_t! => ', str(len(self.arr_pk_t)))


        except Exception as ex:
            r_op_today = [1, 'op_today / ' + str(ex)]

        return r_op_today
#=======================================================================
def event_menu(event, db_TODAY):
    rq = [0,event]
    #-------------------------------------------------------------------
    os.system('cls')  # on windows
    if event == 'prn_cfg_SOFT'  :
        print('prn_cfg_SOFT ...')
        rq = db_TODAY.prn(p_cfg_SOFT = True)
    #-------------------------------------------------------------------
    if event == 'prn_cfg_PACK'  :
        print('prn_cfg_PACK ...')
        rq = db_TODAY.prn(p_cfg_PACK = True)
    #-------------------------------------------------------------------
    if event == 'prn_cfg_ALARM'  :
        print('prn_cfg_ALARM ...')
        rq = db_TODAY.prn(p_cfg_ALARM = True)
    #-------------------------------------------------------------------
    if event == 'prn_ar_FILE'  :
        print('prn_ar_FILE ...')
        rq = db_TODAY.prn(p_ar_FILE = True)
    #-------------------------------------------------------------------
    if event == 'prn_hist_in_FILE'  :
        print('prn_hist_in_FILE ...')
        rq = db_TODAY.prn(p_hist_in_file = True)
    #-------------------------------------------------------------------
    if event == 'prn_data_FUT'  :
        print('prn_data_FUT ...')
        rq = db_TODAY.prn(p_data_FUT = True)
    #-------------------------------------------------------------------
    if event == 'prn_hst_FUT_t'  :
        print('prn_hst_FUT_t ...')
        rq = db_TODAY.prn(p_hst_FUT_t = True)
    #-------------------------------------------------------------------
    if event == 'prn_arr_FUT_t'  :
        print('prn_arr_FUT_t ...')
        rq = db_TODAY.prn(p_arr_FUT_t = True)
    #-------------------------------------------------------------------
    if event == 'prn_arr_FUT'  :
        print('prn_arr_FUT ...')
        rq = db_TODAY.prn(p_arr_fut = True)
    #-------------------------------------------------------------------
    if event == 'prn_arr_PK_t'  :
        print('prn_arr_PK_t ...')
        rq = db_TODAY.prn(p_arr_PK_t = True)
    #-------------------------------------------------------------------
    if event == 'prn_arr_PK'  :
        print('prn_arr_PK ...')
        rq = db_TODAY.prn(p_arr_pk = True)
    #-------------------------------------------------------------------
    if event == 'rd_term_FUT'  :
        print('rd_term_FUT ...')
        rq = db_TODAY.op(rd_term_FUT = True)
    #-------------------------------------------------------------------
    if event == 'rd_term_HST'  :
        print('rd_term_HST ...')
        rq = db_TODAY.op(rd_term_HST = True)
    #-------------------------------------------------------------------
    if event == 'rd_cfg_PACK'  :
        print('rd_cfg_PACK ...')
        rq = db_TODAY.op(rd_cfg_PACK = True)
    #-------------------------------------------------------------------
    if event == 'rd_data_FUT'  :
        print('rd_data_FUT ...')
        rq = db_TODAY.op(rd_data_FUT = True)
    #-------------------------------------------------------------------
    if event == 'rd_hst_FUT_t'  :
        print('rd_hst_FUT_t ...')
        rq = db_TODAY.op(rd_hst_FUT_t = True)
    #-------------------------------------------------------------------
    if event == 'rd_hst_PCK_t'  :
        print('rd_hst_PCK_t ...')
        rq = db_TODAY.op(rd_hst_PCK_t = True)
    #-------------------------------------------------------------------
    if event == 'rd_hst_FUT'  :
        print('rd_hst_FUT ...')
        rq = db_TODAY.op(rd_hst_FUT = True)
    #-------------------------------------------------------------------
    if event == 'rd_hst_PCK'  :
        print('rd_hst_PCK ...')
        rq = db_TODAY.op(rd_hst_PCK = True)
    #-------------------------------------------------------------------
    if event == 'ASK_BID'  :
        print('clc_ASK_BID ...')
        rq = db_TODAY.op(clc_ASK_BID = True)
    #-------------------------------------------------------------------
    if event == 'ASK_BID_t'  :
        print('clc_ASK_BID_t ...')
        rq = db_TODAY.op(clc_ASK_BID_t = True)
    #-------------------------------------------------------------------
    if event == 'EMA_f'  :
        print('clc_EMA_f ...')
        rq = db_TODAY.op(clc_EMA = True)
    #-------------------------------------------------------------------
    if event == 'EMA_f_t'  :
        print('clc_EMA_f_t ...')
        rq = db_TODAY.op(clc_EMA_t = True)
    #-------------------------------------------------------------------
    if event == 'wr_hst_PCK'  :
        print('wr_hst_PCK ...')
        rq = db_TODAY.op(wr_hst_PCK = True)
    #-------------------------------------------------------------------
    if event == 'wr_hist_FUT_t'  :
        print('wr_hist_FUT_t ...')
        rq = db_TODAY.op(wr_hist_FUT_t = True)
    #-------------------------------------------------------------------
    if event == 'wr_hst_PCK_t'  :
        print('wr_hst_PCK_t ...')
        rq = db_TODAY.op(wr_hst_PCK_t = True)
    #-------------------------------------------------------------------
    if event == 'wr_data_FUT'  :
        print('wr_data_FUT ...')
        rq = db_TODAY.op(wr_data_FUT = True)
    #-------------------------------------------------------------------
    if event == 'auto_TEST'  :
        print('auto_TEST ...')
        rq = db_TODAY.op(
                        rd_cfg_SOFT  = True,
                        rd_cfg_PACK  = True,
                        rd_cfg_ALARM = True,

                        rd_term_FUT  = True,
                        wr_data_FUT  = True,
                        rd_data_FUT  = True,

                        rd_hst_FUT  = True,
                        clc_ASK_BID = True,
                        clc_EMA     = True,
                        wr_hst_PCK  = True,
                        rd_hst_PCK  = True,

                        rd_term_HST   = True,
                        wr_hist_FUT_t = True,
                        rd_hst_FUT_t  = True,
                        clc_ASK_BID_t = True,
                        clc_EMA_t     = True,
                        wr_hst_PCK_t  = True,
                        rd_hst_PCK_t  = True,


                        )
    #-------------------------------------------------------------------

    print('rq = ', rq)
#=======================================================================


#=======================================================================
def main():
    while True:  # init db_TODAY ---------------------------------------
        c_dir    = os.path.abspath(os.curdir)
        db_TODAY = Class_term_TODAY(c_dir + '\\DB\\term_today.sqlite')
        lg_FILE  = Class_LOGGER(    c_dir + '\\LOG\\d_logger.log')

        rq = db_TODAY.op(
                        rd_cfg_SOFT  = True,
                        rd_cfg_PACK  = True,
                        rd_cfg_ALARM = True,
                        rd_data_FUT  = True,
                        rd_hst_FUT_t = True,
                        rd_hst_PCK_t = True,
                        rd_hst_FUT   = True,
                        rd_hst_PCK   = True,
                        )
        if rq[0] != 0 : #prn_rq('INIT rd_cfg_SOFT TODAY', rq)
            print('INIT = > ', rq[1])
        else:
            print('INIT cfg_term_data_hist TODAY = > ', rq)
            if len(db_TODAY.nm) == 0:
                print('cfg_pack.nm = 0   It can not be EMPTY !')
                break
        break

    while True:  # init MENU -------------------------------------------
        def_txt, frm = [], '{: <10}  => {: ^15}\n'
        def_txt.append(frm.format('term_today' , '\\DB\\term_today.sqlite'))
        #def_txt.append(frm.format('ARCHV' , '\\DB\\term_archiv.sqlite'))
        def_txt.append(frm.format('hst_FUT_t' , str(len(db_TODAY.arr_fut_t))))
        def_txt.append(frm.format('hst_PK_t' , str(len(db_TODAY.arr_pk_t))))

        # Display data
        layout = [
                    [sg.Menu(menu_def, tearoff=False, key='menu_def')],
                    [sg.Multiline( default_text=''.join(def_txt),
                        size=(50, 5), key='txt_data', autoscroll=False, focus=False),],
                    #[sg.T('',size=(40,1))],
                    [sg.T('',size=(50,2), font='Helvetica 8', key='txt_status')],
                 ]
        sg.SetOptions(element_padding=(0,0))
        window = sg.Window('Test db_today', grab_anywhere=True).Layout(layout).Finalize()
        window.FindElement('txt_data').Update(''.join(def_txt))
        break

    tm_out, mode, frm = 360000, 'manual', '%d.%m.%Y %H:%M:%S'
    stts  = time.strftime(frm, time.localtime()) + '\n' + 'event = manual'
    window.FindElement('txt_status').Update(stts)
    win2_active = False
    while True:  # MAIN cycle ------------------------------------------
        stroki = []
        event, values = window.Read(timeout = tm_out )
        #---------------------------------------------------------------
        event_menu(event, db_TODAY)
        #---------------------------------------------------------------
        if event is None or event == 'Quit' or event == 'Exit': break
        #---------------------------------------------------------------
        if event == 'auto'   :    tm_out, mode =  14550,   'auto'
        #---------------------------------------------------------------
        if event == 'manual' :    tm_out, mode = 360000, 'manual'
        #---------------------------------------------------------------
        if event == '__TIMEOUT__':
            rq = db_TODAY.op(
                    rd_term_FUT = True,     # 1. rd file FUT
                    rd_term_HST = True,     # 2. rd file HIST
                    wr_data_FUT = True,     # 3. wr table data_FUT
                    wr_hist_FUT_t = True,   # 4. wr table hist_FUT_today
                    rd_hst_FUT_t  = True,   # 5. rd table hist_FUT_today
                    clc_ASK_BID_t = True,   # 6. calc ASK/BID for hist_PACK_today
                    clc_EMA_t     = True,   # 7. calc EMA for hist_PACK_today
                    wr_hst_PCK_t  = True,   # 8. wr table hist_PACK_today
                    )
            print('__TIMEOUT__ = > ', rq )
            #bp()
        #-------------------------------------------------------------------
        if event == 'win2_active' and not win2_active:
            win2_active = True
            window.Hide()

            X_bottom_left = 0
            Y_bottom_left = 0
            X_top_right   = 1040
            Y_top_right   = 500
            nom_pckt  = 0
            layout2 = [
                        [sg.Graph(canvas_size=(X_top_right, Y_top_right),
                            graph_bottom_left=(X_bottom_left, Y_bottom_left),
                            graph_top_right  =(X_top_right,   Y_top_right),
                            background_color='white',
                            key='graph')],
                        [sg.T(110*'_', size=(110,1), key='name_pckt')],
                        [sg.Button('inc_PACK'), sg.Button('My_But_2'),  sg.Button('draw_GRAPH'), sg.Quit(auto_size_button=True)],
                    ]
            win2 = sg.Window('Graph of Sine Function').Layout(layout2)
            win2.Finalize()

            graph = win2.FindElement('graph')
            graph.DrawLine((X_bottom_left,Y_bottom_left+1),  (X_top_right,Y_bottom_left+1))
            graph.DrawLine((X_bottom_left+1, Y_bottom_left), (X_bottom_left+1,Y_top_right))
            k_axis_Y = 900

            while True:
                ev2, vals2 = win2.Read(timeout=5000)
                print(ev2, vals2)
                if ev2 is None or ev2 == 'Quit':
                    win2.Close()
                    win2_active = False
                    window.UnHide()
                    break

                if event == '__TIMEOUT__':
                    pass

                if ev2 in ('inc_PACK', 'My_But_2', 'draw_GRAPH'):
                    graph.Erase()
                    graph = win2.FindElement('graph')
                    graph.DrawLine((X_bottom_left,Y_bottom_left+1),  (X_top_right,Y_bottom_left+1))
                    graph.DrawLine((X_bottom_left+1, Y_bottom_left), (X_bottom_left+1,Y_top_right))

                if ev2 == 'inc_PACK':
                    nom_pckt = (nom_pckt + 1) % len(db_TODAY.nm)
                    str_pck = db_TODAY.nm[nom_pckt] + '___'
                    koef_pckt = db_TODAY.koef[nom_pckt]
                    for i, item in enumerate(koef_pckt):
                        str_pck +='_'.join(str(x) for x in koef_pckt[i]) + '___'
                    win2.FindElement('name_pckt').Update(str_pck)
                    print(str_pck)

                if ev2 == 'draw_GRAPH':
                    k_axis_Y += 100
                    if k_axis_Y > 900:
                        k_axis_Y = 50
                    for x in range(X_bottom_left, X_top_right):
                        y = math.sin(x/5)*k_axis_Y
                        x_prev = x - 1
                        y_prev = math.sin(x_prev/5)*k_axis_Y
                        graph.DrawLine((x_prev,y_prev), (x,y), width=1, color='green')

                if ev2 == 'My_But_2':
                    print('X_bottom_left = ',X_bottom_left)
                    print('Y_bottom_left = ',Y_bottom_left)
                    print('X_top_right = ',  X_top_right)
                    print('Y_top_right = ',  Y_top_right)

                    # Draw axis X
                    for x in range(int(X_top_right/10), X_top_right, int(X_top_right/10)):
                        graph.DrawLine((x, Y_bottom_left + 25), (x, Y_top_right - 25), color='lightgrey')
                    # Draw axis Y
                    for y in range( int(Y_top_right/10), Y_top_right , int(Y_top_right/10) ):
                        graph.DrawLine((X_bottom_left + 25, y), (X_top_right - 25, y), color='lightgrey')

                    # Select lists for GRAPH
                    print('nom_pckt =', nom_pckt)
                    print('db_TODAY.arr_pk[-1] = ', db_TODAY.arr_pk[-1].dt)
                    print('len db_TODAY.arr_pk = ', len(db_TODAY.arr_pk))
                    len_arr_pk = len(db_TODAY.arr_pk)
                    num_start = len_arr_pk-1040
                    num_finish= len_arr_pk-0
                    arr_GRAPH = db_TODAY.arr_pk[num_start:num_finish]

                    x_DT, y_ASK, y_BID, y_EMA, y_EMAr, y_CNT = [], [], [], [], [], []
                    for i, item in enumerate(arr_GRAPH):
                        x_DT.append(item.dt)
                        y_ASK.append(item.arr[nom_pckt][0])
                        y_BID.append(item.arr[nom_pckt][1])
                        y_EMA.append(item.arr[nom_pckt][2])
                        y_EMAr.append(item.arr[nom_pckt][3])
                        y_CNT.append(item.arr[nom_pckt][4])

                    k_max, k_max_y_CNT = max([max(y_ASK), max(y_BID), max(y_EMA), max(y_EMAr)]), max(y_CNT)
                    k_min, k_min_y_CNT = min([min(y_ASK), min(y_BID), min(y_EMA), min(y_EMAr)]), min(y_CNT)

                    print('origin MAX ', k_max, k_max_y_CNT)
                    print('origin MIN ', k_min, k_min_y_CNT)

                    print('Y_top_right - Y_bottom_left = ', (Y_top_right - Y_bottom_left))
                    print('k_max - k_min = ', (k_max - k_min))
                    koef_Y = (Y_top_right - Y_bottom_left) / (k_max - k_min)
                    print('koef_Y  = ', koef_Y)

                    y0_ASK = [int(koef_Y * (jtem - k_min)) for jtem in y_ASK]
                    y1_BID = [int(koef_Y * (jtem - k_min)) for jtem in y_BID]
                    y2_EMA = [int(koef_Y * (jtem - k_min)) for jtem in y_EMA]
                    y3_EMAr = [int(koef_Y * (jtem - k_min)) for jtem in y_EMAr]

                    x0_DT = []
                    print('X_top_right - X_bottom_left   ', X_top_right - X_bottom_left)
                    print('len(y0_ASK)                   ', len(y0_ASK))
                    step_X = int((X_top_right - X_bottom_left) / len(y0_ASK))
                    print('step_X                        ', step_X)

                    x = 0
                    for i, y in enumerate(y0_ASK):
                        x0_DT.append(x)
                        x += step_X

                    for i, x_cr in enumerate(x0_DT):
                        if i != 0:
                            x_pr = x0_DT[i - 1]
                            graph.DrawLine((x_pr, y0_ASK[i-1]), (x_cr, y0_ASK[i-0]),  width=1, color='blue')
                            graph.DrawLine((x_pr, y1_BID[i-1]), (x_cr, y1_BID[i-0]),  width=1, color='red')
                            graph.DrawLine((x_pr, y2_EMA[i-1]), (x_cr, y2_EMA[i-0]),  width=3, color='green')
                            graph.DrawLine((x_pr, y3_EMAr[i-1]),(x_cr, y3_EMAr[i-0]), width=5, color='brown')

        #---------------------------------------------------------------
        window.FindElement('txt_data').Update('\n'.join(stroki))
        stts  = time.strftime(frm, time.localtime()) + '\n'
        stts += 'event = ' + event
        window.FindElement('txt_status').Update(stts)

    return 0

#=======================================================================
if __name__ == '__main__':
    import sys
    sys.exit(main())
