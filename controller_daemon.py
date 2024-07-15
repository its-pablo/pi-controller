#!/usr/bin/python3

# Imports
import messages_pb2 as messages
import multiprocessing as mp
import os
import queue
import socket
import sys
import threading
import time
from controller import Controller
from google.protobuf.message import DecodeError
from pathlib import Path

# Important constants
VERSION = '0.1'
HOST = 'localhost'
PORT = 50007
SCHEDULE_FILE_NAME_SUFFIX = '_schedule.json'
EVENT_LOG_FILE_NAME = Path( __file__ ).resolve().parent / 'event_log.txt'
DEMO_MODE = False
MUTE_HEARTBEAT = True
ENABLE_TIMING = False

###############################################################################
# Process that handles the control and requests
def control_loop( q_in, q_out, kill, s_file_name_suffix, el_file_name, demo_mode=False ):
	# Create controller
	controller = Controller( s_file_name_suffix, el_file_name, demo_mode=demo_mode )
	
	print( 'Controller process is running' )
	# Print process ID in case it gets hung
	print( 'PID:', os.getpid() )
	
	while True:
		if kill.is_set():
			break
			
		try:
			# Execution beyond get_nowait() only occures if the q_in is non-empty
			container = q_in.get_nowait()
			#---------------------------------------------------------------------

			if container.HasField( 'set_state' ):
				controller.set_device_state( container.set_state )

			elif container.HasField( 'get_states' ):
				container.CopyFrom( controller.get_device_states() )
				q_out.put( container )

			elif container.HasField( 'set_event' ):
				success, conflicting_event = controller.schedule_event( container.set_event )
				if not success:
					container = messages.container()
					msg = 'Failed to schedule event, conflicted with another event!'
					container.info = msg
					q_out.put( container )

			elif container.HasField( 'get_events' ):
				container.CopyFrom( controller.get_all_scheduled_events() )
				q_out.put( container )

			elif container.HasField( 'cancel_event' ):
				controller.cancel_scheduled_event( container.cancel_event )

			elif container.HasField( 'peak_logs' ):
				container.CopyFrom( controller.peak_event_log() )
				q_out.put( container )

			# Secret option
			elif container.HasField( 'demo_override' ):
				controller.override( container.demo_override )

			else:
				print( 'An unsupported message has been received' )

		except queue.Empty:
			pass

		#########################################
		# DO ALL OUR GENERAL CONTROL TASKS HERE #
		#########################################
		# Check if events have expired
		controller.run_schedules()
		# Run devices
		controller.run_rules()
		#########################################
		#             END OF CONTROL            #
		#########################################

