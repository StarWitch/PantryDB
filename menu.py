#!/usr/bin/env python
from backend import PantryDB

class CLIMenu(object):
	''' 
	Command Line Menu class

	add_option() is used to make a new list of menu options
	input_check() ensures that menu option selection is validated
	display() shows the menu to the user
	'''

	def __init__(self, header):
		self.header = header
		self.options = []

	def add_option(self, item, function, args):
		''' 
		Adds an option to the new menu
		item = what the menu displays to the user
		function = the function that gets called when selected
		args = the arguments to pass to that function
		'''
		num = self.options.__len__() # length of menu list
		item_to_add = [num, item, function, args]
		self.options.append(item_to_add)

	def display(self):
		'''
		Displays the list (self.options) formed with add_option
		'''
		while True:
			print "->", self.header
			for item in self.options:
				print "-->", item[0], "-", item[1]

			self.selection = (raw_input("Select an option [0-%s]: " % int(len(self.options) - 1)))
			
			input_validated = self.input_check(self.selection, self.options.__len__(), 0)
			
			if input_validated:
				return self.options[int(self.selection)][2], self.options[int(self.selection)][3]

	def input_check(self, *args): # (args = input, maximum, minimum)
		'''
		Checks numerical input to ensure it is validated

		This is used for both menu input checking, and SQL item selection checking
		'''
		if args[0].isdigit() and (int(args[0]) >= int(args[2])) and (int(args[0]) < int(args[1])):
			return True
		else:	
			print "INVALID INPUT, PLEASE RETRY!"
			return False

	def get_function(self, function, args):
		''' parses function with varying amounts of arguments '''
		try:
			return function()
		except TypeError:
			return function(*args)	

