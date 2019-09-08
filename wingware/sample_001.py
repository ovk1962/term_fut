koef = '0:1:SR,9:-10:MX'  

arr_koef = []
for item_k in koef.split(','):
#    arr_koef.append([int(item_k.split(':')[0]), int(item_k.split(':')[1]), item_k.split(':')[2]])
    arr_koef.append([int(f) if f.replace('-','').isdigit() else f for f in item_k.split(':')])

print('koef     = ', koef)
print('arr_koef = ', arr_koef)
print('STR arr_koef = ', str(arr_koef))  # !!!

koef = [[7, 1, 'SR'], [9, -10, 'MX']]
arr_koef = ''
for item in koef:
    str_koef = ':'.join([str(f) for f in item])
    arr_koef += str_koef + ','
arr_koef = arr_koef[:-1]
print(arr_koef)
#print(str_ema)
#[float(f) if f.replace('.','',1).isdigit() else f for f in buf]
        





