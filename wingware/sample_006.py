class Class_str_FUT():
    fAsk, fBid = range(2)
    def __init__(self):
        self.ind_s, self.dt, self.arr  = 0, '', []

    def prnt(self):
        print(self.ind_s, '  ', self.dt)
        for i, item in enumerate(self.arr): print(i, item) 

fut_SR = Class_str_FUT()
SR = fut_SR
fut_SR.arr = [1,2,3]
print('fut_SR.arr = ', fut_SR.arr)
print('SR.arr     = ', SR.arr)

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