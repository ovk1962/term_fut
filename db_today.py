#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  db_today.py
#
#=======================================================================
import os, sys, math, time, sqlite3, logging
from datetime import datetime, timezone
from ipdb import set_trace as bp    # to set breakpoints just -> bp()
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
    def prn(self):
        frm = '{: ^15}{: ^15}'
        s = ''
        s += frm.format('acc_date', self.acc_date) + '\n'
        s += frm.format('acc_bal',  self.acc_bal) + '\n'
        s += frm.format('acc_prf',  self.acc_prf) + '\n'
        s += frm.format('acc_go',   self.acc_go) + '\n'
        s += frm.format('acc_depo', self.acc_depo) + '\n'

        return s
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

    def prn(self):
        s = ''
        frm = '{: ^8}{: ^8}{: ^8}{: ^12}{: ^12}{: ^12}'
        #s = frm.format('sP_code','sRest','sVar_mrg','sAsk','sBid','sFut_go') + '\n'
        s = frm.format(self.sP_code, self.sRest, self.sVar_mrg, self.sAsk, self.sBid, self.sFut_go)
        return s
#=======================================================================
class Class_STR_PACK():
    def __init__(self):
        self.ind= 0
        self.dt = ''
        self.tm = ''
        self.pk = []    # list of obj Class_sPACK()

    def prn(self):
        s = ''
        frm = '{: ^14}{: ^12}{: ^12}'
        s =  frm.format('ind','dt','tm') + '\n'
        s += frm.format(self.ind, self.dt, self.tm) + '\n'
        if len(self.pk) == 0:
            s += 'len(self.pk) = 0'
        else:
            frm = '{:^5}{:^12}{:^12}{:^12}{:^12}{:^4}'
            s += frm.format('pk[i]','pAsk','pBid','EMAf','EMAf_r','cnt_EMAf_r') + '\n'
            for i_pk, it in enumerate(self.pk):
                s += frm.format(str(i_pk), it.pAsk, it.pBid, it.EMAf, it.EMAf_r, it.cnt_EMAf_r) + '\n'
        return s
#=======================================================================
class Class_sPACK():
    def __init__(self):
        self.pAsk = 0.0
        self.pBid = 0.0
        self.EMAf = 0.0
        self.EMAf_r = 0.0
        self.cnt_EMAf_r = 0.0

    def prn(self):
        frm = '{:^8}{:^8}{:^8}{:^6}{:^4}'
        s = frm.format('pAsk','pBid','EMAf','EMAf_r','cnt_EMAf_r') + '\n'
        s += frm.format(self.pAsk, self.pBid, self.EMAf, self.EMAf_r, self.cnt_EMAf_r)
        return s
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

    def prn(self):
        frm = '{: ^6}{: ^8}{: ^8}{: ^12}{: ^12}{: ^12}'
        s = frm.format('ind','dt','tm','pAsk','pBid', 'EMAf')+ '\n'
        s += frm.format(self.sP_code, self.sRest, self.sVar_mrg, self.sAsk,  self.sBid, self.sFut_go) + '\n'
        return s
