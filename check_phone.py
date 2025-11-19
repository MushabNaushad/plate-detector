import subprocess
import time
import RPi.GPIO as GPIO

# Configuration
Target_Phone_MAC = "90:B7:90:07:FC:F0"  # Replace with your phone's MAC
GATE_PIN = 17 # GPIO pin connected to the relay

# Setup GPIO
#GPIO.setmode(GPIO.BCM)
#GPIO.setup(GATE_PIN, GPIO.OUT)
#GPIO.output(GATE_PIN, GPIO.LOW) # Keep gate closed initially

def check_presence(address):
    # l2ping sends a ping to the bluetooth device
    # -c 1 sends 1 packet, -t 1 sets timeout to 1 second
    command = f"sudo l2ping -c 1 -t 1 {address}"
    try:
        subprocess.check_output(command, shell=True)
        return True
    except subprocess.CalledProcessError:
        return False

def open_gate():
    print("Car detected! Opening Gate...")
   # GPIO.output(GATE_PIN, GPIO.HIGH)
   # time.sleep(1) # Simulate button press duration
   # GPIO.output(GATE_PIN, GPIO.LOW)
   # time.sleep(60) # Wait 60s before scanning again so the gate doesn't toggle

try:
    print("Scanning for car...")
    while True:
        if check_presence(Target_Phone_MAC):
            open_gate()
        else:
            print("No car in range...")
        
        time.sleep(2) # Wait between scans to save CPU/interference

except KeyboardInterrupt:
    GPIO.cleanup()
