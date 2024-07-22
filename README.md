**THE GIST OF IT:**

Pi-Controller serves 2 main purposes:
  - (1) to allow a user (my dad; but also maybe you) to define a set of basic rules to govern the operation of GPIO pin outputs based on the state of other GPIO pins.
  - (2) to allow a user to define scheduled events to govern the operation of GPIO pin outputs so long as they do not conflict with the basic rules of operation defined for the GPIO pin.

**MOTIVATING EXAMPLE:**

My dad has a Raspberry Pi Zero W hooked up to a few sensors and actuators that allow him to controll different aspects of his garden. The original goal was to create a means by which he could schedule watering his garden as well as automcatically run a water pump according to some rules. A bit more about my dad's garden set up:
  - an underground water storage tank that collects rain water (the "WELL"), and a sensor that determines when the tank is empty, we call this sensor the WELL_EMPTY sensor.
  - an above ground water storage tank that is used to water the garden, the tank has two sensors to determine whether the tanks are empty or full, respectively known as TANK_EMPTY and TANK_FULL sensors.
  - a pump that can pump water from the well to the above ground tank, the pump is controlled by a solid state relay which we just call PUMP.
  - a solenoid valve that can let water out of the above ground tank and onto the garden when watering, we just call this VALVE.
  - and lastly, there exists a sensor that determines if it has rained recently. The sensor is active low so more intuitively we call it the DRY sensor since it is active when things are dry.

I originally designed https://github.com/its-pablo/garden/ to address these specific requirements and it works pretty good! However, at some point my dad mentioned he was thinking of adding some more valves to the system and that's when I realized it would be a pain in the ass to work things over every time I had to add a new device to the system. And so Pi-Controller was born!

The cool thing about Pi-Controller which solves this issue is that the user can define what devices they have hooked up to their Pi and some basic rules of operation for the output devices. So when the time comes my dad can just modify the device config file slightly and it should just work.

**HIGH LEVEL WALKTHROUGH OF SETTING UP FOR MY DAD'S USE CASE:**

So, as we covered before, my dad has a few sensors and output he controls over GPIO pins as well as some rules he would like applied to his outputs. I didn't go over the rules before so let me summarize them:
 - Rules for the PUMP:
   - The PUMP should be OFF if the WELL_EMPTY sensor is active or the TANK_FULL sensor is active. The idea here is we don't want to dry run the pump (pump air through it) or continue to pump when the above ground tank is already full.
   - The PUMP should be ON when the TANK_EMPTY sensor is active and the WELL_EMPTY sensor is not active. The idea here is we want to pump water from the underground tank to the above ground tank when the above ground tank is empty and there is water in the underground tank. The WELL_EMPTY sensor not being active is a bit redundant here because the OFF rule always preempts the ON rule, but whatever, it makes things more clear.
 - Rules for the VALVE:
   - The VALVE should be OFF if the TANK_EMPTY sensor is active or if the DRY sensor is not active. Some bonus info: the valve is actually connected to a secret hidden pump that automatically activates when a pressure difference is detected. The idea behind this rule is we want to stop watering if the above ground tank is empty (to avoid dry running this secret hidden pump) and we should also stop watering if it isn't dry (in other words, it rained recently so we don't want to water on top of that).

Now that we have covered these rules, you know just about everything regarding my dad's garden (hurray). So how do we actually start to set this up? We need to pick some GPIO pins to connect your stuff to! For my dad, he has things mapped as follows:
  - VALVE -> GPIO 17
  - PUMP -> GPIO 25
  - TANK_FULL -> GPIO 21
  - TANK_EMPTY -> GPIO 20
  - WELL_EMPTY - > GPIO 16
  - DRY -> GPIO 12

Having picked some pins we can have a look at the [device_config.txt](https://github.com/its-pablo/pi-controller/blob/main/device_config.txt) (the linked version may actually have some more stuff than shown below, but for the conceptual example we'll want to stick with the sample shown below).

```
#DEVICE_NAME: DEVICE_TYPE GPIO_PIN HAS_ON_RULES HAS_OFF_RULES
VALVE: OUTPUT 17 FALSE TRUE
PUMP: OUTPUT 25 TRUE TRUE
TANK_FULL: INPUT 21 FALSE FALSE
TANK_EMPTY: INPUT 20 FALSE FALSE
WELL_EMPTY: INPUT 16 FALSE FALSE
DRY: INPUT 12 FALSE FALSE

#RULES
VALVE_OFF_RULES:
TANK_EMPTY or not DRY

PUMP_OFF_RULES:
WELL_EMPTY or TANK_FULL

PUMP_ON_RULES:
TANK_EMPTY and not WELL_EMPTY

```

NOTA BENE: The blank line at the end of the device_config.txt file matters, I was a bit lazy when implementing this so you're going to have to deal with it.

Let's focus on the first section of the device config. When defining a device you have to follow the DEVICE_NAME: DEVICE_TYPE GPIO_PIN HAS_ON_RULES HAS_OFF_RULES format. For device names all I have tried is all caps words joined by underscores, I imagine other things might work too. The device type can be either OUTPUT or INPUT. Outputs are going to be the things you're controlling and inputs are going to be your sensors. The GPIO pin is self explanatory, just the number corresponding to your GPIO pin. For outputs, you can also define on rules and off rules. If a device has an on or off rule you must state so by marking it TRUE in the appropriate field, as shown in the sample above.

Having defined some on/off rules for the outputs let's look at how we specify the rules. For each rule we have specified we need a section "DEVICE_NAME_ON/OFF_RULES:" depending on the device name and whether an on or off rule has been specified. What can go in a rule? You can think of them as a Python if statement (they will become that soon enough), so anything that you would typically write in a Python if statement in terms of "and", "or", and "not" (and maybe others, but I haven't bothered to try) are fair game for your rules. Additionally, your rules can span multiple lines and the result is an or of the separate rules, so:

