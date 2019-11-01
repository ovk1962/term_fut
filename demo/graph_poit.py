#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  graph_poit.py
#
#  Copyright 2019 OVK <ovk.rus@gmail.com>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#
import math
import PySimpleGUI as sg

def main():

    X_bottom_left = -100
    Y_bottom_left = -1000
    X_top_right   = 100
    Y_top_right   = 1000
    layout = [[sg.Graph(canvas_size=(440, 220),
                    graph_bottom_left=(X_bottom_left, Y_bottom_left),
                    graph_top_right  =(X_top_right,   Y_top_right),
                    background_color='white',
                    key='graph')],
              [sg.Button('My_But_1'), sg.Button('My_But_2'),  sg.Button('My_But_PLUS'), sg.Quit(auto_size_button=True)],
            ]
    window = sg.Window('Graph of Sine Function').Layout(layout)
    window.Finalize()


    graph = window.FindElement('graph')
    graph.DrawLine((X_bottom_left,0),  (X_top_right,0))
    graph.DrawLine((0, Y_bottom_left), (0,Y_top_right))
    k_axis_Y = 900
    for x in range(X_bottom_left, X_top_right):
        y = math.sin(x/20)*k_axis_Y
        if -100 < x < -30:
            graph.DrawPoint((x,y),size=3, color='red')
        elif -300 < x < 0:
            graph.DrawPoint((x,y),size=1, color='blue')
        else:
            x_prev = x - 1
            y_prev = math.sin(x_prev/20)*k_axis_Y
            graph.DrawLine((x_prev,y_prev), (x,y), width=2, color='red')
        #print(x,y)
    #button, values = window.Read()

    while (True):
        # This is the code that reads and updates your window
        event, values = window.Read(timeout=500)
        print(event)
        if event in ('Quit', None):
            break

        if event in ('My_But_1', 'My_But_2', 'My_But_PLUS'):
            graph.Erase()
            graph = window.FindElement('graph')
            graph.DrawLine((X_bottom_left,0),  (X_top_right,0))
            graph.DrawLine((0, Y_bottom_left), (0,Y_top_right))

        if event == 'My_But_1':
            k_axis_Y = 900
            for x in range(X_bottom_left, X_top_right):
                y = math.sin(x/20)*k_axis_Y
                x_prev = x - 1
                y_prev = math.sin(x_prev/20)*k_axis_Y
                graph.DrawPoint((x,y),size=1, color='blue')

        if event == 'My_But_2':
            k_axis_Y = 300
            for x in range(X_bottom_left, X_top_right):
                y = math.sin(x/20)*k_axis_Y
                x_prev = x - 1
                y_prev = math.sin(x_prev/20)*k_axis_Y
                graph.DrawLine((x_prev,y_prev), (x,y), width=2, color='red')

        if event == 'My_But_PLUS':
            k_axis_Y += 100
            if k_axis_Y > 900:
                k_axis_Y = 100
            for x in range(X_bottom_left, X_top_right):
                y = math.sin(x/20)*k_axis_Y
                x_prev = x - 1
                y_prev = math.sin(x_prev/20)*k_axis_Y
                graph.DrawLine((x_prev,y_prev), (x,y), width=1, color='green')

    window.Close()  # Don't forget to close your window!

    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main())
