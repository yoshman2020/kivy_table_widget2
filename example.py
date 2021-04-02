#!/usr/bin/env python3.9
# -*- coding: utf-8 -*-

# Example module
# Copyright (C) 2021 Yoshman <yoshman2020@gmail.com>
# Copyright (C) 2014 Musikhin Andrey <melomansegfault@gmail.com>

from kivy.resources import resource_add_path
from kivy.core.text import LabelBase, DEFAULT_FONT
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty
from kivy.core.window import Window
from kivy.app import App
from kivy.clock import Clock
from kivy.config import Config
from kivy.lang import Builder

import random

Config.set("input", "mouse", "mouse, disable_multitouch")
Window.size = (500, 300)

resource_add_path('./fonts')
LabelBase.register(DEFAULT_FONT, 'mplus-2c-regular.ttf')

Builder.load_string('''
#:kivy 2.0
#:import Table table

<MainScreen>:
    Table:
        id: my_table
''')


class MainScreen(BoxLayout):
    """docstring for MainScreen"""

    my_table = ObjectProperty()

    def __init__(self):
        super(MainScreen, self).__init__()
        Clock.schedule_once(self.init_ui, 0)

    def init_ui(self, dt=0):
        self.my_table = self.ids.my_table
        self.my_table.cols = 3
        self.my_table.cols_width = [300, 500, 'auto']
        for i in range(10):
            self.my_table.add_row([Button, {'text': 'button%s' % i,
                                            'sort_key': float,
                                            'color_widget': [0, 0, 0.5, 1],
                                            'color_click': [0, 1, 0, 1]
                                            }],
                                  [TextInput, {'text': str(random.uniform(0, 100)),
                                               'sort_key': float,
                                               'color_click': [1, 0, .5, 1]
                                               }],
                                  [Button, {'text': self.randomname(5),
                                            'color_widget': [1, 1, 1, 1],
                                            'color_click': [0.8, 0.8, 0.8, 1]
                                            }],
                                  )
        self.my_table.scroll_view.bar_width = 10
        self.my_table.scroll_view.scroll_type = ['bars']
        self.my_table.grid.cells[0][0].text = 'edited button text'
        self.my_table.grid.cells[1][1].text = 'edited textinput text'
        self.my_table.grid.cells[3][0].height = 100
        self.my_table.label_panel.labels[1].text = '列１'
        self.my_table.label_panel.labels[2].text = '列２'
        self.my_table.label_panel.labels[3].text = '列３'
        # print("ROW COUNT:", self.my_table.row_count)

    def randomname(self, n):

        words = ["あ", "い", "う", "え", "お", "か", "き", "く", "け", "こ", "さ", "し", "す", "せ", "そ", "た", "ち", "つ", "て", "と", "な", "に", "ぬ",
                 "ね", "の", "は", "ひ", "ふ", "へ", "ほ", "ま", "み", "む", "め", "も", "や", "ゆ", "よ", "ら", "り", "る", "れ", "ろ", "わ", "を", "ん"]
        word = ""
        for i in range(n):
            word += words[random.randint(0, len(words) - 1)]
        return word

        # return ''.join(random.choices(string.ascii_letters + string.digits, k=n))


class TestApp(App):
    """ App class """

    def build(self):
        return MainScreen()

    def on_pause(self):
        return True


if __name__ in ('__main__', '__android__'):
    TestApp().run()
