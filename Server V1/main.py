"""Team Lightning Project 2017 Pet Pal Home-Care System
Author: Ben Dodd (mitgobla)
Version: 1.0.2
Date: 20/03/17"""

import socket #Used to create the server
import sys #Used to terminate the program
import time #Used to pausing and time management
import os #Used to gather temperature
from threading import Thread #Used to run server more efficiently
import pigpio #Used for the control of LEDs

HOST = '192.168.1.64' #Local IP address of the PI when running on the BTBusinessHub
PORT = 80 #Unblocked HTTP port
RED_PIN = 27 #GPIO Pin for RED LED
GREEN_PIN = 17 #GPIO Pin for GREEN LED
BLUE_PIN = 22 #GPIO Pin for BLUE LED

class Bowl(): #Ultrasonic Sensor Module
    """Class used to store and calculate bowl values"""
    def __init__(self): #Creates all the variables to be used by the class
        """Class used to store and calculate bowl values"""
        #Status: stores the state of the bowl e.g. calibrating, fill, etc.
        self.status = 'Need Setup'
        #Depth: stores the depth of the bowl e.g. full, empty, etc.
        self.depth = 'Empty'
        print("Created bowl module")

    def set_status(self, new_status):
        """Change the status of the bowl""" #<---
        self.status = new_status
        print("Bowl Status: ", self.status)
        return self.status

    def set_depth(self, new_depth):
        """Change the depth value of the bowl""" #<---
        self.depth = new_depth
        print("Bowl Depth: ", self.depth)
        return self.depth

    def get_depth(self):
        """Get the depth value of the bowl""" #<---
        print("Bowl Depth: ", self.depth)
        return self.depth

    def get_status(self):
        """Get the status of the bowl""" #<---
        print("Bowl Status: ", self.status)
        return self.status

class Temperature(): #Temperature module
    """Class used to store and calculate temperature values"""
    def __init__(self):
        """Class used to store and calculate temperature values"""
        self.temperature = 'Need Setup' #Stores values like Hot, Mild, etc.
        print("Created temperature module")

    def set_temperature(self, new_temperature):
        """Change the temperature value of the hub""" #<---
        self.temperature = new_temperature
        print("Temperature: ", self.temperature)
        return self.temperature

    def get_temperature(self):
        """Get the temperature value of the hub""" #<---
        print("Temperature: ", self.temperature)
        return self.temperature

class Lighting():
    """Class used to control LED lighting"""
    def __init__(self):
        """Class used to control LED lighting"""
        self.hub = pigpio.pi()
        self.red_led = self.hub.set_PWM_dutycycle(27, 0) #Sets the RED LED brightness to 0
        self.green_led = self.hub.set_PWM_dutycycle(17, 0)
        self.blue_led = self.hub.set_PWM_dutycycle(22, 0)
        print("Created LED module")

    def reset(self):
        """Turns off all the LEDs"""
        self.red_led = self.hub.set_PWM_dutycycle(27, 0)
        self.green_led = self.hub.set_PWM_dutycycle(17, 0)
        self.blue_led = self.hub.set_PWM_dutycycle(22, 0)
        print("Reset ALL LEDS")

    def red(self, brightness):
        """Configure the Red LED"""
        if isinstance(brightness, str):
            try:
                if int(brightness) > 255:
                    self.red_led = self.hub.set_PWM_dutycycle(27, 255)
                elif int(brightness) < 0:
                    self.red_led = self.hub.set_PWM_dutycycle(27, 0)
                else:
                    self.red_led = self.hub.set_PWM_dutycycle(27, int(brightness))
                print("Updated Brightness")
            except TypeError as error_message:
                print("Invalid brightness value.\n", error_message)
        elif isinstance(brightness, int):
            if brightness > 255:
                self.red_led = self.hub.set_PWM_dutycycle(27, 255)
            elif brightness < 0:
                self.red_led = self.hub.set_PWM_dutycycle(27, 0)
            else:
                self.red_led = self.hub.set_PWM_dutycycle(27, brightness)
            print("Updated Brightness")
        else:
            print("Invalid brightness value.")

    def green(self, brightness):
        """Configure the Red LED"""
        if isinstance(brightness, str):
            try:
                if int(brightness) > 255:
                    self.green_led = self.hub.set_PWM_dutycycle(17, 255)
                elif int(brightness) < 0:
                    self.green_led = self.hub.set_PWM_dutycycle(17, 0)
                else:
                    self.green_led = self.hub.set_PWM_dutycycle(17, int(brightness))
                print("Updated Brightness")
            except TypeError as error_message:
                print("Invalid brightness value.\n", error_message)
        elif isinstance(brightness, int):
            if brightness > 255:
                self.green_led = self.hub.set_PWM_dutycycle(17, 255)
            elif brightness < 0:
                self.green_led = self.hub.set_PWM_dutycycle(17, 0)
            else:
                self.green_led = self.hub.set_PWM_dutycycle(17, brightness)
            print("Updated Brightness")
        else:
            print("Invalid brightness value.")

    def blue(self, brightness):
        """Configure the Red LED"""
        if isinstance(brightness, str):
            try:
                if int(brightness) > 255:
                    self.blue_led = self.hub.set_PWM_dutycycle(22, 255)
                elif int(brightness) < 0:
                    self.blue_led = self.hub.set_PWM_dutycycle(22, 0)
                else:
                    self.blue_led = self.hub.set_PWM_dutycycle(22, int(brightness))
                print("Updated Brightness")
            except TypeError as error_message:
                print("Invalid brightness value.\n", error_message)
        elif isinstance(brightness, int):
            if brightness > 255:
                self.blue_led = self.hub.set_PWM_dutycycle(22, 255)
            elif brightness < 0:
                self.blue_led = self.hub.set_PWM_dutycycle(22, 0)
            else:
                self.blue_led = self.hub.set_PWM_dutycycle(22, brightness)
            print("Updated Brightness")
        else:
            print("Invalid brightness value.")

