class Class_sPACK():
    pAsk, pBid, EMAf, EMAf_r, cnt_EMAf_r = range(5)
    def __init__(self):  
        self.dt  = ''
        self.arr = []

st= '30.08.2019 10:00:10 -42805 -41628 -33366,2 -33300 -111|-775 -759 -738,6 -735 -11|5322 5338 5333,2 5340 9|529 554 749,0 750 -8|-1943 -1906 -1697,1 -1695 -26|-925 -911 -811,3 -810 -10|-1281 -1222 -1096,1 -1095 -15|-8465 -8422 -8178,7 -8175 -5|-835 -799 -594,7 -585 -5|-6460 -6382 -7330,6 -7320 13|-27076 -26882 -26663,2 -26655 -4|-16116 -15764 -15362,4 -15300 -18|-18471 -18129 -17393,0 -17300 -8|'

# parsing from STR to INT
buf = st.replace(',','.').split('|')
del buf[-1]
s = Class_sPACK()
for cn, item in enumerate(buf):
    if cn == 0 : s.dt = item.split(' ')[0:2]
    ind_0 = 0 if cn != 0 else 2
    s.arr.append([float(f) for f in item.split(' ')[ind_0:]])
        
print('dt  = ', s.dt)
print('arr = ', s.arr)
nom_pck = 0
print('First PACK = ['+'0'+']',            s.arr[nom_pck])
nom_pck = len(s.arr)-1
print('Last  PACK = [', str(nom_pck), ']', s.arr[nom_pck])
print('Last  PACK[pAsk]       ',  s.arr[nom_pck][s.pAsk])
print('Last  PACK[pBid]       ',  s.arr[nom_pck][s.pBid])
print('Last  PACK[EMAf]       ',  s.arr[nom_pck][s.EMAf])
print('Last  PACK[EMAf_r]     ',  s.arr[nom_pck][s.EMAf_r])
print('Last  PACK[cnt_EMAf_r] ',  s.arr[nom_pck][s.cnt_EMAf_r])

# parsing from INT to STR
st_p = ''
for item in s.arr:
    for jtem in item:
        st_p += ''.join(str(int(jtem))) + ' '
    st_p = st_p[:-1]
    st_p += '|'
    st_p = st_p.replace('.',',')
st_p = ' '.join(s.dt) + ' ' + st_p

print('st_p = ', st_p)
print('st   = ', st)