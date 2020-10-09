#!/usr/bin/python
import ast
import datetime
import json
import mysql.connector
import os.path
import re
import requests

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException

import lib.utils.database as database
import lib.utils.scraper_utils as scraper_utils
import lib.utils.set_library as set_library

# Determines whether scraper has made sufficient determinations for each field.
def checkPlacement(placement):
    bad = False

    if len(placement) != 9:
        bad = True

    else:
        # heat_id placement[0]

        # numeric_placement
        if not re.search(r'^\d+$', placement[1]):
            bad = True
            placement[1] = [placement[1]]

        # competitor_number
        if not re.search(r'^\d+$', placement[2]):
            bad = True
            placement[2] = [placement[2]]

        # lead name: check for leading/trailing space
        if re.search(r'^\ ', placement[3]) or re.search(r'\ $', placement[3]):
            bad = True
            placement[3] = [placement[3]]

        # lead_id placement[4]

        # follow name: check for leading/trailing space and trailing ' -'
        if re.search(r'\ \-$', placement[5]) or re.search(r'^\ ', placement[5]) or re.search(r'\ $', placement[5]):
            bad = True
            placement[5] = [placement[5]]

        # follow id placement[6]

        # location placement[7]

        # full text placement[8]

    if bad:

        # Write to misfits file
        misfits_file = open("./output/misfit-placements.txt", "a")
        misfits_file.write(str(placement))
        misfits_file.write("\n")
        misfits_file.close()

    else:

        # Add placement to file
        f = open("output/placements.txt", "a")
        f.write(str(placement))
        f.write("\n")
        f.close()


def buildBCEPlacementsTable(comp_ids, quick):

    print("\nPulling placements from Ballroom Comp Express")

    # Call Ballroom Comp Express API
    apikey = {"apikey": "8OGUr7i7bxohfo16"}
    r = requests.get("https://ballroomcompexpress.com/api/competitions", params=apikey)
    competitions = r.json()

    new_ids = set()

    for comp in competitions:
        if not set([comp["compid"]]).issubset(comp_ids):
            print("New comp", comp["compid"])
            new_ids.add(comp["compid"])

        else:
            print(comp["compid"], "already in DB")
            if quick:
                return

    for id in new_ids:

        # Get competitor info
        r = requests.get("https://ballroomcompexpress.com/api/competitions/" + id + "/dancers", params=apikey)
        dancers = r.text

        # Trim query prefix
        if len(dancers.split(";")) < 2:
            print("Error retrieving competitor info.")

        else:
            dancers = dancers.split(";")[1]
            dancers = json.loads(dancers)

            # Iterate through events
            r = requests.get("https://ballroomcompexpress.com/api/competitions/" + id + "/events", params=apikey)
            events = r.json()
            for event in events:
                uri = "https://ballroomcompexpress.com/api/competitions/" + id + "/events/" + event["eventid"]
                r = requests.get(uri, params=apikey)
                placements = r.json()

                if len(placements["entrants"]) > 0:
                    for competitor_number, entrant in placements["entrants"].items():

                        checkPlacement([id + "-" + event["eventid"],
                            entrant["place"],
                            competitor_number,
                            format_name(dancers[entrant["leaderid"]]["lname"] + ", " + dancers[entrant["leaderid"]]["fname"]),
                            entrant["leaderid"],
                            format_name(dancers[entrant["followerid"]]["lname"] + ", " + dancers[entrant["followerid"]]["fname"]),
                            entrant["followerid"],
                            "",
                            ""])


