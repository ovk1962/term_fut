#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  demo_simul_table.py
#
#  Copyright 2020 OVK <ovk.rus@gmail.com>
#
import PySimpleGUI as sg
def main():
    headings = ['HEADER 1', 'HEADER 2', 'HEADER 3','HEADER 4']
    header =  [[sg.Text('  ')] + [sg.Text(h, size=(14,1)) for h in headings]]
    input_rows = [[sg.Input(size=(15,1), pad=(0,0)) for col in range(4)] for row in range(10)]
    layout = header + input_rows + [[sg.Button('Change'), sg.Quit(auto_size_button=True)]]
    window = sg.Window('Table Simulation',  font='Courier 12', grab_anywhere=False).Layout(layout)

    while True:
        event, values = window.Read()
        print(event, values)
        if event in ('Quit', None):
            break
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main())
