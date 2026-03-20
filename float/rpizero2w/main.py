import time, sys, os

common_path = os.path.join(os.path.dirname(__file__), '../../common')
sys.path.insert(0, common_path)

import ms5837

from rf_communication import receive_string, send_string

sensor = ms5837.MS5837_02BA()
sensor.setFluidDensity(998)  # kg/m^3 for ms5837 depth calculation

if not sensor.init():
    print("Sensor could not be initialized")
    exit(1)

def create_data_packet(company_number, start_time) -> str:
    """
    Creates a comma-separated data packet string with required fields.
    Format: company,time,pressure,depth,temperature
    """
    if not sensor.read():
        print("Sensor read failed!")
        return None

    float_time = time.time() - start_time

    packet_parts = [
        str(company_number),
        f"{float_time:.3f}",  # seconds
        f"{sensor.pressure():.3f}",  # millibar
        f"{sensor.depth():.3f}",  # meters
    ]
    
    return ",".join(packet_parts)  # Join with commas

def parse_data_packet(packet_string: str) -> dict:
    """
    Parses a comma-separated data packet string back into a dictionary.
    Expected format: company,time,pressure,depth
    """
    try:
        parts = packet_string.split(",")
        if len(parts) != 4:
            raise ValueError("Invalid packet format: expected 4 fields")
        
        return {
            "company": parts[0],
            "time": float(parts[1]),
            "pressure": float(parts[2]),
            "depth": float(parts[3])
        }
    except (ValueError, IndexError) as e:
        print(f"Error parsing packet: {e}")
        return None

def main():
    while True:
        packet_string = receive_string()
        parsed = parse_data_packet(packet_string)
        if parsed:
            print(f"Parsed: Company={parsed['company']}, Time={parsed['time']:.3f}s, Pressure={parsed['pressure']:.3f}mbar, Depth={parsed['depth']:.3f}m")
        time.sleep(1)  # Interval between packets

if __name__ == "__main__":
    main()