# event_id | placement | competitor number | lead name | lead id | follow name | follow id | location | raw_text
def buildO2CMPlacementsTable(comp_ids, quick):

    print("\nScraping O2CM placements")

    # start = False

    comp_id = ''
    current_date = datetime.datetime.now()
    year = current_date.year
    month = current_date.month

    while year != 2004:

        print("searching", year, month)

        # Initialize web driver
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        driver = webdriver.Chrome(options=options)

        # GET request to competition results page
        driver.get('http://results.o2cm.com/')

        # Find form and filter by year and month
        month_element = driver.find_element_by_id("inmonth")
        month_element.clear()
        month_element.send_keys(month)

        year_element = driver.find_element_by_id("inyear")
        year_element.clear()
        year_element.send_keys(year)

        driver.find_element_by_name("Go").click()

        allCompResultsPage = BeautifulSoup(driver.page_source, 'html.parser')

        # Iterates through every competition on results.o2cm.com
        for comp in allCompResultsPage.select('a'):

            if re.search('(?<=event=).*?(?=&)', comp['href']):
                # e.g. scoresheet3.asp?event=okc19&heatid=40453020&bclr=#FFFFFF&tclr=#000000
                comp_id = re.search('(?<=event=).*?(?=&)', comp['href']).group(0)
                print(comp_id)

                if set([comp_id]).issubset(comp_ids):
                    print(comp_id, "present in DB")

                    if quick:
                        return

                    comp_ids.add(comp_id)

                else:
                    # Initialize web driver
                    options = webdriver.ChromeOptions()
                    options.add_argument('headless')
                    driver = webdriver.Chrome(options=options)

                    # GET request to competition results page
                    driver.get('http://results.o2cm.com/?event=' + comp_id)

                    # Attempt to locate 'submit' button and click to reach complete results
                    # page
                    try:
                        ok_button = driver.find_element_by_xpath("//input[@type='submit']")
                        ok_button.click()
                        comp_all_page = BeautifulSoup(driver.page_source, 'html.parser')
                        results_table = comp_all_page.select('table[width]')[1]

                        # Parse competitor drop down, get competitor ID info
                        # initialize empty data structure
                        competitor_ids = {}

                        if comp_all_page.find(id='selEnt') != None:

                            competitors = comp_all_page.find(id='selEnt')

                            # add each competitor number and text to data structure
                            for competitor in competitors.find_all('option'):
                                competitor_ids[format_name(competitor.get_text(strip=True))] = competitor['value']

                        heat_id = ''

                        # For every event at a competition, find the things
                        for row in results_table.find_all('tr'):

                            # A row with an anchor element denotes a new event
                            if len(row.select('a')) > 0:

                                # Get heat_id
                                href = row.select('a')[0]['href']
                                heat_id = re.search('(?<=heatid=).*?(?=&)', href).group(0)
                                heat_id = comp_id + heat_id
                                # scoresheet3.asp?event=okc19&heatid=40453020&bclr=#FFFFFF&tclr=#000000

                            # Another entry in same event
                            else:
                                if len(row.select('td')) >= 3:
                                    row_text = row.select('td')[2].get_text(strip=True)

                                    clean_row = scraper_utils.cleanText(row_text)

                                    # '1) 210 Jackson Fossen & Claire Thompson - MN'
                                    # '8) TBA TBA& TBA TBA'

                                    if clean_row != '----' and clean_row != '':

                                        ##########################################
                                        # Determine and save each placement here #
                                        ##########################################

                                        if not re.search(r'^\d+\)\s\d?\d?\d?\s?[\w\d\"\'\`\-\.\,\?\!\_\/\#\(\)\s]*\s?&\s?', clean_row):
                                            f = open("./output/failed-pattern.txt", "a")
                                            f.write(clean_row)
                                            f.write("\n")
                                            f.close()

                                        else:
                                            # Overall placement in event
                                            numeric_placement = "0"
                                            if re.search(r'^\d\d?\d?(?=\))', clean_row):
                                                numeric_placement = re.search(r'^\d\d?\d?(?=\))', clean_row).group(0)
                                                clean_row = re.sub(numeric_placement + "\)", scraper_utils.subSpace(numeric_placement + ")"), clean_row)
                                                clean_row = re.sub(r'^\s*', '', clean_row)

                                            # Competitor Number
                                            competitor_number = "X"
                                            if re.search(r'^\s*\d+', clean_row):
                                                competitor_number = re.search(r'^\s*\d+', clean_row).group(0)
                                                competitor_number = re.sub(r'\s', '', competitor_number)

                                            clean_row = re.sub(competitor_number, scraper_utils.subSpace(competitor_number), clean_row)

                                            # Couple/Competitors
                                            # Lead name is any text before an ampersand
                                            lead_name = " "
                                            if re.search(r'^.*(?=\ *\&)', clean_row):
                                                lead_name = re.search(r'^.*(?=\ *\&)', clean_row).group(0)

                                            # Remove leading/trailing spaces from lead name
                                            lead_name = re.sub(r'^\ *', '', lead_name)
                                            lead_name = re.sub(r'\ *$', '', lead_name)

                                            # Lead ID (for this comp anyway)
                                            lead_id = ''
                                            if competitor_ids.get(lead_name):
                                                lead_id = competitor_ids[lead_name]

                                            # Follow name is any text after an ampersand
                                            follow_name = re.search(r'(?<=\&).*$', clean_row).group(0)

                                            # Remove leading spaces from follow name
                                            follow_name = re.sub(r'^\ *', '', follow_name)

                                            # Filter potential location info
                                            location = ''
                                            if re.search(r'\ *(\-\ )?\-\ \ ?[\w\s\-\(\)]+$', follow_name):
                                                location = re.search(r'\ *(\-\ )?\-\ \ ?[\w\s\-\(\)]+$', follow_name).group(0)
                                                location = re.sub(r'^\ *(\-\ )?\-\ \ ?', '', location)

                                                # Remove location info from follow_name
                                                follow_name = re.sub(r'\ *(\-\ )?\-\ \ ?[\w\s\-\(\)]+$', '', follow_name)

                                            # Remove trailing space/hyphens from follow_name
                                            follow_name = re.sub(r'[\ \-]*$', '', follow_name)

                                            # Follow ID (for this comp anyway)
                                            follow_id = ''
                                            if competitor_ids.get(follow_name):
                                                follow_id = competitor_ids[follow_name]

                                            # Complete Placement
                                            placement = [heat_id, numeric_placement, competitor_number, lead_name, lead_id, follow_name, follow_id, location, row_text] # TO DO: couple_id? lead_id? follow_id?

                                            checkPlacement(placement)


                    except NoSuchElementException:
                        print('No button for ' + comp_id)
                        no_button_file = open("output/no-button-comp.txt", "a")
                        no_button_file.write(comp_id)
                        no_button_file.write("\n")
                        no_button_file.close()

                # else:
                #     print("skip " + comp_id)

        # Update date variables
        month = month - 1
        if month == 0:
            month = 12
            year = year - 1

    # while comp_id != stop_point

