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
import ipdb

#=======================================================================
class Class_STR_PACK():
    def __init__(self):
        self.ind= 0
        self.dt = ''
        self.tm = ''
        self.pk = []    # list of obj Class_sPACK()
#=======================================================================
class Class_sPACK():
    def __init__(self):
        self.pAsk = 0.0
        self.pBid = 0.0
        self.EMAf = 0.0
        self.EMAf_r = 0.0
        self.cnt_EMAf_r = 0.0
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
        # cfg_pack
        self.nm   = []  # list NM   of packets
        self.koef = []  # list KOEF of packets
        self.nul  = []  # list NUL  of packets
        self.ema  = []  # list EMA  of packets
        # hist_FUT
        self.hst_fut  = []  # list of [[ind_sec string] ... ]
        self.arr_fut  = []  # list period 1 minute
        # hist_PACK
        self.buf_arc  = []
        self.hst_pack = []  # list of [[ind_sec string] ... ]
        #self.arr_pack = []  # list of [[ind_sec string] ... ]
        self.arr_pk   = []  # list of obj [Class_STR_PACK ... ]

    def prn(self,p_clear = True,
            p_cfg_PACK   = False,
            p_hist_FUT   = False,
            p_hist_PACK  = False
            ):
        r_prn = [0, 'ok']
        try:
            if p_clear:
                os.system('cls')  # on windows

            if p_cfg_PACK:
                print('..... cfg_PACK ..... ')
                print(self.path_db)
                print('len(cfg_PACK) => ', len(self.nm))
                if len(self.nm) > 0:
                    print('\n  nm       nul     ema[]     koef[]\n')
                    for i, item in enumerate(self.nm):
                        print('{: ^5}{: ^15}{}{}'.format(self.nm[i], self.nul[i], self.ema[i], self.koef[i]))
                    print()

            if p_hist_FUT:
                pass

            if p_hist_PACK:
                pass

        except Exception as ex:
            r_prn = [1, 'op_archiv / ' + str(ex)]

        return r_prn

    def op(self,
            rd_cfg_PACK  = False,
            wr_cfg_PACK  = False,
            rd_hist_FUT = False,
            wr_hist_FUT = False,
            rd_hist_PACK  = False,
            wr_hist_PACK  = False,
            calc_ASK_BID  = False,
            calc_ASK_BID_pk  = False,
            calc_EMA_pk      = False,
            prp_hist_PACK = False
            ):
        r_op_archiv = []
        self.conn = sqlite3.connect(self.path_db)
        try:
            with self.conn:
                r_op_archiv = [0, 'ok']
                self.cur = self.conn.cursor()

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

                if wr_cfg_PACK:
                    duf_list = []
                    for j, jtem in enumerate(self.nm):
                        buf = (self.nm[j], ','.join(self.koef[j]), self.nul[j], ':'.join(self.ema[j]))
                        duf_list.append(buf)

                    self.cur.execute('DELETE FROM ' + 'cfg_PACK')
                    self.cur.executemany('INSERT INTO ' + 'cfg_PACK' + ' VALUES' + '(?,?,?,?)', duf_list)
                    self.conn.commit()

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
                    print('len(hst_pack) = ', len(self.hst_pack))

                    self.arr_pk  = []
                    #for i_str in self.hst_pack:
                    for cnt, i_str in enumerate(self.hst_pack):
                        #self.ind / dt / tm / pk = 0, '', '', []
                        buf_pack = Class_STR_PACK()
                        buf_pack.ind = int(i_str[0])
                        buf = i_str[1].split('|')[0].split(' ')
                        buf_pack.dt, buf_pack.tm  = buf[0], buf[1]
                        #
                        buf_pack.pk = [] # list of obj Class_PACK()
                        buf = i_str[1].replace(',','.').split('|')
                        del buf[-1]
                        for cnt, item in enumerate(buf):
                            str_mdl  = item.split(' ')
                            ind_0 = 0
                            if cnt == 0: ind_0 = 2
                            buf_p = Class_sPACK()
                            buf_p.pAsk       = float(str_mdl[0+ind_0])
                            buf_p.pBid       = float(str_mdl[1+ind_0])
                            buf_p.EMAf       = float(str_mdl[2+ind_0])
                            buf_p.EMAf_r     = float(str_mdl[3+ind_0])
                            buf_p.cnt_EMAf_r = float(str_mdl[4+ind_0])
                            buf_pack.pk.append(buf_p)
                        self.arr_pk.append(buf_pack)
                        if len(self.arr_pk) % 10000 == 0:  print(len(self.arr_pk), end='\r')

                if wr_hist_PACK:
                    name_list =[]
                    if len(self.arr_pk) > 0:
                        for i_hist, item_hist in enumerate(self.arr_pk):
                            buf_dt = item_hist.dt + ' ' + item_hist.tm + ' '
                            buf_s = ''
                            for i_pack, item_pack in enumerate(item_hist.pk):
                                buf_s += str(item_pack.pAsk) + ' ' + str(item_pack.pBid)     + ' '
                                buf_s += str(item_pack.EMAf) + ' ' + str(item_pack.EMAf_r) + ' ' + str(item_pack.cnt_EMAf_r) + '|'
                            name_list.append((item_hist.ind, buf_dt + buf_s.replace('.', ',')))

                    ''' rewrite data from table ARCHIV_PACK & PACK_TODAY & DATA ----'''
                    self.cur.execute('DELETE FROM ' + 'hist_PACK')
                    self.cur.executemany('INSERT INTO ' + 'hist_PACK' + ' VALUES' + '(?,?)', name_list)
                    self.conn.commit()

                if calc_ASK_BID_pk:
                    ''' init  table ARCHIV_PACK  --------------------'''
                    self.arr_pk  = []
                    for idx, item in enumerate(self.arr_fut):
                        ipdb.set_trace()
                        if idx % 1000 == 0:  print(idx, end='\r')
                        buf_pack = Class_STR_PACK()
                        buf_pack.ind = int(item[0])
                        buf_pack.dt, buf_pack.tm  = item[1].split(' ')
                        #
                        buf_pack.pk = [] # list of obj Class_PACK()
                        for p, ptem in enumerate(self.nm):
                            ask_p = bid_p = 0
                            for jdx, jtem in enumerate(self.koef[p]):
                                #print(jtem)
                                i_koef = int(jtem.split(':')[0])
                                k_koef = int(jtem.split(':')[1])
                                ask_j = float(item[2 + 2*i_koef])
                                bid_j = float(item[2 + 2*i_koef + 1])
                                if k_koef > 0 :
                                    ask_p = ask_p + k_koef * ask_j
                                    bid_p = bid_p + k_koef * bid_j
                                if k_koef < 0 :
                                    ask_p = ask_p + k_koef * bid_j
                                    bid_p = bid_p + k_koef * ask_j
                            #
                            buf_pack.pk.append(Class_sPACK())
                            ask_bid_AVR = 0
                            if idx == 0:
                                null_prc = int((ask_p + bid_p)/2)
                                self.nul[p] = null_prc
                                buf_pack.pk[p].pAsk, buf_pack.pk[p].pBid = 0, 0
                                buf_pack.pk[p].EMAf, buf_pack.pk[p].EMAf_r = 0, 0
                                buf_pack.pk[p].cnt_EMAf_r = 0
                            else:
                                null_prc = self.nul[p]
                                ask_p = int(ask_p - null_prc)
                                bid_p = int(bid_p - null_prc)
                                ask_bid_AVR = int((ask_p + bid_p)/2)
                                buf_pack.pk[p].pAsk = ask_p
                                buf_pack.pk[p].pBid = bid_p
                        self.arr_pk.append(buf_pack)
                        ''' self.arr_pk[nom_stroki].dt/tm/pk[nom_pack] '''

                    # update self.nul[i_pack] in table cfg_PACK ----
                    duf_list = []
                    for j, jtem in enumerate(self.nm):
                        buf = (self.nm[j], ','.join(self.koef[j]), self.nul[j], ':'.join(self.ema[j]))
                        duf_list.append(buf)
                    self.cur.execute('DELETE FROM ' + 'cfg_PACK')
                    self.cur.executemany('INSERT INTO ' + 'cfg_PACK' + ' VALUES' + '(?,?,?,?)', duf_list)
                    self.conn.commit()

                if calc_EMA_pk:
                    koef_EMA, k_EMA_rnd = [], []
                    for kdx, ktem in enumerate(self.arr_pk[0].pk):
                        koef_EMA.append(round(2/(1+int(self.ema[kdx][0])),5))
                        k_EMA_rnd.append(int(self.ema[kdx][1]))

                    for idx, item in enumerate(self.arr_pk):
                        if idx % 1000 == 0:  print(idx, end='\r')
                        for pdx, ptem in enumerate(item.pk):
                            prev_EMAf = ask_bid_AVR = 0
                            if idx == 0:
                                ptem.EMAf, ptem.EMAf_r, ptem.cnt_EMAf_r = 0, 0, 0
                            else:
                                ask_bid_AVR = int((ptem.pAsk + ptem.pBid)/2)
                                prev_EMAf = self.arr_pk[idx-1].pk[pdx].EMAf
                                ptem.EMAf = round(prev_EMAf + (ask_bid_AVR - prev_EMAf) * koef_EMA[pdx], 1)
                                ptem.EMAf_r = k_EMA_rnd[pdx] * math.ceil(ptem.EMAf / k_EMA_rnd[pdx] )

                                prev_EMAf_r = self.arr_pk[idx-1].pk[pdx].EMAf_r
                                i_cnt = self.arr_pk[idx-1].pk[pdx].cnt_EMAf_r
                                if prev_EMAf_r > ptem.EMAf_r:
                                    ptem.cnt_EMAf_r = 0 if i_cnt > 0 else i_cnt-1
                                elif prev_EMAf_r < ptem.EMAf_r:
                                    ptem.cnt_EMAf_r = 0 if i_cnt < 0 else i_cnt+1
                                else:
                                    ptem.cnt_EMAf_r = i_cnt

                            self.arr_pk[idx].pk[pdx] = ptem

        except Exception as ex:
            r_op_archiv = [1, 'op_archiv / ' + str(ex)]

        return r_op_archiv

