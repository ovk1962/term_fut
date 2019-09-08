from enum import Enum, auto 
class cst(Enum):
    ZOMBIE  = auto()
    WARRIOR = auto()
    BEAR    = auto()
    pAsk, pBid, EMAf, EMAf_r, cnt_EMAf_r = range(5)
    
print(cst())