# end

# Add placements to DB after full list generated
def addToDB():

    # connect to db
    mydb = database.getDB()

    # initialize cursor
    cursor = mydb.cursor()

    # check if comp table exists
    # create if not exist
    cursor.execute("CREATE TABLE IF NOT EXISTS placements (" +
                        " event_id varchar(255) NOT NULL," +
                        " placement float," +
                        " competitor_number int," +
                        " lead_name varchar(255)," +
                        " lead_id varchar(255)," +
                        " follow_name varchar(255)," +
                        " follow_id varchar(255)," +
                        " location varchar(50)," +
                        " raw_text varchar(255)," +
                        " CONSTRAINT event_entry PRIMARY KEY (event_id,competitor_number)," +
                        " FOREIGN KEY (event_id) REFERENCES events (event_id))")

    cursor.execute("CREATE TABLE IF NOT EXISTS temp_placements (" +
                        " event_id varchar(255) NOT NULL," +
                        " placement float," +
                        " competitor_number int," +
                        " lead_name varchar(255)," +
                        " lead_id varchar(255)," +
                        " follow_name varchar(255)," +
                        " follow_id varchar(255)," +
                        " location varchar(50)," +
                        " raw_text varchar(255)," +
                        " CONSTRAINT event_entry PRIMARY KEY (event_id,competitor_number))")

    if not os.path.exists("output/placements.txt"):
        print("No placements to add to DB.")

    else:
        # Open output/placements.txt
        with open("output/placements.txt", "r") as placements_file:

            # iterate through file, do for every line
            for placement in placements_file:
                placement_summary = ast.literal_eval(placement)

                # Add placement summary to table
                insert = ("INSERT IGNORE INTO temp_placements (event_id, " +
                                            "placement, " +
                                            "competitor_number, " +
                                            "lead_name, " +
                                            "lead_id, " +
                                            "follow_name, " +
                                            "follow_id, " +
                                            "location, " +
                                            "raw_text) " +
                                "VALUES('" + placement_summary[0] + "', '" +
                                            str(placement_summary[1]) + "', '" +
                                            str(placement_summary[2]) + "', '" +
                                            placement_summary[3] + "', '" +
                                            placement_summary[4] + "', '" +
                                            placement_summary[5] + "', '" +
                                            placement_summary[6] + "', '" +
                                            placement_summary[7] + "', '" +
                                            re.escape(placement_summary[8]) + "')")

                cursor.execute(insert)
                mydb.commit()

        insert = ("INSERT IGNORE INTO placements (event_id, " +
                                    "placement, " +
                                    "competitor_number, " +
                                    "lead_name, " +
                                    "lead_id, " +
                                    "follow_name, " +
                                    "follow_id, " +
                                    "location, " +
                                    "raw_text) " +
            "SELECT * from temp_placements " +
            "WHERE event_id IN (SELECT event_id FROM events)")

        cursor.execute(insert)
        mydb.commit()

        # delete rows from temp placements that have been successfully inserted into placements
        delete = ("DELETE FROM temp_placements WHERE event_id IN (SELECT event_id FROM placements) " +
            "AND placement IN (SELECT placement FROM placements)")

        cursor.execute(delete)
        mydb.commit()

        placements_file.close()

    # Close DB connection
    cursor.close()


def format_name(name):
    if re.match(r'^[\w\d\s\-\`\'\.]*\,\s[\w\d\s\-\`\'\.]*$', name):
        last_name = re.search(r'^[\w\d\s\-\`\'\.]*(?=\,\s)', name).group(0)
        first_name = re.search(r'(?<=\,\s)[\w\d\s\-\`\'\.]*$', name).group(0)

        # strip leading & trailing spaces
        first_name = re.sub(r'\s*$', '', first_name)
        first_name = re.sub(r'^\s*', '', first_name)

        last_name = re.sub(r'\s*$', '', last_name)
        last_name = re.sub(r'^\s*', '', last_name)

        # convert to lowercase
        first_name = first_name.lower()
        last_name = last_name.lower()

        # escape accents/apostrophes
        first_name = re.sub("'", "\\'", first_name)
        last_name = re.sub("'", "\\'", last_name)

        return first_name + " " + last_name

    else:
        return re.sub("'", "\\'", name)