#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  demo_a_few_UI.py
#
#
import os
import PySimpleGUI as sg
#=======================================================================
menu_def = [sg.Menu([
            ['MODE', [  'AUTO', 'Manual',  'Test',   'Calendar', '---',
                        'SLIDER_COMBO','---',
                        'Exit',],]],
            tearoff=False, key='MENU') ]
#=======================================================================
def open_AUTO(wndw):
    os.system('cls')  # on windows
    wndw.Close()
    layout_AUTO =[ menu_def,
                [sg.Input(key='-AUTO IN-')],
                [sg.Button('AUTO', key='-AUTO BT-'), sg.Exit()]]
    sg.ChangeLookAndFeel('GreenTan')
    wndw = sg.Window('AUTO', location=(100, 100)).Layout(layout_AUTO)
    return wndw
#=======================================================================
def event_menu_AUTO(ev, val, wndw):
    rq = [0,ev]
    #-------------------------------------------------------------------
    if ev == '-AUTO BT-'  :
        if 'OK' == sg.PopupOKCancel('\n' + val['-AUTO IN-'] + '\n'):
            print('Ok')
        else:
            print('Cancel')
    #-------------------------------------------------------------------
    print('rq = ', rq)
#=======================================================================
def open_MANUAL(wndw):
    wndw.Close()
    os.system('cls')  # on windows
    layout_MANUAL =[ menu_def,
                [sg.Input(key='-MANUAL IN-')],
                [sg.Button('MANUAL', key='-MANUAL BT-'), sg.Exit()]]
    sg.ChangeLookAndFeel('BlueMono')
    wndw = sg.Window('Manual', location=(300, 200)).Layout(layout_MANUAL)
    return wndw
#=======================================================================
def open_TEST(wndw):
    wndw.Close()
    os.system('cls')  # on windows
    layout_TEST =[ menu_def,
                [sg.Input(key='-TEST IN-')],
                [sg.Button('TEST', key='-TEST BT-'), sg.Exit()]]
    sg.ChangeLookAndFeel('TanBlue')
    wndw = sg.Window('Test', location=(500, 300)).Layout(layout_TEST)
    return wndw
#=======================================================================
def open_CALENDAR(wndw):
    wndw.Close()
    os.system('cls')  # on windows
    layout_CALENDAR =[ menu_def,
                [sg.T('Calendar Test')],
                [sg.In('', size=(20,1), key='-CALENDAR IN-'),
                 sg.CalendarButton('Choose Date', target='-CALENDAR IN-', key='-CALENDAR date-')],
                [sg.Button('CALENDAR', key='-CALENDAR BT-'), sg.Exit()]]
    sg.ChangeLookAndFeel('BrownBlue')
    wndw = sg.Window('Calendar', location=(700, 400)).Layout(layout_CALENDAR)
    return wndw
#=======================================================================
def open_SLIDER(wndw):
    wndw.Close()
    os.system('cls')  # on windows
    column1 = [
        [sg.Text('Pick operation', size = (15,1), font = ('Calibri', 12, 'bold'))],
        [sg.InputCombo(['Add','Subtract','Multiply','Divide'], default_value = 'Add', size = (10,6))],
        [sg.Text('', size =(1,4))]]
    column2 = [
        [sg.ReadButton('Submit', font = ('Calibri', 12, 'bold'), )], #button_color = ('White', 'Red'))],
        [sg.Text('Result:', font = ('Calibri', 12, 'bold'))],[sg.InputText(size = (12,1), key = '_result_')]
        ]
    layout_SLIDER_COMBO = [ menu_def,
        [sg.Text('Slider and Combo box demo', font = ('Calibri', 14,'bold'))],
        [sg.Slider(range = (-9, 9),orientation = 'v', size = (5,20), default_value = -3),
          sg.Slider(range = (-9, 9),orientation = 'v', size = (5, 20), default_value = 4),
          sg.Text('   '), sg.Column(column1), sg.Column(column2)]]
    sg.ChangeLookAndFeel('NeutralBlue')
    wndw = sg.Window('SLIDER_COMBO', location=(750, 150)).Layout(layout_SLIDER_COMBO)
    return wndw
#=======================================================================
def event_menu_SLIDER(ev, val, wndw):
    rq = [0,ev]
    #-------------------------------------------------------------------
    if ev == 'Submit'  :
        result = 0.0
        if val[2] == 'Add':
            result = val[0] + val[1]
        elif val[2] == 'Multiply':
            result = val[0] * val[1]
        elif val[2] == 'Subtract':
            result = val[0] - val[1]
        elif val[2] == 'Divide':              #check for zero
            if val[1] ==0:
                sg.Popup('Second value can\'t be zero')
                result = 'NA'
            else:
                result = val[0] / val[1]
        wndw.FindElement('_result_').Update(result)
    #-------------------------------------------------------------------
    print('rq = ', rq)
#=======================================================================
def main():
    wndw = sg.Window('AUTO').Layout([menu_def, [sg.Exit()]])
    wndw = open_AUTO(wndw)
    while True:
        # for sg.Input must be => wndw.Read()  OR  timeout > 10000
        event, values = wndw.Read(timeout = 10000)
        print('event = ', event, '     values =', values)
        if event in (None, 'Exit'): break
        if event == '__TIMEOUT__':
            pass
        else:
            if event in ['AUTO', 'Manual', 'Test', 'Calendar', 'SLIDER_COMBO']:
                if event == 'AUTO':
                    wndw = open_AUTO(wndw)
                if event == 'Manual':
                    wndw = open_MANUAL(wndw)
                if event == 'Test':
                    wndw = open_TEST(wndw)
                if event == 'Calendar':
                    wndw = open_CALENDAR(wndw)
                if event == 'SLIDER_COMBO':
                    wndw = open_SLIDER(wndw)
            else:
                event_menu_AUTO(event, values, wndw)
                event_menu_SLIDER(event, values, wndw)

    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main())
