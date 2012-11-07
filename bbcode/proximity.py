import os
import select
import datetime

PWM_FREQUENCY = 3 #hz
MIN_DUTY_NS   = 500000

PWM_PATH      = "/sys/class/pwm/"
GPIO_PATH     = "/sys/class/gpio/"

gpio0 = 0
gpio1 = gpio0+32
gpio2 = gpio1+32
gpio3 = gpio2+32

pwm_pins = {
    "P8_13": { "name": "EHRPWM2B", "gpio": gpio0+23, "mux": "gpmc_ad9", "eeprom": 15, "pwm" : "ehrpwm.2:1"  },
    "P8_19": { "name": "EHRPWM2A", "gpio": gpio0+22, "mux": "gpmc_ad8", "eeprom": 14, "pwm" : "ehrpwm.2:0"  },
    "P9_14": { "name": "EHRPWM1A", "gpio": gpio1+18, "mux": "gpmc_a2", "eeprom": 34, "pwm" : "ehrpwm.1:0" },
    "P9_16": { "name": "EHRPWM1B", "gpio": gpio1+19, "mux": "gpmc_a3", "eeprom": 35, "pwm" : "ehrpwm.1:1" },
    "P9_31": { "name": "SPI1_SCLK", "gpio": gpio3+14, "mux": "mcasp0_aclkx", "eeprom": 65 , "pwm": "ehrpwm.0:0"},
    "P9_29": { "name": "SPI1_D0", "gpio": gpio3+15, "mux": "mcasp0_fsx", "eeprom": 61 , "pwm": "ehrpwm.0:1"},
    "P9_42": { "name": "GPIO0_7", "gpio": gpio0+7, "mux": "ecap0_in_pwm0_out", "eeprom": 4, "pwm": "ecap.0"},
    "P9_28": { "name": "SPI1_CS0", "gpio": gpio3+17, "mux": "mcasp0_ahclkr", "eeprom": 63, "pwm": "ecap.2" },
}


class Proximity:
	def attach(self, pin, gpio):
		if not pin in pwm_pins:
			raise Exception('Pin ' + pin + 'is not pwm capable')
		else:
			self.__pin = PWM_PATH+pwm_pins[pin]["pwm"]
			self.__gpio = GPIO_PATH
			self.__gpioNum = gpio
			
			val = open(self.__pin + "/request").read()
			if val.find('free') < 0:
				raise Exception('Pin ' + pin + ' is already in use')
			
			open(self.__pin + "/request", 'w').write("1")
			open(self.__pin + "/run", 'w').write("0")
			open(self.__pin + "/period_freq", 'w').write(str(PWM_FREQUENCY))
			open(self.__pin + "/duty_ns", 'w').write(str(MIN_DUTY_NS))
			open(self.__pin + "/run", 'w').write("1")
			
			open(self.__gpio + "/export", 'w').write(self.__gpioNum)
			open(self.__gpio + "/gpio" + self.__gpioNum + "/direction", 'w').write("in")
			open(self.__gpio + "/gpio" + self.__gpioNum + "/edge", 'w').write("both")
			
			self.__attached_pwm = True

	def start(self):
		fd = os.open(self.__gpio + "/gpio" + self.__gpioNum + "/value", os.O_RDONLY | os.O_NONBLOCK)
		
		READ_ONLY = select.POLLPRI
		poller = select.poll()
		poller.register(fd, READ_ONLY)
		
		toggle = 0
		pre = 0
		post = 0
		
		while True:
			events = poller.poll(-1)
			
			os.lseek(fd, 0, 0)
			
			if((toggle == 0) and (os.read(fd, 2) == '1\n')):
				toggle = 1
				pre = datetime.datetime.now().microsecond
			
			if((toggle == 1) and (os.read(fd, 2) == '0\n')):
				toggle = 0
				post = datetime.datetime.now().microsecond	
				print "Delta: ", (post - pre)

	def detach(self):
		open(self.__pin + "/run", 'w').write("0")
		open(self.__pin + "/request", 'w').write("0")
		open(self.__gpio + "/unexport", 'w').write(self.__gpioNum)
		self.__attached_pwm = False	
	
	def __del__(self):
		self.detach()
