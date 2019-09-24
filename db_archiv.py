#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  db_archiv.py
#
#=======================================================================
import os, sys, math, time, sqlite3, logging
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
class Class_term_ARCHIV():
    def __init__(self, path_term_archiv):
        self.path_db = path_term_archiv
        #self.table_db = []
        self.conn = ''
        self.cur  = ''
        # cfg_pack
        self.nm   = []  # list NM   of packets
        self.koef = []  # list KOEF of packets
        self.nul  = []  # list NUL  of packets
        self.ema  = []  # list EMA  of packets
        # hist_FUT
        self.arr_fut = []  # list period 1 minute
        # hist_PACK
        self.buf_arc = []
        self.arr_pk  = []  # list of obj [Class_STR_PACK ... ]

    def prn(self,
            p_cfg_PACK   = False,
            p_arr_fut   = False,
            p_arr_pk    = False
            ):
        try:
            if p_cfg_PACK:
                if len(self.nm) > 0:
                    frm = '{: ^5}{: ^15}{}{}{}'
                    print(frm.format('nm','nul','ema[]','        ','koef[]'))
                    for i, item in enumerate(self.nm):
                        print(frm.format(self.nm[i], str(self.nul[i]), self.ema[i], '   ', self.koef[i]))
            if p_arr_fut:
                hist = self.arr_fut
                print('len(arr_fut)   => ' + str(len(hist)) )
                for i in [0,1,2]: print(hist[i])
                print('. _ . _ . _ . _ . _ . _ . _ . _ .')
                print(hist[-1])
            if p_arr_pk:
                hist = self.arr_pk
                print('len(arr_pk)    => ' + str(len(hist)) )
                for i in [0,1,2]: print(hist[i])
                print('. _ . _ . _ . _ . _ . _ . _ . _ .')
                print(hist[-1])
        except Exception as ex:
            err_msg = 'prn / ' + str(ex)
            r_prn = [1, err_msg]
            print(err_msg)
        return [0, 'ok']

    def op(self,
            rd_cfg_PACK = False,
            rd_hst_FUT  = False,
            rd_hst_PCK  = False,
            wr_cfg_PACK  = False,
            wr_hist_FUT  = False,
            wr_hist_PACK = False,
            clc_ASK_BID  = False,
            clc_EMA      = False,
            prp_hist_PACK   = False
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
                        self.nm.append(item[0])          # ['pckt0']
                        arr_k    = item[1].split(',')
                        arr_koef = []
                        for item_k in arr_k:             # '0:2:SR' => [0, 32, 'SR']
                            buf_k = [int(f) if f.replace('-','').isdigit() else f for f in item_k.split(':')]
                            arr_koef.append(buf_k)
                        self.koef.append(arr_koef)       #  [[0, 2, 'SR'],[9, -20, 'MX'], ...
                        self.nul.append(int(item[2]))    #  [0]
                        self.ema.append([int(e) for e in item[3].split(':')]) # [1111, 15]

                if wr_cfg_PACK:
                    duf_list = []
                    # for j, jtem in enumerate(self.nm):
                        # #bp()
                        # buf = (self.nm[j], ','.join(self.koef[j]), self.nul[j], ':'.join(self.ema[j]))
                        # print(j, buf)
                        # duf_list.append(buf)
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

                if rd_hst_FUT:
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

                if wr_hist_FUT:
                    self.cur.executemany("INSERT INTO " + 'hist_FUT' + " VALUES(?, ?)", self.buf_arc)
                    self.conn.commit()

                if rd_hst_PCK:
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

                if wr_hist_PACK:
                    name_list =[]
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
                            name_list.append((item_hist.ind, buf_dt + buf_s.replace('.', ',')))

                    ''' rewrite data from table ARCHIV_PACK & PACK_TODAY & DATA ----'''
                    self.cur.execute('DELETE FROM ' + 'hist_PACK')
                    self.cur.executemany('INSERT INTO ' + 'hist_PACK' + ' VALUES' + '(?,?)', name_list)
                    self.conn.commit()

                if clc_ASK_BID:
                    ''' init  table ARCHIV_PACK  --------------------'''
                    self.arr_pk  = []  # Class_str_PCK()
                    fAsk, fBid = range(2)
                    for idx, item in enumerate(self.arr_fut): # change STRINGs
                        if idx % 1000 == 0:  print(idx, end='\r')
                        arr_bb = Class_str_PCK()
                        arr_bb.ind, arr_bb.dt  = item.ind_s, item.dt
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

                if clc_EMA:
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

        except Exception as ex:
            err_msg = 'op_archiv / ' + str(ex)
            r_prn = [1, err_msg]
            r_op_archiv = [1, err_msg]
            print(err_msg)

        return r_op_archiv
#=======================================================================
def event_menu(event, db_ARCHIV):
    #-------------------------------------------------------------------
    os.system('cls')  # on windows
    if event == 'prn_cfg_PACK'  :
        print('prn_cfg_PACK...')
        rq = db_ARCHIV.prn(p_cfg_PACK = True)
    #-------------------------------------------------------------------
    if event == 'prn_arr_FUT'  :
        print('prn_arr_FUT...')
        rq = db_ARCHIV.prn(p_arr_fut  = True)
    #-------------------------------------------------------------------
    if event == 'prn_arr_PACK'  :
        print('prn_arr_PACK...')
        rq = db_ARCHIV.prn(p_arr_pk   = True)
    #-------------------------------------------------------------------
    if event == 'rd_cfg_PACK'  :
        print('rd_cfg_PACK...')
        rq = db_ARCHIV.op(rd_cfg_PACK = True)
    #-------------------------------------------------------------------
    if event == 'rd_hst_FUT'   :
        print('rd_hst_FUT...')
        rq = db_ARCHIV.op(rd_hst_FUT = True) #rd_hist_FUT
    #-------------------------------------------------------------------
    if event == 'rd_hst_PCK'  :
        print('rd_hst_PCK...')
        rq = db_ARCHIV.op(rd_hst_PCK = True) # rd_hist_PACK
    #-------------------------------------------------------------------
    if event == 'wr_cfg_PACK'  :
        print('wr_cfg_PACK...')
        rq = db_ARCHIV.op(wr_cfg_PACK = True) # wr_cfg_PACK
    #-------------------------------------------------------------------
    if event == 'wr hist_FUT'   :
        # test array to write in DB
        db_ARCHIV.buf_arc = [[1564771509, '02.08.2019 18:45:09|22330|22334|23042|23048|51207|51244|41607|41631|4238|4240|5662|5669|144912|145063|19623|19645|129450|129460|2693,65|2694|129605|129983|18198|18220|73876|74066|32303|32384|27099|27138|7990|7998|8286|8308|98810|99112|26222|26273|157054|157864|'],]
        print('wr hist_FUT...')
        rq = db_ARCHIV.op(wr_hist_FUT = True)
    #-------------------------------------------------------------------
    if event == 'wr hist_PACK'  :
        print('wr hist_PACK...')
        rq = db_ARCHIV.op(wr_hist_PACK = True)
    #-------------------------------------------------------------------
    if event == 'ASK_BID'  :
        print('calc ASK_BID...')
        rq = db_ARCHIV.op(clc_ASK_BID = True)  #calc_ASK_BID_pk
    #-------------------------------------------------------------------
    if event == 'EMA_f'  :
        print('calc EMA_f...')
        rq = db_ARCHIV.op(clc_EMA = True) #  calc_EMA_pk
    #-------------------------------------------------------------------
    if event is None or event == 'Quit' or event == 'Exit':
        rq = [0,'Finish']

    print('rq = ', rq)
#=======================================================================
def main():
    while True:  # init db_ARCHIV --------------------------------------
        c_dir = os.path.abspath(os.curdir)
        #bp()
        path_ARCHIV = c_dir + '\\DB\\term_archiv.sqlite'
        print(path_ARCHIV)
        db_ARCHIV = Class_term_ARCHIV(path_ARCHIV)
        lg_FILE   = Class_LOGGER(c_dir + '\\LOG\\d_logger.log')

        rq = db_ARCHIV.op(
                        rd_cfg_PACK  = True,
                        rd_hst_FUT   = True, #rd_hist_FUT
                        rd_hst_PCK   = True, #rd_hist_PACK
                        )
        if rq[0] != 0 :
            print('INIT db_ARCHIV is not OK')
            print(' '.join(str(e) for e in rq))
        else:
            print('INIT cfg_data_hist ARCHIV = > ', rq)
            if len(db_ARCHIV.nm) == 0:
                print('cfg_PACK can not be EMPTY !')
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
        ['PRINT arc  ', ['prn_cfg_PACK', '---', 'prn_arr_FUT', '---', 'prn_arr_PACK'],],
        ['READ  arc  ', ['rd_cfg_PACK',  '---', 'rd_hst_FUT',  '---', 'rd_hst_PCK']  ,],
        ['WRITE arc  ', ['wr_cfg_PACK',  '---', 'wr hist_FUT', '---', 'wr hist_PACK'],],
        ['CALC',        ['ASK_BID',      '---', 'EMA_f',       '---', 'cnt'] ,],
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
