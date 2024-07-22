# THE GIST OF IT

Pi-Controller serves 2 main purposes:
  - (1) to allow a user (my dad; but also maybe you) to define a set of basic rules to govern the operation of GPIO pin outputs based on the state of other GPIO pins.
  - (2) to allow a user to define scheduled events to govern the operation of GPIO pin outputs so long as they do not conflict with the basic rules of operation defined for the GPIO pin.

This is achieved with a client-server model. The Pi runs a server that receives requests from the client and runs the control logic of the GPIO pins. The client can get information from the server and make requests of the Pi.

# MOTIVATING EXAMPLE

My dad has a Raspberry Pi Zero W hooked up to a few sensors and actuators that allow him to controll different aspects of his garden. The original goal was to create a means by which he could schedule watering his garden as well as automcatically run a water pump according to some rules. A bit more about my dad's garden set up:
  - an underground water storage tank that collects rain water (the "WELL"), and a sensor that determines when the tank is empty, we call this sensor the WELL_EMPTY sensor.
  - an above ground water storage tank that is used to water the garden, the tank has two sensors to determine whether the tanks are empty or full, respectively known as TANK_EMPTY and TANK_FULL sensors.
  - a pump that can pump water from the well to the above ground tank, the pump is controlled by a solid state relay which we just call PUMP.
  - a solenoid valve that can let water out of the above ground tank and onto the garden when watering, we just call this VALVE.
  - and lastly, there exists a sensor that determines if it has rained recently. The sensor is active low so more intuitively we call it the DRY sensor since it is active when things are dry.

I originally designed https://github.com/its-pablo/garden/ to address these specific requirements and it works pretty good! However, at some point my dad mentioned he was thinking of adding some more valves to the system and that's when I realized it would be a pain in the ass to work things over every time I had to add a new device to the system. And so Pi-Controller was born!

The cool thing about Pi-Controller which solves this issue is that the user can define what devices they have hooked up to their Pi and some basic rules of operation for the output devices. So when the time comes my dad can just modify the device config file slightly and it should just work.

# SOME NOTES ON THE ARCHITECTURE

Pi-Controller consists of a client and a server. The client and server are implemented using simple TCP/IP communications over a socket. This approach is suitable for a local network setup and that's what it has been tested on so far. The client and server communicate with each other by serializing the Google protocol buffer messages defined in messages.proto.

## A bit more about the server:

