#!/usr/bin/python
import mysql.connector
import os
import sys

import lib.utils.database as database
import lib.table_builders.events as events
import lib.table_builders.placements as placements
import lib.table_builders.competitions as competitions


#########
# Get IDs
#########

if sys.argv[1] == "all":
    quick = False

elif sys.argv[1] == "recent":
    quick = True

else:
    print("invalid option", sys.argv[1])

# connect to db initialize cursor
mydb = database.getDB()
cursor = mydb.cursor()

# Get competition IDs
query = "SELECT comp_id FROM competitions ORDER BY date DESC"

comp_ids = set()
first = ""

try:
    cursor.execute(query)
    rows = cursor.fetchall()
    if rows:
        first = rows[0][0]
        for row in rows:
            comp_ids.add(row[0])
    print("Found", len(rows), "competitions IDs. Most recent:", first)

except:
    print("Error executing query")

# Get event IDs
query = "SELECT comp_id FROM competitions WHERE comp_id IN (SELECT comp_id FROM events) ORDER BY date DESC"

event_ids = set()
first = ""

try:
    cursor.execute(query)
    rows = cursor.fetchall()
    if rows:
        first = rows[0][0]
        for row in rows:
            event_ids.add(row[0])
    print("Found", len(rows), "competitions with events present. Most recent:", first)

except:
    print("Error executing query")

# Get comp_ids from events that have placements
query = ("SELECT comp_id " +
        "FROM competitions " +
        "WHERE comp_id IN " +
            "(SELECT comp_id " +
            "FROM events " +
            "WHERE event_id IN (SELECT event_id FROM placements)) " +
        "ORDER BY date " +
        "DESC")

first = ""
placement_ids = set()

try:
    cursor.execute(query)
    rows = cursor.fetchall()
    if rows:
        first = rows[0][0]
        for row in rows:
            placement_ids.add(row[0])
    print("Found", len(rows), "competitions with placements present. Most recent:", first)

except:
    print("Error executing query")


# close db connection
cursor.close()

############################
# Update tables individually
############################

competitions.buildBCECompTable(comp_ids, quick)
competitions.buildO2CMCompTable(comp_ids, quick)

events.buildBCEEventsTable(event_ids, quick)
events.buildO2CMEventsTable(event_ids, quick)
events.addToDB()

placements.buildBCEPlacementsTable(placement_ids, quick)
placements.buildO2CMPlacementsTable(placement_ids, quick)
placements.addToDB()
