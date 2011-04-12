import pygtk
import gtk
import sqlite3
import os
import sys
import polib

usr_home = os.environ['HOME']
wordgroupz_dir = usr_home+'/.wordgroupz'
db_file_path = wordgroupz_dir+'/wc.db'

class wc_db:
    
    def __init__(self):
        if not os.path.exists(wordgroupz_dir):
            os.mkdir(wordgroupz_dir, 0755)    
        conn = sqlite3.connect(db_file_path)
        c = conn.cursor()
        tables = []
        for x in c.execute('''select name from sqlite_master'''):
            tables.append(x[0])
        if not 'terms' in tables:        
            c.execute('''create table terms (term text, translation text, context text, app text, category text)''')
            conn.commit()
        c.close()
        conn.close()
        
    def open_connection(self):
        self.conn = sqlite3.connect(db_file_path)
        self.c = self.conn.cursor()
        self.conn.text_factory = str
        
    def close_connection(self):
        self.c.close()
        self.conn.close()
        
    def store_data_from_po_file(self, term, translation, app, category, context=''):
        self.open_connection()
        t = (term, translation, context, app, category)
        self.c.execute('''insert into terms values (?,?,?,?,?)''',t)
        self.conn.commit()
        self.close_connection()
    
    def get_categories(self):
        self.open_connection()
        self.c.execute('''select category from terms group by category order by category''')
        result = self.c.fetchall()
        self.close_connection()
        return result
    
    def get_apps(self, category):
        self.open_connection()
        self.c.execute("""select app from terms where category=? group by app order by app""",(category,))
        result = self.c.fetchall()
        self.close_connection()
        return result
        
    def get_terms_per_app(self, app, category=None):
        self.open_connection()
        if category is None:
            self.c.execute("""select term, translation, context from terms where app=?""",(app,))
        else:
            self.c.execute("""select term, translation, context from terms where app=? and category=?""",(app,category,))
        results = self.c.fetchall()
        self.close_connection()
        return results
    def update_column(self, col, new_text, msgid, app, category):
        self.open_connection()
        self.c.execute("""update terms set %s='%s' where term='%s' and app = '%s' and category='%s'"""%(col, new_text, msgid, app, category))
        self.conn.commit()
        self.close_connection()

    def add_entry(self, msgid, msgstr, context, app, cat):
        self.open_connection()
        t = (msgid, msgstr, context, app, cat,)
        self.c.execute("""insert into terms values(?,?,?,?,?)""", t)
        self.conn.commit()
        self.close_connection()

def parse_po(db, filename, app, category):
    po = polib.pofile(filename)
    for i in po.translated_entries():
        term = i.msgid
        translation = i.msgstr
        db.store_data_from_po_file(term, translation, app, category)
    
