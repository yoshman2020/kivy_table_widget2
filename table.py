#!/usr/bin/env python3.9
# -*- coding: utf-8 -*-

# Table module
# Copyright (C) 2021 Yoshman <yoshman2020@gmail.com>
# Copyright (C) 2014 Musikhin Andrey <melomansegfault@gmail.com>

# import kivy
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.core.window.window_sdl2 import WindowSDL
from kivy.lang import Builder
from kivy.graphics import Color, Rectangle
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.splitter import Splitter
from kivy.uix.button import Button, ButtonBehavior
from kivy.graphics import Line
from os.path import join, dirname, abspath
import math
import unicodedata


Builder.load_file(join(dirname(abspath(__file__)), 'table.kv'))


class Table(FocusBehavior, BoxLayout):
    """My table widget"""

    default_col_width = 300

    def __init__(self, **kwargs):
        super(Table, self).__init__(**kwargs)
        self._cols = 2
        self._cols_width = []
        self._chosen_row = 0
        Clock.schedule_once(self.init_ui, 0)
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

    def init_ui(self, dt=0):
        # Getting the LabelPanel object for working with it
        self._label_panel = self.children[1].children[0]
        # Getting the GridTable object for working with it
        self._grid = self.children[0].children[0].children[0]
        # Getting the NumberPanel object for working with it
        self._number_panel = self.children[0].children[0].children[1]
        # Getting the ScrollViewTable object for working with it
        self._scroll_view = self.children[0]

    @ property
    def scroll_view(self):
        return self._scroll_view

    @ property
    def grid(self):
        """ Grid object """
        return self._grid

    @ property
    def label_panel(self):
        """ Label panel object """
        return self._label_panel

    @ property
    def number_panel(self):
        """ Number panel object """
        return self._number_panel

    @ property
    def cols(self):
        """ Get/set number of columns """
        return self._cols

    @ cols.setter
    def cols(self, number=0):
        self._cols = number
        self.grid.cols = number
        for num in range(number):
            sp = NewLabelSplitter(strip_size=4, sizable_from='right',
                                  size_hint_x=None, min_size=10)
            lbl = NewLabel()
            lbl.col = num
            sp.add_widget(lbl)
            sp.fbind(
                'width', self._on_change_label_width, col=num
            )
            sp.width = 10
            self.label_panel.add_widget(sp)
            self._cols_width.append(self.default_col_width)

    @ property
    def cols_width(self):
        """ column width """
        return self._cols_width

    @ cols_width.setter
    def cols_width(self, cols_width=[]):
        left = self.cols - len(cols_width)
        if left:
            for col in range(left):
                cols_width.append(self.default_col_width)

        self._cols_width = cols_width
        self.set_col_width()

    @ property
    def row_count(self):
        """ Get row count in our table """
        grid_item_count = len(self.grid.children)
        count = math.floor(grid_item_count / self._cols)
        remainder = grid_item_count % self._cols
        if remainder > 0:
            count += 1
        return count

    @ property
    def chosen_row(self):
        """ selected row number """
        return self._chosen_row

    @ chosen_row.setter
    def chosen_row(self, value):
        self._chosen_row = value

    def add_button_row(self, *args):
        """
        Add new row to table with Button widgets.
        Example: add_button_row('123', 'asd', '()_+')
        """
        if len(args) == self._cols:
            row_widget_list = []
            for num, item in enumerate(args):
                Cell = type('Cell', (NewCell, Button), {})
                cell = Cell()
                cell.text = item
                self.grid.add_widget(cell)
                # Create widgets row list
                row_widget_list.append(self.grid.children[0])
            # Adding a widget to two-level array
            self._grid._cells.append(row_widget_list)
            self.number_panel.add_widget(NewNumberLabel(
                text=str(self.row_count)))
        else:
            print('ERROR: Please, add %s strings in method\'s arguments' %
                  str(self._cols))

    def add_row(self, *args):
        """
        Add new row to table with custom widgets.
        Example: add_row([Button, text='text'], [TextInput])
        """
        if len(args) == self._cols:
            row_widget_list = []
            for num, item in enumerate(args):
                Cell = type('Cell', (NewCell, item[0]), {})
                cell = Cell()
                for key in item[1].keys():
                    setattr(cell, key, item[1][key])
                cell.width = self.label_panel.children[
                    self._cols - num % self._cols - 1].width
                cell.cell_type = item[0]
                self.grid.add_widget(cell)
                # Create widgets row list
                row_widget_list.append(self.grid.children[0])
            # Adding a widget to two-level array
            self._grid._cells.append(row_widget_list)
            # when label width set to 'auto', width doesn't set. so set texture_size
            lbl = NewNumberLabel()
            lbl.text = str(self.row_count)
            lbl._label.refresh()
            lbl.texture_size = lbl._label._size_texture
            self.number_panel.add_widget(lbl)
            self.set_col_width()
            # Default the choosing
            if len(self.grid.cells) == 1:
                self.choose_row(0, True)
                # self.choose_row(0)

        else:
            print('ERROR: Please, add %s strings in method\'s arguments' %
                  str(self._cols))

    def del_row(self, number):
        """ Delete a row by number """
        if len(self.grid.cells) > number:
            for cell in self.grid.cells[number]:
                self.grid.remove_widget(cell)
            del self.grid.cells[number]
            self.number_panel.remove_widget(self.number_panel.children[0])
            # If was deleted the chosen row
            if self._chosen_row == number:
                self.choose_row(number, True)
                # self.choose_row(number)
        else:
            print('ERROR: Nothing to delete...')

    def del_row_all(self):
        [self.del_row(0) for cell in self.grid.cells[:]]

    def choose_row(self, row_num=0, edit_row=False):
        # def choose_row(self, row_num=0):
        """
        Choose a row in our table.
        Example: choose_row(1)
        """
        if len(self.grid.cells) > row_num:
            for col_num in range(self._cols):
                old_grid_element = self.grid.cells[self._chosen_row][col_num]
                current_cell = self.grid.cells[row_num][col_num]
                old_grid_element._background_color(
                    old_grid_element.color_widget)
                current_cell._background_color(current_cell.color_click)
            self._chosen_row = row_num
            self.on_select()
        elif len(self.grid.cells) == 0:
            print('ERROR: Nothing to choose...')
        else:
            for col_num in range(self._cols):
                old_grid_element = self.grid.cells[self._chosen_row][col_num]
                current_cell = self.grid.cells[-1][col_num]
                old_grid_element._background_color(
                    old_grid_element.color_widget)
                current_cell._background_color(current_cell.color_click)
            self._chosen_row = row_num

        # print('_chosen_row=', self._chosen_row)
        if not edit_row:
            if self.parent:
                self.focus_out(self.parent, False)
            self.focus = True

    def _on_focus(self, instance, value, *largs):
        # without this method, error occurred when set focus
        try:
            super(Table, self)._on_focus(instance, value, *largs)
        except KeyError:
            pass
        pass

    def _on_change_label_width(self, *args, **kwargs):
        """ change label width """
        if not args or len(args) < 2:
            return
        if 'col' not in kwargs:
            return
        col = kwargs['col']
        width = args[1]
        if not self._grid or not self._grid._cells:
            return
        for row in self._grid._cells:
            row[col].width = width
        pass

    def get_east_asian_width_count(self, text):
        """ consider double-byte charactor """
        count = 0
        for c in text:
            if unicodedata.east_asian_width(c) in 'FWA':
                count += 2
            else:
                count += 1
        return count

    def get_auto_width(self, text):
        """ adjust width to the text """
        return self.get_east_asian_width_count(text) * 10

    def set_col_width(self):
        """ set column width """
        col = 0
        for width in self.cols_width:
            tcol = self.cols - col - 1
            if len(self.label_panel.children) < tcol:
                return
            if col < self.cols:
                if width == 'default' or width == '':
                    self.label_panel.children[tcol].width = self.default_col_width
                elif width == 'auto':
                    self.label_panel.children[tcol].width = \
                        self.get_auto_width(
                        self.label_panel.children[tcol].children[1].ids.new_label.text
                    )
                else:
                    self.label_panel.children[tcol].width = width
                col += 1

    def focus_out(self, p, checked):
        """ focus out """
        if not checked and p.parent:
            if not type(p.parent) is WindowSDL:
                self.focus_out(p.parent, False)
        if len(p.children):
            for child in p.children:
                self.focus_out(child, True)
        if hasattr(p, 'focus'):
            p.focus = False
        pass

    def _keyboard_closed(self):
        pass

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        """ Method of pressing keyboard  """
        if not self.focus:
            return
        if keycode[0] == 273:   # UP
            # print(keycode)
            self.scroll_view.up()
        if keycode[0] == 274:   # DOWN
            # print(keycode)
            self.scroll_view.down()
        if keycode[0] == 281:   # PageDown
            # print(keycode)
            self.scroll_view.pgdn()
        if keycode[0] == 280:   # PageUp
            # print(keycode)
            self.scroll_view.pgup()
        if keycode[0] == 278:   # Home
            # print(keycode)
            self.scroll_view.home()
        if keycode[0] == 279:   # End
            # print(keycode)
            self.scroll_view.end()

    def sort_list(self, col, rev):
        """ sort by row """
        if not len(self._grid.cells):
            return

        data_list = []
        for row_num, cell in enumerate(self._grid.cells):
            data = []
            for col_num in range(self._cols):
                data.append(cell[col_num].text)
            data_list.append(data)

        sort_key = self._grid.cells[0][col].sort_key
        if sort_key:
            try:
                data_list.sort(key=lambda x: (
                    sort_key(x[col])), reverse=rev)
            except Exception:
                data_list.sort(key=lambda x: x[col], reverse=rev)
        else:
            data_list.sort(key=lambda x: x[col], reverse=rev)
        for row_num, cell in enumerate(self._grid.cells):
            for col_num in range(self._cols):
                cell[col_num].text = data_list[row_num][col_num]

        # delete △ mark
        for parent in self._label_panel.children:
            if isinstance(parent, NullLabel):
                continue
            child = parent.children[1].canvas.after.children
            if 2 < len(child):
                child.remove(child[2])
                child.remove(child[1])

        # add △ mark
        cols = len(self._label_panel.children) - 1
        label_col = self._label_panel.children[cols - col - 1].children[1]
        points = [
            label_col.pos[0] + label_col.width - 15, label_col.pos[1] + 10,
            label_col.pos[0] + label_col.width - 5, label_col.pos[1] + 10,
            label_col.pos[0] + label_col.width - 10, label_col.pos[1] + 20
        ] if not rev else [
            label_col.pos[0] + label_col.width - 15, label_col.pos[1] + 20,
            label_col.pos[0] + label_col.width - 5, label_col.pos[1] + 20,
            label_col.pos[0] + label_col.width - 10, label_col.pos[1] + 10
        ]
        label_col.canvas.after.add(
            Line(points=points, width=1, close=True))
        pass

    def on_select(self, *args, **kwargs):
        """ override this method when customize the action """
        pass


