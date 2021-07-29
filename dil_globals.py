# Soluter global variables
from time import sleep
from os import path, listdir
import GPIO_actuators as Ga
import subprocess

GPIO_config_file = './config/GPIO_config.txt'
configfile = './config/diluter_config.txt'
sequences_path = './sequences'

# initialize python editor
PYTHON_EDITOR = '/usr/bin/thonny'
#editor = os.environ.get('EDITOR', PYTHON_EDITOR)

##################################### CONSOLE  ########################################
hp_console = None

diluter_config = {
                'stepperX_GPIO': [13, 19, 6, 5],
                'stepperZ_GPIO': [3, 2, 4, 17],
                'syringeLatch_GPIO' : 26,
                'stXcurrentPos' : 0,
                'stZcurrentPos' : 0,
                'stXLeftmost' : 0,
                'stZLowest' : 0,
                'stXRightmost' : 0,
                'stZHighest' : 0,
                'sc_pos' : 0,
                'tc_pos' : 33,
                'mc_pos' : 66,
                'wc_pos' : 100,
                'sy_ext_e' : 5,
                'sy_ext_f' : 40,
                'sy_rtr_e' : 40,
                'sy_rtr_f' : 95,
                'syr_vol' : 10,
                'stepX' : 20,
                'stepZ' : 20
            }

stepperX = Ga.Stepper(diluter_config['stepperX_GPIO'])
stepperZ = Ga.Stepper(diluter_config['stepperZ_GPIO'])
steppertype = 'bipolar'

syringeLatch = Ga.Actuator(diluter_config['syringeLatch_GPIO'])


def setDiluterConfig():
    if path.exists(configfile) == True:
         
        with open(configfile,'r') as inf:
            dil_config = eval(inf.read())
#            p_console.write2Console(diluter_config)
#             for ckey in diluter_config:
        return dil_config
                
    else:
        return diluter_config
        hp_console.write2Console('No config file, please perform calibration first!')
         
    

def saveDiluterConfig():
    with open(configfile,'w') as inf:
        
        inf.write('{\n')
        
        for ckey in diluter_config:
            if isinstance(diluter_config[ckey], str):
                inf.write("   '" + ckey + "': '"  + str(diluter_config[ckey]) + "',\n")
            else:
                inf.write("   '" + ckey + "': "  + str(diluter_config[ckey]) + ",\n")

        inf.write('}')
        print(diluter_config)

##################################### Functions  ########################################
def runStepperX(steps):
    stepperX.runStepper(200, steps, steppertype)
    diluter_config['stXcurrentPos'] += steps
    hp_console.write2Console('Current X position: ' +  str(diluter_config['stXcurrentPos']))
    
def runStepperZ(steps):
    print(steps)
    stepperZ.runStepper(300, steps, steppertype)
    diluter_config['stZcurrentPos'] += steps
    hp_console.write2Console('Current Z position: ' +  str(diluter_config['stZcurrentPos']))
    
def moveToPos(posStr):
    if posStr[2] == 'Z' or posStr[1] == 'y':
        print('posStr: ' + str(diluter_config[posStr]))
        runStepperZ(int(diluter_config[posStr]) - int(diluter_config['stZcurrentPos']))
        hp_console.write2Console('Move to: ' + posStr + ' @' +  str(diluter_config[posStr]))
        diluter_config['stZcurrentPos'] = diluter_config[posStr]
    else:
        runStepperX(int(diluter_config[posStr]) - int(diluter_config['stXcurrentPos']))
        hp_console.write2Console('Move to: ' + posStr + ' @' +  str(diluter_config[posStr]))
        diluter_config['stXcurrentPos'] = diluter_config[posStr]
        
# def moveToPos(absPos):
#     runStepperX(absPos)
#     hp_console.write2Console('Move to: ' + str(absPos))
        
