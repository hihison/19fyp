from threading import Lock
from flask import Flask, render_template, session, request
from flask_socketio import SocketIO, emit, join_room, leave_room, \
	close_room, rooms, disconnect
import time
import os
import json
def num(s):
	try:
		return int(s)
	except ValueError:
		return s


import serial.tools.list_ports
for port in serial.tools.list_ports.comports():
	if (port.manufacturer=="Arduino (www.arduino.cc)"):
		print("Target found and its location is : "+str(port.device))
		target = str(port.device)
		break
	else:
		print("device target not found")
		exit()
print("Connecting "+" "+target)
import serial
ser=serial.Serial(target, 9600, timeout= 0.5 )
print("Connected : "+ser.name)
print("This is the port : "+ser.port)
print("===============================")

async_mode = None

app = Flask(__name__)

app.config['KEY'] = 'HAHA'
socketio = SocketIO(app, async_mode=async_mode)

thread = None
thread_lock = Lock()

#sensor stat
light = False
water = False
auto = True

def background_thread():
	"""Example of how to send server generated events to clients."""
	while True:
		#socketio.sleep(1)
		arduino_txt = ser.readline().decode("utf-8").replace("\n", "")
		if len(arduino_txt)>0:
			data_updating(arduino_txt)
			print(arduino_txt)
			socketio.emit('arduino_log',
						{'data': arduino_txt})

def stat_change(data):
	if(data == '1'):
		return True
	else:
		return False

def bool_to_str(bool):
	if(bool):
		return "已開啟"
	else:
		return "已關閉"

def stat_update(water_stat,auto_stat,light_stat):
	global light
	global water
	global auto
	
	light = light_stat
	water = water_stat
	auto =  auto_stat

	socketio.emit('stat_updating',
				{'light':bool_to_str(light_stat),'auto':bool_to_str(auto_stat),'water':bool_to_str(water_stat)})
	
def data_updating(txt):
	data=''
	data_type=''
	if (txt.find("Humi") > -1):
		data = txt.replace("Humi = ","")
		data_type = 'dirt_humi'
	
	if (txt.find("Light") > -1):
		data = txt.replace("Light = ","")
		data_type = 'light'
	
	if (txt.find("PUMP_STAT")> -1):
		data = txt.replace("PUMP_STAT: ","")
		data = data.replace("AUTO_STAT: ","")
		data = data.replace("LIGHT_STAT: ","")
		data = data.split("\t")
		water = stat_change(data[0])
		auto = stat_change(data[1])
		light = stat_change(data[2])
		stat_update(water,auto,light)

	
	if ( data != '' and data_type != ''):
		socketio.emit('data_updating',
						{'data_type':data_type ,'data':data})

@app.route('/')
def index():
	return render_template('index.html')
	
@socketio.on( 'mode changer')
def event (txt):
	print("GET HTML: "+txt)
	
	global light
	global water
	global auto
	
	#light switch
	if (txt == 'light'):
		ser.write(b'0')
		light = not light
		mode = bool_to_str(light)
		print("Python to arduino: Light Control.")


	#water switch
	if (txt == 'water' and auto != True):
		ser.write(b'1')
		water = not water
		mode = bool_to_str(water)
		print("Python to arduino: Water Control.")

	#auto mode
	if (txt == 'auto'):
		ser.write(b'2')
		auto = not auto
		mode = bool_to_str(auto)
		print("Python to arduino: Auto Mode Switch.")

	#data
	if (txt == 'data'):
		ser.write(b'3')
		mode = '已取得'
		print("Python to arduino: Get Data.")
		
	get_log()
	ser.write(b'4')
	socketio.emit('update', { 'item': txt, 'now': mode})
	

def get_log():
	socketio.emit('get_log',{})

@socketio.on('output_log')
def output_log(data):
	print (data)
	with open('data.json', 'w') as outfile:
		json.dump(data, outfile)



@socketio.on('connect')
def test_connect():
	global thread
	with thread_lock:
		if thread is None:
			thread = socketio.start_background_task(background_thread)
	emit('arduino_log', {'data': 'Connect Success!', 'count': 0})
	socketio.sleep(1)
	ser.write(b'4')
	socketio.sleep(1)
	ser.write(b'3')

	
if __name__ == '__main__':
	#socketio.bind("192.168.0.107:5000");
	socketio.run(app,host='192.168.43.153',debug = True )
