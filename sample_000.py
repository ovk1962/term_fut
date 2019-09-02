class Class_sPACK():
    pAsk, pBid, EMAf, EMAf_r, cnt_EMAf_r = range(5)
    def __init__(self):  
        self.dt  = ''
        self.arr = []
    
class Class_sFUT():
    sP_code, sRest, sVar_mrg, sOpen_prc, sLast_prc, sAsk, sBuy_qty, sBid, sSell_qty, sFut_go, sOpen_pos = range(11)
    def __init__(self):  
        self.arr = []
        
class Class_str_FUT():
    fAsk, fBid = range(2)
    def __init__(self):
        self.ind_s, self.dt, self.arr  = 0, '', []

    def prnt(self):
        print(self.ind_s, '  ', self.dt)
        for i, item in enumerate(self.arr): print(i, item)    
        
st= '30.08.2019 10:00:10 -42805 -41628 -33366,2 -33300 -111|-775 -759 -738,6 -735 -11|5322 5338 5333,2 5340 9|529 554 749,0 750 -8|-1943 -1906 -1697,1 -1695 -26|-925 -911 -811,3 -810 -10|-1281 -1222 -1096,1 -1095 -15|-8465 -8422 -8178,7 -8175 -5|-835 -799 -594,7 -585 -5|-6460 -6382 -7330,6 -7320 13|-27076 -26882 -26663,2 -26655 -4|-16116 -15764 -15362,4 -15300 -18|-18471 -18129 -17393,0 -17300 -8|'

buf = st.replace(',','.').split('|')
del buf[-1]
s = Class_sPACK()
for cn, item in enumerate(buf):
    if cn == 0 : s.dt = item.split(' ')[0:2]
    ind_0 = 0 if cn != 0 else 2
    s.arr.append([float(f) for f in item.split(' ')[ind_0:]])

#print('dt  = ', s.dt)
#print('arr = ', s.arr)
    
nom_pck = 0
#print('First PACK = ', nom_pck, '\n', s.arr[nom_pck])
nom_pck = -1
#print('Last  PACK = ', nom_pck, '\n', s.arr[nom_pck])
#print('Last  PACK[pAsk]       ',  s.arr[nom_pck][s.pAsk])
#print('Last  PACK[pBid]       ',  s.arr[nom_pck][s.pBid])
#print('Last  PACK[EMAf]       ',  s.arr[nom_pck][s.EMAf])
#print('Last  PACK[EMAf_r]     ',  s.arr[nom_pck][s.EMAf_r])
#print('Last  PACK[cnt_EMAf_r] ',  s.arr[nom_pck][s.cnt_EMAf_r])

st_p = ''
for item in s.arr:
    for jtem in item:
        st_p += ''.join(str(int(jtem))) + ' '
    st_p = st_p[:-1]
    st_p += '|'
    st_p = st_p.replace('.',',')
    
st_p = ' '.join(s.dt) + ' ' + st_p

#print('st_p = ', st_p)
#print('st   = ', st)

sf= 'SRU9|0|0|0|22507|22507|786|22509|771|3901,8|698224|0|'

buf = sf.replace(',','.').split('|')
del buf[-1]
#print(buf)
f = Class_sFUT()
f.arr = [float(f) if f.replace('.','',1).isdigit() else f for f in buf]
#print(f.arr[f.sP_code], f.arr[f.sRest], '\n', f.arr)

st_f = (123456, '30.08.2019 10:00:10|22273|22282|23441|23450|53879|53943|40810|40838|3875|3878|5406|5412|155905|156050|19478|19485|128460|128470|2718,4|2719,1|128664|129130|17289|17341|72507|72624|32202|32241|26543|26615|7332|7344|8131|8170|96124|96278|26510|26539|151675|152525|',)

print(st_f)
arr_fut  = []
st_FUT = Class_str_FUT()
st_FUT.ind_s = st_f[0]
st_FUT.dt    = st_f[1].split('|')[0]
arr_buf      = st_f[1].replace(',', '.').split('|')[1:-1]
for item in (zip(arr_buf[::2], arr_buf[1::2])):
    st_FUT.arr.append([float(item[0]), float(item[1])])

print(st_FUT.ind_s)
print(st_FUT.dt)
print(st_FUT.arr)
#st_FUT.prnt()