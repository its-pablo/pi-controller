# Imports
import control_utils as utils
import heapq
import messages_pb2 as messages
import time
from datetime import datetime
from datetime import timedelta
from dev_gen import gen_devices
from pathlib import Path

BASE_PATH = Path( __file__ ).resolve().parent
SCHEDULE_FILE_NAME_SUFFIX = '_schedule.json'
EVENT_LOG_FILE_NAME = BASE_PATH / 'event_log.txt'

class Controller:
    
    # Init controller
    def __init__ ( self, s_file_name_suffix=None, el_file_name=None, demo_mode=False ):
        # Save event log file name
        if el_file_name:
            self.el_file_name = el_file_name
        else:
            self.el_file_name = EVENT_LOG_FILE_NAME

        # Save schedule file name suffix
        if s_file_name_suffix:
            self.s_file_name_suffix = s_file_name_suffix
        else:
            self.s_file_name_suffix = SCHEDULE_FILE_NAME_SUFFIX
        
        # Generate controller interfaces
        gen_devices( demo_mode=demo_mode )

        # Import the generated devices interface
        from devices import devices
        self.devices = devices

        # Store the output keys for convenience
        self.outputs = [ device for device in self.devices if self.devices[ device ][ 0 ] ]

        # Check to see which devices are outputs and initialize their schedules and other relevant
        self.scheds = {}
        self.scheds_files = {}
        self.inhibits = {}
        for device in self.outputs:
            self.scheds[ device ] = []
            self.scheds_files[ device ] = BASE_PATH / ( device + self.s_file_name_suffix )
            utils.initialize_schedule( self.scheds[ device ], self.scheds_files[ device ] )
            if self.scheds[ device ]:
                self.inhibits[ device ] = ( self.scheds[ device ][ 0 ][ 1 ].state.state == messages.STATE.DEV_UNINHIBITED )
            else:
                self.inhibits[ device ] = False
    
    # Check all scheduled events
    def run_schedules ( self ):
        import devices
        # Process schedule for all output devices
        for device in self.outputs:
            # Check if schedule empty
            if self.scheds[ device ]:
                # Get time now
                time_now = int( time.time() )
                # Check if top of heap queue is expired
                if time_now > self.scheds[ device ][ 0 ][ 0 ]:
                    # Pop event out of queue
                    _, event = heapq.heappop( self.scheds[ device ] )
                    # Get current state of device
                    cur_state = self.devices[ device ][ 1 ]()
                    # Check what kind of event and handle accordingly
                    if event.state.state == messages.STATE.DEV_ACTIVE:
                        if not cur_state:
                            cur_state = devices.start( device )
                            if cur_state:
                                print( device, 'is now active' )
                                utils.log_event( device + ' IS NOW ACTIVE', self.el_file_name )
                                # Schedule new inactive event if neccessary
                                if event.duration.seconds > 0:
                                    new_event = messages.container.SCHEDULED_DEVICE_EVENT()
                                    new_event.CopyFrom( event )
                                    new_event.timestamp.seconds = event.timestamp.seconds + event.duration.seconds
                                    new_event.duration.seconds = 0
                                    new_event.period.seconds = 0
                                    new_event.state.state = messages.STATE.DEV_INACTIVE
                                    heapq.heappush( self.scheds[ device ], ( new_event.timestamp.seconds, new_event ) )
                        else:
                            print( device, 'device is already active' )
                        # Reschedule active event if neccessary
                        if event.period.seconds > 0:
                            event.timestamp.seconds = event.timestamp.seconds + event.period.seconds
                            heapq.heappush( self.scheds[ device ], ( event.timestamp.seconds, event ) )
                    elif event.state.state == messages.STATE.DEV_INACTIVE:
                        if cur_state:
                            cur_state = devices.stop( device )
                            if not cur_state:
                                print( device, 'is now inactive' )
                                utils.log_event( device + ' IS NOW INACTIVE', self.el_file_name )
                        else:
                            print( device, 'is already inactive' )
                    elif event.state.state == messages.STATE.DEV_UNINHIBITED:
                        # We are now uninhibited
                        self.inhibits[ device ] = False
                        print( device, 'is now uninhibited' )
                        utils.log_event( device + ' IS NOW UNINHIBITED', self.el_file_name )
                    elif event.state.state == messages.STATE.DEV_INHIBITED:
                        # We are now inhibited, stop the device and set the flag
                        devices.stop( device )
                        self.inhibits[ device ] = True
                        print( device, 'is now inhibited' )
                        utils.log_event( device + ' IS NOW INHIBITED', self.el_file_name )
                        # Schedule an uninhibit event when the duration is up if needed
                        if event.duration.seconds > 0:
                            new_event = messages.container.SCHEDULED_DEVICE_EVENT()
                            new_event.CopyFrom( event )
                            new_event.timestamp.seconds = event.timestamp.seconds + event.duration.seconds
                            new_event.duration.seconds = 0
                            new_event.period.seconds = 0
                            new_event.state.state = messages.STATE.DEV_UNINHIBITED
                            heapq.heappush( self.scheds[ device ], ( new_event.timestamp.seconds, new_event ) )
                        # Reschedule inhibit event if neccessary
                        if event.period.seconds > 0:
                            event.timestamp.seconds = event.timestamp.seconds + event.period.seconds
                            heapq.heappush( self.scheds[ device ], ( event.timestamp.seconds, event ) )
                    
                    utils.save_schedule( self.scheds[ event.state.device_name ], self.scheds_files[ event.state.device_name ] )

    # Check all device operating rules
    def run_rules ( self ):
        import devices
        # Process rules for all devices
        for device in self.outputs:
            # Check if inhibited
            if self.inhibits[ device ]:
                # Make sure device is off
                devices.stop( device )
            else:
                pre_state = self.devices[ device ][ 1 ]()
                devices.run( device )
                post_state = self.devices[ device ][ 1 ]()
                if pre_state != post_state:
                    if post_state:
                        print( device, 'is now active' )
                        utils.log_event( device + ' IS NOW ACTIVE', self.el_file_name )
                    else:
                        print( device, 'is now inactive' )
                        utils.log_event( device + ' IS NOW INACTIVE', self.el_file_name )

    # Set device state
    def set_device_state ( self, state ):
        import devices
        # If state active and not inhibited
        if state.state == messages.STATE.DEV_ACTIVE and not self.inhibits[ state.device_name ]:
            # If there is a scheduled inactive event remove it
            if self.scheds[ state.device_name ] and self.scheds[ state.device_name ][ 0 ][ 1 ].state.state == messages.STATE.DEV_INACTIVE:
                heapq.heappop( self.scheds[ state.device_name ] )
            pre_state = self.devices[ state.device_name ][ 1 ]()
            post_state = devices.start( state.device_name )
            if pre_state != post_state:
                print( state.device_name, 'is now active' )
                utils.log_event( state.device_name + ' IS NOW ACTIVE', self.el_file_name )
        # If state is inactive, deactivate
        elif state.state == messages.STATE.DEV_INACTIVE:
            # If there is a scheduled inactive event remove it
            if self.scheds[ state.device_name ] and self.scheds[ state.device_name ][ 0 ][ 1 ].state.state == messages.STATE.DEV_INACTIVE:
                heapq.heappop( self.scheds[ state.device_name ] )
            pre_state = self.devices[ state.device_name ][ 1 ]()
            post_state = devices.stop( state.device_name )
            if pre_state != post_state:
                print( state.device_name, 'is now inactive' )
                utils.log_event( state.device_name + ' IS NOW INACTIVE', self.el_file_name )
        # If state is uninhibited, uninhibit
        elif state.state == messages.STATE.DEV_UNINHIBITED:
            self.inhibits[ state.device_name ] = False
            # If there is a scheduled uninhibit event remove it
            if self.scheds[ state.device_name ] and self.scheds[ state.device_name ][ 0 ][ 1 ].state.state == messages.STATE.DEV_UNINHIBITED:
                heapq.heappop( self.scheds[ state.device_name ] )
        # If state is inhibited, inhibit
        elif state.state == messages.STATE.DEV_INHIBITED:
            self.inhibits[ state.device_name ] = True
            # If there is a scheduled inactive event remove it
            if self.scheds[ state.device_name ] and self.scheds[ state.device_name ][ 0 ][ 1 ].state.state == messages.STATE.DEV_INACTIVE:
                heapq.heappop( self.scheds[ state.device_name ] )
            # Turn off the device
            pre_state = self.devices[ state.device_name ][ 1 ]()
            post_state = devices.stop( state.device_name )
            if pre_state != post_state:
                print( state.device_name, 'is now inactive' )
                utils.log_event( state.device_name + ' IS NOW INACTIVE', self.el_file_name )
    
    # Get device states
    def get_device_states ( self ):
        container = messages.container()
        for device in self.devices:
            state = container.states.state.add()
            state.device_name = device
            if device in self.outputs and self.inhibits[ device ]:
                state.state = messages.STATE.DEV_INHIBITED
            elif self.devices[ device ][ 1 ]():
                state.state = messages.STATE.DEV_ACTIVE
            else:
                state.state = messages.STATE.DEV_INACTIVE
            state.is_output = self.devices[ device ][ 0 ]
        return container
    
    # Schedule an event
    def schedule_event ( self, event ):
        for _, scheduled_event in self.scheds[ event.state.device_name ]:
            #if scheduled_event.state.state != messages.STATE.DEV_INACTIVE and scheduled_event.state.state != messages.STATE.DEV_UNINHIBITED and utils.does_schedule_conflict( event, scheduled_event ):
            if utils.does_schedule_conflict( event, scheduled_event ):
                return ( False, scheduled_event )
        heapq.heappush( self.scheds[ event.state.device_name ], ( event.timestamp.seconds, event ) )
        utils.save_schedule( self.scheds[ event.state.device_name ], self.scheds_files[ event.state.device_name ] )
        return ( True, None )

    # Get events scheduled for a device
    def get_scheduled_events ( self, device ):
        num_events = 0
        container = messages.container()
        if self.scheds[ device ] and self.scheds[ device ][ 0 ][ 1 ].state.state != messages.STATE.DEV_INACTIVE and self.scheds[ device ][ 0 ][ 1 ].state.state != messages.STATE.DEV_UNINHIBITED:
            for _, event in self.scheds[ device ]:
                event_out = container.events.event.add()
                event_out.CopyFrom( event )
                num_events = num_events + 1
        elif self.scheds[ device ]:
            for _, event in self.scheds[ device ][ 1: ]:
                event_out = container.events.event.add()
                event_out.CopyFrom( event )
                num_events = num_events + 1
        if num_events == 0:
            container.no_events = device
        return container
    
    # Get all scheduled events
    def get_all_scheduled_events ( self ):
        num_events = 0
        container = messages.container()
        for device in self.outputs:
            if self.scheds[ device ] and self.scheds[ device ][ 0 ][ 1 ].state.state != messages.STATE.DEV_INACTIVE and self.scheds[ device ][ 0 ][ 1 ].state.state != messages.STATE.DEV_UNINHIBITED:
                for _, event in self.scheds[ device ]:
                    event_out = container.events.event.add()
                    event_out.CopyFrom( event )
                    num_events = num_events + 1
            elif self.scheds[ device ]:
                for _, event in self.scheds[ device ][ 1: ]:
                    event_out = container.events.event.add()
                    event_out.CopyFrom( event )
                    num_events = num_events + 1
        if num_events == 0:
            container.no_events = ''
        return container

    # Cancel scheduled event
    def cancel_scheduled_event ( self, event ):
        clean_sched = []
        event_cancelled = False
        for _, scheduled_event in self.scheds[ event.state.device_name ]:
            if not utils.does_schedule_conflict( event, scheduled_event ):
                heapq.heappush( clean_sched, ( scheduled_event.timestamp.seconds, scheduled_event ) )
            else:
                event_cancelled = True
        if event_cancelled:
            self.scheds[ event.state.device_name ] = clean_sched.copy()
            utils.save_schedule( self.scheds[ event.state.device_name ], self.scheds_files[ event.state.device_name ] )

    # Peak event log
    def peak_event_log ( self, lines ):
        container = messages.container()
        container.logs = utils.peak_event_log( lines, EVENT_LOG_FILE_NAME )
        return container

    # Override input, only to be used in demo mode
    def override ( self, state ):
        if state.state == messages.STATE.DEV_ACTIVE:
            self.devices[ state.device_name ][ 2 ]( True )
        elif state.state == messages.STATE.DEV_INACTIVE:
            self.devices[ state.device_name ][ 2 ]( False )
