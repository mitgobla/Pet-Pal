import socket
import sys
import time
import pigpio
from threading import Thread
import os
host = '192.168.1.64'
port = 80
red = 27#17#22
green = 17#27
blue = 22#17

BOWL = 'Empty'
ROOM = b'Mild'
MODE = 'TEMP'
DEPTH = b'Empty'
p = pigpio.pi()
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def reset():
    rl = p.set_PWM_dutycycle(red, 0)
    gl = p.set_PWM_dutycycle(green, 0)
    bl = p.set_PWM_dutycycle(blue, 0)
    p.stop()

def rd(br):
    rl = p.set_PWM_dutycycle(red, br)

def gr(br):
    gl = p.set_PWM_dutycycle(green, br)

def bu(br):
    bl = p.set_PWM_dutycycle(blue, br)

CALI = False

try:
    s.bind((host, port))
except socket.error as msg:
    print("Failed to bind. Error:", str(msg))
    try:
        port += 1
        s.bind((host, port))
    except socket.error as msg:
        print("Failed to bind. Error:", str(msg))
        sys.exit()



def temp_change():
    while MODE == 'TEMP':
        with os.popen('vcgencmd measure_temp') as measurement:
            cel = measurement.read().strip()
            degrees = int(cel[5:len(cel)-4])-15
        percent = (degrees/26)
        if CALI == False:
            if percent >= 0.9:
                rd(229)
                gr(0)
                bu(5)
                ROOM = b'Hot'
            elif percent >= 0.8:
                rd(231)
                gr(47)
                bu(4)
                ROOM = b'Warm'
            elif percent >= 0.7:
                rd(234)
                gr(98)
                bu(9)
                ROOM = b'Moderate'
            elif percent >= 0.6:
                rd(236)
                gr(148)
                bu(14)
                ROOM = b'Mild'
            elif percent >= 0.5:
                rd(239)
                gr(198)
                bu(50)
                ROOM = b'Cool'
            elif percent >= 0.4:
                rd(237)
                gr(242)
                bu(100)
                ROOM = b'Cold'
            elif percent >= 0.3:
                rd(229)
                gr(252)
                bu(150)
                ROOM = b'Cold'
            else:
                rd(150)
                gr(150)
                bu(200)
                ROOM = b'Cold'
            print(ROOM)
        time.sleep(5)
            
print("Host: ", host, " Port: ", port)
Thread(target=temp_change).start()
s.listen(100)
rd(0)
gr(0)
bu(0)
while 1:
    conn, addr = s.accept()
    print("Connected with ", addr[0], ":", addr[1])
    data = conn.recv(1024)
    #Connect to the ultrasonic sensor (Bowl sensor)
    if data == b'I am an ultrasonic sensor':
        time.sleep(1) #Pause to wait for incoming instruction
        while 1: #Now listen for data
            try: #Try and receive an instruction
                data = conn.recv(1024)
            except ConnectionResetError: #If no instruction was received
                break #Ignore operation and carry on as normal
            if not data: #Again, if no instruction was received
                break
            if data == b'I am calibrating': #The bowl is calibrating its depth
                #Full PURPLE
                CALI = True
                gr(0)
                bu(255)
                rd(255)
                print("Calibrating")
            elif data == b'Fill bowl': #User must then fill the bowl with water
                #Full YELLOW
                CALI = True
                bu(10)
                rd(255)
                gr(100)
                print("Fill bowl")
            elif data == b'CHECK': #When the client completes a check
                CALI = False
                print("Calibration done")
                break #Nothing to do. We just wait until it connects again.
            if MODE == 'BOWL':
                if data == b'Full': #Interactive lightning shows bowl depth on hub
                    #Full GREEN
                    rd(0)
                    bu(0)
                    gr(255)
                    DEPTH = b'Full'
                elif data == b'Low': #****
                    #ORANGE
                    rd(255)
                    gr(120)
                    DEPTH = b'Low'
                elif data == b'Empty': #****
                    #Full RED
                    rd(255)
                    gr(0)
                    DEPTH = b'Empty'
                elif data == b'Done': #When the client completes calibration
                    #Full Green
                    rd(0)
                    bu(0)
                    gr(55)
                    break
                print("Depth ", DEPTH)
    elif data == b'mode bowl':
        MODE = 'BOWL'
        print("Mode changed to bowl")
    elif data == b'mode temp':
        MODE = 'TEMP'
        print("Mode changed to temp")
        CALI = False
        Thread(target=temp_change).start()
    elif data == b'give temp':
        time.sleep(1)
        conn.send(b'temp '+ROOM)
        print(ROOM)
    elif data == b'give bowl':
        time.sleep(1)
        conn.send(b'bowl '+DEPTH)
        print(DEPTH)
    elif not data or data == b'close':
        conn.close()
        s.close()
        reset()
        sys.exit()
try:
    conn.close()
    s.close()
    reset()
except:
    pass

