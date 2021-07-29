# import the necessary packages
import tkinter as tki
import dil_globals as dlg
import RPi.GPIO as GPIO
import console_panel as hpc
#import seq_control


def onClose():
    dlg.saveDiluterConfig()
    root.destroy()
    
dlg.sequences = dlg.listSequences(dlg.sequences_path)

dlg.diluter_config = dlg.setDiluterConfig()

# initialize the root window
 
mainw_w = 640
mainw_h = 480
padding = 8
header = padding

calib_Z_w = (mainw_w - 3 * padding) /2
calib_Z_h = mainw_h * 0.2

containers_X_w = calib_Z_w
containers_X_h = 1.5 * calib_Z_h

calib_S_w = calib_Z_w
calib_S_h = calib_Z_h  + containers_X_h + padding 

calib_X_w = 2 * calib_Z_w + padding
calib_X_h = mainw_h * 0.17

sequences_w = (mainw_w - 3 * padding) * 0.4
sequences_h = mainw_h - calib_S_h - calib_X_h - header - 3 * padding

console_w = mainw_w - sequences_w - 3 * padding
console_h = sequences_h

root = tki.Tk()
scr_w = root.winfo_screenwidth()
scr_h = root.winfo_screenheight()
x = int(scr_w/2 - mainw_w/2)
y = int(scr_h/2 - mainw_h/2)


root.geometry(f'{mainw_w}x{mainw_h}+{x}+{y}')

# set a callback to handle when the window is closed
root.wm_title("Soluter Control Panel V1.0")
root.wm_protocol("WM_DELETE_WINDOW", onClose)

# Set panels
calib_Z = tki.LabelFrame(root, text = "Z-axis Calibration")
containers_X = tki.LabelFrame(root, text = "Containers Calibration")
calib_S = tki.LabelFrame(root, text = "Syringe Calibration")
calib_X = tki.LabelFrame(root, text = "X-axis Calibration")
sequences = tki.LabelFrame(root, text = "Sequences")
hp_console_w = tki.LabelFrame(root, text = "Status Console")

calib_Z.place(x = padding, y = header, width = calib_Z_w, height = calib_Z_h) # Z-axis calibration
containers_X.place(x = padding, y = header + calib_Z_h + padding, width = containers_X_w, height = containers_X_h) # containers positions
calib_S.place(x = 2 * padding + calib_Z_w, y = header, width = calib_S_w, height = calib_S_h) # syringe calibration
calib_X.place(x = padding, y = header + calib_S_h + padding, width = calib_X_w, height = calib_X_h) # X-axis calibration
sequences.place(x = padding, y = header + calib_S_h + calib_X_h + 2 * padding, width = sequences_w, height = sequences_h) # Sequences

##################################### CONSOLE  ########################################
hp_console_w.place(x = sequences_w  + 2*padding, y = header + calib_S_h + calib_X_h + 2 * padding, width = console_w, height = console_h) # Status console
dlg.hp_console = hpc.hpConsole(hp_console_w)

################################# Calibration Z-axis ##########################################

sszlabel = tki.Label(calib_Z, text = "Step Size:")
sszlabel.place(relx = 0.61, rely = 0.3)
calib_Z_stepS = tki.Spinbox(calib_Z, from_= 2, to = 998, increment = 2)
calib_Z_stepS.place(relwidth = 0.15, relx = 0.84, rely = 0.3)
calib_Z_stepS.delete(0, tki.END)
calib_Z_stepS.insert(0, str(dlg.diluter_config['stepZ']))

upZ_btn = tki.Button(calib_Z, text = "UP", command = lambda: dlg.runStepperZ(int(calib_Z_stepS.get())))
upZ_btn.place(relwidth = 0.15, height = 20, relx = 0.84, rely = 0.0)
downZ_btn = tki.Button(calib_Z, text = "DN", command = lambda: dlg.runStepperZ(-int(calib_Z_stepS.get())))
downZ_btn.place(relwidth = 0.15, height = 20, relx = 0.84, rely = 0.65)

