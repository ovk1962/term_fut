#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      OVK
#
# Created:     17.04.2020
# Copyright:   (c) OVK 2020
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import PySimpleGUI as sg
print(sg.__file__)

def main():
    # Design pattern 2 - First window remains active
    menu_def = [['MODE', ['AUTO', 'Manual', '---', 'Exit',]]        ]
    tab1_layout =  [[sg.T('This is inside tab 01')]                 ]
    tab2_layout =  [[sg.T('This is inside tab 020')],
                    [sg.T('This is inside tab 021')],
                    [sg.T('This is inside tab 022')],
                    [sg.T('This is inside tab 023')],
                    [sg.T('This is inside tab 024')],
                    [sg.In(key='-in_tab02-')]                       ]

    layout1 = [[sg.Menu(menu_def)                                   ],
              [sg.TabGroup([[sg.Tab('Tab 1', tab1_layout),
               sg.Tab('Tab 2', tab2_layout)]])                      ],
              [sg.Input(do_not_clear=True, key='-INPUT_1-')         ],
              [sg.Text(text=' ', size=(15,1), key='-in_tab-')       ],
              [sg.Button('Launch 2'),
               sg.Button('Launch 3'),
               sg.Button('Exit')                                   ]]

    layout2 = [ [sg.Text('Window 2')],
                [sg.Input(do_not_clear=True, key='-in_layout_2-')],
                [sg.Button('Close')]]

    layout3 = [ [sg.Text('Window 3')],
                [sg.Input(do_not_clear=True, key='-in_layout_3-')],
                [sg.Text(text=' ', size=(15,1))],
                [sg.Button('Close')]]

    win1 = sg.Window('Window 1', layout1)
    win2_active = False
    win3_active = False

    while True:
        #--- read 'Window 1' -------------------------------------------
        ev1, vals1 = win1.Read(timeout=100)
        print(ev1, vals1)
        if ev1 is None or ev1 == 'Exit':
            break

        #--- open 'Window 2' -------------------------------------------
        if not win2_active and ev1 == 'Launch 2':
            win2_active = True
            win2 = sg.Window('Window 2', layout2)
        if win2_active:
            ev2, vals2 = win2.Read(timeout=100)
            if ev2 is None or ev2 == 'Close':
                win2_active  = False
                win2.Close()

        #--- open 'Window 3' -------------------------------------------
        if not win3_active and ev1 == 'Launch 3':
            win3_active = True
            win3 = sg.Window('Window 3', layout3)
        if win3_active:
            ev3, vals3 = win3.Read(timeout=100)
            win3.FindElement('-in_layout_3-').Update(vals1['-in_tab02-'])
            if ev3 is None or ev3 == 'Close':
                win3_active  = False
                win3.Close()


if __name__ == '__main__':
    main()
