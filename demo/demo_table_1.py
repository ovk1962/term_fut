#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  demo_table_1.py
#
#  Copyright 2020 OVK <ovk.rus@gmail.com>
#

import PySimpleGUI as sg

def main():
    #layout_COL_buttons = []
    header_list = [' nm ','          koef         ',' nul ',' ema ']
    MAX_ROWS = 7
    MAX_COL = len(header_list)
    matrix = [[str(x + y*10) for x in range(MAX_COL)] for y in range(MAX_ROWS)]
    print(matrix)
    #
    layout = [ [sg.Table(values=matrix,
                            headings=header_list,
                            #max_col_width=5,
                            auto_size_columns=True,
                            key='_table_',
                            justification='center',
                            alternating_row_color='lightblue',
                            num_rows=min(len(matrix), 10) ),
                sg.Column([sg.Button(i)] for i in range(4))],
               [sg.Button('Read'), sg.T(10*''), sg.Exit()]  ]

    window = sg.Window('Table', grab_anywhere=False).Layout(layout)
    while True:
        event, values = window.Read(timeout = 1000)
        print(event)
        print(values)
        if event in [None, 'Exit']:
            break
        if event == 'Read':
            if len(values['_table_']) == 0:
                sg.PopupOK('\n You have to choise ROW !\n',
                        background_color = 'Gold')
            else:
                print(matrix[values['_table_'][0]])
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main())