#=======================================================================
def _err_(msg, rq, Prn = True):
    err_msg  = msg
    err_msg += '  '.join(str(e) for e in rq)
    if Prn  :
        #os.system('cls')  # on windows
        print(err_msg)
#=======================================================================
def dbg_prn(db_ARCHIV, b_clear = True,
        b_cfg_pack  = False,
        b_fut_arc   = False,
        b_pack_arc  = False,
        b_arr_pk    = False,

        ):
    if b_clear:
        os.system('cls')  # on windows

    if b_cfg_pack:
        rq = db_ARCHIV.prn(p_cfg_PACK   = True)
        if rq[0] != 0 : _err_('PRINT cfg_hist ARCHIV', rq)

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
        print('len(arr_pk)  => ', len(db_ARCHIV.arr_pk))
        if len(db_ARCHIV.arr_pk) > 4:
            h = db_ARCHIV.arr_pk[0]
            print('arr_pk[0].ind => ',  h.ind)
            print('arr_pk[0].dt => ' ,  h.dt)
            print('arr_pk[0].tm => ' ,  h.tm)
            print('arr_pk[0].pk[0].ask/bid => ' ,  h.pk[0].pAsk, h.pk[0].pBid, h.pk[0].EMAf, h.pk[0].EMAf_r, h.pk[0].cnt_EMAf_r)
            print('arr_pk[0].pk[1].ask/bid => ' ,  h.pk[1].pAsk, h.pk[1].pBid, h.pk[1].EMAf, h.pk[1].EMAf_r, h.pk[1].cnt_EMAf_r)
            print('arr_pk[0].pk[2].ask/bid => ' ,  h.pk[2].pAsk, h.pk[2].pBid, h.pk[2].EMAf, h.pk[2].EMAf_r, h.pk[2].cnt_EMAf_r)
            print('. . . . .')
            h = db_ARCHIV.arr_pk[1]
            print('arr_pk[1].ind => ',  h.ind)
            print('arr_pk[1].dt => ' ,  h.dt)
            print('arr_pk[1].tm => ' ,  h.tm)
            print('arr_pk[1].pk[0].ask/bid => ' ,  h.pk[0].pAsk, h.pk[0].pBid, h.pk[0].EMAf, h.pk[0].EMAf_r, h.pk[0].cnt_EMAf_r)
            print('arr_pk[1].pk[1].ask/bid => ' ,  h.pk[1].pAsk, h.pk[1].pBid, h.pk[1].EMAf, h.pk[1].EMAf_r, h.pk[1].cnt_EMAf_r)
            print('arr_pk[1].pk[2].ask/bid => ' ,  h.pk[2].pAsk, h.pk[2].pBid, h.pk[2].EMAf, h.pk[2].EMAf_r, h.pk[2].cnt_EMAf_r)
            print('. . . . .')
            h = db_ARCHIV.arr_pk[-1]
            print('arr_pk[-1].ind => ',  h.ind)
            print('arr_pk[-1].dt => ' ,  h.dt)
            print('arr_pk[-1].tm => ' ,  h.tm)
            print('arr_pk[-1].pk[0].ask/bid => ',  h.pk[0].pAsk, h.pk[0].pBid, h.pk[0].EMAf, h.pk[0].EMAf_r, h.pk[0].cnt_EMAf_r)
            print('arr_pk[-1].pk[1].ask/bid => ',  h.pk[1].pAsk, h.pk[1].pBid, h.pk[1].EMAf, h.pk[1].EMAf_r, h.pk[1].cnt_EMAf_r)
            print('arr_pk[-1].pk[2].ask/bid => ',  h.pk[2].pAsk, h.pk[2].pBid, h.pk[2].EMAf, h.pk[2].EMAf_r, h.pk[2].cnt_EMAf_r)
        print('')