#=======================================================================
class Class_term_TODAY():
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
        self.hst_fut   = []  # list of [[ind_sec string] ... ]
        self.hst_1_fut = []  # list period 1 minute
        self.arr_1_fut = []  # list period 1 minute
        #
        self.sec_10_00 = 36000      # seconds from 00:00 to 10:00
        self.sec_14_00 = 50400      # seconds from 00:00 to 14:00
        self.sec_14_05 = 50700      # seconds from 00:00 to 14:05
        self.sec_18_45 = 67500      # seconds from 00:00 to 18:45
        self.sec_19_05 = 68700      # seconds from 00:00 to 19:05
        self.sec_23_45 = 85500      # seconds from 00:00 to 23:45
        #
        self.hst_pk_t  = []  # list of [[ind_sec string] ... ]
        self.arr_pk_t  = []  # list of [[ind_sec string] ... ]

    def prn(self,
            p_cfg_PACK  = False,
            p_cfg_SOFT  = False,
            p_cfg_ALARM = False,
            p_data_FUT  = False,
            p_hst_fut   = False,
            p_arr_1_fut = False,
            p_hst_pk    = False,
            p_arr_pk    = False
            ):
        s = ''
        try:
            if p_cfg_PACK:
                s += '_____ cfg_PACK ____________________________' + '\n'
                if len(self.nm) > 0:
                    frm = '{: ^5}{: ^15}{}{}{}'
                    s += frm.format('nm','nul','ema[]','        ','koef[]') + '\n'
                    for i, item in enumerate(self.nm):
                        s += frm.format(self.nm[i], str(self.nul[i]), self.ema[i], '   ', self.koef[i])+ '\n'

            if p_cfg_SOFT:
                s += '_____ cfg_SOFT ____________________________' + '\n'
                frm = '{: <18}{: <55}'
                s += frm.format('titul',self.titul) + '\n'
                s += frm.format('dt_start',self.dt_start) + '\n'
                s += frm.format('dt_start_sec',str(self.dt_start_sec)) + '\n'
                s += frm.format('path_file_DATA',self.path_file_DATA) + '\n'
                s += frm.format('path_file_HIST',self.path_file_HIST) + '\n'
                s += frm.format('path_term_today',self.path_db) + '\n'

            if p_cfg_ALARM:
                s += '_____ cfg_ALARM ___________________________' + '\n'
                if len(self.nm) > 0:
                    frm = '{: ^8}{: ^5}'
                    s += frm.format('nm','ena_cnt_ema') + '\n'
                    for i, item in enumerate(self.nm_alarm):
                        s += frm.format(self.nm_alarm[i], str(self.ena_cnt_ema[i])) + '\n'

            if p_data_FUT:
                s += '_____ data_FUT ____________________________' + '\n'
                frm = '{: <15}{: <25}'
                a = self.account
                s += 'self.account. => \n'
                s += frm.format('  acc_date', a.acc_date) + type(a.acc_date).__name__ + '\n'
                s += frm.format('  acc_bal',  a.acc_bal ) + type(a.acc_bal).__name__  + '\n'
                s += frm.format('  acc_prf',  a.acc_prf ) + type(a.acc_prf).__name__  + '\n'
                s += frm.format('  acc_go',   a.acc_go  ) + type(a.acc_go).__name__   + '\n'
                s += frm.format('  acc_depo', a.acc_depo) + type(a.acc_depo).__name__ + '\n'
                a = self.dt_fut
                s += 'self.dt_fut[' + str(len(self.dt_fut)) + ']. => \n'
                frm = '{: <6}{: ^6}{: ^6}{: ^9}{: ^9}{: ^9}{: ^7}{: ^9}{: ^9}{: ^9}'
                s += frm.format('sP_cd','sRest','sVar_m','sOpen','sLast',
                                'sAsk','sBuy_q','sBid','sSell_q','sFut_go') + '\n'
                for f in self.dt_fut:
                    s += frm.format(f.sP_code, int(f.sRest), int(f.sVar_mrg), f.sOpen_prc,
                                    int(f.sLast_prc), f.sAsk, int(f.sBuy_qty), f.sBid, int(f.sSell_qty),
                                    int(f.sFut_go)) + '\n'

            if p_hst_fut:
                s += '_____ hst_fut _____________________________' + '\n'
                hist = self.hst_fut
                s += 'len(hst_fut)   => ' + str(len(hist)) + '\n'
                if len(hist) > 4:
                    s += 'hst_fut[i] TUPLE (float, str_fut) => ' + '\n'
                    s += '0    => '  +  ' '.join(str(h) for h in hist[0]) + '\n'
                    for i in range(1,4):
                        s += str(i) + '    => ' + hist[i][1].split('|')[0] + '\n'
                    s += '. . . . . . . . . . . . . .' + '\n'
                    s += str(len(hist)-1) + ' => ' + hist[-1][1].split('|')[0] + '\n'

            if p_arr_1_fut:
                s += '_____ arr_1_fut ___________________________' + '\n'
                hist = self.arr_1_fut
                s += 'len(arr_fut)   => ' + str(len(hist)) + '\n'
                if len(hist) > 4:
                    s += 'arr_fut[i] LIST [float, dt_tm, floats] => \n'
                    s += '0    => '  + ' '.join(list(map(lambda x:str(x), hist[0]))) + '\n'
                    for i in range(1,4):
                        s += str(i) + '    => ' + hist[i][1] + '\n'
                    s += '. . . . . . . . . . . . . .' + '\n'
                    s += str(len(hist)-1) + '    => ' + hist[-1][1] + '\n'

            if p_hst_pk:
                s += '_____ hst_pk_t ____________________________' + '\n'
                hist = self.hst_pk_t
                #bp()
                s += 'len(hst_pk_t)   => ' + str(len(hist)) + '\n'
                if len(hist) > 4:
                    s += 'hst_pk_t[i] TUPLE (float, str_fut) => ' + '\n'
                    s += '0    => '  +  ' '.join(str(h) for h in hist[0]) + '\n'
                    for i in range(1,4):
                        s += str(i) + '    => ' + hist[i][1].split('|')[0] + '\n'
                    s += '. . . . . . . . . . . . . .' + '\n'
                    s += str(len(hist)-1) + ' => ' + hist[-1][1].split('|')[0] + '\n'


            if p_arr_pk:
                s += '_____ arr_pk_t ____________________________' + '\n'
                hist = self.arr_pk_t
                s += 'len(arr_pk_t)   => ' + str(len(hist)) + '\n'
                #bp()
                if len(hist) > 4:
                    for i in range(1,2):
                        s += 'arr_pk_t[' + str(i) + ']   =>\n' + hist[i].prn()
                    s += '. . . . . . . . . . . . . .' + '\n'
                    s += 'arr_pk_t[' + str(len(hist)-1) + '] => \n' + hist[-1].prn()

        except Exception as ex:
            r_prn = [1, 'op_archiv / ' + str(ex)]

        return [0, s]

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
                    self.hst_pk_t  = []
                    self.arr_pk_t  = []
                    for item in self.nm:
                        #self.hst_pk_t.append([])
                        self.arr_pk_t.append([])
                    #print('clr_hist_FUT_today / len(arr_pk_t) = ', len(self.arr_pk_t))
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
                    self.cur.execute('SELECT * from ' + 'hist_PACK_today')
                    self.hst_pk_t = []
                    self.hst_pk_t = self.cur.fetchall()    # read table name_tbl
                    print('len(hst_pk_t) = ', len(self.hst_pk_t))
                    if len(self.hst_pk_t) != 0:
                        self.arr_pk_t  = []
                        for cnt, i_str in enumerate(self.hst_pk_t):
                            #self.ind / dt / tm / pk = 0, '', '', []
                            bp = Class_STR_PACK()
                            bp.ind = int(i_str[0])
                            buf = i_str[1].split('|')[0].split(' ')
                            bp.dt, bp.tm  = buf[0], buf[1]
                            #
                            bp.pk = [] # list of obj Class_PACK()
                            buf = i_str[1].replace(',','.').split('|')
                            del buf[-1]
                            for cn, item in enumerate(buf):
                                ind_0 = 0
                                if cn == 0: ind_0 = 2
                                str_mdl  = item.split(' ')
                                bpp = Class_sPACK()
                                bpp.pAsk       = float(str_mdl[0+ind_0])
                                bpp.pBid       = float(str_mdl[1+ind_0])
                                bpp.EMAf       = float(str_mdl[2+ind_0])
                                bpp.EMAf_r     = float(str_mdl[3+ind_0])
                                bpp.cnt_EMAf_r = float(str_mdl[4+ind_0])
                                bp.pk.append(bpp)
                            self.arr_pk_t.append(bp)
                    else:
                        pass
                    if (len(self.arr_pk_t) == 0):
                        for item in self.nm:
                            self.arr_pk_t.append([])

                if wr_hist_PACK_today:
                    #rq = self.obj_table.rewrite_table('hist_PACK_today', hist_arc, val = '(?,?)')
                    self.cur.execute('DELETE FROM ' + 'hist_PACK_today')
                    self.cur.executemany('INSERT INTO ' + 'hist_PACK_today' + ' VALUES' + '(?,?)', self.hst_pk_t)
                    self.conn.commit()

        except Exception as ex:
            r_op_today = [1, 'op_today / ' + str(ex)]

        return r_op_today
