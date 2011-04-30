import pygtk
import gtk
import polib
import csv

GLADE_FILE = 'wc_new.glade'
class gui:
    def parse_file(self, filename):
        f = open(filename, 'r')
        self.entries = f.read().split('\n')
    
    def on_file_set(self, widget=None, event=None):
        if self.file_button.get_filename() is not None:
            self.b_import_next.set_sensitive(True)
    
    def refresh_list(self):
        self.treestore.clear()
        for entry in self.entries:
            self.treestore.append(None, [entry])
        
    
    def on_import_next_clicked(self, widget=None, event=None):
        self.parse_file(self.file_button.get_filename())
        self.import_window.hide()
        self.refresh_list()
        self.list_window.show()
        
    def on_list_window_destroyed(self, widget=None, event=None):
        gtk.main_quit()
        
    def edit(self, widget=None, event=None):
        #self.entry_frame.hide()
        self.entry_label.hide()
        self.edit_entry.show()
        self.edit_entry.set_text(self.entry_label.get_text())
        self.b_edit.hide()
        
    def entry_changed(self, widget=None, event=None):
        new_text = self.edit_entry.get_text()

        if new_text.strip() == '':
            self.error_msg.show()
            self.prev_button.set_sensitive(False)
            self.next_button.set_sensitive(False)
        else:
            self.error_msg.hide()
            self.prev_button_status = self.prev_button.get_sensitive()
            self.next_button_status = self.next_button.get_sensitive()            
            if self.index > 1:
                self.prev_button.set_sensitive(True)
            else:
                self.prev_button.set_sensitive(False)
            if self.index < len(self.entries) - 3:
                self.next_button.set_sensitive(True)
            else:
                self.next_button.set_sensitive(False)
        self.entries[self.index] = self.edit_entry.get_text()
        self.refresh_list()
    
    def on_prev_clicked(self, widget=None, event=None):
        if self.index > 1:
            self.prev_button.set_sensitive(True)
        else:
            self.prev_button.set_sensitive(False)
        self.index -= 1
        self.entry_label.show()
        self.edit_entry.hide()
        self.b_edit.show()
        self.entry_label.set_text(self.entries[self.index])
        if self.index < len(self.entries) - 1:
            self.next_button.set_sensitive(True)
        else:
            self.next_button.set_sensitive(False)

    def on_next_clicked(self, widget=None, event=None):
        if self.index < len(self.entries) - 3:
            self.next_button.set_sensitive(True)
        else:
            self.next_button.set_sensitive(False)
        self.index += 1
        self.entry_label.show()
        self.edit_entry.hide()
        self.b_edit.show()
        self.entry_label.set_text(self.entries[self.index])

        if self.index >= 1:
            self.prev_button.set_sensitive(True)
        else:
            self.prev_button.set_sensitive(False)

    def on_delete_clicked(self, widget=None, event=None):
        self.error_msg.hide()
        self.entries.remove(self.entries[self.index])
        self.refresh_list()
        self.entry_label.show()
        self.edit_entry.hide()
        self.b_edit.show()
        if self.index == len(self.entries) - 1 and self.index > 0:
            self.index = self.index - 1
        elif self.index == 0 and len(self.entries) == 1:
            self.examine_window_destroy()
            return
        self.entry_label.set_text(self.entries[self.index])
        
    def examine_window_destroy(self, widget=None, event=None):
        self.examine_window.destroy()

    def on_examine_clicked(self, widget=None, event=None):
        builder = gtk.Builder()
        builder.add_from_file(GLADE_FILE)
        self.examine_window = builder.get_object('examine_dialog')
        self.examine_window.connect('destroy', self.examine_window_destroy, None)
        self.entry_label = builder.get_object('label3')
        self.edit_entry = builder.get_object('entry1')
        self.edit_entry.connect('changed', self.entry_changed, None)
        self.b_edit = builder.get_object('edit')
        self.b_edit.connect('clicked', self.edit, None)
        model, iter = self.selection.get_selected()
        if iter is not None:
            self.index = int(model.get_path(iter)[0])
        else:
            self.index = 0
        self.error_msg = builder.get_object('hbox7')
        self.entry_label.set_text(self.entries[self.index])
        self.next_button = builder.get_object('next1')
        self.prev_button = builder.get_object('prev')
        self.delete_button = builder.get_object('delete')
        if self.index >= 1:
            self.prev_button.set_sensitive(True)
        else:
            self.prev_button.set_sensitive(False)
        if self.index < len(self.entries) - 2:
            self.next_button.set_sensitive(True)
        else:
            self.next_button.set_sensitive(False)
        self.next_button.connect('clicked', self.on_next_clicked, None)
        self.prev_button.connect('clicked', self.on_prev_clicked, None)
        self.delete_button.connect('clicked', self.on_delete_clicked, None)
        self.examine_window.show()
    def save_to_html(self, filename):
        table = """<table border="1">\n<tr>\n<th align="left">Source Entity</th><th align="left">Translation</th>\n</tr>"""
        for entry in self.entries:
            row = "\n<tr><td>" + entry + "</td><td></td></tr>"
            table = table + row
        html = """<html>\n<head></head>\n<body>\n""" + table + """\n</body>\n</html>"""
        f = open(filename, 'w')
        f.write(html)
        f.close()
        
    def save_to_pot(self, filename):
        po = polib.POFile()
        po.metadata = {
            'Project-Id-Version': '1.0',
            'Report-Msgid-Bugs-To': 'you@example.com',
            'POT-Creation-Date': '2007-10-18 14:00+0100',
            'PO-Revision-Date': '2007-10-18 14:00+0100',
            'Last-Translator': 'you <you@example.com>',
            'Language-Team': 'English <yourteam@example.com>',
            'MIME-Version': '1.0',
            'Content-Type': 'text/plain; charset=utf-8',
            'Content-Transfer-Encoding': '8bit',
        }
        for entry in self.entries:
            value = polib.POEntry(
                msgid=entry,
                msgstr=""
            )
            po.append(value)
        po.save(filename)

    def save_to_csv(self, filename):
        f = open(filename, 'w')
        writer = csv.writer(f, delimiter = ',', quotechar = "'", quoting = csv.QUOTE_ALL)
        for entry in self.entries:
            writer.writerow([entry])

    def on_export_clicked(self, widget=None, event=None):
        filename = self.export_file_button.get_filename()
        if filename.endswith('.txt'):
            f = open(filename, 'w')
            f.write('\n'.join(self.entries))
            f.close()
        elif filename.endswith('.pot'):
            self.save_to_pot(filename)
        elif filename.endswith('.html'):
            self.save_to_html(filename)
        elif filename.endswith('.csv'):
            self.save_to_csv(filename)
            
    def cell_edited_cb(self, cell, path, new_text, user_data):
        path = int(path)
        if new_text.strip() == '':
            self.entries.remove(self.entries[path])
        else:
            self.entries[path] = new_text
        self.refresh_list()
    
    def delete_from_list(self, widget=None, event=None):
        model, iter = self.selection.get_selected()
        path = int(model.get_path(iter)[0])
        self.entries.remove(self.entries[path])
        self.refresh_list()
    
    def tree_select_changed(self, widget=None, event=None):
        model, iter = self.selection.get_selected()
        if iter is not None:
            self.delete__button.set_sensitive(True)
        else:
            self.delete__button.set_sensitive(False)
    
    def get_wrap_width(self):
        return (self.list_window.get_size()[0] - 50)
        
    def dynamic_wrap(self, window, allocation, args=None):
        self.cell.set_property('wrap-width', self.get_wrap_width())
    
    def __init__(self):
        self.builder = gtk.Builder()
        self.builder.add_from_file(GLADE_FILE)
        self.import_window = self.builder.get_object('import_window')
        self.import_window.connect('destroy', gtk.main_quit, None)
        self.file_button = self.builder.get_object('filechooserbutton1')
        self.file_button.set_title('Select a *.txt file to import')
        self.file_button.connect('file-set', self.on_file_set, None)
        self.b_import_next = self.builder.get_object('next')
        self.b_import_next.connect('clicked', self.on_import_next_clicked, None)
        self.list_window = self.builder.get_object('listWindow')
        self.list_window.connect('destroy', self.on_list_window_destroyed, None)
        self.list_window.connect('size-allocate', self.dynamic_wrap, None)
        self.list_scroller = self.builder.get_object('scrolledwindow1')
        self.treeview = gtk.TreeView()
        self.tvcolumn = gtk.TreeViewColumn('Entries')
        self.treeview.append_column(self.tvcolumn)
        self.cell = gtk.CellRendererText()
        self.cell.set_property('editable', True)
        self.cell.set_property('wrap-mode', gtk.WRAP_WORD)
        self.cell.set_property('wrap-width', self.get_wrap_width())
        self.cell.connect('edited', self.cell_edited_cb, None)
        self.tvcolumn.pack_start(self.cell, True)
        self.tvcolumn.add_attribute(self.cell, 'text', 0)
        self.treestore = gtk.TreeStore(str)
        self.treeview.set_model(self.treestore)
        self.treeview.expand_all()
        self.selection = self.treeview.get_selection()
        self.selection.connect('changed', self.tree_select_changed)
        self.error_msg = self.builder.get_object('hbox7')
        self.treeview.show()
        self.list_scroller.add(self.treeview)
        self.b_examine = self.builder.get_object('examine')
        self.b_examine.connect('clicked', self.on_examine_clicked, None)
        self.export_button = self.builder.get_object('export')
        self.export_button.connect('clicked', self.on_export_clicked, None)
        self.delete__button = self.builder.get_object('delete_')
        self.delete__button.connect('clicked', self.delete_from_list, None)
        self.export_file_button = self.builder.get_object('filechooserbutton2')
        self.import_window.show()

if __name__ == '__main__':
    g = gui()
    gtk.main()
        