class ScrollViewTable(ScrollView):
    """ScrollView for grid table"""

    def __init__(self, **kwargs):
        super(ScrollViewTable, self).__init__(**kwargs)
        self.bind(size=self._redraw_widget)
        self._color = [.2, .2, .2, 1]
        # Start scroll_y position
        self.scroll_y = 1

    @ property
    def color(self):
        """ Background color """
        return self._color

    @ color.setter
    def color(self, color):
        with self.canvas.before:
            # Not clear, because error
            self._color = color
            Color(*self._color)
        self._redraw_widget()

    def up(self, row_num=1):
        """ Scrolling up when the chosen row is out of view """
        if self.size != [100.0, 100.0] and (self.parent.row_count != 0):
            if self.parent._chosen_row - row_num > 0:
                self.parent.choose_row(self.parent._chosen_row - row_num)
            else:
                self.parent.choose_row(0)
            grid_height = float(self.children[0].height)
            scroll_height = float(grid_height - self.height)
            cur_cell = self.children[0].children[0].\
                cells[self.parent._chosen_row][0]
            cur_cell_height = float(cur_cell.height)
            cur_row_y = float(cur_cell.y)
            # The convert scroll Y position
            _scroll_y = self.scroll_y * scroll_height + self.height - \
                cur_cell_height
            # Jump to the chosen row
            top_scroll_excess = cur_row_y - cur_cell_height
            down_scroll_excess = cur_row_y + self.height - cur_cell_height
            if _scroll_y > down_scroll_excess or _scroll_y < top_scroll_excess:
                new_scroll_y = 0 + \
                    1 * ((cur_row_y - self.height / 2) / 100) / \
                    (scroll_height / 100)
                if new_scroll_y < 0:
                    self.scroll_y = 0
                else:
                    self.scroll_y = new_scroll_y
            # Scrolling to follows the current row
            if (cur_row_y) > _scroll_y:
                self.scroll_y = self.scroll_y + \
                    1 * (cur_cell_height / 100) / (scroll_height / 100)
            # Stopping the scrolling when start of grid
            if self.scroll_y > 1:
                self.scroll_y = 1
            self._update_mouse(self.effect_y, self.scroll_y)

    def down(self, row_num=1):
        """ Scrolling down when the chosen row is out of view """
        if self.size != [100.0, 100.0] and (self.parent.row_count != 0):
            if self.parent._chosen_row + row_num < self.parent.row_count - 1:
                self.parent.choose_row(self.parent._chosen_row + row_num)
            else:
                self.parent.choose_row(self.parent.row_count - 1)
            grid_height = float(self.children[0].height)
            scroll_height = float(grid_height - self.height)
            cur_cell = self.children[0].children[0].\
                cells[self.parent._chosen_row][0]
            cur_cell_height = float(cur_cell.height)
            cur_row_y = float(cur_cell.y)
            # The convert scroll Y position
            _scroll_y = self.scroll_y * scroll_height
            # Jump to the chosen row
            top_scroll_excess = cur_row_y - self.height + cur_cell_height
            down_scroll_excess = cur_row_y + cur_cell_height
            if _scroll_y < top_scroll_excess or _scroll_y > down_scroll_excess:
                new_scroll_y = 0 + \
                    1 * ((cur_row_y - self.height / 2) / 100) / \
                    (scroll_height / 100)
                if new_scroll_y > 1:
                    self.scroll_y = 1
                else:
                    self.scroll_y = new_scroll_y
            # Scrolling to follows the current row
            if cur_row_y < _scroll_y:
                self.scroll_y = self.scroll_y - \
                    1 * (cur_cell_height / 100) / (scroll_height / 100)
            # Stopping the scrolling when end of grid
            if self.scroll_y < 0:
                self.scroll_y = 0
            self._update_mouse(self.effect_y, self.scroll_y)

    def home(self):
        """ Scrolling to the top of the table """
        if self.parent.row_count != 0:
            self.scroll_y = 1
            self.parent.choose_row(0)
            self._update_mouse(self.effect_y, self.scroll_y)

    def end(self):
        """ Scrolling to the bottom of the table """
        if self.parent.row_count != 0:
            self.scroll_y = 0
            self.parent.choose_row(self.parent.row_count - 1)
            self._update_mouse(self.effect_y, self.scroll_y)

    def pgup(self, row_count=10):
        """ Scrolling up when the chosen row is out of view, but with step """
        if self.parent.row_count != 0:
            self.up(row_count)

    def pgdn(self, row_count=10):
        """
        Scrolling down when the chosen row is out of view, but with step
        """
        if self.parent.row_count != 0:
            self.down(row_count)

    def _update_mouse(self, event, value):
        """ Updating the mouse position """
        if event:
            event.value = (event.max + event.min) * value

    def _redraw_widget(self, *args):
        """ Method of redraw this widget """
        with self.canvas.before:
            Rectangle(pos=self.pos, size=self.size)
        # Editting the number panel width
        number_panel = self.children[0].children[1]
        if number_panel.auto_width and len(number_panel.children) > 0:
            last_number_label = self.children[0].children[1].children[0]
            number_panel.width_widget = last_number_label.texture_size[0] + 10

    def on_scroll_move(self, *args, **kwargs):
        """ scroll with hedder """
        super(ScrollViewTable, self).on_scroll_move(*args, **kwargs)
        self.parent._label_panel.parent.scroll_x = self.scroll_x


