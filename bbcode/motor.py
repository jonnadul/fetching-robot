import os
import time

DEFAULT_DUTY_NS = 2000000 #2 ms
PWM_FREQUENCY = 50 #hz 

PWM_PATH   = "/sys/class/pwm/"
GPIO_PATH  = "/sys/class/gpio/"

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

class Motor:
	def attach(self, pinOne, pinTwo, gpioLF, gpioLB, gpioRF, gpioRB):
		if (not pinOne in pwm_pins) or (not pinTwo in pwm_pins):
			raise Exception("Pins " + pinOne + " or " + pinTwo  + " is not pwm capable");
		else:
			self.__pwmLeft = PWM_PATH+pwm_pins[pinOne]["pwm"]
			self.__pwmRight = PWM_PATH+pwm_pins[pinTwo]["pwm"]

			self.__gpio = GPIO_PATH
			self.__gpioNumLF = gpioLF
			self.__gpioNumLB = gpioLB
			self.__gpioNumRF = gpioRF
			self.__gpioNumRB = gpioRB
			
			valOne = open(self.__pwmLeft + "/request").read()
			valTwo = open(self.__pwmRight + "/request").read()

			if (valOne.find('free') < 0) or (valTwo.find('free') < 0):
				raise Exception("Pins " + pinOne + " or " + pinTwo + " is already in use")
			
			open(self.__pwmLeft + "/request", 'w').write("1")
			open(self.__pwmLeft + "/run", 'w').write("0")
			open(self.__pwmLeft + "/period_freq", 'w').write(str(PWM_FREQUENCY))
			open(self.__pwmLeft + "/duty_ns", 'w').write("0")
				  
			open(self.__pwmRight + "/request", 'w').write("1")
			open(self.__pwmRight + "/run", 'w').write("0")
			open(self.__pwmRight + "/period_freq", 'w').write(str(PWM_FREQUENCY))
			open(self.__pwmRight + "/duty_ns", 'w').write("0")
	
			open(self.__gpio + "/export", 'w').write(self.__gpioNumLF)
			open(self.__gpio + "/gpio" + self.__gpioNumLF + "/direction", 'w').write("out")
 
			open(self.__gpio + "/export", 'w').write(self.__gpioNumLB)
			open(self.__gpio + "/gpio" + self.__gpioNumLB + "/direction", 'w').write("out")
			
			open(self.__gpio + "/export", 'w').write(self.__gpioNumRF)
			open(self.__gpio + "/gpio" + self.__gpioNumRF + "/direction", 'w').write("out")
 
			open(self.__gpio + "/export", 'w').write(self.__gpioNumRB)
			open(self.__gpio + "/gpio" + self.__gpioNumRB + "/direction", 'w').write("out")
			
			self.__attached_pwm = True

	def move(self, seconds, direction):
		open(self.__pwmLeft + "/run", 'w').write("0")
		open(self.__pwmRight + "/run", 'w').write("0")
		
		open(self.__pwmLeft + "/duty_ns", 'w').write(str(DEFAULT_DUTY_NS))
		open(self.__pwmRight + "/duty_ns", 'w').write(str(DEFAULT_DUTY_NS))
		
		if(direction == 'forward'):
			open(self.__gpio + "/gpio" + self.__gpioNumLF + "/value", 'w').write("0")
			open(self.__gpio + "/gpio" + self.__gpioNumLB + "/value", 'w').write("1")
			open(self.__gpio + "/gpio" + self.__gpioNumRF + "/value", 'w').write("0")
			open(self.__gpio + "/gpio" + self.__gpioNumRB + "/value", 'w').write("1")
		elif(direction == 'backward'):
			open(self.__gpio + "/gpio" + self.__gpioNumLF + "/value", 'w').write("1")
			open(self.__gpio + "/gpio" + self.__gpioNumLB + "/value", 'w').write("0")
			open(self.__gpio + "/gpio" + self.__gpioNumRF + "/value", 'w').write("1")
			open(self.__gpio + "/gpio" + self.__gpioNumRB + "/value", 'w').write("0")
		
		open(self.__pwmLeft + "/run", 'w').write("1")
		open(self.__pwmRight + "/run", 'w').write("1")
		
		time.sleep(seconds)
		
		open(self.__pwmLeft + "/run", 'w').write("0")
		open(self.__pwmRight + "/run", 'w').write("0")
	
	def direction(self, seconds, direction):
		open(self.__pwmLeft + "/run", 'w').write("0")
		open(self.__pwmRight + "/run", 'w').write("0")
		
		open(self.__pwmLeft + "/duty_ns", 'w').write(str(DEFAULT_DUTY_NS))
		open(self.__pwmRight + "/duty_ns", 'w').write(str(DEFAULT_DUTY_NS))
		
		if(direction == 'right'):
			open(self.__gpio + "/gpio" + self.__gpioNumLF + "/value", 'w').write("1")
			open(self.__gpio + "/gpio" + self.__gpioNumLB + "/value", 'w').write("0")
			open(self.__gpio + "/gpio" + self.__gpioNumRF + "/value", 'w').write("0")
			open(self.__gpio + "/gpio" + self.__gpioNumRB + "/value", 'w').write("1")
		elif(direction == 'left'):
			open(self.__gpio + "/gpio" + self.__gpioNumLF + "/value", 'w').write("0")
			open(self.__gpio + "/gpio" + self.__gpioNumLB + "/value", 'w').write("1")
			open(self.__gpio + "/gpio" + self.__gpioNumRF + "/value", 'w').write("1")
			open(self.__gpio + "/gpio" + self.__gpioNumRB + "/value", 'w').write("0")
		
		open(self.__pwmLeft + "/run", 'w').write("1")
		open(self.__pwmRight + "/run", 'w').write("1")
		
		time.sleep(seconds)
		
		open(self.__pwmLeft + "/run", 'w').write("0")
		open(self.__pwmRight + "/run", 'w').write("0")
	
	def detach(self):
		open(self.__pwmLeft + "/run", 'w').write("0")
		open(self.__pwmRight + "/run", 'w').write("0")
		
		open(self.__pwmLeft + "/request", 'w').write("0")
		open(self.__pwmRight + "/request", 'w').write("0")
		
		open(self.__gpio + "/unexport", 'w').write(self.__gpioNumLF)
		open(self.__gpio + "/unexport", 'w').write(self.__gpioNumLB)
		open(self.__gpio + "/unexport", 'w').write(self.__gpioNumRF)
		open(self.__gpio + "/unexport", 'w').write(self.__gpioNumRB)
		self.__attached_pwm = False
	
	def __del__(self):
		self.detach()
