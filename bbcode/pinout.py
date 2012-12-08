import os
import time
PWM_PATH = "/sys/class/pwm/"
GPIO_PATH = "/sys/class/gpio/"

# -------------- from bonescript's bone.js ----------------------
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

def f_read(file_name):
	file_value = open(file_name, 'r').read()
	return file_value

def f_write_e(file_name, file_value):
	file_handle = open(file_name, 'r+')
	file_handle.seek(0)
	file_handle.write(file_value)
	#file_handle.flush()
	#file_handle.close()
def f_write(file_name, file_value):
	open(file_name, 'w').write(file_value)
