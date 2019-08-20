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
            frm = '{:^12}{:^12}{:^12}{:^12}{:^4}'
            s += frm.format('pAsk','pBid','EMAf','EMAf_r','cnt_EMAf_r') + '\n'
            for item in self.pk:
                s += frm.format(item.pAsk, item.pBid, item.EMAf, item.EMAf_r, item.cnt_EMAf_r) + '\n'
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
class Class_term_ARCHIV():
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
        self.hst_pk = []  # list of [[ind_sec string] ... ]
        #self.arr_pack = []  # list of [[ind_sec string] ... ]
        self.arr_pk = []  # list of obj [Class_STR_PACK ... ]

    def prn(self,
            p_cfg_PACK   = False,
            p_hst_fut   = False,
            p_arr_fut   = False,
            p_hst_pk    = False,
            p_arr_pk    = False
            ):
        s = ''
        try:
            if p_cfg_PACK:
                s += ' cfg_PACK _________________________________' + '\n'
                if len(self.nm) > 0:
                    frm = '{: ^5}{: ^15}{}{}{}'
                    s += frm.format('nm','nul','ema[]','        ','koef[]') + '\n'
                    for i, item in enumerate(self.nm):
                        s += frm.format(self.nm[i], str(self.nul[i]), self.ema[i], '   ', self.koef[i])+ '\n'

            if p_hst_fut:
                s += ' hst_fut __________________________________' + '\n'
                hist = self.hst_fut
                s += 'len(hst_fut)   => ' + str(len(hist)) + '\n'
                if len(hist) > 4:
                    s += 'hst_fut[i] TURPLE (float, str_fut) => ' + '\n'
                    s += '0    => '  +  ' '.join(str(h) for h in hist[0]) + '\n'
                    for i in range(1,4):
                        s += str(i) + '    => ' + hist[i][1].split('|')[0] + '\n'
                    s += '. . . . . . . . . . . . . .' + '\n'
                    s += str(len(hist)-1) + ' => ' + hist[-1][1].split('|')[0] + '\n'

            if p_arr_fut:
                s += ' arr_fut __________________________________' + '\n'
                hist = self.arr_fut
                s += 'len(arr_fut)   => ' + str(len(hist)) + '\n'
                if len(hist) > 4:
                    s += 'arr_fut[i] LIST [float, dt_tm, floats] => \n'
                    s += '0    => '  + ' '.join(list(map(lambda x:str(x), hist[0]))) + '\n'
                    for i in range(1,4):
                        s += str(i) + '    => ' + hist[i][1] + '\n'
                    s += '. . . . . . . . . . . . . .' + '\n'
                    s += str(len(hist)-1) + '    => ' + hist[-1][1] + '\n'

            if p_hst_pk:
                s += ' hst_pk _________________________________' + '\n'
                hist = self.hst_pk
                s += 'len(hst_pk)   => ' + str(len(hist)) + '\n'
                if len(hist) > 4:
                    s += 'hst_pk[i] TURPLE (float, str_pack) => ' + '\n'
                    s += '0    => '  +  ' '.join(str(h) for h in hist[0]) + '\n'
                    for i in range(1,4):
                        s += str(i) + '    => ' + hist[i][1].split('|')[0] + '\n'
                    s += '. . . . . . . . . . . . . .' + '\n'
                    s += str(len(hist)-1) + ' => ' + hist[-1][1].split('|')[0] + '\n'

            if p_arr_pk:
                s += ' arr_pk ___________________________________' + '\n'
                hist = self.arr_pk
                s += 'len(arr_pk)   => ' + str(len(hist)) + '\n'
                if len(hist) > 4:
                    for i in range(1,2):
                        s += 'arr_pk[' + str(i) + ']   =>\n' + hist[i].prn()
                    s += '. . . . . . . . . . . . . .' + '\n'
                    s += 'arr_pk[' + str(len(hist)-1) + '] => \n' + hist[-1].prn()

        except Exception as ex:
            r_prn = [1, 'op_archiv / ' + str(ex)]

        return [0, s]

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
                    self.hst_pk = []
                    self.hst_pk = self.cur.fetchall()    # read table name_tbl
                    print('len(hst_pk) = ', len(self.hst_pk))

                    self.arr_pk  = []
                    #for i_str in self.hst_pk:
                    for cnt, i_str in enumerate(self.hst_pk):
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
                        self.arr_pk.append(bp)
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
                        if idx % 1000 == 0:  print(idx, end='\r')
                        bp = Class_STR_PACK()
                        bp.ind = int(item[0])
                        bp.dt, bp.tm  = item[1].split(' ')
                        #
                        bp.pk = [] # list of obj Class_PACK()
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
                            bp.pk.append(Class_sPACK())
                            ask_bid_AVR = 0
                            if idx == 0:
                                null_prc = int((ask_p + bid_p)/2)
                                self.nul[p] = null_prc
                                bp.pk[p].pAsk, bp.pk[p].pBid = 0, 0
                                bp.pk[p].EMAf, bp.pk[p].EMAf_r = 0, 0
                                bp.pk[p].cnt_EMAf_r = 0
                            else:
                                null_prc = self.nul[p]
                                ask_p = int(ask_p - null_prc)
                                bid_p = int(bid_p - null_prc)
                                ask_bid_AVR = int((ask_p + bid_p)/2)
                                bp.pk[p].pAsk = ask_p
                                bp.pk[p].pBid = bid_p
                        self.arr_pk.append(bp)
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
def prn_rq(msg, rq, Prn = True):
    err_msg  = msg
    err_msg += '\n'.join(str(e) for e in rq)
    if Prn  :
        print(err_msg + '\n')
