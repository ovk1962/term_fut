#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      OVK
#
# Created:     18.05.2020
# Copyright:   (c) OVK 2020
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import sys
if sys.version_info[0] >= 3:
    import PySimpleGUI as sg
else:
    import PySimpleGUI27 as sg

"""
    Simple field validation
    Input field should only accept digits.
    If non-digit entered, it is deleted from the field
"""

def main():
    layout_ROW_buttons = [[sg.Button(i) for i in range(4)]]    # A list of buttons is created - STRING(Row) of Buttons
    #print(layout_ROW_buttons)
    layout_COL_buttons = [[sg.Button(i)] for i in range(4)]    # a List of lists of buttons.  Notice the ] after Button - Column of Buttons
    #print(layout_COL_buttons)

    #layout = layout_ROW_buttons
    #layout += sg.Column(layout_COL_buttons)
    #layout += [sg.Column(layout_COL_buttons), [sg.OK()]]
    #layout += [[sg.Checkbox('P'+str(i)) for i in range(4)]]    # a List of lists of buttons.  Notice the ] after Button - Column of Buttons

    #for radio_num in range(5):                  # loop through 5 radio buttons and add to row
    #    layout += [sg.Radio('', group_id=qnum, size=(7, 2), key=(qnum, radio_num))]

    col = []
    for i in range(4):
       col.append( [sg.Text('col Row 2'), sg.Input('col input 1'), sg.Checkbox('P'+str(i))])
       #[sg.Text('col Row 2'), sg.Input('col input 1'), sg.Checkbox('P1')],
       #[sg.Text('col Row 3'), sg.Input('col input 2'), sg.Checkbox('P2')],
       #[sg.Text('col Row 4'), sg.Input('col input 3'), sg.Checkbox('P3')],
       #[sg.Text('col Row 5'), sg.Input('col input 4'), sg.Checkbox('P4')]
       #]

    layout = [
                [sg.Column(layout_COL_buttons), sg.Column(layout_COL_buttons),
                 sg.Column(layout_COL_buttons),
                 sg.Text('Enter some info'), sg.Input()],
                [sg.Exit()]]

    #layout.append(sg.Cancel())

    window = sg.Window('Generated Layouts').Layout(layout)

    event, values = window.Read()
    print(event, values)
    window.Close()

if __name__ == '__main__':
    import sys
    sys.exit(main())
