import menu
import sys

if __name__ == "__main__":
	print "Welcome to PantryDB v0.1"
	try: 
		UI = menu.CLInterface()
		UI.menu_begin()
	except KeyboardInterrupt:
		print "Keyboard Interrupted" 
		UI.shutdown()
	except SystemExit:
		sys.exit(0)