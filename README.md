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
