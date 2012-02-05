#!/usr/bin/python


import sys, re, pygtk
sys.path.append('./dict-parsers')
from tanakaCorpus import Corpus
pygtk.require('2.0')
import gtk

class GrammarLearner():
    """
    """
    
    def __init__(self, corpus_loc = None):
        """
        
        Arguments:
        - `corpus_loc`:
        """

        self.corpus = Corpus(corpus_loc)
        
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_title('corpus_search')
        self.window.set_position(gtk.WIN_POS_CENTER)
        self.window.set_size_request(500, 500)
        self.window.connect('destroy', gtk.main_quit)

        self.make_gui_widgets()

        v1 = gtk.HBox()
        v1.pack_start(self.search_btn, False, False, 0)
        v1.pack_start(self.entry)
        
        scr_win = gtk.ScrolledWindow()
        scr_win.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scr_win.add_with_viewport(self.treeview)

        v3 = gtk.VBox()
        v3.pack_start(self.menubar, False, False, 0)
        v3.pack_start(scr_win, True, True, 0)
        v3.pack_start(v1, False, False,0)
        v3.pack_end(self.status, False, False, 0)

        self.window.add(v3)
        self.window.set_focus(self.entry)
        self.window.show_all()

    def make_gui_widgets(self):
        self.create_entry()
        self.create_buttons()
        self.create_treeview()
        self.create_statusbar()
        self.create_menubar()
        
    def create_entry(self):
        self.entry = gtk.Entry()
        self.entry.set_visibility(True)
        #self.entry.connect('key-press-event', self.do_search, 'entry')
        
    def create_statusbar(self):
        self.status = gtk.Statusbar()

        
    def create_menubar(self):
        self.menubar = gtk.MenuBar()
        filemenu = gtk.Menu()
        file_ = gtk.MenuItem("File")
        file_.set_submenu(filemenu)

        open_ = gtk.MenuItem("Open")
        open_.connect("activate", self.open_dialogue)
        filemenu.append(open_)
        
        exit_ = gtk.MenuItem("Exit")
        exit_.connect("activate", gtk.main_quit)
        filemenu.append(exit_)

        self.menubar.append(file_)

    def open_dialogue(self, widget):
        dia = gtk.FileChooserDialog(title='Corpus Location', action=gtk.FILE_CHOOSER_ACTION_OPEN, buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
                
        res = dia.run()

        if res == gtk.RESPONSE_OK:
            self.corpus.read_corpus(dia.get_filename())
       
        dia.destroy()

    def create_buttons(self):
        self.search_btn = gtk.Button('Search')
        self.search_btn.connect('clicked', self.query_corpus, 'search_btn')
                
    def create_treeview(self):
        self.liststore = gtk.ListStore(str, str, bool)
        self.treeview = gtk.TreeView(self.liststore)

        cell = gtk.CellRendererText()
        togCell = gtk.CellRendererToggle()
        togCell.set_property('activatable', True)
        togCell.connect('toggled', self.toggled, self.liststore)
        tcol = gtk.TreeViewColumn('Results', cell, markup=0)
        togcol = gtk.TreeViewColumn('Save', togCell, active=2)

        tcol.add_attribute(cell, 'text', 1)
        #tcol.add_attribute(togCell, 'active', 0)

        self.treeview.append_column(togcol)
        self.treeview.append_column(tcol)
        
        
        self.treeview.set_tooltip_column(1)
        
    def toggled(self, cell, path, model):
        if path is not None:
            it = model.get_iter(path)
            model[it][2] = not model[it][2]

    def query_corpus(self, widget, event, data=None):
        self.update_liststore(self.corpus.do_search(self.entry.get_text()))

    def no_dict_dialog(self):
        label = gtk.Label('Cannot find any data. You have probably not yet input the location of the Tanaka Corpus.')
        label.set_line_wrap(True)
        label.set_justify(gtk.JUSTIFY_CENTER)
        label.show()
        dialog = gtk.Dialog('Cannot find dictionary', self.window, gtk.DIALOG_MODAL, buttons=(gtk.STOCK_OK, gtk.RESPONSE_OK))
        dialog.vbox.pack_start(label)
        dialog.run()       
        dialog.destroy()

    def update_liststore(self, data):
        if data == -1:
            no_dict_dialog()
        else:
            self.liststore.clear()
            for item in data[1:]:
                sp = item[0].split('\t')
                jp = sp[0]
                en,id_ = sp[1].split('#ID=')
                self.liststore.append([self.apply_markup(jp, data[0]), en, False])
            self.status.push(1, 'Found %d sentences containing "%s".'%(len(data[1:]), data[0]))

    def apply_markup(self, sentence, word):
        self.highlight_colour = 'red'
        return sentence.replace(word, '<span foreground="red">%s</span>'%(word))
                    
def main():
    gtk.main()

if __name__ == '__main__':
    if len(sys.argv) == 1:
        GrammarLearner()
    else:
        GrammarLearner(sys.argv[1])
    main()
