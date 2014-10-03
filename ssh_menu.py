#!/usr/bin/python
# Terminator by Chris Jones <cmsj@tenshu.net>
# GPL v2 only
"""ssh_menu.py - Terminator Plugin to add an SSH Menu"""
import sys
import os

# Fix imports when testing this file directly
if __name__ == '__main__':
  sys.path.append( os.path.join(os.path.dirname(__file__), "../.."))

import gtk
import terminatorlib.plugin as plugin
from terminatorlib.config import Config
from terminatorlib.translation import _
from terminatorlib.util import get_config_dir

(CC_COL_NAME, CC_COL_COMMAND) = range(0,2)

# Every plugin you want Terminator to load *must* be listed in 'AVAILABLE'
AVAILABLE = ['SSHMenu']

class SSHMenu(plugin.MenuItem):
    """SSH Menu"""
    capabilities = ['terminal_menu']
    cmd_list = []
    conf_file = os.path.join(get_config_dir(),"ssh_menu")

    def __init__( self):
      config = Config()
      sections = config.plugin_get_config(self.__class__.__name__)
      if not isinstance(sections, dict):
          return
      for part in sections:
        s = sections[part]
        if not (s.has_key("name") and s.has_key("command")):
          print "SSHMenu: Ignoring section %s" % s
          continue
        name = s["name"]
        command = s["command"]
        self.cmd_list.append(
                              { 'name' : name,
                                'command' : command
                              }
                            )
    def callback(self, menuitems, menu, terminal):
        """Add our menu items to the menu"""
        item = gtk.MenuItem(_('SSH Menu'))
        item.connect("activate", self.menu, terminal)
        menuitems.append(item)


      #  submenu = gtk.Menu()
      #  item.set_submenu(submenu)

      #  menuitem = gtk.ImageMenuItem(gtk.STOCK_PREFERENCES)
      #  menuitem.connect("activate", self.configure)
      #  submenu.append(menuitem)

            
    def _save_config(self):
      config = Config()
      i = 0
      length = len(self.cmd_list)
      while i < length:
        name = self.cmd_list[i]['name']
        command = self.cmd_list[i]['command']
       
        item = {}
        item['name'] = name
        item['command'] = command

        config.plugin_set(self.__class__.__name__, name, item)
        config.save()
        i = i + 1


    def _save_order(self,selection, data):
      print "todo!"


    def _execute(self, treeview, path, view_column, data):
      (model, iter) = data['selection'].get_selected()
      command = model.get_value(iter,1)
      if command[len(command)-1] != '\n':
        command = command + '\n'
      data['terminal'].vte.feed_child(command)


    def menu(self, widget, terminal, data = None):
      ui = {}

      window = gtk.Window()
      scroll = gtk.ScrolledWindow(None, None)
      scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_ALWAYS)
      #scroll.set_border_width(1)


      window.set_title("SSH Menu")
      window.move(1,100)
      window.resize(200,500)
      window.set_resizable(True)
      #window. set_decorated(False)
       # Create a new button
      buttonsbox = gtk.HBox(False, 0)
      box1 = gtk.VBox(False, 0)

      button = gtk.Button("Close", gtk.STOCK_CLOSE)
      button.connect_object("clicked", gtk.Widget.destroy, window)

      buttonPreferences = gtk.Button("Close", gtk.STOCK_PREFERENCES)
      buttonPreferences.connect("clicked", self.configure)
      

      buttonsbox.pack_start(button, True, False, 0)
      buttonsbox.pack_end(buttonPreferences, True, False, 0)
      box1.pack_start(buttonsbox, False, False, 0)


      
      store = gtk.TreeStore(str,str)
      rabbit = store.append(None, ["Main","men"])
      for command in self.cmd_list:
        store.append(rabbit,[command['name'], command['command']])
 
      treeview = gtk.TreeView(store)
      selection = treeview.get_selection()
      selection.set_mode(gtk.SELECTION_SINGLE)

      selection.connect("changed", self._save_order, {'terminal' : terminal, 'selection' : selection })
      treeview.connect("row-activated", self._execute, {'terminal' : terminal, 'selection' : selection })
      ui['treeview'] = treeview

      renderer = gtk.CellRendererText()
      column = gtk.TreeViewColumn("Hosts", renderer, text=CC_COL_NAME)


      treeview.append_column(column)



      treeview.set_reorderable(True)
      treeview.set_enable_search(True)


      hbox = gtk.HBox()
      hbox.pack_start(treeview)

      outbox = gtk.VBox(False, 0)



      inbox = gtk.VBox(False, 0)
      inbox.pack_start(scroll, True, True, 5)
      inbox.pack_start(box1,False, False, 8)


      scroll.add_with_viewport(hbox)
      scroll.show()
      outbox.pack_start(inbox)
      window.add(outbox)
      window.show_all()

      return

    def configure(self, widget, data = None):
      ui = {}
      window = gtk.Dialog(
                      _("SSH Menu Configuration"),
                      None,
                      gtk.DIALOG_MODAL,
                      (
                        gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                        gtk.STOCK_OK, gtk.RESPONSE_ACCEPT
                      )
                    )
      store = gtk.ListStore(str, str)

      for command in self.cmd_list:
        store.append([command['name'], command['command']])
 
      treeview = gtk.TreeView(store)
      #treeview.connect("cursor-changed", self.on_cursor_changed, ui)
      selection = treeview.get_selection()
      selection.set_mode(gtk.SELECTION_SINGLE)
      selection.connect("changed", self.on_selection_changed, ui)
      ui['treeview'] = treeview

      renderer = gtk.CellRendererText()
      column = gtk.TreeViewColumn("Name", renderer, text=CC_COL_NAME)
      treeview.append_column(column)

      renderer = gtk.CellRendererText()
      column = gtk.TreeViewColumn("Command", renderer, text=CC_COL_COMMAND)
      treeview.append_column(column)

      hbox = gtk.HBox()
      hbox.pack_start(treeview)
      window.vbox.pack_start(hbox)

      button_box = gtk.VBox()

      button = gtk.Button(stock=gtk.STOCK_GOTO_TOP)
      button_box.pack_start(button, False, True)
      button.connect("clicked", self.on_goto_top, ui) 
      button.set_sensitive(False)
      ui['button_top'] = button

      button = gtk.Button(stock=gtk.STOCK_GO_UP)
      button_box.pack_start(button, False, True)
      button.connect("clicked", self.on_go_up, ui)
      button.set_sensitive(False)
      ui['button_up'] = button

      button = gtk.Button(stock=gtk.STOCK_GO_DOWN)
      button_box.pack_start(button, False, True)
      button.connect("clicked", self.on_go_down, ui) 
      button.set_sensitive(False)
      ui['button_down'] = button

      button = gtk.Button(stock=gtk.STOCK_GOTO_LAST)
      button_box.pack_start(button, False, True)
      button.connect("clicked", self.on_goto_last, ui) 
      button.set_sensitive(False)
      ui['button_last'] = button

      button = gtk.Button(stock=gtk.STOCK_NEW)
      button_box.pack_start(button, False, True)
      button.connect("clicked", self.on_new, ui) 
      ui['button_new'] = button

      button = gtk.Button(stock=gtk.STOCK_EDIT)
      button_box.pack_start(button, False, True)
      button.set_sensitive(False)
      button.connect("clicked", self.on_edit, ui) 
      ui['button_edit'] = button

      button = gtk.Button(stock=gtk.STOCK_DELETE)
      button_box.pack_start(button, False, True)
      button.connect("clicked", self.on_delete, ui) 
      button.set_sensitive(False)
      ui['button_delete'] = button



      hbox.pack_start(button_box)
      window.show_all()
      res = window.run()
      if res == gtk.RESPONSE_ACCEPT:
        #we save the config
        iter = store.get_iter_first()
        self.cmd_list = []
        while iter:
          (name, command) = store.get(iter,
                                              CC_COL_NAME,
                                              CC_COL_COMMAND)
          self.cmd_list.append(
                            {'name': name,
                            'command' : command}
                              )
          iter = store.iter_next(iter)
        self._save_config()
      
      window.destroy()
      return








    def on_selection_changed(self,selection, data=None):
      treeview = selection.get_tree_view()
      (model, iter) = selection.get_selected()
      data['button_top'].set_sensitive(iter is not None)
      data['button_up'].set_sensitive(iter is not None)
      data['button_down'].set_sensitive(iter is not None)
      data['button_last'].set_sensitive(iter is not None)
      data['button_edit'].set_sensitive(iter is not None)
      data['button_delete'].set_sensitive(iter is not None)

    def _create_command_dialog(self, name_var = "", command_var = ""):
      dialog = gtk.Dialog(
                        _("New Command"),
                        None,
                        gtk.DIALOG_MODAL,
                        (
                          gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                          gtk.STOCK_OK, gtk.RESPONSE_ACCEPT
                        )
                      )
      table = gtk.Table(3, 2)

      label = gtk.Label(_("Name:"))
      table.attach(label, 0, 1, 1, 2)
      name = gtk.Entry()
      name.set_text(name_var)
      table.attach(name, 1, 2, 1, 2)
      
      label = gtk.Label(_("Command:"))
      table.attach(label, 0, 1, 2, 3)
      command = gtk.Entry()
      command.set_text(command_var)
      table.attach(command, 1, 2, 2, 3)

      dialog.vbox.pack_start(table)
      dialog.show_all()
      return (dialog,name,command)

    def _error(self, msg):
      err = gtk.MessageDialog(dialog,
                              gtk.DIALOG_MODAL,
                              gtk.MESSAGE_ERROR,
                              gtk.BUTTONS_CLOSE,
                              msg
                            )
      err.run()
      err.destroy()

      


    def on_new(self, button, data):
      (dialog,name,command) = self._create_command_dialog()
      res = dialog.run()
      item = {}
      if res == gtk.RESPONSE_ACCEPT:
        item['name'] = name.get_text()
        item['command'] = command.get_text()
        if item['name'] == '' or item['command'] == '':
          err = gtk.MessageDialog(dialog,
                                  gtk.DIALOG_MODAL,
                                  gtk.MESSAGE_ERROR,
                                  gtk.BUTTONS_CLOSE,
                                  _("You need to define a name and command")
                                )
          err.run()
          err.destroy()
        else:
          # we have a new command
          store = data['treeview'].get_model()
          iter = store.get_iter_first()
          name_exist = False
          while iter != None:
            if store.get_value(iter,CC_COL_NAME) == item['name']:
              name_exist = True
              break
            iter = store.iter_next(iter)
          if not name_exist:
            store.append((item['name'], item['command']))
          else:
            self._err(_("Name *%s* already exist") % item['name'])
      dialog.destroy()

    def on_goto_top(self, button, data):
      treeview = data['treeview']
      selection = treeview.get_selection()
      (store, iter) = selection.get_selected()
      
      if not iter:
        return
      firstiter = store.get_iter_first()
      store.move_before(iter, firstiter)

    def on_go_up(self, button, data):
      treeview = data['treeview']
      selection = treeview.get_selection()
      (store, iter) = selection.get_selected()
       
      if not iter:
        return

      tmpiter = store.get_iter_first()

      if(store.get_path(tmpiter) == store.get_path(iter)):
        return

      while tmpiter:
        next = store.iter_next(tmpiter)
        if(store.get_path(next) == store.get_path(iter)):
          store.swap(iter, tmpiter)
          break
        tmpiter = next

    def on_go_down(self, button, data):
      treeview = data['treeview']
      selection = treeview.get_selection()
      (store, iter) = selection.get_selected()
      
      if not iter:
        return
      next = store.iter_next(iter)
      if next:
        store.swap(iter, next)

    def on_goto_last(self, button, data):
      treeview = data['treeview']
      selection = treeview.get_selection()
      (store, iter) = selection.get_selected()
      
      if not iter:
        return
      lastiter = iter
      tmpiter = store.get_iter_first()
      while tmpiter:
        lastiter = tmpiter
        tmpiter = store.iter_next(tmpiter)
      
      store.move_after(iter, lastiter)

 
    def on_delete(self, button, data):
      treeview = data['treeview']
      selection = treeview.get_selection()
      (store, iter) = selection.get_selected()
      if iter:
        store.remove(iter)
      
      return
 
    def on_edit(self, button, data):
      treeview = data['treeview']
      selection = treeview.get_selection()
      (store, iter) = selection.get_selected()
      
      if not iter:
        return
       
      (dialog,name,command) = self._create_command_dialog(
                                                name_var = store.get_value(iter, CC_COL_NAME),
                                                command_var = store.get_value(iter, CC_COL_COMMAND)
                                                                  )
      res = dialog.run()
      item = {}
      if res == gtk.RESPONSE_ACCEPT:
        item['name'] = name.get_text()
        item['command'] = command.get_text()
        if item['name'] == '' or item['command'] == '':
          err = gtk.MessageDialog(dialog,
                                  gtk.DIALOG_MODAL,
                                  gtk.MESSAGE_ERROR,
                                  gtk.BUTTONS_CLOSE,
                                  _("You need to define a name and command")
                                )
          err.run()
          err.destroy()
        else:
          tmpiter = store.get_iter_first()
          name_exist = False
          while tmpiter != None:
            if store.get_path(tmpiter) != store.get_path(iter) and store.get_value(tmpiter,CC_COL_NAME) == item['name']:
              name_exist = True
              break
            tmpiter = store.iter_next(tmpiter)
          if not name_exist:
            store.set(iter,
                      CC_COL_NAME, item['name'],
                      CC_COL_COMMAND, item['command']
                      )
          else:
            self._err(_("Name *%s* already exist") % item['name'])

      dialog.destroy()
 
      
if __name__ == '__main__':
  c = SSHMenu()
  c.configure(None, None)
  gtk.main()

