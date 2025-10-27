import hub, time

from hub import port

def swing(degrees, power):

    swingSpeed = int(power)

    drawSpeed = int(power * 0.25)

    time.sleep(0.5)

    motor.run_for_degrees(port.B, degrees, drawSpeed)

    time.sleep(1)

    motor.run_for_degrees(port.B, -2 * degrees, swingSpeed)

    time.sleep(3)

    motor.run_for_degrees(port.B, degrees, drawSpeed)


swing(75, 300);