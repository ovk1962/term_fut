from enum import Enum, auto 
class cst(Enum):
    ZOMBIE  = auto()
    WARRIOR = auto()
    BEAR    = auto()
    pAsk, pBid, EMAf, EMAf_r, cnt_EMAf_r = range(5)
    
word = 'Python'
print(word)
print(word[-1])
print(word[-2])
print(word[:-1])
print(word[-1:])
print(word[-2:])
print(word[-3:-1])
ln = len(word)
print(word[ln-6:ln-1])