class CLInterface(CLIMenu):
	'''
	Command Line Interface class 

	connection_begin() initializes the PantryDB backend, which connects to MySQL
	connection_end() attempts to gracefully shut down the MySQL connection
	menu_begin() specifies the menu options available to the user
	input_info() prompts user for data entry
	modify_info() prompts user to modify existing data
	delete_info() prompts user to delete existing data
	display_info() gathers headers and all currently-existing database entries
	initialize_info() initializes the database if it hasn't been already
	get_function() parses the function from the menu option, and its arguments into something usable
	set_switcher() controls which menu is presented to the user
	shutdown() is self-explanatory

	'''

	def __init__(self):
		'''
		Initialize with default SQL parameters

		Change them here if you want different default values
		'''
		self.hostname = "localhost"
		self.username = "pantryuser"
		self.password = "pantrypassword"
		self.database = "pantrydb"
		self.table = "Food"
		self.sql = False

	def connection_begin(self):
		'''
		Begin connection to SQL server, prompting for input 
		'''
		try:
			connected = self.sql.status() # check to see if connected
		except:
			connected = False
		
		if not connected:
			config_mode = (raw_input("Configure DB Connection? (no = use defaults) [y/N]: ")).lower()

			if (config_mode == "y"): 
				hostinfo = (raw_input("Please enter hostname of MySQL DB [%s]: " % (self.hostname)))
				if (hostinfo):
					self.hostname = hostinfo

				userinfo = (raw_input("Please enter username of MySQL DB [%s]: " % (self.username)))
				if (userinfo):
					self.username = userinfo

				passinfo = (raw_input("Please enter password of MySQL DB [%s]: " % (self.password)))
				if (passinfo):
					self.password = passinfo

				datainfo = (raw_input("Please enter name of MySQL DB [%s]: " % (self.database)))
				if (datainfo):
					self.database = datainfo

				tableinfo = (raw_input("Please enter name of MySQL table [%s]: " % (self.table)))
				if (tableinfo):
					self.table = tableinfo

			else:
				print "Using default connection values"
			
			self.sql = PantryDB(self.hostname, self.username, self.password, \
				self.database, self.table)
			success = self.sql.connect()

			if success[0] == True:
				print "Connected to database."
			else:
				print success[1] # print error message

		else:
			print "Already connected to database!"

	def connection_end(self):
		'''
		Attempts to disconnect from the SQL server gracefully
		'''
		try:
			success = self.sql.disconnect()
			if success:
				print "Database disconnected successfully."
			else:
				print "Database already disconnected!"
		except AttributeError:
			print "Database not loaded in this instance"

	def populate_menu(self):
		self.main_menu = CLIMenu("Main Menu")
		self.main_menu.add_option("Data Entry", self.set_switcher, "0")
		self.main_menu.add_option("Database Options", self.set_switcher, "1")
		self.main_menu.add_option("Quit Program", self.shutdown, None)
				
		self.data_menu = CLIMenu("Data Menu")
		self.data_menu.add_option("Input Foods", self.input_info, None)
		self.data_menu.add_option("Modify Foods", self.modify_info, None)
		self.data_menu.add_option("Delete Foods", self.delete_info, None)
		self.data_menu.add_option("Back to Main Menu", self.set_switcher, "x")

		self.db_menu = CLIMenu("Database Menu")
		self.db_menu.add_option("Open Database", self.connection_begin, None)
		self.db_menu.add_option("Check Database", self.initialize_info, None)
		self.db_menu.add_option("Close Database", self.connection_end, None)
		self.db_menu.add_option("RESET DATABASE", self.reset_warning, None)
		self.db_menu.add_option("Back to Main Menu", self.set_switcher, "x")

	def menu_begin(self):
		''' 
		Main menu method

		Creates menu options using CLIMenu.add_option(*), displays menu

		Upon menu item selection, it parses the associated function, 
		and calls it with its specified arguments using get_function()

		'''

		self.menu_select = "x" # key for which menu should be displayed
		self.connection_begin()
		self.populate_menu() # populate the menu objects with items

		while True:
			if self.menu_select == "x":
				''' Main menu '''
				received_function = self.main_menu.display()
				self.main_menu.get_function(received_function[0], received_function[1])

			if self.menu_select == "0":
				''' Data entry menu - only show if DB is connected '''
				if self.sql.status():
					received_function = self.data_menu.display()
					self.data_menu.get_function(received_function[0], received_function[1])
						
				else:
					print "!!! YOU MUST OPEN THE DATABASE FIRST!"
					self.set_switcher("x") # reset to main menu

			if self.menu_select == "1":
				''' Database options menu '''
				received_function = self.db_menu.display()
				self.db_menu.get_function(received_function[0], received_function[1])
				

	def display_info(self):
		''' Gets and displays headers for the items, and then the items themselves'''
		information = self.sql.display_db()
		if information:
			print "%s | %2s | %3s | %4s | %5s" % \
					(information[0][0][0].upper(), information[0][1][0].upper(), \
					information[0][2][0].upper(), information[0][3][0].upper(), \
					information[0][4][0].upper()) # header information
			try:
				for item in information[1]: # all the actual data in the DB
					print "#%s -> %2s: %3s, %4s (%5s)" % (item[0], item[1], item[2], item[3], item[4])
			except IndexError:
				print "No items in database yet."
		else:
			print "No information retreived - try connecting first?"		

	def input_info(self):
		''' Prompts for new entry in database '''
		while True:
			self.display_info()
			choice = (raw_input("Input new item? [y/N] ")).lower()
			if (choice == "y"):
				name = raw_input("Name of item?: ")
				description = raw_input("Description?: ")
				qty = raw_input("Quantity of item?: ")
				self.sql.insert_row_db(name, description, qty)
			else:
				break

	def modify_info(self):
		''' Modifies database entries based on prompts '''
		while True:
			self.display_info()
			choice = (raw_input("Modify item? [y/N] ")).lower()
			if (choice == "y"):
				item = []
				id_num = raw_input("ID of item?: ")
				item.append(id_num)
				maximum = self.sql.get_maximum() # get the max ID of all items in the DB
				input_validated = CLIMenu.input_check(self, id_num, maximum, 1)
				try:
					if input_validated: # returns True if a legal number
						info_to_edit = self.sql.select_one(id_num)
						print "-> Now editing the following entry:"
						print "#%s -> %2s: %3s, %4s" % (info_to_edit[0], info_to_edit[1], \
							info_to_edit[2], info_to_edit[3])

						name = raw_input("Change name? [%s] " % (info_to_edit[1])) # %s displays current info
						if (name):
							item.append(name)
						else: 
							item.append(info_to_edit[1]) # if nothing has been entered, already-existing info

						description = raw_input("Change description? [%s] " % (info_to_edit[2]))
						if (description):
							item.append(description)
						else:
							item.append(info_to_edit[2])

						qty = raw_input("Change quantity? [%s] " % (info_to_edit[3]))
						if (qty):
							item.append(qty)
						else:
							item.append(info_to_edit[3])

						success = self.sql.update_row_db(item) # pushes new info to DB
						if success:
							print "Entry #%s Modified Successfully" % (id_num)
						else:
							print "Entry #%s NOT Modified - Error Occurred" % (id_num)
				except TypeError:
					print "Entry #%s appears to not exist, please retry" % (id_num)
			else:
				break

	def delete_info(self):
		''' Deletes specified item from DB '''
		while True:
			self.display_info() # show what's in the database
			choice = ((raw_input("Delete item? [y/N] ")).lower())[0]
			if (choice == "y"):
				id_num = raw_input("ID of item?: ")
				maximum = self.sql.get_maximum() # get max ID of all items in DB
				input_validated = CLIMenu.input_check(self, id_num, maximum, 1) # 'minimum' is '1' since IDs start from 1
				if input_validated:
					second_choice = (raw_input("Are you sure you want to delete item? [y/N] ")).lower()
					if (second_choice == "y"):
						success = self.sql.remove_row_db(id_num) # removes specified item
						if success:
							print "Item #%s deleted successfully!" % (id_num)
						else:
							print "Item #%s NOT DELETED!" % (id_num)
					else:
						break
			else:
				break

	def initialize_info(self):
		''' checks to see if the database has already been initialized '''
		checked = self.sql.check_db() # checks if any info currently exists
		if not checked:
			print "It appears the database has not been initialized"
			print "Would you like to initialize the database?"
			self.reset_warning()
		else:
			print "Database already initialized!"

	def reset_warning(self):
		choice = (raw_input("(WARNING: This will erase all data!) [y/N] ")).lower()
		if (choice == "y"): 
			second_choice = raw_input("Are you really sure? [y/N] ")
			if (second_choice):
				second_choice = second_choice[0].lower()
			if (second_choice == "y"):
				result = self.sql.reset_db(True) # reset the DB back to nothing
				if result:
					print "Successfully initialized database!"
				else:
					print "Wipe unsuccessful - check DB connection?"

	def set_switcher(self, switcher):
		''' switches the menu_select variable to bring up a new menu '''
		self.menu_select = switcher 

	def shutdown(self):
		''' shutdown function '''
		self.connection_end()
		print "Exiting!"
		raise SystemExit()