class ScrollViewBoxLayout(GridLayout):
    """ScrollView's BoxLayout class"""

    def __init__(self, **kwargs):
        super(ScrollViewBoxLayout, self).__init__(**kwargs)
        self.bind(minimum_height=self.setter('height'))
        # horizontal scroll
        self.bind(minimum_width=self.setter('width'))


class ScrollViewLabel(ScrollView):
    """ horizontal scroll """

    _visible = True

    def __init__(self, **kwargs):
        super(ScrollViewLabel, self).__init__(**kwargs)

    @ property
    def visible(self):
        """ Get/set panel visibility """
        return self._visible

    @ visible.setter
    def visible(self, visible=True):
        if visible:
            self._visible = visible
            self.height = self._height
        else:
            self._visible = visible
            self.height = 0

    def on_scroll_move(self, *args, **kwargs):
        super(ScrollViewLabel, self).on_scroll_move(*args, **kwargs)
        self.parent._scroll_view.scroll_x = self.scroll_x


class LabelPanel(BoxLayout):
    """Panel for column labels"""

    def __init__(self, **kwargs):
        super(LabelPanel, self).__init__(**kwargs)
        self.bind(size=self._redraw_widget)
        # for scroll
        self.bind(minimum_height=self.setter('height'))
        self.bind(minimum_width=self.setter('width'))
        self._visible = True
        self._height = 30
        self._color = [.2, .2, .2, 1]

    @ property
    def labels(self):
        """ List of label objects """
        # add splitter for set column width
        return [child.children[1] if 1 < len(child.children) else child
                for child in reversed(self.children)]

    @ property
    def color(self):
        """ Background color """
        return self._color

    @ color.setter
    def color(self, color):
        self._color = color
        self._redraw_widget()

    @ property
    def visible(self):
        """ Get/set panel visibility """
        return self.parent._visible

    @ visible.setter
    def visible(self, visible=True):
        if visible:
            self.parent._visible = visible
            self.parent.height = self.parent._height
        else:
            self.parent._visible = visible
            self.parent.height = 0

    @ property
    def height_widget(self):
        """ Get/set panel height """
        return self.parent.height

    @ height_widget.setter
    def height_widget(self, height=30):
        if self.parent._visible:
            self.parent._height = height
            self.parent.height = height
            self._height = height
            self.height = height

    def _redraw_widget(self, *args):
        """ Method of redraw this widget """
        with self.canvas.before:
            self.canvas.before.clear()
            if len(self.children) > 0:
                self.children[-1].color = self._color
            Color(*self._color)
            Rectangle(pos=self.pos, size=self.size)