def setPos(posStr):
    if posStr[2] == 'Z' or posStr[1] == 'y':
        diluter_config[posStr] = diluter_config['stZcurrentPos']
        hp_console.write2Console(posStr + ' set @: ' +  str(diluter_config['stZcurrentPos']))
    else:
        diluter_config[posStr] = diluter_config['stXcurrentPos']
        hp_console.write2Console(posStr + ' set @: ' +  str(diluter_config['stXcurrentPos']))

def runSequence(str_val):
    seq_module = str_val.get()
    hp_console.write2Console('Running: ' + seq_module)
    readControlBatch(sequences_path + '/' + seq_module + '.txt')
    
def editSeq(str_val):
    edit_path = './sequences/' + str_val.get() + '.txt'
    hp_console.write2Console('Editing: ' +  edit_path)
    subprocess.call([PYTHON_EDITOR, edit_path])
    
def runStepper(stepper, st_steps, st_speed = 100):
    hp_console.write2Console('Running stepper motor @speed:' + str(st_speed) + ' steps:' + str(st_steps))
    stepper.runStepper(st_speed, st_steps, steppertype)

##############################################################
###                 SEQUENCE DEFINITIONS                   ###
##############################################################

# command sequences in dropdown menu. Names should exactly match that of the functions

sequences = []

def listSequences(path):
    sequence_files = listdir(path)
    sequences = []
    for seq in sequence_files:
        seq_file = seq.split('.')
        if seq_file[0][0].isalnum() and len(seq_file) > 1:
            if seq_file[1] == 'txt':
                sequences.append(seq_file[0])

    return sequences

#################### Read Sequences ##########################

def readControlBatch(seq_path):
    if path.exists(seq_path) == True:

        with open(seq_path,'r') as inf:
            lines = inf.readlines()
            for line in lines:
                if line[0].isalnum():
                    command = line[:-1].split(' ')
                    command_str = ''
                    if command[0] == 'wait':
                        wait_time = int(command[1]) / 1000
                        hp_console.write2Console('wait time: ' + str(wait_time) + 's')
                        sleep(wait_time)
                    elif command[0] == 'moveX':                        
                        if len(command) == 2:                            
                            if command[1] == 'sample':
                                 moveToPos('sc_pos')
                            elif command[1] == 'diluter':
                                 moveToPos('tc_pos')
                            elif command[1] == 'mixing':
                                 moveToPos('mc_pos')
                            elif command[1] == 'waste':
                                 moveToPos('wc_pos')
                            else:
                                 hp_console.write2Console('invalid command: ' + command[1])
                        else:
                            hp_console.write2Console('invalid number of commands: ' + command[0])
                    elif command[0] == 'moveZ':
                         if len(command) == 2:                             
                             if command[1] == 'syrRE':       # syringe retracted empty
                                 syringeLatch.Off()
                                 moveToPos('sy_rtr_e')
                             elif command[1] == 'syrEE':     # syringe extended empty
                                 syringeLatch.Off()
                                 moveToPos('sy_ext_e')
                             elif command[1] == 'syrRF':     # syringe retracted full
                                 syringeLatch.Off()
                                 moveToPos('sy_rtr_f')
                             elif command[1] == 'syrEF':     # syringe extended full
                                 syringeLatch.On()
                                 moveToPos('sy_ext_f')
                             else:
                                 hp_console.write2Console('invalid command: ' + command[1])
                         elif len(command) == 3:
                             if command[1] == 'syrEL':       # syringe extended load
                                 absPos = (float(command[2]) / float(diluter_config['syr_vol']))
                                 * (diluter_config['stZHighest'] - diluter_config['stZLowest']) + diluter_config['stZLowest'] - diluter_config['stZcurrentPos']
                                 moveToAbsPos(absPos)
                             elif command[1] == 'syrEUL':    # syringe extended unload
                                 moveToPos('sy_ext_e')
                             else:
                                 hp_console.write2Console('invalid command: ' + command[1] + command[2])
                         else:
                            hp_console.write2Console('invalid number of commands: ' + command[0])

    else:
         hp_console.write2Console('No config file')
         

# diluter_config = setDiluterConfig()
         
#print(diluter_config)         