#=======================================================================
def menu_PRINT(db_ARCHIV, b_clear = True,
        b_cfg_pack  = False,
        b_hst_fut   = False,
        b_arr_fut   = False,
        b_hst_pk  = False,
        b_arr_pk    = False,

        ):
    if b_clear:
        os.system('cls')  # on windows

    if b_cfg_pack:
        rq = db_ARCHIV.prn(p_cfg_PACK = True)
        prn_rq('PRINT p_cfg_PACK ARCHIV\n', rq)

    if b_hst_fut:
        rq = db_ARCHIV.prn(p_hst_fut  = True)
        if rq[0] != 0 : prn_rq('PRINT b_hst_fut ARCHIV', rq)
        else: print(rq[1])

    if b_arr_fut:
        rq = db_ARCHIV.prn(p_arr_fut  = True)
        if rq[0] != 0 : prn_rq('PRINT b_arr_fut ARCHIV', rq)
        else: print(rq[1])

    if b_hst_pk:
        rq = db_ARCHIV.prn(p_hst_pk = True)
        if rq[0] != 0 : prn_rq('PRINT b_hst_pk ARCHIV', rq)
        else: print(rq[1])

    if b_arr_pk:
        rq = db_ARCHIV.prn(p_arr_pk   = True)
        if rq[0] != 0 : prn_rq('PRINT b_arr_pk ARCHIV', rq)
        else: print(rq[1])
#=======================================================================
def event_menu(event, db_ARCHIV):
    #-------------------------------------------------------------------
    if event == 'prn cfg_PACK'  :
        menu_PRINT(db_ARCHIV, b_cfg_pack = True)
    #-------------------------------------------------------------------
    if event == 'prn hist_FUT'  :
        menu_PRINT(db_ARCHIV, b_hst_fut  = True)
    #-------------------------------------------------------------------
    if event == 'prn arr_FUT'  :
        menu_PRINT(db_ARCHIV, b_arr_fut = True)
    #-------------------------------------------------------------------
    if event == 'prn hist_PACK'  :
        menu_PRINT(db_ARCHIV, b_hst_pk = True)
    #-------------------------------------------------------------------
    if event == 'prn arr_PACK'  :
        menu_PRINT(db_ARCHIV, b_arr_pk = True)
    #-------------------------------------------------------------------
    if event == 'rd cfg_PACK'  :
        rq = db_ARCHIV.op(rd_cfg_PACK = True)
        prn_rq('db_ARCHIV / rd cfg_PACK', rq)
    #-------------------------------------------------------------------
    if event == 'rd hist_FUT'   :
        rq = db_ARCHIV.op(rd_hist_FUT = True)
        prn_rq('db_ARCHIV / rd_hist_FUT ', rq)
    #-------------------------------------------------------------------
    if event == 'rd hist_PACK'  :
        rq = db_ARCHIV.op(rd_hist_PACK = True)
        prn_rq('db_ARCHIV / rd_hist_PACK ', rq)
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
        prn_rq('db_ARCHIV / wr_hist_FUT ', rq)
    #-------------------------------------------------------------------
    if event == 'wr hist_PACK'  :
        rq = db_ARCHIV.op(wr_hist_PACK = True)
        prn_rq('db_ARCHIV / wr_hist_PACK ', rq)
    #-------------------------------------------------------------------
    if event == 'ASK_BID'  :
        rq = db_ARCHIV.op(calc_ASK_BID_pk = True)
        prn_rq('db_ARCHIV / calc_ASK_BID ', rq)
    #-------------------------------------------------------------------
    if event == 'EMA_f'  :
        rq = db_ARCHIV.op(calc_EMA_pk = True)
        prn_rq('db_ARCHIV / calc_EMA_pk ', rq)
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
                        rd_hist_FUT  = True,
                        rd_hist_PACK = True,
                        )
        if rq[0] != 0 : prn_rq('INIT cfg_hist ARCHIV', rq)
        else:
            print('INIT cfg_data_hist ARCHIV = > ', rq)
            if len(db_ARCHIV.nm) == 0:
                prn_rq('cfg_pack.nm = 0  ', [' ', 'It can not be EMPTY !'] )
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
        ['PRINT arc  ',
            ['prn cfg_PACK', '---',
             'prn hist_FUT', 'prn arr_FUT', '---',
             'prn hist_PACK','prn arr_PACK'],],
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