#=======================================================================
def prn_rq(msg, rq, Prn = True):
    err_msg  = msg
    err_msg += '\n'.join(str(e) for e in rq)
    if Prn  :
        print(err_msg + '\n')
#=======================================================================
def menu_PRINT(db_TODAY, b_clear = True,
        b_cfg_pack  = False,
        b_cfg_soft  = False,
        b_cfg_alarm = False,
        b_data_fut  = False,
        b_hst_fut   = False,
        b_arr_fut   = False,
        b_hst_pk    = False,
        b_arr_pk    = False,
        ):
    if b_clear:
        os.system('cls')  # on windows

    if b_cfg_pack:
        rq = db_TODAY.prn(p_cfg_PACK = True)
        prn_rq('PRINT p_cfg_PACK db_TODAY\n', rq)

    if b_cfg_soft:
        rq = db_TODAY.prn(p_cfg_SOFT = True)
        prn_rq('PRINT p_cfg_PACK db_TODAY\n', rq)

    if b_cfg_alarm:
        rq = db_TODAY.prn(p_cfg_ALARM = True)
        prn_rq('PRINT p_cfg_ALARM db_TODAY\n', rq)

    if b_data_fut:
        rq = db_TODAY.prn(p_data_FUT = True)
        prn_rq('PRINT p_data_FUT db_TODAY\n', rq)

    if b_hst_fut:
        rq = db_TODAY.prn(p_hst_fut = True)
        prn_rq('PRINT p_hist_FUT db_TODAY\n', rq)

    if b_arr_fut:
        rq = db_TODAY.prn(p_arr_1_fut = True)
        prn_rq('PRINT p_arr_1_fut db_TODAY\n', rq)

    if b_hst_pk:
        rq = db_TODAY.prn(p_hst_pk = True)
        prn_rq('PRINT p_hist_PK db_TODAY\n', rq)

    if b_arr_pk:
        rq = db_TODAY.prn(p_arr_pk = True)
        prn_rq('PRINT p_arr_pk db_TODAY\n', rq)
