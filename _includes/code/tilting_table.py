''' Tilting Table Maze Code

Christopher Foraste

November 15, 2024

Credits: The Stepper Motor code from the ME 30 Website was used to get the stepper motors working. All other code is my own.

'''


import time, board, analogio, digitalio

from adafruit_motor import stepper


# Set the number of steps for one rotation of the motor. For the stepper motor in the ME 30 kit, one rotation takes 200 steps.

STEPS = 200


# Define Stepper Pins

coils = (

    digitalio.DigitalInOut(board.D2),  # A1

    digitalio.DigitalInOut(board.D3),  # A2

    digitalio.DigitalInOut(board.D4),  # B1

    digitalio.DigitalInOut(board.D5),  # B2

)


coils2 = (

    digitalio.DigitalInOut(board.D6),  # A1

    digitalio.DigitalInOut(board.D7),  # A2

    digitalio.DigitalInOut(board.D8),  # B1

    digitalio.DigitalInOut(board.D9),  # B2

)


for coil in coils:

    coil.direction = digitalio.Direction.OUTPUT


for coil in coils2:

    coil.direction = digitalio.Direction.OUTPUT


# Define Joystick Inputs

lstick = analogio.AnalogIn(board.A1)

rstick = analogio.AnalogIn(board.A0)


# Define Switch boundaries

ls_lowermid = 30000;

ls_uppermid = 35000;


rs_lowermid = 25000;

rs_uppermid = 35000;


# Define Motor

motor = stepper.StepperMotor(coils[0], coils[1], coils[2], coils[3], microsteps=None)

motor2 = stepper.StepperMotor(coils2[0], coils2[1], coils2[2], coils2[3], microsteps=None)


min_delay = .003;

max_delay = .008;


m1cooldown = 0

m1lastping = time.monotonic()


m2cooldown = 0

m2lastping = time.monotonic()


print("Starting")


stepsLeft = 0;

stepsRight = 0;


while True:

    if(time.monotonic() - m2lastping > m2cooldown):

        if(lstick.value < ls_lowermid and stepsLeft <= 90):

            m2cooldown = min_delay + ((max_delay - min_delay) / ls_lowermid) * (lstick.value)

            motor2.onestep(direction=0)

            stepsLeft += 1;

            m2lastping = time.monotonic()

        elif(lstick.value > ls_uppermid and stepsLeft >= -45):

            m2cooldown = min_delay + ((max_delay - min_delay) / (65536 - ls_uppermid)) * (65536 - lstick.value)

            motor2.onestep(direction=1)

            stepsLeft -= 1;

            m2lastping = time.monotonic()


    if(time.monotonic() - m1lastping > m1cooldown):

        if(rstick.value < rs_lowermid and stepsRight <= 90):

            m1cooldown = min_delay + ((max_delay - min_delay) / rs_lowermid) * (rstick.value)

            motor.onestep(direction=1)

            stepsRight += 1;

            m1lastping = time.monotonic()

        elif(rstick.value > rs_uppermid and stepsRight >= -45):

            m1cooldown = min_delay + ((max_delay - min_delay) / (65536 - rs_uppermid)) * (65536 - rstick.value)

            motor.onestep(direction=0)

            stepsRight -= 1;

            m1lastping = time.monotonic()

    time.sleep(0.0005)


motor.release()