class NumberPanel(BoxLayout):
    """Num panel class"""

    def __init__(self, **kwargs):
        super(NumberPanel, self).__init__(**kwargs)
        self.bind(size=self._redraw_widget)
        self._visible = True
        self._width = 30
        self._color = [.2, .2, .2, 1]
        self._auto_width = True

    @ property
    def auto_width(self):
        """ Auto width this panel """
        return self._auto_width

    @ auto_width.setter
    def auto_width(self, value):
        self._auto_width = value

    @ property
    def color(self):
        """ Background color """
        return self._color

    @ color.setter
    def color(self, color):
        self._color = color
        self._redraw_widget()

    @ property
    def visible(self):
        """ Get/set panel visible """
        return self._visible

    @ visible.setter
    def visible(self, visible=True):
        # Get null label object
        null_label = self.parent.parent.parent.label_panel.children[-1]
        if visible:
            self._visible = visible
            self.width = self._width
            null_label.width = self._width
        else:
            self._visible = visible
            self.width = 0
            null_label.width = 0
            null_label.texture_size = (0, 0)

    @ property
    def width_widget(self):
        """ Get/set panel width """
        return self._width

    @ width_widget.setter
    def width_widget(self, width):
        null_label = self.parent.parent.parent.label_panel.children[-1]
        if self._visible:
            self._width = width
            self.width = width
            null_label.width = width

    def _redraw_widget(self, *args):
        """ Method of redraw this widget """
        with self.canvas.before:
            self.canvas.before.clear()
            Color(*self._color)
            Rectangle(pos=self.pos, size=self.size)