```
VALVE_OFF_RULES:
TANK_EMPTY or not DRY
```

is equivalent to:

```
VALVE_OFF_RULES:
TANK_EMPTY
not DRY
```

Let me show you what this config file becomes, I think that will aid in understanding what is going on here. Running [dev_gen.py](https://github.com/its-pablo/pi-controller/blob/main/dev_gen.py) takes the device_config.txt and generates a devices.py file. Here is what devices.py looks like for the sample device config:

```python
# THIS FILE IS AUTOGENERATED AND WILL BE OVERWRITTEN, DO NOT EXPECT MODIFICATIONS TO REMAIN

from gpiozero import DigitalOutputDevice, DigitalInputDevice

# OUTPUT DEVICES:
VALVE = DigitalOutputDevice(17)
PUMP = DigitalOutputDevice(25)

# INPUT DEVICES:
TANK_FULL = DigitalInputDevice(21)
TANK_EMPTY = DigitalInputDevice(20)
WELL_EMPTY = DigitalInputDevice(16)
DRY = DigitalInputDevice(12)

# Create device dictionary
devices = {}

# Generic status getter
def get_status ( device ):
	return device.is_active

# Generic status setter
def set_status ( device, status ):
	device.on() if status else device.off()
	return device.is_active

# OFF rule for VALVE, returns True if device should be OFF
def VALVE_off_rule ():
	if get_status( TANK_EMPTY ) or not get_status( DRY ):
		return True

	return False

# ON rule for PUMP, returns True if device should be ON
def PUMP_on_rule ():

	if get_status( TANK_EMPTY ) and not get_status( WELL_EMPTY ):
		return True

	return False

# OFF rule for PUMP, returns True if device should be OFF
def PUMP_off_rule ():
	if get_status( WELL_EMPTY ) or get_status( TANK_FULL ):
		return True

	return False

# Generic stop function
def stop ( device_name ):
	return devices[ device_name ][ 2 ]( False )

# Generic start function
def start ( device_name ):
	# If we have an off rule and it is true, we should not start the device
	if devices[ device_name ][ 4 ] is not None and devices[ device_name ][ 4 ]():
		return False
	return devices[ device_name ][ 2 ]( True )

# Generic run function
def run ( device_name ):
	# Check if we should not be running
	if devices[ device_name ][ 4 ] is not None and devices[ device_name ][ 4 ]():
		devices[ device_name ][ 2 ]( False )
	# Check if we should be running
	elif devices[ device_name ][ 3 ] is not None and devices[ device_name ][ 3 ]():
		devices[ device_name ][ 2 ]( True )

# Initialize device dictionary
# DEVICE_NAME: DEVICE_TYPE[0], GETTER[1], SETTER[2], ON_RULE[3], OFF_RULE[4]
devices[ 'VALVE' ] = [ True, lambda: get_status( VALVE ), lambda status: set_status( VALVE, status ), None, VALVE_off_rule ]
devices[ 'PUMP' ] = [ True, lambda: get_status( PUMP ), lambda status: set_status( PUMP, status ), PUMP_on_rule, PUMP_off_rule ]
devices[ 'TANK_FULL' ] = [ False, lambda: get_status( TANK_FULL ), None, None, None ]
devices[ 'TANK_EMPTY' ] = [ False, lambda: get_status( TANK_EMPTY ), None, None, None ]
devices[ 'WELL_EMPTY' ] = [ False, lambda: get_status( WELL_EMPTY ), None, None, None ]
devices[ 'DRY' ] = [ False, lambda: get_status( DRY ), None, None, None ]

```

As you can see, the output devices and input devices are initialized as their corresponding GPIO types on the specified pins, etc. I don't want to get into the implementation details too much, but what is probably most interesting here is how the on and off rules become functions. The following rules:

```
#RULES
VALVE_OFF_RULES:
TANK_EMPTY or not DRY

PUMP_OFF_RULES:
WELL_EMPTY or TANK_FULL

PUMP_ON_RULES:
TANK_EMPTY and not WELL_EMPTY
```

became:

```python
# OFF rule for VALVE, returns True if device should be OFF
def VALVE_off_rule ():
	if get_status( TANK_EMPTY ) or not get_status( DRY ):
		return True

	return False

# ON rule for PUMP, returns True if device should be ON
def PUMP_on_rule ():

	if get_status( TANK_EMPTY ) and not get_status( WELL_EMPTY ):
		return True

	return False

# OFF rule for PUMP, returns True if device should be OFF
def PUMP_off_rule ():
	if get_status( WELL_EMPTY ) or get_status( TANK_FULL ):
		return True

	return False
```