class gui:
    def __init__(self):
        self.builder = gtk.Builder()
        self.builder.add_from_file('wc.glade')
        self.window = self.builder.get_object('window1')
        self.window.connect('destroy', gtk.main_quit, None)
        #self.builder.connect_signals()
        self.treeview = gtk.TreeView()
        self.tvcolumn = gtk.TreeViewColumn('Word Collections')
        self.treeview.append_column(self.tvcolumn)
        self.cell = gtk.CellRendererText()
        self.tvcolumn.pack_start(self.cell, True)
        self.tvcolumn.add_attribute(self.cell, 'text', 0)
        self.treestore = gtk.TreeStore(str)
        self.treeview.set_model(self.treestore)
        self.treeview.expand_all()
        self.selection = self.treeview.get_selection()
        self.selection.connect('changed',self.tree_select_changed)
        self.vbox2 = self.builder.get_object('vbox2')
        self.scrolledwindow2 = self.builder.get_object('scrolledwindow2')
        self.scrolledwindow2.add(self.treeview)
        #self.treeview.set_reorderable(True)
        
        self.treeview1 = gtk.TreeView()
        self.treestore1 = gtk.TreeStore(str, str, str)
        self.treeview1.set_model(self.treestore1)
        self.tvcol1 = gtk.TreeViewColumn('MsgID')
        self.treeview1.append_column(self.tvcol1)
        self.cell = gtk.CellRendererText()
        self.tvcol1.pack_start(self.cell, True)
        self.tvcol1.add_attribute(self.cell, 'text',0)
        #self.cell.set_property('wrap-mode', 1)
        #self.cell.set_property('wrap-width', 200)
        self.tvcol2 = gtk.TreeViewColumn('MsgStr')
        self.treeview1.append_column(self.tvcol2)
        self.cell = gtk.CellRendererText()
        self.cell.set_property('editable', True)
        self.cell.connect('edited', self.cell_edited_cb, (self.treeview1.get_model(), 1))
        self.tvcol2.pack_start(self.cell,True)
        self.tvcol2.add_attribute(self.cell, 'text', 1)
        self.tvcol3 = gtk.TreeViewColumn('Context')
        self.treeview1.append_column(self.tvcol3)
        self.cell = gtk.CellRendererText()
        self.cell.set_property('editable', True)
        self.cell.connect('edited', self.cell_edited_cb, (self.treeview1.get_model(), 2))
        self.tvcol3.pack_start(self.cell, True)
        self.tvcol3.add_attribute(self.cell, 'text', 2)
        #self.tvcol2.add_attribute(self.cell,'wrap-width', 20)
        self.selection1 = self.treeview1.get_selection()
        self.selection1.connect('changed',self.tree1_select_changed)
        #self.treeview1.set_reorderable(True)
        self.treeview.expand_all()
        self.scrolledwindow1 = self.builder.get_object('scrolledwindow1')
        self.scrolledwindow1.add(self.treeview1)
        self.entry_app = self.builder.get_object('entry1')
        self.entry_cat = self.builder.get_object('entry2')
        
        self.file_button = self.builder.get_object('filechooserbutton1')
        self.file_button.set_title('Select a *.po file')
        self.b_submit = self.builder.get_object('submit')
        self.b_submit.connect("clicked", self.submit, None)
        self.filter = self.builder.get_object('filefilter1')
        self.filter.set_name('PO files')
        self.filter.add_mime_type('PO')
        self.filter.add_pattern('*.po')
        self.b_move = self.builder.get_object('move')
        self.b_move.connect('clicked', self.move_entry, None)
        self.b_delete = self.builder.get_object('delete')
        self.b_delete.connect('clicked', self.delete_entry, None)
        
        self.app_combo = gtk.combo_box_new_text()
        self.app_combo.append_text("None")
        self.category_combo = gtk.combo_box_new_text()
        self.category_combo.connect('changed', self.category_changed, None)
        for i in db.get_categories():
            self.category_combo.append_text(i[0])
        self.move_hbox = self.builder.get_object('hbox6')
        self.move_hbox.pack_start(gtk.Label('Application'), expand=False)
        self.move_hbox.pack_start(self.app_combo)
        self.move_hbox.pack_start(gtk.Label('Category'), expand=False)
        self.move_hbox.pack_start(self.category_combo)
        self.b_move_ok = gtk.Button('OK')
        self.b_move_ok.show()
        self.control_hbox = self.builder.get_object('hbox4')
        self.control_hbox.hide()
        #self.b_move_ok.connect('clicked', self.move_ok)
        self.hbox5 = self.builder.get_object('hbox5')
        self.move_hbox.show_all()
        #self.move_hbox.set_sensitive(False)
        self.b_add = self.builder.get_object('add')
        self.b_add.connect('clicked', self.add_entry, None)
        #add
        #self.add_app_combo = gtk.combo_box_new_text()
        #self.add_cat_combo = gtk.combo_box_new_text()
        #populate combo boxes
        #for i 
        self.window.show()
        self.treeview.show_all()
        self.treeview1.show_all()
        
        for i in db.get_categories():
            piter = self.treestore.append(None, [i[0]])
            
            for j in db.get_apps(i[0]):
                self.treestore.append(piter, [j[0]])
        self.treeview.expand_all()
    def add_entry(self, widget=None, event=None):
        msgid = self.builder.get_object('msgid_entry').get_text()
        msgstr = self.builder.get_object('msgstr_entry').get_text()
        context = self.builder.get_object('context_entry').get_text()
        app = self.builder.get_object('app_entry').get_text()
        category = self.builder.get_object('cat_entry').get_text()
        db.add_entry(msgid, msgstr, context, app, category)
        self.refresh_tree()
        #self.refresh_tree()
    def get_app_category(self):
        if self.iter1 is not None:
            if len(self.model1.get_path(self.iter1)) == 2:
                piter = self.model1.iter_parent(self.iter1)
                app = str(self.model1.get_value(piter,0))
                #self.app = app
                category = str(self.model.get_value(self.iter,0))
            elif len(self.model1.get_path(self.iter1)) == 1:
                app = self.model.get_value(self.iter, 0)
                category = str(self.model.get_value(self.model.iter_parent(self.iter), 0))
            return (app, category)
    def refresh_tree(self):
        try:
            old_iter = self.iter
            old_path = self.model.get_path(self.iter)
        except:
            pass
        self.treestore.clear()
        for i in db.get_categories():
            piter = self.treestore.append(None, [i[0]])

            for j in db.get_apps(i[0]):
                self.treestore.append(piter, [j[0]])
        #self.old_iter = self.iter
        try:
            self.expand_tree_to_new(self.treeview, self.entry_app.get_text(), self.entry_cat.get_text(), old_iter=old_path)
        except:
            self.treeview.expand_all()

    def delete_entry(self, widget=None, event=None):
        app, category = self.get_app_category()
        msgid = str(self.model1.get_value(self.iter1, 0))
        db.open_connection()
        db.c.execute("""delete from terms where term='%s' and app='%s' and category='%s'"""%(msgid, app, category))
        db.conn.commit()
        db.close_connection()
        self.refresh_tree()
        self.tree_select_changed()
        
    def category_changed(self, widget=None, event=None):
        app_model = self.app_combo.get_model()
        app_model.clear()
        new_cat = self.category_combo.get_active_text()
        app, category = self.get_app_category()
        print new_cat
        apps = []
        for i in db.get_apps(new_cat):
            apps.append(i[0])
        if 'Global' not in apps:
            self.app_combo.append_text('Global')
        for i in apps:
            self.app_combo.append_text(i)

    def move_entry(self, widget=None, event=None):
        new_app = self.app_combo.get_active_text()
        new_category = self.category_combo.get_active_text()
        app, category = self.get_app_category()
        db.open_connection()
        msgid = str(self.model1.get_value(self.iter1, 0))
        db.c.execute("""update terms set app='%s', category='%s' where term='%s' and app='%s' and category='%s'"""%(new_app, new_category, msgid, app, category))
        db.conn.commit()
        db.close_connection()
        old_path = self.model.get_path(self.iter)
        self.refresh_tree()
        self.tree_select_changed()
        
        self.expand_tree_to_new(self.treeview, new_app, new_category, old_iter=old_path)

    def cell_edited_cb(self, cell, path, new_text, user_data):
        print path
        liststore, column = user_data
        if column == 1:
            col = 'translation'
        elif column == 2:
            col = 'context'
        liststore[path][column] = new_text
        print liststore[path.split(':')[0]][0]
        l = len(path)
        selection = self.treeview.get_selection()
        model, iter = selection.get_selected()
        p = model.get_path(iter)
        if len(p)==1:
            app = unicode(liststore[path.split(':')[0]][0])
            print "App : "+ app
            category = unicode(model.get_value(iter,0))
            print 'Category : ' + category
        elif len(p) == 2:
            app = unicode(model.get_value(iter, 0))
            print "App: "+ app
            piter = model.iter_parent(iter)
            category  = unicode(model.get_value(piter,0))
            print 'Category : ' + category

        term = liststore[path][0]
        print 'term : ' + term
        db.update_column(col, new_text, term, app, category)
        #if column == 1:
            
    #selection.select_iter(iter)
    def expand_tree_to_new(self, treeview, new_app, new_category, old_iter=None):
        model = treeview.get_model()
        selection = treeview.get_selection()
        piter = model.get_iter_root()
        while piter is not None:
            if model.get_value(piter, 0) == new_category and model.iter_has_child(piter):
                chiter = model.iter_children(piter)
                while chiter is not None:
                    if model.get_value(chiter,0) == new_app:
                        treeview.expand_to_path(model.get_path(chiter))
                        selection.select_iter(chiter)
                        break
                    else:
                        chiter = model.iter_next(chiter)
                break
            piter = model.iter_next(piter)
        if piter is None:
            self.treeview.expand_all()
            selection.select_path(old_iter)

    def submit(self, widget=None, event=None):
        if self.file_button.get_filename() is not None and self.entry_app.get_text() is not '' and self.entry_cat.get_text() is not '':
            parse_po(db, self.file_button.get_filename(), self.entry_app.get_text(), self.entry_cat.get_text())
        self.refresh_tree()
    def tree1_select_changed(self, widget=None, event=None):
        self.model1, self.iter1 = self.selection1.get_selected()
        #self.b_move.set_sensitive(False)
        self.control_hbox.hide()
        if self.iter1 is not None:
            #self.b_move.set_sensitive(True)
            self.control_hbox.show_all()
            if len(self.model1.get_path(self.iter1)) == 2:
                piter = self.model1.iter_parent(self.iter1)
                app = str(self.model1.get_value(piter,0))
                #self.app = app
                category = str(self.model.get_value(self.iter,0))
            elif len(self.model1.get_path(self.iter1)) == 1:
                app = self.model.get_value(self.iter, 0)
                try:
                    category = str(self.model.get_value(self.model.iter_parent(self.iter), 0))
                    
                except:
                    self.control_hbox.hide()
                    category = None

            app_model = self.app_combo.get_model()
            iter = app_model.get_iter_root()
            print app_model.get_value(iter,0)
            while iter is not None:
                if app_model.get_value(iter,0) == app:
                    #self.app_combo.set_active_iter(iter)
                    break
                iter = app_model.iter_next(iter)
            category_model = self.category_combo.get_model()
            iter = category_model.get_iter_root()
            while iter is not None and category is not None:
                if category_model.get_value(iter,0) == category:
                    self.category_combo.set_active_iter(iter)
                    break
                iter = category_model.iter_next(iter)
            self.builder.get_object('app_entry').set_text(app)
            self.builder.get_object('cat_entry').set_text(category)
     
    def tree_select_changed(self, widget=None, event=None):
        self.treestore1.clear()
        self.model, self.iter = self.selection.get_selected()
        #print self.iter
        #print self.model.get_path(self.iter)
        if self.iter is not None:
            self.tree_value = self.model.get_value(self.iter, 0)
            apps = []
            categories = []
            for i in db.get_categories():
                if i[0] not in categories:
                    categories.append(i[0])
                for j in db.get_apps(i[0]):
                    if j[0] not in apps:
                        apps.append(j[0])
            if self.tree_value in apps:
                cat = str(self.model.get_value(self.model.iter_parent(self.iter), 0))
                for i in db.get_terms_per_app(self.tree_value, category=cat):
                    self.treestore1.append(None, [i[0], i[1],i[2]])
            elif self.tree_value in categories:
                for i in db.get_apps(self.tree_value):
                    piter = self.treestore1.append(None, [i[0], '', ''])
                    for j in db.get_terms_per_app(i[0], category=self.tree_value):
                        self.treestore1.append(piter, [j[0],j[1],j[2]])
                self.treeview1.expand_all()       
            path = self.model.get_path(self.iter)
            if len(path) == 2:
                app = str(self.model.get_value(self.iter, 0))
                cat = str(self.model.get_value(self.model.iter_parent(self.iter), 0))
            elif len(path) == 1:
                app = ''
                cat = str(self.model.get_value(self.iter, 0))
            self.builder.get_object('app_entry').set_text(app)
            self.builder.get_object('cat_entry').set_text(cat)
if __name__ == '__main__':
    db = wc_db()
    g = gui()
    gtk.main()
