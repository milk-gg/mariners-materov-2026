import time

import ms5837

from common.rf_communication import recieve_string, send_string

sensor = ms5837.MS5837_02BA()

if not sensor.init():
    print("Sensor could not be initialized")
    exit(1)

def main():
    if sensor.read():
        print(("P: %0.1f mbar  %0.3f psi\tT: %0.2f C  %0.2f F") % (
            sensor.pressure(),
            sensor.pressure(ms5837.UNITS_psi),
            sensor.temperature(),
            sensor.temperature(ms5837.UNITS_Farenheit)))
    else:
        print("Sensor read failed!")
        exit(1)

if __name__ == "__main__":
    main()