The server is run by executing controller_daemon.py. The main process of the server handles the communications and consists of two threads to handle the receiving and sending as well as a third timer thread that handles checking for a pulse from the client. By design, if no requests are received from the client for 5 seconds the server severs the connection. In addition to the main process, there is another process that handles all the control logic for the GPIO devices (including the scheduling). The two processes communicate with each other internally using [multiprocessing](https://docs.python.org/3/library/multiprocessing.html#) [Events](https://docs.python.org/3/library/multiprocessing.html#multiprocessing.Event) and [Queues](https://docs.python.org/3/library/multiprocessing.html#pipes-and-queues). There are two queues, one for handling inbound request from the client, and one for handling outbound responses from the server. The receiver thread in the main process places requests in the inbound queue and the control process consumes the requests. When needed, the control process places responses in the outbound queue which the sender thread in the main process consumes and sends to the client.

## A bit more about the client:

The client UI was designed using QT Designer and generally adheres to QT development framework. The client is run by executing remote_gardener.py. Within the client there are 4 threads; (1) the main thread of the UI, (2) an updater thread that handles updating the appropriate UI elements when new information is received from the server, (3) a sender thread that handles sending requests to the server, and (4) a receiver thread that handles the responses from the server. All these threads are QThreads (which is QT's flavor of threading) and communicate with each other using queues and signals and slots.

# SETTING UP FOR A DEMO

I think the easiest way to get started is to not worry about the Pi yet and just set up a demo on your local machine running both the client and server. The assumption here is that you are familiar with Python to some extent and that your machine has python and pip installed. For awareness, I am running Python 3.10.6 as of writing this README and you probably will have to run at least 3.9 (I used math.lcm which was added in 3.9). Also, I am using a Windows machine, but my dad is on Mac and hasn't had any issues on his end. Anyhow, here is a step by step of how to get set up:
  1. Download the latest release or clone the repository to your machine.
  2. Open a terminal in the directory containing the source code.
  3. Install the dependencies; you have two options here:
     - You could just install the exact same stuff that's on my machine by running `pip install -r requirements.txt`, HOWEVER...
     - You should only really need to install protobuf (for the messaging) and PyQt6 (for the client UI). You can install these two as follows:
       `pip install protobuf==5.27.2`
       `pip install PyQt6==6.4.2`
  4. If you just want to see how it works, you can skip modifying the device_config.txt. However, if you have an idea of what you want to do go ahead and modify it to suit your needs. More info on modifying the device config in the [WALKTHROUGH OF SETTING UP THE DEVICE CONFIG FOR MY DAD'S USE CASE](https://github.com/its-pablo/pi-controller/tree/main#walkthrough-of-setting-up-the-device-config-for-my-dads-use-case) section. I would recommend reading this at this stage anyways.
  5. At this point you should be ready to run the controller_daemon.py server locally. Run `python .\controller_daemon.py --demo_mode True` your output should look something like this:
     ```
     Starting controller_daemon with the following args:
        HOST: localhost IPv4: 127.0.0.1
        PORT: 50007
        SCHEDULE_FILE_NAME_SUFFIX: _schedule.json
        EVENT_LOG_FILE_NAME: some\path\event_log.txt
        DEMO_MODE: True
     controller_daemon verion 0.1 is now running!
     PID: 36704
     Attempting to bind socket
     Socket is bound to:
     ('127.0.0.1', 50007)
     Socket is listening
     Controller process is running
     PID: 4896
     ```
  6. On a separate terminal, you'll want to run the client UI. Run `python .\remote_controller.py --demo_mode True`. After a second or two you should see the UI:

<div align="center">
	<img src="https://github.com/its-pablo/pi-controller/blob/main/images/remote_controller_on_boot.png">
</div>

  7. Now you can replace the IP addy in the Host field with "localhost" and hit connect. It should connect right away, otherwise it might hang for a second and then give you some sort of error message in the output box if something goes wrong. Anyhow, here is what your client UI might look like after connecting (this will depend based on the device_config.txt!!):

<div align="center">
	<img src="https://github.com/its-pablo/pi-controller/blob/main/images/remote_controller_on_connect.png">
</div>

  8. You can now play around in the client UI! If you break it let me know how you did it. Read the [WALKTHROUGH OF THE CLIENT UI](https://github.com/its-pablo/pi-controller/tree/main#walkthrough-of-the-client-ui) section if you want to know what everything does.

# WALKTHROUGH OF SETTING UP THE DEVICE CONFIG FOR MY DAD'S USE CASE

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

# WALKTHROUGH OF THE CLIENT UI

Let's go over the client's user interface! When you first run the client in step 6 of the [SETTING UP FOR A DEMO](https://github.com/its-pablo/pi-controller/tree/main#setting-up-for-a-demo) section you should have seen the following:

<div align="center">
	<img src="https://github.com/its-pablo/pi-controller/blob/main/images/remote_controller_on_boot.png">
</div>

As you can tell, everything but the Connection group box is greyed out and disabled. To interact with anything you first have to connect to the server. You can connect to the server by specifying the host name and port number of the server. Once you connect successfully, things should look similar to this:

<div align="center">
	<img src="https://github.com/its-pablo/pi-controller/blob/main/images/remote_controller_on_connect.png">
</div>

Now the different interfaces should be enabled and the connection box should be greyed out and disabled. As you can see, when we connected a bunch of labels appeared in the Status group box as well as some radio buttons in the Controls group box. This may look different for you! The reason is because the labels and radio buttons are set up based on the information received from the server which reflects whatever you configured in the device_config.txt file.

Let's focus on the Controls group box. At the very top there is a list of device radio buttons, these correspond to the output devices you set up in your config. These radio buttons control what device you will be interacting with the controls as well as what device we are displaying the schedule for (more about the Schedule group box in a bit). Skipping the Event Duration group box for a minute... Let's have a look at the push buttons: Activate, Deactivate, Uninhibit, and Inhibit.
  - Activate: the activate push button allows you to activate whatever output is currently being controlled. The client will send the server a request to activate the device.
  - Deactivate: the deactivate push button allows you to deactivate whatever output is currently being controlled. The client will send the server a request to activate the device.
  - Inhibit: the inibit push button bla bla bla. What does it mean for a device to be inhibited? When a device is inhibited we "turn it off" meaning the normal rules of operation defined in the device config will not apply while the device is inhibited and the device cannot be activated. The device will remain inhibited until it is uninhibited!
  - Uninhibit: the uninhibit push button bla bla bla.
The Print Schedule push button we will cover later when we go over the Schedule group box. Let's go over the Event Duration group box. When the check box in the Event Duration groub box is checked the behavior of the Activate and Inhibit push buttons is modified. When Event Duration is enabled the Activate and Inhibit actions will request the server perform the corresponding action but only for the duration specified. After the period of time specified is up, the device's state will return to normal operation (which typically means the device will return to the inactive state).

Now for the Miscellaneous group box. The Peak Event Log button will request the last 10 events logged by the server, this will contain any record of activations, deactivations, inhibitions, or uninhibitions by any of the devices. The Shutdown button is not typically available and is only there because we are running in demo mode! The Shutdown button send the server a request to shutdown. This is only really useful during debugging, testing, and demoing since you might run into issues and what to restart the server. Typically the server is expected to be running 24/7. The About button simply prints some info about the version, the name of the author (that's me) and my email address if you have questions.

The Output group box is fairly self explanatory.

The Status group box displays the status of all the devices. This is also fairly self explanatory. However, there is some secret sauce here when running in demo mode. When the client and server are both in demo mode you can actually click on an input device's status to toggle it between active and inactive! This is useful if you just want to test a proof of concept before deploying to an actual system because you can simulate different scenarios and observe whether you output are behaving according to the rules you set. Here is a quick example:

<div align="center">
	<img src="https://github.com/its-pablo/pi-controller/blob/main/images/sensor_override_demo.gif">
</div>

Bonus points if you understand why the PUMP became ACTIVE when the TANK_EMPTY sensor became ACTIVE.

Now for the Schedule group box. The calendar shows you at a glance how many event are scheduled on any given day for the selected device. There are no scheduled events unless you schedule some, so let's do that! Double click on a day. After double clicking on a day you should see something like this pop up:

<div align="center">
	<img src="https://github.com/its-pablo/pi-controller/blob/main/images/day_schedule_blank.png">
</div>

What you are seeing is an empty schedule for the day you chose. In this popup you can schedule new events that will start on this day at the time specified, for the duration specified, and will repeat as often as indicated by the period. Some caveats about the shceduling: (1) events may not take place in the past, (2) the duration may not be greater than or equal to the period (unless the period is 0), (3) a period of 0 indicates that the event does not repeat and will only occur once, (4) the duration must be greater than 0, (5) events may not conflict with existing events. You can schedule activate events and inhibit events. The idea here comes from my dad's garden. For example, you may want to water you garden at specific intervals and times (a scheduled activate event) or maybe you want to disable the pump at night because it is noisy and you don't want to drain the solar charged battery (a scheduled inhibit event). Anyhow, try scheduling some events and it should look similar to the following:

<div align="center">
	<img src="https://github.com/its-pablo/pi-controller/blob/main/images/day_schedule_some.png">
</div>

Now once you exit the day schedule popup you should be able to see the calendar itself also shows some information regarding the scheduled events (notable how many occur on any given day):

<div align="center">
	<img src="https://github.com/its-pablo/pi-controller/blob/main/images/remote_controller_some.png">
</div>

That about covers most of everything for the client UI. If you have any questions you can ask me.