hlabel = tki.Label(calib_Z, text = "Highest Position:")
hlabel.place(relx = 0.01, rely = 0)
sethZ_btn = tki.Button(calib_Z, text = "Set", command = lambda: dlg.setPos('stZHighest'))
sethZ_btn.place(relwidth = 0.15, height = 20, relx = 0.4, rely = 0.0)
move2hZ_btn = tki.Button(calib_Z, text = "Move to", command = lambda: dlg.moveToPos('stZHighest'))
move2hZ_btn.place(relwidth = 0.25, height = 20, relx = 0.55, rely = 0.0)

llabel = tki.Label(calib_Z, text = "Lowest Position:")
llabel.place(relx = 0.01, rely = 0.65)
setlZ_btn = tki.Button(calib_Z, text = "Set", command = lambda: dlg.setPos('stZLowest'))
setlZ_btn.place(relwidth = 0.15, height = 20, relx = 0.4, rely = 0.65)
move2lZ_btn = tki.Button(calib_Z, text = "Move to", command = lambda: dlg.moveToPos('stZLowest'))
move2lZ_btn.place(relwidth = 0.25, height = 20, relx = 0.55, rely = 0.65)

################################# Containers Calibration X-axis ##################################

sclabel = tki.Label(containers_X, text = "Sample Container:")
sclabel.place(relx = 0.01, rely = 0.12)
# scposlabel = tki.Label(containers_X, text = str(dlg.diluter_config['sc_pos']))
# scposlabel.place(relx = 0.45, rely = 0.12)
scset_btn = tki.Button(containers_X, text = "Set", command = lambda: dlg.setPos('sc_pos'))
scset_btn.place(relwidth = 0.15, height = 20, relx = 0.55, rely = 0.12)
scmove2_btn = tki.Button(containers_X, text = "Move to", command = lambda: dlg.moveToPos('sc_pos'))
scmove2_btn.place(relwidth = 0.25, height = 20, relx = 0.7, rely = 0.12)

tclabel = tki.Label(containers_X, text = "Diluter Container:")
tclabel.place(relx = 0.01, rely = 0.32)
# tcposlabel = tki.Label(containers_X, text = str(dlg.diluter_config['tc_pos']))
# tcposlabel.place(relx = 0.45, rely = 0.32)
tcset_btn = tki.Button(containers_X, text = "Set", command = lambda: dlg.setPos('tc_pos'))
tcset_btn.place(relwidth = 0.15, height = 20, relx = 0.55, rely = 0.32)
tcmove2_btn = tki.Button(containers_X, text = "Move to", command = lambda: dlg.moveToPos('tc_pos'))
tcmove2_btn.place(relwidth = 0.25, height = 20, relx = 0.7, rely = 0.32)

mclabel = tki.Label(containers_X, text = "Mixing Container:")
mclabel.place(relx = 0.01, rely = 0.52)
# mcposlabel = tki.Label(containers_X, text = str(dlg.diluter_config['mc_pos']))
# mcposlabel.place(relx = 0.45, rely = 0.52)
mcset_btn = tki.Button(containers_X, text = "Set", command = lambda: dlg.setPos('mc_pos'))
mcset_btn.place(relwidth = 0.15, height = 20, relx = 0.55, rely = 0.52)
mcmove2_btn = tki.Button(containers_X, text = "Move to", command = lambda: dlg.moveToPos('mc_pos'))
mcmove2_btn.place(relwidth = 0.25, height = 20, relx = 0.7, rely = 0.52)

wclabel = tki.Label(containers_X, text = "Waste Container:")
wclabel.place(relx = 0.01, rely = 0.72)
# wcposlabel = tki.Label(containers_X, text = str(dlg.diluter_config['wc_pos']))
# wcposlabel.place(relx = 0.45, rely = 0.72)
wcset_btn = tki.Button(containers_X, text = "Set", command = lambda: dlg.setPos('wc_pos'))
wcset_btn.place(relwidth = 0.15, height = 20, relx = 0.55, rely = 0.72)
wcmove2_btn = tki.Button(containers_X, text = "Move to", command = lambda: dlg.moveToPos('wc_pos'))
wcmove2_btn.place(relwidth = 0.25, height = 20, relx = 0.7, rely = 0.72)

