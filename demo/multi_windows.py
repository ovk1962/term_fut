#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  multi_windows.py
#
import PySimpleGUI as sg


def main():

    # Design pattern 1 - First window does not remain active

    layout = [[ sg.Text('Window 1'),],
              [sg.Input(do_not_clear=True)],
              [sg.Text(60*' ', key='_OUTPUT_1')],
              [sg.Button('Launch 2'), sg.Button('Exit')]]

    win1        = sg.Window('Window 1').Layout(layout)
    win2_active = False

    while True:
        ev1, vals1 = win1.Read(timeout=100)
        if ev1 is None or ev1 == 'Exit':
            break
        print(vals1)
        win1.FindElement('_OUTPUT_1').Update(vals1[0])

        if ev1 == 'Launch 2'  and not win2_active:
            win2_active = True
            win1.Hide()
            layout2 = [[sg.Text('Window 2')],       # note must create a layout from scratch every time. No reuse
                       [sg.Text(60*' ', key='_OUTPUT_2')],
                       [sg.Button('Exit')]]

            win2 = sg.Window('Window 2').Layout(layout2)
            while True:
                ev2, vals2 = win2.Read(timeout=100)
                if ev2 is None or ev2 == 'Exit':
                    win2.Close()
                    win2_active = False
                    win1.UnHide()
                    break
                print(vals1)
                win2.FindElement('_OUTPUT_2').Update(vals1[0])

    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main())