class Hub():
    """Class used for main server management"""
    def __init__(self, host, port):
        """Class used for main server management"""
        self.temp_module = None
        self.bowl_module = None
        self.led_module = None
        self.server_running = False
        self.mode = None
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.changeable_port = int(port)
            self.server.bind((str(host), int(port)))
            print("Created host and port")
        except socket.error:
            try:
                self.changeable_port += 1
                self.server.bind((str(host), self.changeable_port))
                print('Created host and port')
            except socket.error as error_message:
                print("Failed to bind. Error:", str(error_message))
                sys.exit()

    def add_temperature_module(self):
        """Create a temperature module"""
        self.temp_module = Temperature()
        with os.popen('vcgencmd measure_temp') as measurement:
            raw_temperature = measurement.read().strip()
            celsius = int(raw_temperature[5:len(raw_temperature)-4])-15
        if celsius/26 >= 0.66:
            self.temp_module.set_temperature(b'Hot')            
        elif celsius/26 >= 0.33:
            self.temp_module.set_temperature(b'Normal')
        else:
            self.temp_module.set_temperature(b'Cold')
        print("Added Temperature module")

    def set_temperature_module(self):
        """Update the temperature"""
        with os.popen('vcgencmd measure_temp') as measurement:
            raw_temperature = measurement.read().strip()
            celsius = int(raw_temperature[5:len(raw_temperature)-4])-15
        if celsius/26 >= 0.66:
            self.temp_module.set_temperature(b'Hot')
        elif celsius/26 >= 0.33:
            self.temp_module.set_temperature(b'Normal')
        else:
            self.temp_module.set_temperature(b'Cold')
            print("Updated Temperature Module")

    def add_bowl_module(self):
        #Status information:
        #1: First time setup
        #2: Calibrating
        #3. Fill the Bowl
        #4. Done Calibration
        """Create a Bowl module"""
        self.bowl_module = Bowl()
        self.bowl_module.set_status("1")
        print("Added Bowl Module")

    def set_bowl_module(self, depth):
        """Update the bowl"""
        self.bowl_module.set_depth(depth)
        print("Updated Bowl Module")

    def set_bowl_status(self, status):
        """Update the bowl status"""
        self.bowl_module.set_status(status)
        print("Updated Bowl Module Status")

    def add_led_module(self):
        """Gains control of the LEDs on the hub"""
        self.led_module = Lighting()
        self.led_module.red(255)
        self.led_module.green(255)
        print("Added LED Module")

    def run_server(self):
        """Run the server side of the hub"""
        #--------------------- ADD MODULES HERE --------------
        self.add_bowl_module()
        self.add_temperature_module()
        #-----------------------------------------------------





        #-----------------------------------------------------
        self.server_running = True
        self.run_visuals()
        self.server.listen(100)
        print("Waiting for connections")
        while self.server_running:
            connection, address = self.server.accept()
            print("Connected with ", address[0], ":", address[1])
            #----------------------------------------------------
            data = connection.recv(1024)
            #----------------------------------------------------
            #------------------ CODES ---------------------------
            #1: Ultrasonic sensor
            #1a:    Calibrating
            #1b:    Fill Bowl
            #1c:    Calibrated
            #1A:    Full
            #1B:    Low
            #1C:    Empty
            #2: Mobile Phone
            #2a:    Mode Temp
            #2b:    Mode Bowl
            #2c:    Mode None
            #2A:    Get Bowl
            #2B:    Get Temp
            if data == b'1': #ULTRASONIC SENSOR HAS CONNECTED
                print("Ultrasonic sensor has connected")
                time.sleep(1) #ALLOW DELAY FOR DATA TO BE RECEIVED
                try:
                    data = connection.recv(1024) #DEVICE IS SENDING INFORMATION
                    print("Data received from ultrasonic sensor")
                except (ConnectionAbortedError, ConnectionResetError): #DEVICE HAS DISCONNECTED
                    break
                #------------- PROCESS DATA --------------------
                if not data: #DEVICE HAS DISCONNECTED CORRECTLY
                    break
                elif data == b'1a': #DEVICE IS CALIBRATING
                    print("Ultrasonic sensor calibrating")
                    self.bowl_module.set_status("2")
                elif data == b'1b': #DEVICE WANTS USER TO FILL BOWL
                    print("Ultrasonic sensor needs filling")
                    self.bowl_module.set_status("3")
                elif data == b'1c': #DEVICE IS COMPLETE
                    print("Ultrasonic sensor completed")
                    self.bowl_module.set_status("4")
                elif data == b'1A': #DEVICE IS FULL
                    print("Bowl is full")
                    self.bowl_module.set_depth(b'Full')
                elif data == b'1B': #DEVICE IS LOW
                    print("Bowl is low")
                    self.bowl_module.set_depth(b'Low')
                elif data == b'1C': #DEVICE IS EMPTY
                    print("Bowl is empty")
                    self.bowl_module.set_depth(b'Empty')
                try:
                    connection.close()
                except Exception:
                    pass
            #--------------------------------------------------------------
            elif data == b'2': #MOBILE PHONE HAS CONNECTED
                print("Phone has connected")
                time.sleep(1) #ALLOW DELAY FOR DATA TO BE RECEIVED
                try:
                    data = connection.recv(1024) #DEVICE IS SENDING INFORMATION
                    print("Data received from phone")
                except (ConnectionAbortedError, ConnectionResetError): #DEVICE HAS DISCONNECTED
                    break
                #------------- PROCESS DATA --------------------
                if not data:
                    break
                elif data == b'2a':
                    self.mode = "Temp"
                    print("Mode changed to Temp")
                elif data == b'2b':
                    self.mode = "Bowl"
                    print("Mode changed to Bowl")
                elif data == b'2c':
                    self.mode = None
                    print("Mode changed to None")
                elif data == b'2A':
                    time.sleep(1)
                    print("Sending depth")
                    connection.send(b'bowl '+self.bowl_module.get_depth())
                elif data == b'2B':
                    print("Sending Temperature")
                    time.sleep(1)
                    connection.send(b'temp '+self.temp_module.get_temperature())
                try:
                    connection.close()
                except Exception:
                    pass
            elif not data or data == b'forceshutdown':
                connection.close()
                self.server_running = False
        self.server.close()

    def run_visuals(self):
        """Run the visual side of the hub"""
        while self.server_running:
            while self.mode == "Temp":
                print("Temp Mode LED")
                temp = self.temp_module.get_temperature()
                if temp == b'Hot':
                    print("LED HOT")
                    self.led_module.red(255)
                    self.led_module.green(100)
                    self.led_module.blue(0)
                if temp >= b'Normal':
                    print("LED NORMAL")
                    self.led_module.red(0)
                    self.led_module.green(255)
                    self.led_module.blue(50)
                else:
                    print("LED COLD")
                    self.led_module.red(0)
                    self.led_module.green(50)
                    self.led_module.blue(255)
                time.sleep(15)
            while self.mode == "Bowl":
                print("Bowl mode LED")
                status = self.bowl_module.get_status()
                if status == "1":
                    print("LED RED")
                    self.led_module.red(255)
                    self.led_module.green(0)
                    self.led_module.blue(0)
                elif status == "2":
                    print("LED PURPLE")
                    self.led_module.red(255)
                    self.led_module.green(0)
                    self.led_module.blue(255)
                elif status == "3":
                    print("LED CYAN")
                    self.led_module.red(0)
                    self.led_module.green(255)
                    self.led_module.blue(255)
                elif status == "4":
                    depth = self.bowl_module.get_depth()
                    if depth == b'Full':
                        self.led_module.red(0)
                        self.led_module.green(255)
                        self.led_module.blue(0)
                    elif depth == b'Low':
                        self.led_module.red(255)
                        self.led_module.green(255)
                        self.led_module.blue(0)
                    else:
                        self.led_module.red(255)
                        self.led_module.green(0)
                        self.led_module.blue(0)
                time.sleep(15)
            while self.mode is None:
                self.led_module.reset()
                time.sleep(5)

PET_PAL = Hub(HOST, PORT)
Thread(target=PET_PAL.run_server()).start()
