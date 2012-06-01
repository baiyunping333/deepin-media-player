#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 ~ 2012 Deepin, Inc.
#               2011 ~ 2012 Wang Yong
# 
# Author:     Hailong Qiu <qiuhailong@linuxdeepin.com>
# Maintainer: Hailong Qiu <qiuhailong@linuxdeepin.com>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from dtk.ui.draw import draw_pixbuf
from dtk.ui.draw import draw_font
import gtk




class TreeView(gtk.DrawingArea):
    
    def __init__(self, height = 30, font_size = 10, font_color = "#FFFFFF"):
        gtk.DrawingArea.__init__(self)
        
        # root node.
        self.root = Tree()
        self.set_can_focus(True)
        # Init DrawingArea event.
        self.add_events(gtk.gdk.ALL_EVENTS_MASK)        
        self.connect("button-press-event", self.press_notify_event)
        self.connect("motion-notify-event", self.move_notify_event)
        self.connect("expose-event", self.draw_expose_event)
        self.connect("key-press-event", self.key_press_tree_view)
        self.connect("leave-notify-event", self.clear_move_notify_event)
        self.connect("realize", lambda w: self.grab_focus()) # focus key after realize
        # 
        self.height = height # child widget height.
        self.move_height = 0 #
        self.press_height = 0
        # Position y.
        self.draw_y_padding = 0
        # Draw press move bool.
        self.press_draw_bool = False
        self.move_draw_bool = False
        # Font init.
        self.font_size = font_size
        self.font_color = font_color
        # Key map dict.
        self.keymap = {
            "Up"     : self.up_key_press,
            "Down"   : self.down_key_press,
            }
        
    def clear_move_notify_event(self, widget, event): # focus-out-event
        self.move_color = False
        self.queue_draw()
        
    def up_key_press(self):
        self.move_height -= self.height
        
    def down_key_press(self):
        self.move_height += self.height
                
    def key_press_tree_view(self, widget, event):
        keyval = gtk.gdk.keyval_name(event.keyval)
        
        # Up Left.
        if self.keymap.has_key(keyval):
            self.keymap[keyval]()
        
        # Set : 0 < self.move_height > self.allocation.height ->
        if (self.move_height < 0) or (self.move_height > self.allocation.height):
            if self.move_height < 0:
                self.move_height = 0
            elif self.move_height > self.allocation.height:
                self.move_height = int(self.allocation.height) / self.height * self.height
        # expose-evet queue_draw.
        self.queue_draw()
        
    def draw_expose_event(self, widget, event):
        cr = widget.window.cairo_create()
        rect = widget.allocation
        x, y, w, h = rect.x, rect.y, rect.width, rect.height
        
        if self.press_draw_bool:
            cr.set_source_rgba(1, 0, 0, 0.3)
            self.draw_y_padding = int(self.press_height) / self.height * self.height
            cr.rectangle(x, y + self.draw_y_padding, w, self.height)
            cr.fill()
                                    
        if self.move_draw_bool:
            cr.set_source_rgba(0, 0, 1, 0.3)
            self.draw_y_padding = int(self.move_height) / self.height * self.height
            cr.rectangle(x, y + self.draw_y_padding, w, self.height)
            cr.fill()
        
        return True
    
    def set_font_size(self, size):
        if size > self.height / 2:
            size = self.height / 2
        
        self.font_size = size
        
    def press_notify_event(self, widget, event):
        self.press_draw_bool = True
        self.press_height = event.y
        self.queue_draw()
        
    def move_notify_event(self, widget, event):
        self.move_draw_bool = True
        self.move_height = event.y
        self.queue_draw()
        
    def add_node(self,root_name, node_name):
        self.root.add_node(root_name, node_name, Tree())
        
    def sort(self):                
        for key in self.root.child_dict.keys():
            if self.root.child_dict[key].child_dict:
                self.sort2(self.root.child_dict[key])
        
    def sort2(self, node):        
        print "--"        
        for key in node.child_dict.keys():
            print key
            if node.child_dict[key].child_dict:
                self.sort2(node.child_dict[key])
                print "--"
        
        
class Tree(object):
    def __init__(self):
        self.parent_node = None
        self.child_dict = {}
        self.child_show_bool = False
        
        self.name = ""
        self.pixbuf = None
        
        
    def add_node(self, root_name, node_name, node):
        # Root node add child widget.
        if not root_name:
            if node_name and node:
                # Set node.
                node.name = node_name
                self.parent_node = None
                self.child_dict[node_name] = node
        else:    
            for key in self.child_dict.keys():                
                if key == root_name:                    
                    # Set node.
                    node.name = node_name
                    self.parent_node = None
                    self.child_dict[key].child_dict[node_name] = node
                    break                
                
                self.scan_node(self.child_dict[key], root_name, node_name, node)
                    
    def scan_node(self, node, scan_root_name, node_name, save_node):
        if node.child_dict:
            for key in node.child_dict.keys():
                if key == scan_root_name:                    
                    save_node.name = node_name
                    node.child_dict[key].child_dict[node_name] = save_node
                
                else:    
                    self.scan_node(node.child_dict[key], scan_root_name, node_name, save_node)
                    
                    
    def sort(self):                
        for key in self.child_dict.keys():
            if self.child_dict[key].child_dict:
                self.sort2(self.child_dict[key])
        
    def sort2(self, node):        
        print "--"        
        for key in node.child_dict.keys():
            print key
            if node.child_dict[key].child_dict:
                self.sort2(node.child_dict[key])
                print "--"                
                
                
                
#======== Test ===============
if __name__ == "__main__":

    
    win = gtk.Window(gtk.WINDOW_TOPLEVEL)        
    win.connect("destroy", gtk.main_quit)
    tree_view = TreeView()
    win.add(tree_view)
    win.show_all()
    tree_view.add_node(None, "aa")
    tree_view.add_node(None, "bb")
    tree_view.add_node(None, "cc")
    tree_view.add_node("cc", "cc11")
    tree_view.add_node("cc", "cc22")
    
    tree_view.add_node("cc11", "cc11cc11")
    tree_view.add_node("cc11", "cc11cc22")
    tree_view.add_node("cc11", "cc11cc33")
    tree_view.add_node("cc11", "cc11cc44")
    tree_view.add_node("cc11", "aaaaa3243")
    tree_view.add_node("cc11", "bbbbb234")
    tree_view.add_node("cc11", "aaaaa")
    
    tree_view.add_node("aaaaa", "bbbbb")
    tree_view.add_node("aaaaa", "bbbb1234b")
    tree_view.add_node("aaaaa", "bbbb1234b")
    tree_view.add_node("aaaaa", "bbbb1234b")
    tree_view.add_node("aaaaa", "bbbb1234b")
    tree_view.add_node("aaaaa", "bbbb1234b")
    
    tree_view.root.sort()    
    

    gtk.main()

    