class GridTable(GridLayout):
    """This is the table itself"""

    def __init__(self, **kwargs):
        super(GridTable, self).__init__(**kwargs)
        self.bind(size=self._redraw_widget)
        self.bind(minimum_height=self.setter('height'))
        # for horizontal scroll
        self.bind(minimum_width=self.setter('width'))
        self._color = [.2, .2, .2, 1]
        self._cells = []
        self._current_cell = None

    @ property
    def current_cell(self):
        """ Current cell """
        return self._current_cell

    @ current_cell.setter
    def current_cell(self, value):
        self._current_cell = value

    @ property
    def color(self):
        """ Background color """
        return self._color

    @ color.setter
    def color(self, color):
        self._color = color
        self._redraw_widget()

    @ property
    def cells(self):
        """ Two-level array of cells """
        return self._cells

    def _get_row_index(self, item_object):
        """ Get select item index """
        for index, child in enumerate(reversed(self.children)):
            if item_object == child:
                columns = self.parent.parent.parent._cols
                row_index = math.floor(index / columns)
                # print(str(row_index), 'row is chosen')
                return row_index
                break

    def _redraw_widget(self, *args):
        """ Method of redraw this widget """
        self.parent.parent.color = self._color
        # Hide the grid view and the number panel if the grid view is empty
        if len(self.children) == 0:
            self.height = .01
            self.parent.children[-1].height = .01


