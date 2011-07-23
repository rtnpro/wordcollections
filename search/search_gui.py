import gtk
import os
import search as s
from optparse import OptionParser

class searchUI:
  def __init__(self):
    
    self.builder = gtk.Builder()
    self.builder.add_from_file("search.glade")
    self.window = self.builder.get_object("MainWindow")
    #self.window.set_default_size(300, 300)
    self.window.set_title("Search")
    self.builder.connect_signals(self)
    
    self.result_scroller = self.builder.get_object("scrolledwindow1")
    
    self.curr_dir = os.getcwd()
    self.path = self.curr_dir + '/im.txt'

  
    self.search_button = self.builder.get_object("search_button")
    self.search_button.connect("clicked",self.on_search_button_clicked)
    self.search_phrase = self.builder.get_object("search_entry")
    
    self.search_button.set_sensitive(False)
    self.view = self.builder.get_object("viewport1")
    
    self.result_frame = self.builder.get_object("result_frame")
    self.error_frame = self.builder.get_object("error_frame")
    self.welcome = self.builder.get_object("welcome")
    self.window.connect("destroy", lambda w: gtk.main_quit())
    
    self.result_frame.hide()
    self.error_frame.hide()
    
    self.result_frame.set_shadow_type(gtk.SHADOW_IN)
    
    self.welcome.set_shadow_type(gtk.SHADOW_IN)
    self.note = self.builder.get_object("label3")
    self.note.set_markup('<b>Results</b>')
    self.note.set_alignment(0.5,0.1)
    
    self.treestore = gtk.ListStore(str,str)
    self.treeview = gtk.TreeView(self.treestore)
    self.treestore.clear()
    
    self.cell = gtk.CellRendererText()
    self.cell.set_property('wrap-mode', gtk.WRAP_WORD)
    
    self.tvcolumn = gtk.TreeViewColumn("", self.cell ,markup=1)
    self.treeview.append_column(self.tvcolumn)
    
    self.treeview.expand_all()
    
    self.welcome.show()
    
  def check_length(self, widget, data):
    if(len(self.search_phrase.get_text())>2):
      self.search_button.set_sensitive(True)
    else:
      self.search_button.set_sensitive(False)
      self.treestore.clear()
      self.error_frame.hide()
      self.result_frame.hide()
      self.welcome.show()
    
  def keyPress(self, widget, data):
    if(len(self.search_phrase.get_text())>2):
      if data.keyval == 65293:
        self.on_search_button_clicked(None)

  def on_search_button_clicked(self, widget, data=None):
    self.parse_file()
    self.treestore.clear()
    table = gtk.Table(columns = 2)
    i = 0
    check = 0
    if(len(self.search_phrase.get_text())>2):
	d = s.search(self.search_phrase.get_text(), self.lines)
	if d == {}:
	  self.note = self.builder.get_object("label4")
	  self.note.set_markup('<b>Search Phrase Not Found </b>')
	  self.note.set_alignment(0.5,0.1)
	  self.welcome.hide()
	  self.result_frame.hide()
	  self.error_frame.show()
	else:
	  self.error_frame.hide()
	  keys = d.keys()
	  if d.has_key('contains'):
	    #label = gtk.Label()
	    #label.set_markup("<b>Contains</b>")
	    #label.set_alignment(0.0, 0)
	    
	    #table.attach(label, 0, 1, i, i+1, xoptions = gtk.FILL)
	    #label.show()
	    entries = d['contains']
	    entries.sort()
	    entries.reverse()
	    for entry in entries:
	      if (entry[1] != ""):
		#print "Entry[1]=",entry[1],"     length",len(entry[1])
		self.treestore.append([None,entry[1]])
		self.treeview.show()
		self.tvcolumn.pack_end(self.cell)
		self.tvcolumn.add_attribute(self.cell, 'text', 0)
	    table.attach(self.treeview, 0, 1, i, i+1)
	    i = i + 1

	    self.welcome.hide()
	    self.view.add(table)
	    if(check == 1):
	      self.view.remove(table)
	    check = 0
	    self.result_frame.show()
	    keys.remove('contains')
	  keys.sort()
	  keys.reverse()
	  for key in keys:
	    #label = gtk.Label()
	    #matches = '%d matches'%key
	    #label.set_markup("<b>"+matches+"</b>")
	    #label.set_alignment(0.0, 0)
		
	    #table.attach(label, 0, 1, i, i+1, xoptions = gtk.FILL)
	    #label.show()
	    entries = d['contains']
	    entries.sort()
	    entries.reverse()
	    
	    entries = d[key]
	    entries.sort()
	    entries.reverse()
	    for entry in entries:
	      if(entry[1] != ""):
		#print "Entry[1]=",entry[1],"     length",len(entry[1])
		self.treestore.append([None,entry[1]])
		self.treeview.show()
		self.tvcolumn.pack_end(self.cell)
		self.tvcolumn.add_attribute(self.cell, 'text', 0)
	    table.attach(self.treeview, 0, 1, i, i+1)
	    i = i + 1
	  table.show()
      
  def parse_file(self):
      f = open(self.path, 'r')
      self.entries = f.read().split('\n')
      self.lines = []
      for i in self.entries:
	if i.find (">") >= 0:
	  i = i.replace(">","&gt;")
	if i.find ("<") >= 0:
	  i = i.replace("<","&lt;")
	self.lines.append(i)
	  
if __name__ == "__main__":
  obj = searchUI()
  obj.window.set_default_size(500,400)
  obj.window.show()
  gtk.main()