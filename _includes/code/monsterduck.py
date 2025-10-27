

from flask import Flask
app = Flask(__name__)

import time
import RPi.GPIO as GPIO
import requests
GPIO.setmode(GPIO.BOARD)

GPIO.setup(12, GPIO.OUT)
GPIO.setup(32, GPIO.OUT)
GPIO.setup(33, GPIO.OUT)
GPIO.setup(35, GPIO.OUT)

start_speed = 0
start_delay = 0
current_speed = 0
chose_speed = False
in_startup = True
chose_delay = False
stopped = False

## VARIABLES TO ADJUST
sensor_pins = [7, 11, 13, 15, 29, 40] # The pins holding the sensors, from Robot's Left -> Right
    # Stage left to stage right if you're a theater person
driving_ramp = "right" # Which ramp you're driving on (actual LR this time)
crit_num = 1 # Number of sensors that must be on to activate a half

motor1pin1 = GPIO.PWM(12, 500)  # channel=12; frequency=500Hz
motor1pin2 = GPIO.PWM(32, 500)
motor1pin1.start(0)
motor1pin2.start(0)

motor2pin1 = GPIO.PWM(33, 500)
motor2pin2 = GPIO.PWM(35, 500)
motor2pin1.start(0)
motor2pin2.start(0)

motors = [[motor1pin1, motor1pin2],[motor2pin1,motor2pin2]]

def drive(speed):
    speed = int(0.331*speed + 32.3)
    print("Driving Now, speed of", speed)
    for i in range(0,2):
        motors[i][0].ChangeDutyCycle(0)
        motors[i][1].ChangeDutyCycle(speed)

def stop():
    print("Stopping Now")
    for i in range(0,2):
        motors[i][0].ChangeDutyCycle(0)
        motors[i][1].ChangeDutyCycle(0)

## Calculation Variables - Do not adjust
num_sensors = len(sensor_pins)
mid_range = num_sensors / 2.0 - 0.5 # Splits our robots sensors into two halves

def setup_sensors(sensor_pins):
    print("A")
    for i in range(0, len(sensor_pins)):
        print(sensor_pins[i])
        GPIO.setup(sensor_pins[i], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    print("B")


def read_sensors(sensor_pins):
    # Read in sensor values
    left_pings = 0
    right_pings = 0
    robot_state = "perfect"
    s = [0, 0, 0, 0, 0, 0]
    for i in range(0, num_sensors):
        s_reading = GPIO.input(sensor_pins[i])
        s[i] = s_reading
        if s_reading == 1 and i < mid_range:
            left_pings = left_pings + 1
        elif s_reading == 1 and i > mid_range:
            right_pings = right_pings + 1
    #print(s)
    if(left_pings >= crit_num and right_pings < crit_num):
        if(driving_ramp == "left"):
            robot_state = "behind"
        elif(driving_ramp == "right"):
            robot_state = "ahead"
    elif(left_pings < crit_num and right_pings >= crit_num):
        if(driving_ramp == "left"):
            robot_state = "ahead"
        elif(driving_ramp == "right"):
            robot_state = "behind"
    return robot_state


def negotiate_target_speed_with_partner(url, desired_speed):
    r = requests.get(url+"/target/"+str(desired_speed))
    print("speed response:", r.text)
    if r.text == "ok":
        if in_startup:
            global start_speed
            start_speed = int(desired_speed)
            global chose_speed
            chose_speed = True
            print('changed chose speed to true')
    return r.text
       

def negotiate_start_delay_with_partner(url,delay):
    r = requests.get(url+"/start/"+str(delay))
    print("delay resopnse:", r.text)
    if r.text == "ok":
        print("they said ok to the delay")
        global chose_delay
        chose_delay = True
        global start_delay
        start_delay = int(delay)
        print("changed chose delay to true")


@app.route('/target/')
def change_speed(speed):
    speed = int(speed)
    print("recieved speed request of", speed)
    if speed == 0:
        stop()
        return "ok"
    elif speed > 200 or speed < 115:
        return "no"
    else:
        if not in_startup:
            print("changing speed now")
            drive(speed)
        else:
            global start_speed
            start_speed = speed
            global chose_speed
            chose_speed = True
    return "ok"


@app.route('/start/')
def start(delay):
    print("in delay app route")
    global chose_delay
    delay = int(delay)
    print("delay:", delay)
    if chose_delay == False and delay > 2 and delay < 11:
        global start_delay
        start_delay = delay
        chose_delay = True
        print("changed chose delay to true")
        return "ok"
    else:
        return "no"


@app.route('/do-once')
def do_once():
    stop()
    setup_sensors(sensor_pins)
    #url = "http://10.243.94.119:5000" # sol, andy, ariana
    #url = "http://10.243.80.29:5000" # ryan
    #url = "http://10.243.83.159:5000" # chris
    #url = "http://10.243.83.139:5000" # audrey
    url = "http://10.243.87.169:5000" # cade
    start_time = time.monotonic()
    speed = 150
    delay = 3
    global chose_speed
    global chose_delay
    global start_delay
    while (chose_speed==False) or (chose_delay==False):
        if time.monotonic() > start_time + 2:
            print("start delay:", start_delay)
            if chose_speed == False:
                print("sending speed", speed)
                negotiate_target_speed_with_partner(url, speed)   # needs partner url and speed request
            if chose_delay == False:
                print("sending delay", delay)
                negotiate_start_delay_with_partner(url, delay)   # needs partner url and speed request
            # read sensors
            if read_sensors(sensor_pins) == "behind":
                print("we are behind and think they started driving")
                #drive(100)
                chose_speed = True
                chose_delay = True
                start_delay = 0
            speed+=10
            if speed == 200:
                speed = 120
            delay+=1
            if delay == 10:
                delay = 0
            start_time = time.monotonic()
    print("SETTLED ON A START SPEED OF", start_speed, "WITH A DELAY OF", start_delay)
    time.sleep(start_delay)
    global in_startup
    in_startup = False
    global current_speed
    current_speed = start_speed
    drive(speed)
    start_time = 0
    partner_speed = current_speed
    time1 = time.monotonic()
    response = "ok"
    asked_again = False
    while True:
        if time.monotonic() > start_time + 0.5:
            robot_state = read_sensors(sensor_pins)
            if response == "no":
                if robot_state == "behind":
                    negotiate_target_speed_with_partner(url, 150)
                elif robot_state == "ahead":
                    negotiate_target_speed_with_partner(url, 150)
                asked_again = True
            if not asked_again:
                if robot_state == "behind":
                    print("behind")
                    # ask partner to slow down
                    response = negotiate_target_speed_with_partner(url, 100)
                    if current_speed < 180:
                        current_speed+=20
                        drive(current_speed)
                elif robot_state == "ahead":
                    print("ahead")
                    # ask partner to slow down
                    response = negotiate_target_speed_with_partner(url, 200)
                    if current_speed > 135:
                        current_speed-=20
                        drive(current_speed)
            else:
                asked_again = False
            start_time = time.monotonic()
        if time.monotonic() > time1 + 60:
            stop()
            break
        if stopped == True:
            break
    return "ready"


@app.route('/emergency-stop')
def emergency_stop():
    stop()
    print("emergency stop")
    global stopped
    stopped = True
    return "stopped"