class NewCell(object):
    """Grid/button element for table"""

    def __init__(self, **kwargs):
        super(NewCell, self).__init__(**kwargs)
        self.bind(size=self._redraw_widget)
        self.bind(on_press=self._on_press_button)
        self._color_widget = [1, 1, 1, 1]
        # color when click
        self._color_click = [0.8, 0.8, 0.8, 1]
        self._cell_type = Button
        self._sort_key = None

    def _background_color(self, value):
        """ Set the background color """
        self.background_color = value

    @ property
    def color_widget(self):
        """ Cell color """
        return self._color_widget

    @ color_widget.setter
    def color_widget(self, value):
        self._color_widget = value
        self.background_color = value

    @ property
    def color_click(self):
        """ Cell click color """
        return self._color_click

    @ color_click.setter
    def color_click(self, value):
        self._color_click = value

    @ property
    def cell_type(self):
        """ type of cell """
        return self._cell_type

    @ cell_type.setter
    def cell_type(self, value):
        self._cell_type = value

    @ property
    def sort_key(self):
        """ sort key """
        return self._sort_key

    @ sort_key.setter
    def sort_key(self, value):
        self._sort_key = value

    @ property
    def data(self):
        """ cell data """
        return self._data

    @ data.setter
    def data(self, value):
        self._data = value

    def _on_press_button(self, *args):
        """ On press method for current object """
        self.parent.current_cell = args[0]
        self.state = 'normal'
        # print('pressed on grid item')
        self.main_table = self.parent.parent.parent.parent
        self.grid = self.parent
        self.main_table.choose_row(self.grid._get_row_index(self))

    def _redraw_widget(self, *args):
        """ Method of redraw this widget """
        # Editting a height of number label in this row
        if not self.parent:
            return
        for num, line in enumerate(self.parent.cells):
            for cell in line:
                if cell == self:
                    self.parent.parent.children[1].children[-(
                        num + 1)].height = self.height
                    break
                break


class NewLabelSplitter(Splitter):
    """ Change label width Splitter """

    def __init__(self, **kwargs):
        super(NewLabelSplitter, self).__init__(**kwargs)
        self.padding = 0
        self.spacing = 0
    pass


class NewLabel(ButtonBehavior, BoxLayout):
    # class NewLabel(Button):
    """Label element for label panel"""

    def __init__(self, **kwargs):
        super(NewLabel, self).__init__(**kwargs)
        self.bind(on_press=self._on_press_button)
        # modify column width when label changed
        self.fbind('text', self._on_text)
        self._rev = False

    @ property
    def col(self):
        """ column index """
        return self._col

    @ col.setter
    def col(self, col):
        self._col = col

    @ property
    def rev(self):
        """ sort(asc,desc) """
        return self._rev

    @ rev.setter
    def rev(self, rev):
        self._rev = rev

    @ property
    def text(self):
        """ text of label """
        return self.ids.new_label.text

    @ text.setter
    def text(self, text):
        self.ids.new_label.text = text

    def _on_press_button(self, touch=None):
        """ On press method for current object """
        # Disable a click
        self.state = 'normal'
        # print('pressed on name label')
        # sort
        self.parent.parent.parent.parent.sort_list(self._col, self._rev)
        self._rev = not self._rev

    def _on_text(self, *args, **kwargs):
        """ adjust auto column width when change the label """
        self.parent.parent.parent.parent.set_col_width()


class NullLabel(Button):
    """Num Label object class"""

    _color = None

    def __init__(self, **kwargs):
        super(NullLabel, self).__init__(**kwargs)
        self.bind(size=self._redraw_widget)
        self.bind(on_press=self._on_press_button)
        self._color = [.2, .2, .2, 1]

    @ property
    def color(self):
        """ Background color """
        return self._color

    @ color.setter
    def color(self, color):
        self._color = color
        self._redraw_widget()

    def _on_press_button(self, touch=None):
        """ On press method for current object """
        # Disable a click
        self.state = 'normal'
        # print('pressed on null label')

    def _redraw_widget(self, *args):
        """ Method of redraw this widget """
        with self.canvas.before:
            self.canvas.before.clear()
            Color(*self._color)
            Rectangle(pos=self.pos, size=self.size)


class NewNumberLabel(Button):
    """Num Label object class"""

    def __init__(self, **kwargs):
        super(NewNumberLabel, self).__init__(**kwargs)
        self.bind(on_press=self._on_press_button)

    def _on_press_button(self, touch=None):
        """ On press method for current object """
        self.state = 'normal'
        # print('pressed on number label')