################################# Syringe Calibration Z-axis ##################################

seelabel = tki.Label(calib_S, text = "Extended Empty:")
seelabel.place(relx = 0.01, rely = 0.05)
# seeposlabel = tki.Label(calib_S, text = str(dlg.diluter_config['sy_ext_e']))
# seeposlabel.place(relx = 0.45, rely = 0.05)
seeset_btn = tki.Button(calib_S, text = "Set", command = lambda: dlg.setPos('sy_ext_e'))
seeset_btn.place(relwidth = 0.15, height = 20, relx = 0.55, rely = 0.05)
seemove2_btn = tki.Button(calib_S, text = "Move to", command = lambda: dlg.moveToPos('sy_ext_e'))
seemove2_btn.place(relwidth = 0.25, height = 20, relx = 0.7, rely = 0.05)

seflabel = tki.Label(calib_S, text = "Extended Full")
seflabel.place(relx = 0.01, rely = 0.2)
# sefposlabel = tki.Label(calib_S, text = str(dlg.diluter_config['sy_ext_f']))
# sefposlabel.place(relx = 0.45, rely = 0.2)
sefset_btn = tki.Button(calib_S, text = "Set", command = lambda: dlg.setPos('sy_ext_f'))
sefset_btn.place(relwidth = 0.15, height = 20, relx = 0.55, rely = 0.2)
sefmove2_btn = tki.Button(calib_S, text = "Move to", command = lambda: dlg.moveToPos('sy_ext_f'))
sefmove2_btn.place(relwidth = 0.25, height = 20, relx = 0.7, rely = 0.2)

srelabel = tki.Label(calib_S, text = "Retracted Empty:")
srelabel.place(relx = 0.01, rely = 0.35)
# sreposlabel = tki.Label(calib_S, text = str(dlg.diluter_config['sy_rtr_e']))
# sreposlabel.place(relx = 0.45, rely = 0.35)
sreset_btn = tki.Button(calib_S, text = "Set", command = lambda: dlg.setPos('sy_rtr_e'))
sreset_btn.place(relwidth = 0.15, height = 20, relx = 0.55, rely = 0.35)
sremove2_btn = tki.Button(calib_S, text = "Move to", command = lambda: dlg.moveToPos('sy_rtr_e'))
sremove2_btn.place(relwidth = 0.25, height = 20, relx = 0.7, rely = 0.35)

srflabel = tki.Label(calib_S, text = "Retracted Full:")
srflabel.place(relx = 0.01, rely = 0.5)
# srfposlabel = tki.Label(calib_S, text = str(dlg.diluter_config['sy_rtr_f']))
# srfposlabel.place(relx = 0.45, rely = 0.5)
srfset_btn = tki.Button(calib_S, text = "Set", command = lambda: dlg.setPos('sy_rtr_f'))
srfset_btn.place(relwidth = 0.15, height = 20, relx = 0.55, rely = 0.5)
srfmove2_btn = tki.Button(calib_S, text = "Move to", command = lambda: dlg.moveToPos('sy_rtr_f'))
srfmove2_btn.place(relwidth = 0.25, height = 20, relx = 0.7, rely = 0.5)

svlabel = tki.Label(calib_S, text = "Syringe Volume (Full - Empty):              ml")
svlabel.place(relx = 0.01, rely = 0.75)
sventry = tki.Entry(calib_S)
sventry.place(relwidth = 0.15, relx = 0.7, rely = 0.75)
sventry.delete(0, tki.END)
sventry.insert(0, str(dlg.diluter_config['syr_vol']))