if __name__ == '__main__':
	# Needed in Windows when creating an executable with PyInstaller
	mp.freeze_support()

	def print_argv_options ():
		print( 'Options are:' )
		print( '\t--help' )
		print( '\t--host [-h] HOST, a valid host' )
		print( '\t--port [-p] PORT, a valid PORT (must be a non-negative integer)' )
		print( '\t--schedule_files_suffix [-sfs] FILE_NAME' )
		print( '\t--log_file [-lf] FILE_NAME' )
		print( '\t--demo_mode [-dm] DEMO_MODE, True or False' )
	# Check arguments
	if len( sys.argv ) == 2 and sys.argv[1] == '--help':
		print_argv_options()
		sys.exit( 0 )
	elif len( sys.argv ) % 2 != 1:
		print( 'Bad arguments' )
		print_argv_options()
		sys.exit( 0 )
	elif len( sys.argv ) > 1:
		for i in range( ( len( sys.argv ) - 1 ) // 2 ):
			arg_opt = sys.argv[ ( 2 * i ) + 1 ]
			arg_val = sys.argv[ ( 2 * i ) + 2 ]
			if arg_opt == '--host' or arg_opt == '-h':
				HOST = arg_val
				try:
					socket.gethostbyname( HOST )
				except socket.gaierror as e:
					print( 'Invalid host name' )
					print( str( e ) )
					sys.exit( 0 )
			elif arg_opt == '--port' or arg_opt == '-p':
				try:
					PORT = int( arg_val )
					if PORT < 0:
						print( 'Negative integer PORT' )
						sys.exit( 0 )
				except ValueError:
					print( 'Non integer PORT' )
					sys.exit( 0 )
			elif arg_opt == '--schedule_files_suffix' or arg_opt == '-sfs':
				SCHEDULE_FILE_NAME_SUFFIX = arg_val
			elif arg_opt == '--log_file' or arg_opt == '-lf':
				EVENT_LOG_FILE_NAME = arg_val
			elif arg_opt == '--demo_mode' or arg_opt == '-dm':
				if arg_val == 'True':
					DEMO_MODE = True
				elif arg_val == 'False':
					DEMO_MODE = False
				else:
					print( 'DEMO_MODE not True or False' )
					sys.exit( 0 )
			else:
				print( 'Unrecognized argument:', arg_opt, arg_val )
				print_argv_options()
				sys.exit( 0 )

	# Check to see if we have write access to the watering schedule
	#if os.path.isfile( WATERING_SCHEDULE_FILE_NAME ) and ( not os.access( WATERING_SCHEDULE_FILE_NAME, os.R_OK ) or not os.access( WATERING_SCHEDULE_FILE_NAME, os.W_OK ) ):
	#	print( 'Do not have read/write access to', WATERING_SCHEDULE_FILE_NAME )
	#	sys.exit( 0 )

	# Check to see if we have write access to the event log
	if os.path.isfile( EVENT_LOG_FILE_NAME ) and ( not os.access( EVENT_LOG_FILE_NAME, os.R_OK ) or not os.access( EVENT_LOG_FILE_NAME, os.W_OK ) ):
		print( 'Do not have read/write access to', EVENT_LOG_FILE_NAME )
		sys.exit( 0 )

	# Print info
	print( 'Starting garden_daemon with the following args:' )
	print( '\tHOST:', HOST, 'IPv4:', socket.gethostbyname( HOST ) )
	print( '\tPORT:', PORT )
	print( '\tSCHEDULE_FILE_NAME_SUFFIX:', SCHEDULE_FILE_NAME_SUFFIX )
	print( '\tEVENT_LOG_FILE_NAME:', EVENT_LOG_FILE_NAME )
	print( '\tDEMO_MODE:', DEMO_MODE )

	# Set up process safe queues
	q_in = mp.Queue() # This queue is going to hold the incoming messages from the client
	q_out = mp.Queue() # This queue is going to hold the outgoing messages to the client
	# Note: "messages" in this context efers to the protobuf messages defined in garden.proto

	# Set up event for terminating threads
	kill = mp.Event()

	# Set connection threading
	s_lock = threading.Lock()
	no_pulse = threading.Event()
	lost_conn = threading.Event()

	with socket.socket( socket.AF_INET, socket.SOCK_STREAM ) as s:
		# Print version
		print( 'controller_daemon verion', VERSION, 'is now running!' )
		# Print process ID in case it gets hung
		print( 'PID:', os.getpid() )

		print( 'Attempting to bind socket' )
		while True:
			try:
				s.bind( ( HOST, PORT ) )
				break
			except OSError:
				continue
			except socket.gaierror as e:
				print( str( e ) )
				print( 'Aborting garden_daemon' )
				sys.exit( 0 )
		print( 'Socket is bound to:' )
		print( s.getsockname() )

		# Turn on the controller process
		controller_process = mp.Process( target=control_loop, daemon=True, args=( q_in, q_out, kill, SCHEDULE_FILE_NAME_SUFFIX, EVENT_LOG_FILE_NAME, DEMO_MODE ), name='controller_process' )
		controller_process.start()

		s.listen( 1 )
		print( 'Socket is listening' )
		conn, addr = s.accept()
		print( 'Socket accepted connection' )
		print( 'Connected by', addr )
		
		# Make socket non-blocking so the sender thread can still pick up the lock
		conn.setblocking( 0 )

		##############################################################
		# Thread that handles sending responses
		def sender():
			print( 'Sender thread is running' )

			# Only run sender thread while the client is alive
			while True:
				if no_pulse.is_set() or kill.is_set() or lost_conn.is_set():
					break

				try:
					# Execution beyond get_nowait() only occures if the q_out is non-empty
					container = q_out.get_nowait()
					#---------------------------------------------------------------------

					# Serialize the data and send it over to the client
					data = container.SerializeToString()
					with s_lock:
						try:
							conn.sendall( data )

						except ConnectionAbortedError:
							lost_conn.set()

						except ConnectionResetError:
							lost_conn.set()

				except queue.Empty:
					pass

		# Turn on the sender thread
		sender_thread = threading.Thread( target=sender, daemon=True )
		sender_thread.start()
		##############################################################

		###########################################################################
		# Timer thread that signals shutting down connection when no pulse detected
		def pulse_mon ():
			if not kill.is_set():
				print( 'Lost the client\'s pulse' )
				no_pulse.set()

		# Turn on pulse monitor timer, 5 second interval
		pulse_timer = threading.Timer( interval=5, function=pulse_mon )
		pulse_timer.start()
		###########################################################################

		# Main thread loop, receives messages from client and dispatches to the gardener
		if ENABLE_TIMING:
			t1 = time.time()
			dt_max = 0.0
		while True:
			# Timing section, useful to perform analysis on how many requests per seconds we can accomodate
			# right now can accomate about 4 to 5 requests per second in the worst case
			if ENABLE_TIMING:
				t0 = t1
				t1 = time.time()
				print( t1 - t0 )
				if t1 - t0 > dt_max:
					print( 'NEW MAX DT' )
					dt_max = t1 - t0

			# Shutdown
			if kill.is_set():
				print( 'Shutting down controller_daemon!' )
				# Join all threads
				controller_process.join()
				sender_thread.join()
				pulse_timer.cancel()

				# Close connection and socket
				conn.close()

				# Print max timing delta if enabled
				if ENABLE_TIMING: print( dt_max )

				# Break out of main loop
				break

			# Check if pulse monitor reported no pulse
			# If no pulse then we join the sender thread,
			# shutdown the connection, and go back to
			# listening for a connection
			if no_pulse.is_set() or lost_conn.is_set():
				print( 'Pulse or connection lost! Shutdown connection...' )

				# Join sender thread
				sender_thread.join()
				pulse_timer.cancel()

				# Reset queues
				def empty_queue ( q ):
					while not q.empty():
						try:
							q.get_nowait()
						except queue.Empty:
							break

				empty_queue( q_in )
				empty_queue( q_out )

				# Shutdown and close connection, we
				# don't have to use s_lock because
				# we already joined sender_thread
				conn.close()

				# Let user know where to connect to
				print( 'Socket is still bound to:' )
				print( s.getsockname() )

				# Listen for new connection
				s.listen( 1 )
				print( 'Socket is listening' )
				conn, addr = s.accept()
				print( 'Socket accepted connection' )
				print( 'Connected by', addr )

				# Make socket non-blocking so the sender thread can still pick up the lock
				conn.setblocking( 0 )

				# Clear events
				lost_conn.clear()
				no_pulse.clear()

				# Restart the sender thread
				sender_thread = threading.Thread( target=sender, daemon=True )
				sender_thread.start()

				# Restart the pulse monitor timer, 5 second interval
				pulse_timer = threading.Timer( interval=5, function=pulse_mon )
				pulse_timer.start()

				# If timing reset time
				if ENABLE_TIMING: t1 = time.time()

			# Normal execution, try to read messages and dispatch them
			with s_lock:
				try:
					# Execution beyond conn.recv() only occurs if it reads successfully
					data = conn.recv( 1024 )
					# -----------------------------------------------------------------
					
					# Only process data if meaningful non-empty
					if data:
						# Clear no pulse signal since we have pulse
						no_pulse.clear()

						# Restart the 5 second pulse monitor
						pulse_timer.cancel()
						pulse_timer = threading.Timer( interval=5, function=pulse_mon )
						pulse_timer.start()

						try:
							# Parse received message
							container = messages.container()
							container.ParseFromString( data )
							# If a heartbeat message ignore
							if container.HasField( 'heartbeat' ):
								if not MUTE_HEARTBEAT:
									print( 'Heartbeat!' )
							# If a shutdown message, send kill signal
							elif container.HasField( 'shutdown' ):
								print( 'Killing' )
								kill.set()
							# Else, let the controller process handle it
							else:
								q_in.put( container )

						except DecodeError:
							print( 'Was not able to parse message!' )

				except BlockingIOError:
					pass

				except ConnectionAbortedError:
					lost_conn.set()

				except ConnectionResetError:
					lost_conn.set()