#=======================================================================
def event_menu(event, db_TODAY):
    #-------------------------------------------------------------------
    if event == 'prn cfg_PACK'  :
        menu_PRINT(db_TODAY, b_cfg_pack  = True)
    #-------------------------------------------------------------------
    if event == 'prn cfg_SOFT'  :
        menu_PRINT(db_TODAY, b_cfg_soft  = True)
    #-------------------------------------------------------------------
    if event == 'prn cfg_ALARM'  :
        menu_PRINT(db_TODAY, b_cfg_alarm = True)
    #-------------------------------------------------------------------
    if event == 'prn data_FUT'  :
        menu_PRINT(db_TODAY, b_data_fut  = True)
    #-------------------------------------------------------------------
    if event == 'prn hist_FUT'  :
        menu_PRINT(db_TODAY, b_hst_fut  = True)
    #-------------------------------------------------------------------
    if event == 'prn arr_FUT'  :
        menu_PRINT(db_TODAY, b_arr_fut  = True)
    #-------------------------------------------------------------------
    if event == 'prn hist_PACK'  :
        menu_PRINT(db_TODAY, b_hst_pk  = True)
    #-------------------------------------------------------------------
    if event == 'prn arr_PACK'  :
        menu_PRINT(db_TODAY, b_arr_pk  = True)
    #-------------------------------------------------------------------
    if event == 'rd cfg_PACK'  :
        rq = db_TODAY.op(rd_cfg_PACK = True)
        prn_rq('db_TODAY / rd cfg_PACK', rq)
    #-------------------------------------------------------------------
    if event == 'rd cfg_SOFT'  :
        rq = db_TODAY.op(rd_cfg_SOFT = True)
        prn_rq('db_TODAY / rd cfg_SOFT', rq)
    #-------------------------------------------------------------------
    if event == 'rd cfg_ALARM'  :
        rq = db_TODAY.op(rd_cfg_ALARM = True)
        prn_rq('db_TODAY / rd cfg_ALARM', rq)
    #-------------------------------------------------------------------
    if event == 'rd data_FUT'  :
        rq = db_TODAY.op(rd_data_FUT = True)
        prn_rq('db_TODAY / rd data_FUT', rq)
    #-------------------------------------------------------------------
    if event == 'rd hst_FUT'  :
        rq = db_TODAY.op(rd_hist_FUT_today = True)
        prn_rq('db_TODAY / rd hst_FUT', rq)



