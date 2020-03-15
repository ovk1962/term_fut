#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  conv_hist.py
#
#  Copyright 2020 OVK <ovk.rus@gmail.com>
#
import sys
from datetime import datetime, timezone
if sys.version_info[0] >= 3:
    import PySimpleGUI as sg
else:
    import PySimpleGUI27 as sg

def GetFileToConv():
    form_rows = [[sg.Text('Enter HIST file to converter')],
                 [sg.Text('File HIST',  size=(15, 1)), sg.InputText(key='file_hist'),  sg.FileBrowse()],
                 [sg.Text('File CONV',  size=(15, 1)), sg.InputText(key='file_conv'),  sg.FileBrowse()],
                 [sg.Text('File DELAY', size=(15, 1)), sg.InputText(key='file_delay'), sg.FileBrowse()],
                 [sg.Submit(), sg.Cancel()]]

    window = sg.Window('File Compare')
    event, values = window.Layout(form_rows).Read()
    return event, values

def main():
    sec_10_00 = 35995      # seconds from 00:00 to 09:59:55
    sec_14_00 = 50405      # seconds from 00:00 to 14:00:05
    sec_14_05 = 50695      # seconds from 00:00 to 14:04:55
    #sec_18_45 = 67500      # seconds from 00:00 to 18:45
    sec_18_45 = 67505      # seconds from 00:00 to 18:45
    sec_19_05 = 68695      # seconds from 00:00 to 19:05
    sec_23_50 = 85800      # seconds from 00:00 to 23:50
    button, values = GetFileToConv()
    f1 = values['file_hist']
    f2 = values['file_conv']
    f3 = values['file_delay']

    hist_in_file = []
    delay_file   = []

    if any((button != 'Submit', f1 =='', f2 =='')):
        sg.PopupError('Operation cancelled')
        sys.exit(69)

    # --- This portion of the code is not GUI related ---
    with open(f1, 'r') as file_hist:
        a = file_hist.readlines()
        for i, item in enumerate(a):
            term_dt = item.split('|')[0]
            dtt = datetime.strptime(str(term_dt), "%d.%m.%Y %H:%M:%S")
            cur_time = dtt.second + 60 * dtt.minute + 60 * 60 * dtt.hour
            if (
                (cur_time > sec_10_00  and # from 10:00 to 14:00
                 cur_time < sec_14_00) or
                (cur_time > sec_14_05  and # from 14:05 to 18:45
                 cur_time < sec_18_45) or
                (cur_time > sec_19_05  and # from 19:05 to 23:45
                 cur_time < sec_23_50)):
                    hist_in_file.append(item)

    with open(f2, 'w') as file_conv:
        for item in hist_in_file:
            file_conv.write(item)

    with open(f3, 'w') as delay_file:
        str_buf = 'start = ' + hist_in_file[0].split('|')[0]
        print(str_buf)
        delay_file.write(str_buf + "\n")
        for i, item in enumerate(hist_in_file[2:]):
            dtp = datetime.strptime(str(hist_in_file[i-1].split('|')[0]), "%d.%m.%Y %H:%M:%S")
            prv_time = dtp.second + 60 * dtp.minute + 60 * 60 * dtp.hour
            dtc = datetime.strptime(str(hist_in_file[i-0].split('|')[0]), "%d.%m.%Y %H:%M:%S")
            cur_time = dtc.second + 60 * dtc.minute + 60 * 60 * dtc.hour
            if (cur_time - prv_time) > 60:
                str_buf = 'delay = ' + hist_in_file[i-1].split('|')[0] + ' ... ' + hist_in_file[i-0].split('|')[0]
                print(str_buf)
                delay_file.write("%s\n" % str_buf)
        str_buf = 'last = ' + hist_in_file[-1].split('|')[0]
        print(str_buf)
        delay_file.write(str_buf)



if __name__ == '__main__':
    main()
