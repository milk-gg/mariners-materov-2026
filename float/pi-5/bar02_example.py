# code via: https://bluerobotics.com/learn/bar-sensors-guide/#code-examples

import ms5837
import time

sensor = ms5837.MS5837_30BA()  # Change to MS5837_02BA if using Bar02

if not sensor.init():
    print("Sensor could not be initialized")
    exit(1)

while True:
    if sensor.read():
        print(("P: %0.1f mbar  %0.3f psi\tT: %0.2f C  %0.2f F") % (
            sensor.pressure(),
            sensor.pressure(ms5837.UNITS_psi),
            sensor.temperature(),
            sensor.temperature(ms5837.UNITS_Farenheit)))
    else:
        print("Sensor read failed!")
        exit(1)