#=======================================================================
def main():
    while True:  # init db_TODAY ---------------------------------------
        c_dir = os.path.abspath(os.curdir)
        #bp()
        path_TODAY = c_dir + '\\DB\\term_today.sqlite'
        print(path_TODAY)
        db_TODAY = Class_term_TODAY(path_TODAY)
        lg_FILE  = Class_LOGGER(c_dir + '\\LOG\\d_logger.log')

        rq = db_TODAY.op(
                        rd_cfg_SOFT  = True,
                        rd_cfg_PACK  = True,
                        rd_cfg_ALARM = True,
                        rd_data_FUT  = True,
                        rd_hist_FUT_today = True,
                        rd_hist_PACK_today = True,
                        )
        if rq[0] != 0 : prn_rq('INIT rd_cfg_SOFT TODAY', rq)
        else:
            print('INIT cfg_data_hist TODAY = > ', rq)
            if len(db_TODAY.nm) == 0:
                prn_rq('cfg_pack.nm = 0  ', [' ', 'It can not be EMPTY !'] )
                break
            if (len(db_TODAY.arr_pk_t) == 0):
                for item in db_TODAY.nm:
                    db_TODAY.arr_pk_t.append([])
        break

    for item in db_TODAY.dt_fut:
        #bp()
        print(item.prn())

    while True:  # init MENU -------------------------------------------
        menu_def = [
        ['PRINT',
            ['prn cfg_PACK', 'prn cfg_SOFT', 'prn cfg_ALARM','---',
             'prn data_FUT', 'prn hist_FUT', 'prn arr_FUT', '---',
             'prn hist_PACK','prn arr_PACK'],],
        ['READ  today', ['rd cfg_PACK', 'rd cfg_SOFT', 'rd cfg_ALARM',  '---',
                         'rd data_FUT', 'rd hst_FUT',  '---',
                         'rd data_TERM', 'rd hst_TERM'],],
        ['WRITE today', ['wr cfg_PACK',  '---', 'wr hist_FUT',  '---', 'wr hist_PACK'] ,],
        ['CALC', ['ASK_BID',  '---', 'EMA_f',  '---', 'cnt'] ,],
        ['Exit', 'Exit']
        ]

        def_txt, frm = [], '{: <15}  => {: ^15}\n'
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
        window = sg.Window('Test db_today', grab_anywhere=True).Layout(layout).Finalize()
        break

    frm = '%d.%m.%Y %H:%M:%S'
    while True:  # MAIN cycle ------------------------------------------
        stroki = []
        event, values = window.Read(timeout=1000000 )
        #---------------------------------------------------------------
        event_menu(event, db_TODAY)
        #---------------------------------------------------------------
        if event is None or event == 'Quit' or event == 'Exit': break
        #---------------------------------------------------------------
        window.FindElement('txt_data').Update('\n'.join(stroki))
        stts  = time.strftime(frm, time.localtime()) + '\n'
        stts += 'event = ' + event
        window.FindElement('txt_status').Update(stts)
        #break

    return 0

#=======================================================================
if __name__ == '__main__':
    import sys
    sys.exit(main())
