import tkinter as tki
import datetime

class hpConsole:
    def __init__(self, topFrame):
        self.root = topFrame

        S = tki.Scrollbar(topFrame)
        self.T = tki.Text(topFrame)

        S.pack(side=tki.RIGHT, fill=tki.Y)
        self.T.pack(side=tki.LEFT, fill = tki.BOTH)

        S.config(command=self.T.yview)
        self.T.config(yscrollcommand=S.set)
        self.T.configure(state = tki.DISABLED)

    def write2Console(self, entry):
        ts = datetime.datetime.now()
        cons_entry = "[{}]  ".format(ts.strftime("%m.%d %H.%M.%S")) + str(entry) +"\n"
        self.T.configure(state = tki.NORMAL)
        self.T.insert(tki.END, cons_entry)
        self.T.configure(state = tki.DISABLED)