#=======================================================================
def event_menu(event, db_ARCHIV):
    #-------------------------------------------------------------------
    if event == 'prn cfg_PACK'  :
        dbg_prn(db_ARCHIV, b_cfg_pack = True)
    #-------------------------------------------------------------------
    if event == 'prn hist_FUT'  :
        dbg_prn(db_ARCHIV, b_fut_arc  = True)
    #-------------------------------------------------------------------
    if event == 'prn hist_PACK'  :
        dbg_prn(db_ARCHIV, b_pack_arc = True)
    #-------------------------------------------------------------------
    if event == 'rd cfg_PACK'  :
        rq = db_ARCHIV.op(rd_cfg_PACK = True)
        if rq[0] != 0 : _err_('db_ARCHIV / rd cfg_PACK', rq)
        else:           dbg_prn(db_ARCHIV, b_cfg_pack = True)
    #-------------------------------------------------------------------
    if event == 'rd hist_FUT'   :
        rq = db_ARCHIV.op(rd_hist_FUT = True)
        if rq[0] != 0 : _err_('db_ARCHIV / rd_hist_FUT ', rq)
        else:           dbg_prn(db_ARCHIV, b_fut_arc = True)
    #-------------------------------------------------------------------
    if event == 'rd hist_PACK'  :
        rq = db_ARCHIV.op(rd_hist_PACK = True)
        if rq[0] != 0 : _err_('db_ARCHIV / rd_hist_PACK ', rq)
        else:           dbg_prn(db_ARCHIV, b_clear = False, b_pack_arc = True)
    #-------------------------------------------------------------------
    if event == 'wr cfg_PACK'  :
        print('pass reserv / wr cfg_PACK')
    #-------------------------------------------------------------------
    if event == 'wr hist_FUT'   :
        # test array to write in DB
        db_ARCHIV.buf_arc = [
        [1564771509, '02.08.2019 18:45:09|22330|22334|23042|23048|51207|51244|41607|41631|4238|4240|5662|5669|144912|145063|19623|19645|129450|129460|2693,65|2694|129605|129983|18198|18220|73876|74066|32303|32384|27099|27138|7990|7998|8286|8308|98810|99112|26222|26273|157054|157864|'],
        ]
        rq = db_ARCHIV.op(wr_hist_FUT = True)
        if rq[0] != 0 : _err_('db_ARCHIV / wr_hist_FUT ', rq)
        else:           dbg_prn(db_ARCHIV, b_fut_arc = True)
    #-------------------------------------------------------------------
    if event == 'wr hist_PACK'  :
        rq = db_ARCHIV.op(wr_hist_PACK = True)
        if rq[0] != 0 : _err_('db_ARCHIV / wr_hist_PACK ', rq)
        else:           dbg_prn(db_ARCHIV, b_pack_arc = True)
    #-------------------------------------------------------------------
    if event == 'ASK_BID'  :
        #rq = db_ARCHIV.op(calc_ASK_BID = True)
        rq = db_ARCHIV.op(calc_ASK_BID_pk = True)
        if rq[0] != 0 : _err_('db_ARCHIV / calc_ASK_BID ', rq)
        else:           dbg_prn(db_ARCHIV, b_clear = False, b_pack_arc = True)
    #-------------------------------------------------------------------
    if event == 'EMA_f'  :
        rq = db_ARCHIV.op(calc_EMA_pk = True)
        if rq[0] != 0 : _err_('db_ARCHIV / calc_EMA_pk ', rq)
        else:           dbg_prn(db_ARCHIV, b_clear = False, b_pack_arc = True)
