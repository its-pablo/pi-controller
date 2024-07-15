# Imports
import heapq
import messages_pb2 as messages
import os
import time
from datetime import datetime
from datetime import timedelta
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse
from math import lcm

# Function for writing protocol buffer message to JSON
def write_message_to_json ( message, file_name ):
    json_message = MessageToJson( message )
    with open( file_name, 'w', encoding='utf-8' ) as file:
        file.write( json_message )

# Save schedule queue
def save_schedule ( schedule, file_name ):
    # Check if anything in queue
    if schedule:
        # Concat all queues into message and write to JSON
        container = messages.container()
        for _, event in schedule:
            event_container = container.events.add()
            event_container.CopyFrom( event )
        # Write to file
        write_message_to_json( container, file_name )

# Log an event to log file
def log_event ( event, file_name ):
    with open( file_name, 'a', encoding='utf-8' ) as file:
        dt = datetime.today()
        log = str( dt ) + ': ' + str( event ) + '\n'
        file.write( log )

# Tail function used to get the last lines of a file
def tail( f, lines=1, _buffer=4098 ):
    """Tail a file and get X lines from the end"""
    # place holder for the lines found
    lines_found = []
    
    # block counter will be multiplied by buffer
    # to get the block size from the end
    block_counter = -1
    
    # loop until we find X lines
    while len( lines_found ) < lines:
        try:
            f.seek( block_counter * _buffer, os.SEEK_END )
        except IOError:  # either file is too small, or too many lines requested
            f.seek( 0 )
            lines_found = f.readlines()
            break
            
        lines_found = f.readlines()
        
        # decrement the block counter to get the
        # next X bytes
        block_counter -= 1
        
    return lines_found[ -lines: ]

# Initialize schedule
def initialize_schedule ( schedule_queue, file_name ):
    if os.path.isfile( file_name ):
        with open( file_name, 'r', encoding='utf-8' ) as file:
            json_message = file.read()
            container = messages.container()
            container = Parse( json_message, container )
            time_now = int( time.time() )

            for event in container.events.event:
                time_scheduled = event.timestamp.seconds
                period_scheduled = event.period.seconds

                # Not expired put back in queue as is
                if time_scheduled > time_now:
                    heapq.heappush( schedule_queue, ( time_scheduled, event ) )

                # Expired but periodic
                elif period_scheduled > 0:
                    time_scheduled = time_scheduled + ( period_scheduled * ( ( ( time_now - time_scheduled ) // period_scheduled ) + 1 ) )
                    event.timestamp.seconds = time_scheduled
                    heapq.heappush( schedule_queue, ( time_scheduled, event ) )

        # Save schedule changes
        save_schedule( schedule_queue, file_name )

# Get last num_lines of event log
def peak_event_log ( num_lines, file_name ):
		logs = ''
		with open( file_name, 'a+', encoding='utf-8' ) as file:
			lines = tail( file, num_lines )
			logs = ''.join( lines )
		return logs

# Do event instances overlap
def does_event_overlap ( event_a_begin, event_a_duration, event_b_begin, event_b_duration ):
    event_a_end = event_a_begin + event_a_duration
    event_b_end = event_b_begin + event_b_duration
    # Case where A starts during B
    if event_a_begin >= event_b_begin and event_a_begin <= event_b_end:
        return True
    # Case where A ends during B
    elif event_a_end >= event_b_begin and event_a_end <= event_b_end:
        return True
    # Case where A starts before B and end after B (encompasses B)
    elif event_a_begin <= event_b_begin and event_a_end >= event_b_end:
        return True
    # Otherwise no overlap
    else:
        return False

# Do scheduled events conflict
def does_schedule_conflict ( event_a, event_b ):
    # Which event occurs first?
    if event_a.timestamp.seconds < event_b.timestamp.seconds:
        event_f = event_a
        event_l = event_b
    elif event_b.timestamp < event_a.timestamp.seconds:
        event_f = event_b
        event_l = event_a
    # Events occur at the same time, they overlap!
    else:
        return True

    # Initialize relevant variables
    event_f_timestamp = event_f.timestamp.seconds
    event_l_timestamp = event_l.timestamp.seconds
    event_f_duration = event_f.duration.seconds
    event_l_duration = event_l.duration.seconds
    event_f_period = event_f.period.seconds
    event_l_period = event_l.period.seconds

    # Check if any of the events are non-recurring (period = 0) and handle the special cases
    if event_f_period == 0:
        return does_event_overlap( event_f_timestamp, event_f_duration, event_l_timestamp, event_l_period )
    elif event_l_period == 0:
        # Fast forward recurring event to nearest instance before non-recurring event
        event_f_timestamp = event_l_timestamp - ( ( event_l_timestamp - event_f_timestamp ) % event_f_period )
        # Check if they overlap
        if does_event_overlap( event_f_timestamp, event_f_duration, event_l_timestamp, event_l_period ):
            return True
        # Fast forward recurring event to the nearest instance after non-recurring event
        event_f_timestamp = event_f_timestamp + event_f_period
        if does_event_overlap( event_f_timestamp, event_f_duration, event_l_timestamp, event_l_period ):
            return True
        # Neither recurring instance nearest to the non-recurring event overlaps, we're good to go
        return False

    # Find number of periods we have to check
    num_periods = lcm( event_f_period, event_l_period ) // event_l_period
    starts = range( event_l_timestamp, event_l_timestamp + ( num_periods * event_l_duration ), num_periods + 1 )

    # Check all the possible collisions
    for start in starts:
        # Fast forward event to nearest
        event_f_timestamp = starts - ( ( starts - event_f_timestamp ) % event_f_period )
        # Check if they overlap
        if does_event_overlap( event_f_timestamp, event_f_duration, start, event_l_period ):
            return True
        # Fast forward recurring event to the nearest instance after non-recurring event
        event_f_timestamp = event_f_timestamp + event_f_period
        if does_event_overlap( event_f_timestamp, event_f_duration, start, event_l_period ):
            return True

    # Passed all checks, does not conflict
    return False
