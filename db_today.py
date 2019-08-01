#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  db_today.py
#
#=======================================================================
import os, sys, math, time
from datetime import datetime, timezone
import sqlite3
if sys.version_info[0] >= 3:
    import PySimpleGUI as sg
else:
    import PySimpleGUI27 as sg
#=======================================================================
def _err_(msg, rq, Prn = True):
    err_msg  = msg
    err_msg += '  '.join(str(e) for e in rq)
    if Prn  :
        os.system('cls')  # on windows
        print(err_msg)
#=======================================================================
def dbg_prn(db_TODAY, b_clear = True,
        b_cfg_soft   = False,
        ):
    if b_clear:
        os.system('cls')  # on windows
    if b_cfg_soft:
        s = db_TODAY
        print('..... cfg_SOFT .....')
        print('path_term_today => ', s.path_db)
        print('titul              => ', s.titul)
        print('path_file_DATA     => ', s.path_file_DATA)
        print('path_file_HIST     => ', s.path_file_HIST)
        print('dt_start           => ', s.dt_start)
#=======================================================================
class Class_ACCOUNT():
    def __init__(self):
        self.acc_date = ''
        self.acc_bal  = 0.0
        self.acc_prf  = 0.0
        self.acc_go   = 0.0
        self.acc_depo = 0.0
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
def main():
    print('start')
    c_dir = os.path.abspath(os.curdir)

    #path_DEBUG  = c_dir + '\\DEBUG\\debug_file.txt'
    #dbg = Class_DEBUG_FILE(path_DEBUG)

    path_TODAY = c_dir + '\\DB\\term_today.sqlite'
    db_TODAY = Class_term_today(path_TODAY)

    rq = db_TODAY.op(rd_cfg_SOFT = True)
    if rq[0] != 0 : _err_('db_TODAY / rd_cfg_SOFT ', rq)
    else:           dbg_prn(db_TODAY, b_cfg_soft = True)


    return 0

#=======================================================================
if __name__ == '__main__':
    import sys
    sys.exit(main())
