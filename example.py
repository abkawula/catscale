#! /usr/bin/python2

import time
import sys
import datetime
import RPi.GPIO as GPIO
from hx711 import HX711
from influx import INFLUX

referenceUnit_A = 1080.6
referenceUnit_B = 108.05
max_queue_length = 10

def cleanAndExit():
    print("Cleaning...")

    if not EMULATE_HX711:
        GPIO.cleanup()
        
    print("Bye!")
    sys.exit()

def getDatapoints(food, water):
    return [{
        "measurement": "cat_food"
        , "time": datetime.datetime.now(datetime.timezone.utc).isoformat()
        , "fields": {
            "weight": food
        }
    }
    , {
       "measurement": "cat_water"
        , "time": datetime.datetime.now(datetime.timezone.utc).isoformat()
        , "fields": {
            "weight": water
        } 
    }]

hx = HX711(dout=5, pd_sck=6, tare_A=-275555.6666666667, gain=128)
influx = INFLUX('localhost', 8086, 'home')

# I've found out that, for some reason, the order of the bytes is not always the same between versions of python, numpy and the hx711 itself.
# Still need to figure out why does it change.
# If you're experiencing super random values, change these values to MSB or LSB until to get more stable values.
# There is some code below to debug and log the order of the bits and the bytes.
# The first parameter is the order in which the bytes are used to build the "long" value.
# The second paramter is the order of the bits inside each byte.
# According to the HX711 Datasheet, the second parameter is MSB so you shouldn't need to modify it.
hx.set_reading_format("MSB", "MSB")

# HOW TO CALCULATE THE REFFERENCE UNIT
# To set the reference unit to 1. Put 1kg on your sensor or anything you have and know exactly how much it weights.
# In this case, 92 is 1 gram because, with 1 as a reference unit I got numbers near 0 without any weight
# and I got numbers around 184000 when I added 2kg. So, according to the rule of thirds:
# If 2000 grams is 184000 then 1000 grams is 184000 / 2000 = 92.
#hx.set_reference_unit(113)
hx.set_reference_unit_A(referenceUnit_A)
hx.set_reference_unit_B(referenceUnit_B)

hx.reset()

hx.set_offset_A(-275514)
hx.set_offset_B(44993.33)

print("Tare done! Add weight now...")

while True:
    try:
        val_A = hx.get_weight_A(51)
        val_B = hx.get_weight_B(51)
        datapoints = getDatapoints(food = val_A, water = val_B)
        influx.write_points(datapoints)
        
        # To get weight from both channels (if you have load cells hooked up 
        # to both channel A and B), do something like this
        #val_A = hx.get_weight_A(5)
        #val_B = hx.get_weight_B(5)
        print("A: %s  B: %s" % ( val_A, val_B ))

        hx.power_down()
        hx.power_up()
        time.sleep(115)

    except (KeyboardInterrupt, SystemExit):
        cleanAndExit()