#=======================================================================
def main():
    while True:  # init db_ARCHIV --------------------------------------
        c_dir = os.path.abspath(os.curdir)
        path_ARCHIV = c_dir + '\\DB\\term_archiv.sqlite'
        print(path_ARCHIV)
        db_ARCHIV = Class_term_archiv(path_ARCHIV)

        rq = db_ARCHIV.op(
                        rd_cfg_PACK  = True,
                        rd_hist_FUT  = True,
                        rd_hist_PACK = True,
                        )
        if rq[0] != 0 : _err_('INIT cfg_hist ARCHIV', rq)

        else:
            print('INIT cfg_data_hist ARCHIV = > ', rq)
            if len(db_ARCHIV.nm) == 0:
                _err_('cfg_pack.nm = 0  ', [' ', 'It can not be EMPTY !'] )
                break
            #if (len(db_ARCHIV.arr_pack) == 0):
                #for item in db_ARCHIV.nm:
                    #db_ARCHIV.arr_pack.append([])
            if (len(db_ARCHIV.arr_pk) == 0):
                for item in db_ARCHIV.nm:
                    db_ARCHIV.arr_pk.append([])
        break




    while True:  # init MENU -------------------------------------------
        menu_def = [
        ['PRINT arc  ', ['prn cfg_PACK', '---', 'prn hist_FUT', '---', 'prn hist_PACK'],],
        ['READ  arc  ', ['rd cfg_PACK',  '---', 'rd hist_FUT',  '---', 'rd hist_PACK'] ,],
        ['WRITE arc  ', ['wr cfg_PACK',  '---', 'wr hist_FUT',  '---', 'wr hist_PACK'] ,],
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
        window = sg.Window('Test db_archiv', grab_anywhere=True).Layout(layout).Finalize()
        break

    frm = '%d.%m.%Y %H:%M:%S'
    while True:  # MAIN cycle ------------------------------------------
        stroki = []
        event, values = window.Read(timeout=1000000 )
        #---------------------------------------------------------------
        event_menu(event, db_ARCHIV)
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
