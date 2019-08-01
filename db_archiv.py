#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  db_archiv.py
#
#=======================================================================
import os, sys, math, time
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
def dbg_prn(db_ARCHIV, b_clear = True,
        b_fut_arc   = False,
        b_pack_arc  = False
        ):
    if b_clear:
        os.system('cls')  # on windows

    if b_fut_arc:
        print('..... hist_FUT_archiv .....')
        print('path_ARCHIV    => ', db_ARCHIV.path_db)
        hist = db_ARCHIV.hst_fut
        print('len(hst_fut_arc)   => ', len(hist))
        if len(hist) > 4:
            print('hst_fut_arc[0] => ',  hist[0])
            print('hst_fut_arc[1] => ',  hist[1][1].split('|')[0])
            print('hst_fut_arc[2] => ',  hist[2][1].split('|')[0])
            print('. . . . .')
            print('hst_fut_arc[-1] => ', hist[-1][1].split('|')[0])
            print('___________________________')
        hist = db_ARCHIV.arr_fut
        print('len(arr_fut_arc)  => ', len(hist))
        if len(hist) > 4:
            print('arr_fut_today[0] => ',  hist[0])
            print('arr_fut_today[1] => ',  hist[1][1].split('|')[0])
            print('arr_fut_today[2] => ',  hist[2][1].split('|')[0])
            print('. . . . .')
            print('arr_fut_today[-1] => ', hist[-1][1].split('|')[0])

    if b_pack_arc:
        print('..... hist_PACK_archiv .....')
        print('path_term_archiv    => ', db_ARCHIV.path_db)
        hist = db_ARCHIV.hst_pack
        print('len(hst_pack_arc)   => ', len(hist))
        if len(hist) > 4:
            print('hst_pack_arc[0] => ',  hist[0])
            print('hst_pack_arc[1] => ',  hist[1][1].split('|')[0])
            print('hst_pack_arc[2] => ',  hist[2][1].split('|')[0])
            print('. . . . .')
            print('hst_pack_arc[-1] => ', hist[-1][1].split('|')[0])
            print('___________________________')
        hist = db_ARCHIV.arr_pack[0]
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
def main():
    print('start')
    c_dir = os.path.abspath(os.curdir)

    #path_DEBUG  = c_dir + '\\DEBUG\\debug_file.txt'
    #dbg = Class_DEBUG_FILE(path_DEBUG)

    path_ARCHIV = c_dir + '\\DB\\term_archiv.sqlite'
    db_ARCHIV = Class_term_archiv(path_ARCHIV)

    rq = db_ARCHIV.op(rd_hist_FUT = True)
    if rq[0] != 0 : _err_('db_ARCHIV / rd_hist_FUT ', rq)
    else:           dbg_prn(db_ARCHIV, b_fut_arc = True)

    rq = db_ARCHIV.op(rd_hist_PACK = True)
    if rq[0] != 0 : _err_('db_ARCHIV / rd_hist_PACK ', rq)
    else:           dbg_prn(db_ARCHIV, b_clear = False, b_pack_arc = True)

    return 0

#=======================================================================
if __name__ == '__main__':
    import sys
    sys.exit(main())
