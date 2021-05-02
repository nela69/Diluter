#
# Simple code editor for editing config files
#

# import Libraries
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import hp_globals as hpg

class HoloPiNotes:
    def __init__(self, app, inputfile):
       
        # create main window instance
        self.main_window = tk.Toplevel(app.root)
         # configure main window
        self.main_window.title('HoloPi Notes')
        if inputfile == hpg.configfile:
            self.main_window.geometry('550x550')
        else:
            self.main_window.geometry('700x700')
        self.main_window.wm_protocol("WM_DELETE_WINDOW", self.onClose)
        self.app = app
        self.confpanel = app.panel2
        self.inputfile = inputfile
        self.fsaved = False

        # create menu bar instance
        menubar = tk.Menu(self.main_window)

        # create 'File' menu items
        file_menu = tk.Menu(menubar, tearoff=0)
        #file_menu.add_command(label="New", command=new_file)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_command(label="Save as...", command=self.save_file_as)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.onClose)

        # add 'File' menu to the menu bar
        menubar.add_cascade(label="File", menu=file_menu)

        # create text area to input text
        self.text_area = tk.Text(self.main_window)
        self.text_area.pack(expand = tk.YES, fill = tk.BOTH, side = tk.LEFT)

        # create scrollbar and link it to the text area
        scroll_bar = ttk.Scrollbar(self.main_window, orient=tk.VERTICAL, command=self.text_area.yview)
        scroll_bar.pack(fill=tk.Y, side=tk.RIGHT)
        self.text_area['yscrollcommand'] = scroll_bar.set

        # Connect menubar to the window
        self.main_window.config(menu=menubar)
        
    # create new file
    def new_file(self):
        # if text wasn't changed
        if not self.text_area.edit_modified():
            # clear text area
            self.text_area.delete('1.0', tk.END)
        
        # otherwise
        else:
            # call 'save as' function
            save_file_as()
            
            # clear text area after
            self.text_area.delete('1.0', tk.END)
        
        # clear 'is_modified' flag
        self.text_area.edit_modified(0)
        
        # restore window title
        main_window.title('HoloPi Notes')
        
    # open existing file
    def open_file(self):
        # if text wasn't changed
        if not self.text_area.edit_modified():
            # try to open file
            try:
                # get the path of file to open
                #path = filedialog.askopenfile(filetypes = (("Text files", "*.txt"), ("All files", "*.*"))).name
               
                # store path in window title for later reference
                self.main_window.title('HoloPi Notes - ' + self.inputfile)
                
                # open file stream
                with open(self.inputfile, 'r') as f:
                    # clear text area and insert file content
                    content = f.read()
                    self.text_area.delete('1.0', tk.END)
                    self.text_area.insert('1.0', content)
                    
                    # clear 'is_modified' flag
                    self.text_area.edit_modified(0)
            
            # exception is thrown if 'Cancel' button is clicked on 'Open file dialogue'
            except:
                pass
        
        # otherwise
        else:
            # call 'save as' function
            save_file_as()
            
            # clear 'is_modified' flag
            self.text_area.edit_modified(0)
            
            # call 'open_file' function recursively        
            open_file()
             
    # save current file
    def save_file(self):
        # try to get current file path
        try:
            # get file path from window title
            path = self.main_window.title().split('-')[1][1:]
        
        # init path variable to empty string on exception
        except:
            path = ''
#        path = "picamconfig.txt"
        # check if file path is available
        if path != '':
            # write file
            with open(path, 'w') as f:
                content = self.text_area.get('1.0', tk.END)
                f.write(content)
                
                self.fsaved = True
        
        # otherwise call 'save as' function
        else:
            save_file_as()
        
        # clear 'is_modified' flag
        #self.text_area.edit_modified(0)

    def save_file_as(self):
        # try to get file path
        try:
            path = filedialog.asksaveasfile(filetypes = (("Text files", "*.txt"), ("All files", "*.*"))).name
            self.main_window.title('HoloPi Notes - ' + path)

        # return if 'Cancel' button is clicked on 'Save file dialogue'
        except:
            return
        
        # otherwise write file to disk
        with open(path, 'w') as f:
            f.write(text_area.get('1.0', tk.END))
            
    def onClose(self):       
        # set the stop event, cleanup the camera, and allow the rest of
        # the quit process to continue
        print("[INFO] closing HoloPi Notes...")
        
        if self.text_area.edit_modified(): # and self.fsaved == True:
            self.save_file()
            if self.inputfile == hpg.configfile:
                print("[INFO] Updating PiCamera config...")
                hpg.picam_config = hpg.setPiCamConfig()
                # hpg.updateConfPanel(self.confpanel)
                hpg.updateConfPanel2(self.app)
            
        self.main_window.destroy()