ng = tki.Entry(calib_S)
ng.place(relwidth = 0.1, relx = 0.55, rely = 0.88)
ng.delete(0, tki.END)
ng.insert(0, str(dlg.diluter_config['syringeLatch_GPIO']))
srfmove2_btn = tki.Button(calib_S, text = "Latch", command = lambda: ToggleGPIO(int(ng.get())))
srfmove2_btn.place(relwidth = 0.25, height = 20, relx = 0.7, rely = 0.9)



#################################  Calibration X-axis ##################################

ssxlabel = tki.Label(calib_X, text = "Step Size:")
ssxlabel.place(relx = 0.39, rely = 0.6)
calib_X_stepS = tki.Spinbox(calib_X, from_= 2, to = 998, increment = 2)
calib_X_stepS.place(relwidth = 0.08, relx = 0.51, rely = 0.58)
calib_X_stepS.delete(0, tki.END)
calib_X_stepS.insert(0, str(dlg.diluter_config['stepZ']))

upZ_btn = tki.Button(calib_X, text = "<<<", command = lambda: dlg.runStepperX(int(calib_X_stepS.get())))
upZ_btn.place(relwidth = 0.1, height = 20, relx = 0.28, rely = 0.6)
downZ_btn = tki.Button(calib_X, text = ">>>", command = lambda: dlg.runStepperX(-int(calib_X_stepS.get())))
downZ_btn.place(relwidth = 0.1, height = 20, relx = 0.6, rely = 0.6)

hlabel = tki.Label(calib_X, text = "Leftmost Position:")
hlabel.place(relx = 0.01, rely = 0.02)
sethZ_btn = tki.Button(calib_X, text = "Set", command = lambda: dlg.setPos('stXLeftmost'))
sethZ_btn.place(relwidth = 0.07, height = 20, relx = 0.25, rely = 0.02)
move2hZ_btn = tki.Button(calib_X, text = "Move to", command = lambda: dlg.moveToPos('stXLeftmost'))
move2hZ_btn.place(relwidth = 0.12, height = 20, relx = 0.32, rely = 0.02)

llabel = tki.Label(calib_X, text = "Rightmost Position:")
llabel.place(relx = 0.51, rely = 0.02)
setlZ_btn = tki.Button(calib_X, text = "Set", command = lambda: dlg.setPos('stXRightmost'))
setlZ_btn.place(relwidth = 0.07, height = 20, relx = 0.75, rely = 0.02)
move2lZ_btn = tki.Button(calib_X, text = "Move to", command = lambda: dlg.moveToPos('stXRightmost'))
move2lZ_btn.place(relwidth = 0.12, height = 20, relx = 0.82, rely = 0.02)

#################################  Operational scripts ##################################

om_var = tki.StringVar(sequences)
om_var.set(dlg.sequences[0])

# initialize python editor
global PYTHON_EDITOR
PYTHON_EDITOR = '/usr/bin/thonny'
#editor = os.environ.get('EDITOR', PYTHON_EDITOR)

sequences_menu = tki.OptionMenu(sequences, om_var, *dlg.sequences)
sequences_menu.place(relwidth = 0.9, relx=0.05, rely = 0)

no_of_cycles = tki.Spinbox(sequences, from_= 1, to = 99)
no_of_cycles.place(relwidth = 0.25, relheight = 0.25, relx=0.05, rely =0.35)

run_seq = tki.Button(sequences, text="Run Sequence", pady = 10, command= lambda: runSequence(om_var))
run_seq.place(relwidth = 0.6, relheight = 0.25, relx=0.35, rely =0.35)

edit_seq = tki.Button(sequences, text="Edit Sequence", pady = 10, command = lambda: dlg.editSeq(om_var))
edit_seq.place(relwidth = 0.9, relheight = 0.25, relx=0.05, rely =0.66)

##### DEBUG ########
def ToggleGPIO(noGPIO):
    if GPIO.input(noGPIO):
        GPIO.output(noGPIO, GPIO.LOW)
    else:
        GPIO.output(noGPIO, GPIO.HIGH)
   
def runSequence(seq):
    dlg.runSequence(seq)

####################### Main ############################

root.mainloop()