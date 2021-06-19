import RPi.GPIO as GPIO
from time import sleep

class Actuator:
    def __init__(self, GPIO_IN1, GPIO_IN2 = 0, GPIO_pwm = 0, freq = 0, init_pwm = 100):
        global GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        self.GPIO_IN1 = GPIO_IN1
        GPIO.setup(GPIO_IN1, GPIO.OUT)     
        self.GPIO_pwm = GPIO_pwm                            
        self.GPIO_IN2 = GPIO_IN2
        
        if GPIO_IN2 > 0:
            GPIO.setup(GPIO_IN2, GPIO.OUT)
        else:
            self.GPIO_CONTROL = GPIO_IN1
        
        if self.GPIO_pwm > 0:
            GPIO.setup(self.GPIO_pwm, GPIO.OUT)
            if freq > 0:
                self.pwm = GPIO.PWM(self.GPIO_pwm, freq)
                self.pwm.start(init_pwm)
            else:
                GPIO.output(self.GPIO_pwm, GPIO.HIGH)

    def setSpeed(self,PWM):
        if self.GPIO_pwm > 0:
#            GPIO.output(self.GPIO_control, GPIO.HIGH)
            self.pwm.ChangeDutyCycle(PWM)
            
    def On(self, direction = 1, run_time = 0):
        if self.GPIO_IN2 > 0 and direction == 1:
            GPIO.output(self.GPIO_IN1, GPIO.HIGH)
            GPIO.output(self.GPIO_IN2, GPIO.LOW)
        elif self.GPIO_IN2 > 0 and direction == -1:
            GPIO.output(self.GPIO_IN1, GPIO.LOW)
            GPIO.output(self.GPIO_IN2, GPIO.HIGH)
        else:
            GPIO.output(self.GPIO_IN1, GPIO.HIGH)
            
        if run_time > 0:
            sleep(run_time)
            GPIO.output(self.GPIO_IN1, GPIO.LOW)
        
    def Off(self):
        GPIO.output(self.GPIO_IN1, GPIO.LOW)
        if self.GPIO_IN2 > 0:
            GPIO.output(self.GPIO_IN2, GPIO.LOW)
        
    def Toggle(self):
        if GPIO.input(self.GPIO_IN1):
            GPIO.output(self.GPIO_IN1, GPIO.LOW)
        else:
            GPIO.output(self.GPIO_IN1, GPIO.HIGH)
            
    def stopPWM(self):
        self.pwm.stop()

class Heater:
    def __init__(self, GPIO_control, GPIO_temp_input):
        self.self.GPIO_control = self.GPIO_control
        GPIO.setup(GPIO_control, GPIO.OUT)
        GPIO.setup(GPIO_temp_input, GPIO.IN)

    def On(self):
        GPIO.output(self.GPIO_control, GPIO.HIGH)
        
    def Off(self):
        GPIO.output(self.GPIO_control, GPIO.LOW)
        
class Stepper:
# 28BYJ-48 5V Stepper Motor (unipolar) and 5V bipolar driver
# PWMA, PWMB, STBY must be set to HIGH on TB6612!!!  
    def __init__(self, stGPIO_config):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        self.AIN1 = stGPIO_config[0]
        self.AIN2 = stGPIO_config[1]
        self.BIN1 = stGPIO_config[2]
        self.BIN2 = stGPIO_config[3]

        GPIO.setup(self.AIN2, GPIO.OUT)
        GPIO.setup(self.AIN1, GPIO.OUT)
        GPIO.setup(self.BIN1, GPIO.OUT)
        GPIO.setup(self.BIN2, GPIO.OUT)

        GPIO.output(self.AIN1,GPIO.LOW)
        GPIO.output(self.AIN2,GPIO.LOW)
        GPIO.output(self.BIN1,GPIO.LOW)
        GPIO.output(self.BIN2,GPIO.LOW)

    def runStepper(self, spd, steps, steppertype = 'unipolar'):
    
        if steppertype == 'unipolar':
            O = self.AIN1
            P = self.AIN2
            B = self.BIN1
            Y = self.BIN2
            
            hc = (1/spd)/2

#            steps = int(abs(angle)/(360/128))
            
            if angle < 0:
                B = self.AIN1
                Y = self.AIN2
                O = self.BIN1
                P = self.BIN2
                
            GPIO.output(O,1)
            sleep(hc)

            for i in range(steps):
                GPIO.output(Y,1)
                sleep(hc)
                GPIO.output(O,0)
                sleep(hc)  
                GPIO.output(P,1)
                sleep(hc)
                GPIO.output(Y,0)
                sleep(hc)
                GPIO.output(B,1)
                sleep(hc)
                GPIO.output(P,0)
                sleep(hc)
                GPIO.output(O,1)
                sleep(hc)
                GPIO.output(B,0)
                sleep(hc)
 
            GPIO.output(self.AIN1,GPIO.LOW)
            GPIO.output(self.AIN2,GPIO.LOW)
            GPIO.output(self.BIN1,GPIO.LOW)
            GPIO.output(self.BIN2,GPIO.LOW)
        
        elif steppertype == 'bipolar':
        #    GPIO.output(STBY, GPIO.HIGH)

#            steps = int(abs(angle)/(360/50))
            spd = spd * 2

            Ap = self.AIN1
            Am = self.AIN2
            Bp = self.BIN1
            Bm = self.BIN2
            
            if steps <  0:
                Ap = self.BIN1
                Am = self.BIN2
                Bp = self.AIN1
                Bm = self.AIN2

            for i in range(abs(steps)):
                GPIO.output(Ap,1)
                GPIO.output(Am,0) 
                sleep(1/spd)
                GPIO.output(Bp,0)
                GPIO.output(Bm,0)
                GPIO.output(Bp,1)
                GPIO.output(Bm,0)
                sleep(1/spd)
                GPIO.output(Ap,0)
                GPIO.output(Am,0)
                GPIO.output(Ap,0)
                GPIO.output(Am,1)
                sleep(1/spd)
                GPIO.output(Bp,0)
                GPIO.output(Bm,0)
                GPIO.output(Bp,0)
                GPIO.output(Bm,1)
                sleep(1/spd)
                GPIO.output(Ap,0)
                GPIO.output(Am,0)
                
            GPIO.output(self.AIN1,GPIO.LOW)
            GPIO.output(self.AIN2,GPIO.LOW)
            GPIO.output(self.BIN1,GPIO.LOW)
            GPIO.output(self.BIN2,GPIO.LOW)
                