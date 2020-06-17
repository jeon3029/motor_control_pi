from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import QtSql
import time
from Raspi_MotorHAT import Raspi_MotorHAT#, Raspi_DCMotor
from sense_hat import SenseHat


#motor init!!!
mh = Raspi_MotorHAT(addr=0x6f)
dcMotor = mh.getMotor(3)#
speed = 125 #
dcMotor.setSpeed(speed)
servo = mh._pwm
servo.setPWMFreq(60)
R_limit = 450
L_limit = 250
mid_center = 350
L_itv = L_limit-mid_center
R_itv = R_limit-mid_center

print("motor init ok")
sen = SenseHat()
print("sensehat init ok")
# TODO: 온도 정보 db에 전달

class pollingThread(QThread):
	def __init__(self):
		super().__init__()

	def run(self):
		self.db = QtSql.QSqlDatabase.addDatabase('QMYSQL')
		self.db.setHostName("3.34.124.67")
		self.db.setDatabaseName("15_10")
		self.db.setUserName("15_10")
		self.db.setPassword("1234")
		ok = self.db.open()
		print(ok)
		self.getQuery()

	def getQuery(self):
		while True:
			time.sleep(0.1)
			#----------------motor hat ----------------------
			query = QtSql.QSqlQuery("select * from command1 order by time desc limit 1");
			query.next()
			cmdTime = query.record().value(0)
			cmdType = query.record().value(1)
			cmdArg = query.record().value(2)
			is_finish = query.record().value(3)

			if is_finish == 0 :
              	#detect new command
				print(cmdTime.toString(), cmdType, cmdArg)

				#update
				query = QtSql.QSqlQuery("update command1 set is_finish=1 where is_finish=0");

				#motor
				if cmdType == "go":
					self.go()
				elif cmdType == "back": 
					self.down()
				elif cmdType == "left": 
					self.left()
				elif cmdType == "right": 
					self.right()
				elif cmdType == "mid": 
					self.mid()
				elif cmdType == "stop":
					self.stop()
          #--------------- sensehat----------------------
			query = QtSql.QSqlQuery("select * from command2 order by time desc limit 1");
			query.next()
			cmdTime = query.record().value(0)
			cmdText = query.record().value(1)
			is_finish = query.record().value(2)
			count = query.record().value(3)
			if is_finish == 0 :
				#detect new command
				print(cmdTime.toString(), cmdType, cmdArg)
				#update
				query = QtSql.QSqlQuery("update command2 set is_finish=1 where is_finish=0");
				#sensehat
				for i in range(count):
					sen.show_message(cmdText)

	def go(self):
		print("MOTOR GO")
		dcMotor.run(Raspi_MotorHAT.FORWARD)
	#time.sleep(1)
	#dcMotor.run(Raspi_MotorHAT.RELEASE)
  
	def stop(self):
		print("MOTOR STOP")
		dcMotor.run(Raspi_MotorHAT.RELEASE)


	def down(self):
		print("MOTOR BACK")
		dcMotor.run(Raspi_MotorHAT.BACKWARD)
		time.sleep(1)
		dcMotor.run(Raspi_MotorHAT.RELEASE)

	def left(self):
		steer(-30)
		print("MOTOR LEFT")

	def right(self):
		steer(30)
		print("MOTOR RIGHT")

	def mid(self):
		steer(0)
		print("MOTOR MID")



def steer(angle=0): #
	if angle <= -30: #
		angle = -30

	if angle >= 30:
		angle = 30

	pulse_time = mid_center

	if angle == 0 :
		pulse_time = mid_center
		servo.setPWM(0,0,mid_center)

	elif angle > 0 : # LEFT
	#a2pul = int(angle*L_itv/30) + mid_center
		pulse_time = int(angle*L_itv/30) + mid_center
		servo.setPWM(0,0,pulse_time)

	elif angle < 0 : #RIGHT
		pulse_time = int(angle*R_itv/30)*(-1) + mid_center
		servo.setPWM(0,0,pulse_time)

	else :
		servo.setPWM(0,0,pulse_time)
    #pulse_time = 170+(340-200)//180*(angle+90)
    #servo.setPWM(0,0,pulse_time)

th = pollingThread()
th.start()

#app = QApplication([])

#infinity loop
while True:
	pass
