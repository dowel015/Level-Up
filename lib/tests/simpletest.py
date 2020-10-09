import mysql.connector

import lib.utils.database as database

# connect to db, initialize cursor
mydb = database.getDB()
cursor = mydb.cursor()

# Assert DB exists

# Competitions
# Assert competitions table exists
# Assert certain records exists and have correct info

# Events
# Assert events table exists
# Assert certain records exists and have correct info

# Placements
# Assert placements table exists
# Assert certain records exists and have correct info