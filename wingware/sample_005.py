class Class_sFUT():
    sP_code, sRest, sVar_mrg, sOpen_prc, sLast_prc, sAsk, sBuy_qty, sBid, sSell_qty, sFut_go, sOpen_pos = range(11)
    def __init__(self):  
        self.arr = []

sf= 'SRU9|0|0|0|22507|22507|786|22509|771|3901,8|698224|0|'
print('sf = ', sf)       
buf = sf.replace(',','.').split('|')
del buf[-1]
print('buf = ', buf)
f = Class_sFUT()
f.arr = [float(f) if f.replace('.','',1).isdigit() else f for f in buf]
print(f.arr[f.sP_code], '   ',f.arr[f.sRest])
print('f.arr = ', f.arr)