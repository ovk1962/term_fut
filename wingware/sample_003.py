#class c():
#    fAsk, fBid = range(2)
#    pAsk, pBid, EMAf, EMAf_r, cnt_EMAf_r = range(5)
#    sP_code, sRest, sVar_mrg, sOpen_prc, sLast_prc, sAsk, sBuy_qty, sBid, sSell_qty, sFut_go, sOpen_pos = range(11)
#
#print(type(c.fAsk), 'c.fAsk = ', c.fAsk)
#print(type(c.pBid), 'c.pBid = ', c.pBid)
#print(type(c.sVar_mrg), 'c.sVar_mrg = ', c.sVar_mrg)

import smtplib 
import ssl 

def send_email(): 
    port = 465  # For SSL 
    smtp_server = "smtp.gmail.com" 
    sender_email = "mobile.ovk@gmail.com" 
    receiver_email = "mobile.ovk@gmail.com" 
    password = "20066002" 
    message = """Subject: Just TEST e-mail from mobile.ovk !""" 
  
    context = ssl.create_default_context() 
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server: 
        print("Sending email") 
        server.login(sender_email, password) 
        server.sendmail(sender_email, receiver_email, message) 
        
send_email() 