#!/usr/bin/python
import ast
import datetime
import mysql.connector
import os.path
import re
import requests

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException

import lib.utils.set_library as set_library
from lib.utils.scraper_utils import cleanText
from lib.utils.scraper_utils import subSpace


# {
#     "compid": "13",
#     "name": "U Dance Fest",
#     "startdate": "2020-03-07",
#     "enddate": "2020-03-08",
#     "email": "info@upartnerdance.org",
#     "website": "http://udancefest.com",
#     "city": "St Paul",
#     "state": "MN",
#     "type": "1",
#     "judges": {
#         "1": {
#             "judgeid": "1",
#             "fname": "Gene",
#             "lname": "Bersten",
#             "ischair": "0"
#         },
#         ...
#     },
#     "partnerships": {
#         "1": {
#             "partnershipid": "1",
#             "leaderid": "670",
#             "followerid": "761",
#             "globalid": "670-761"
#         },
#         ...
#     },
#     "dancers": [
#         "190",
#         "191",
#         "192",
#         ...
#     ],
#     "events": [
#         "1",
#         "2",
#         "3",
#         ...
#     ]
# }

# comp_id | event_id | status | age | style | skill | # couples | # rounds | dances | raw_event_text
def buildBCEEventsTable(comp_ids, quick):

    print("\nPulling events from Ballroom Comp Express")

    # Call Ballroom Comp Express API for competitions
    apikey = {"apikey": "8OGUr7i7bxohfo16"}
    r = requests.get("https://ballroomcompexpress.com/api/competitions", params=apikey)
    competitions = r.json()

    for competition in competitions:
        comp_id = competition["compid"]
        if set([comp_id]).issubset(comp_ids):
            comp_ids.add(comp_id)
            print(comp_id, "present in DB")

            if quick:
                return

        elif not competition["compid"]:
            print("No compid at", competition)
        else:
            comp_ids.add(comp_id)

            # Call Ballroom Comp Express API for events at each comp
            r = requests.get("https://ballroomcompexpress.com/api/competitions/" + comp_id, params=apikey)
            comp_object = r.json()

            for event_id in comp_object["events"]:
                r = requests.get("https://ballroomcompexpress.com/api/competitions/" + comp_id + "/events/" + event_id, params=apikey)
                event = r.json()

                # Format dances to intials e.g. ["Waltz", "Quickstep"] -> WQ
                dances = ""
                for dance in event["dances"]:
                    dances = dances + dance[0]

                # Status
                status = [event["category"].lower()]

                # Event Name
                event_name = re.sub("'", "\\'", event["name"])

                checkEvent([
                    comp_id,
                    comp_id + "-" + event_id,
                    status,
                    [event["age"].lower()],
                    getStyle(event["style"].lower()),
                    [event["level"].lower()],
                    event["numentrants"],
                    len(event["rounds"]),
                    dances,
                    event_name
                ])


# comp_id | event_id | status | age | style | skill | # couples | # rounds | dances | raw_event_text
def buildO2CMEventsTable(comp_ids, quick):

    print("\nScraping O2CM events")

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

        compHTMLTable = allCompResultsPage.select('table[id=main_tbl]')[0]

        # Track event ID's to check for potential duplicates
        heat_uids = set()

        # Iterates through every competition on results.o2cm.com
        for comp in compHTMLTable.select('a'):

            # e.g. scoresheet3.asp?event=okc19&heatid=40453020&bclr=#FFFFFF&tclr=#000000
            comp_id = re.search('(?<=event=).*?(?=&)', comp['href']).group(0)
            print(comp_id)

            if set([comp_id]).issubset(comp_ids):
                print(comp_id, "present in DB")

                if quick:
                    return

                comp_ids.add(comp_id)

            else:
                comp_ids.add(comp_id)

                # Initialize web driver
                options = webdriver.ChromeOptions()
                options.add_argument('headless')
                driver = webdriver.Chrome(options=options)

                # GET request to competition results page
                driver.get('http://results.o2cm.com/?event=' + comp_id)

                # Attempt to locate 'submit' button and click to reach complete
                # results page
                try:
                    ok_button = driver.find_element_by_xpath("//input[@type='submit']")
                    ok_button.click()
                    comp_all_page = BeautifulSoup(driver.page_source, 'html.parser')
                    results_table = comp_all_page.select('table[width]')[1]

                    heat_id = ''
                    status = []
                    age_group = []
                    style = ''
                    skill_level = []
                    dances = []
                    num_rounds = 1
                    num_couples = 0

                    raw_event_text = ""

                    # For every event at a competition, find the things
                    for row in results_table.find_all('tr'):

                        # A row with an anchor element denotes a new event
                        if len(row.select('a')) > 0:

                            # Save info from previous event if it exists
                            if heat_id != '':
                                event_summary = [comp_id, heat_id, status, age_group, style, skill_level, num_couples, num_rounds, dances, raw_event_text]
                                checkEvent(event_summary)

                            # Reset counts
                            num_couples = 0
                            num_rounds = 1

                            # Get heat_id
                            href = row.select('a')[0]['href']
                            heat_id = re.search('(?<=heatid=).*?(?=&)', href).group(0)
                            heat_id = comp_id + heat_id
                            # scoresheet3.asp?event=okc19&heatid=40453020&bclr=#FFFFFF&tclr=#000000

                            # Check for duplicate event ID
                            if heat_id in heat_uids:

                                # Write heat_id to file
                                heat_ids_file = open("./output/heat-ids.txt", "a")
                                heat_ids_file.write(str([comp_id, heat_id, "DUPLICATE"]))
                                heat_ids_file.write("\n")
                                heat_ids_file.close()

                            raw_event_text = row.select('a')[0].get_text(strip=True)
                            event_text = cleanText(raw_event_text)
                            print(raw_event_text)
                            print(event_text)


                            # Get each attribute with get<Attribute>(event_text). After a determination is made, the value for
                            # that field is removed from event_text to avoid the same section of the string being interpreted
                            # multiple ways

                            # Status
                            status = getStatus(event_text)

                            if len(status) == 1:
                                event_text = re.sub(status[0], subSpace(status[0]), event_text)

                            print(event_text)

                            # Age
                            age_group = getAge(event_text)

                            if len(age_group) == 1:
                                event_text = re.sub(age_group[0], subSpace(age_group[0]), event_text)

                            print(event_text)

                            # Style
                            style = getStyle(event_text)

                            event_text = re.sub(style, subSpace(style), event_text)

                            print(event_text)

                            # Level
                            skill_level = getLevel(event_text)

                            if len(skill_level) == 1:
                                event_text = re.sub(skill_level[0], subSpace(skill_level[0]), event_text)

                            print(event_text)

                            # Dances
                            dances = getDances(event_text)

                            dances = re.sub(" ", "", re.escape(dances))

                            event_text = re.sub(dances, subSpace(dances), event_text)

                            print(event_text)

                            # More figuring out level, should move to getLevel
                            stripped_event_text = cleanText(event_text)
                            stripped_event_text = re.sub(" ", "", stripped_event_text)

                            for stat in status:
                                stripped_event_text = re.sub(stat, "", stripped_event_text)

                            for age in age_group:
                                stripped_event_text = re.sub(age, "", stripped_event_text)

                            stripped_event_text = re.sub(style, "", stripped_event_text)
                            stripped_event_text = re.sub(re.escape(dances), "", stripped_event_text)

                            if stripped_event_text == "" and skill_level == []:
                                skill_level = "none"


                        # Another entry in same event
                        else:
                            if len(row.select('td')) >= 3:
                                row_text = row.select('td')[2].get_text(strip=True)

                                # Previous Round
                                if row_text == '----':
                                    num_rounds = num_rounds + 1

                                # Another Result
                                else:
                                    num_couples = num_couples + 1

                    event_summary = [comp_id, heat_id, status, age_group, style, skill_level, num_couples, num_rounds, dances, raw_event_text]

                    print(event_summary)

                    # checkEvent validates each event and writes valid ones to
                    # Events table/file, invalid ones to invalid collection
                    checkEvent(event_summary)

                except NoSuchElementException:
                    print('No button for ' + comp_id)
                    no_button_file = open("output/no-button-comp.txt", "a")
                    no_button_file.write(comp_id)
                    no_button_file.write("\n")
                    no_button_file.close()

        # Update date variables
        month = month - 1
        if month == 0:
            month = 12
            year = year - 1

    # while comp_id != stop_point


def addToDB():

    # Add events to DB after full list generated

    # connect to db
    # MYSQL Connection class https://dev.mysql.com/doc/connector-python/en/connector-python-api-mysql-connector.html
    mydb = mysql.connector.connect(
        host="mysql.danoc14.dreamhosters.com",
        user="danoc14dreamhost",
        passwd="QPdwbeL*",
        database="danoc14_dreamhosters_com"
    )

    # initialize cursor
    cursor = mydb.cursor()

    # check if comp table exists
    # create if not exist
    cursor.execute("CREATE TABLE IF NOT EXISTS events (" +
                        " comp_id varchar(255) NOT NULL," +
                        " event_id varchar(255) NOT NULL," +
                        " status varchar(20)," +
                        " age varchar(30)," +
                        " style varchar(50)," +
                        " skill varchar(50)," +
                        " num_couples int," +
                        " num_rounds int," +
                        " dances varchar(20)," +
                        " raw_text varchar(255)," +
                        " PRIMARY KEY (event_id)," +
                        " FOREIGN KEY (comp_id) REFERENCES competitions (comp_id))")

    # Add any events to DB
    if not os.path.exists("output/events.txt"):
        print("No events to add to DB.")

    else:

        # Open output/events.txt
        events_file = open("output/events.txt", "r")

        # iterate through file, do for every line
        for event in events_file:
            event_summary = ast.literal_eval(event)

            # Add event summary to table
            insert = ("INSERT INTO events (comp_id, " +
                                        "event_id, " +
                                        "status, " +
                                        "age, " +
                                        "style, " +
                                        "skill, " +
                                        "num_couples, " +
                                        "num_rounds, " +
                                        "dances, " +
                                        "raw_text) " +
                            "VALUES('" + event_summary[0] + "', '" +
                                        event_summary[1] + "', '" +
                                        event_summary[2] + "', '" +
                                        event_summary[3] + "', '" +
                                        event_summary[4] + "', '" +
                                        event_summary[5] + "', '" +
                                        str(event_summary[6]) + "', '" +
                                        str(event_summary[7]) + "', '" +
                                        event_summary[8] + "', '" +
                                        event_summary[9] + "')")

            cursor.execute(insert)
            mydb.commit()

        # Close file & DB connection
        events_file.close()

    cursor.close()


# Various Events-specific helpers
#
# Determines whether scraper has made sufficient determinations for each field.
def checkEvent(event_summary):

    # Validate event
    bad = False

    # # Comp ID
    # if not probablyGoodCompId(event_summary[0]):
    #     bad = True
    #     event_summary[0] = [event_summary[0]]

    # # Heat ID
    # if not probablyGoodHeatId(event_summary[1]):
    #     bad = True
    #     event_summary[1] = [event_summary[1]]

    # Status
    if len(event_summary[2]) == 1 and (event_summary[2][0] in set_library.am_pro_status or
                                       event_summary[2][0] in set_library.additional_status):
        event_summary[2] = event_summary[2][0]
    else:
        bad = True

    # Age
    if len(event_summary[3]) == 1 and (event_summary[3][0] in set_library.ages or
                                       event_summary[3][0] in set_library.regex_ages):
        event_summary[3] = event_summary[3][0]
    else:
        bad = True

    # Style
    if not event_summary[4] in set_library.dance_styles:
        bad = True
        event_summary[4] = [event_summary[4]]

    # Level
    if len(event_summary[5]) == 1 and event_summary[5][0] in set_library.all_skill_levels:
        event_summary[5] = event_summary[5][0]
    else:
        bad = True

    # Number of couples
    if int(event_summary[6]) < 0:
        bad = True
        event_summary[6] = [event_summary[6]]

    # Number of rounds
    if int(event_summary[7]) < 0:
        bad = True
        event_summary[7] = [event_summary[7]]

    # Dances?

    if bad:
        # Print
        print("Failure: " + str(event_summary))

        # Write to misfits file
        misfits_file = open("./output/misfit-events.txt", "a")
        misfits_file.write(str(event_summary))
        misfits_file.write("\n")
        misfits_file.close()

    else:
        # # Print
        # print("Success: " + str(event_summary))

        # Add event summary to file
        f = open("output/events.txt", "a")
        f.write(str(event_summary))
        f.write("\n")
        f.close()


# Check to see if scraper properly determined comp ID. Returns a boolean.
def probablyGoodCompId(id):
    return re.search(r'\w{5}\w?', id)


# Check to see if scraper properly determined heat ID. Returns a boolean.
def probablyGoodHeatId(id):
    return re.search(r'\w{12}\w?\w?', id)


# Attemps to classify event based on professional/amateur status. Returns empty
# list if unsuccesful.
def getStatus(event_text):

    if re.search(r"^ $", event_text):
        return "none"

    status = []

    for status_type in set_library.am_pro_status - set_library.basic_status:
        if re.search(status_type + " ", event_text):
            status.append(status_type)

    if len(status) == 0:
        for status_type in set_library.am_pro_status:
            if re.search(status_type + " ", event_text):
                status.append(status_type)

    if len(status) == 0:
        for status_type in set_library.additional_status:
            if re.search(status_type + " ", event_text):
                status.append(status_type)

    if len(status) == 0 and re.search(event_text, "pro"):
        status.append("pro")

    if len(status) == 0:
        status.append("none")

    return status


# Attempts to discern age level of an event from result tag, returns empty
# string if unable
def getAge(event_text):

    if re.search(r"^ $", event_text):
        return "none"

    age_group = []

    for age in (set_library.ages - set_library.age_groups):
        if re.search(age + ' ', cleanText(event_text)):
            age_group.append(re.sub('\\\\', '', age))

    if len(age_group) == 0:
        for age in set_library.ages:
            if re.search(age + ' ', cleanText(event_text)):
                age_group.append(re.sub('\\\\', '', age))

    if len(age_group) == 0:
        age_group.append("none")

    return age_group


# Attempts to discern whether event was International or American Style, returns
# empty string if it fails
def getStyle(text):

    if re.search(r"^ *$", text):
        return "none"

    standard = {"ballroom", "standard" }

    am_or_intl = ""

    for word in set_library.american_styles:
        if word in cleanText(text):
            am_or_intl = "american"
    for word in set_library.international_styles:
        if word in cleanText(text):
            am_or_intl = "intl"


    for word in cleanText(text).split(" "):
        if word == "rhythm":
            return "rhythm"
        elif word == "latin":
            return "latin"
        elif word == "smooth":
            return "smooth"
        elif word in standard:
            return "standard"
        elif word == "fun":
            return "fun"

    # Figure out style from dances and am_or_intl
    if am_or_intl == "american":
        for dance in set_library.smooth_dances:
            if re.search(dance, cleanText(text)):
                return "smooth"
        for dance in set_library.rhythm_dances:
            if re.search(dance, cleanText(text)):
                return "rhythm"

    elif am_or_intl == "intl":
        for dance in set_library.standard_dances:
            if re.search(dance, cleanText(text)):
                return "standard"
        for dance in set_library.latin_dances:
            if re.search(dance, cleanText(text)):
                return "latin"

    if am_or_intl == "":
        for dance in set_library.other_dances:
            if re.search(dance, cleanText(text)):
                return "other"
        for dance_style in set_library.dance_styles:
            if re.search(dance_style, cleanText(text)):
                return dance_style
        return "none"
    else:
        return am_or_intl
        # print("failed to determine style")
        # os._exit(10)


# Attempts to discern the level of an event (standardized format), returns empty string if it fails
def getLevel(event_text):

    # if input is only spaces
    if re.search(r"^\s*?$", event_text):
        return "none"

    skill_level = []

    for level in (set_library.all_skill_levels - set_library.general_skill_levels):
        if re.search(" " + level + " ", event_text) or re.search(r"^" + level + " ", event_text):
            skill_level.append(level)

    if len(skill_level) == 0:
        for level in set_library.all_skill_levels - { "open", "ouvert" }:
            if re.search(" " + level + " ", event_text) or re.search(r"^" + level + " ", event_text):
                skill_level.append(level)


    if skill_level == [] and re.search("open", event_text):
        skill_level.append("open")
    elif skill_level == [] and re.search("ouvert", event_text):
        skill_level.append("ouvert")

    return skill_level


# Determine dances danced in dance event. Dance.
def getDances(event_text):

    # dances = []

    if re.search(r"^\s*?$", event_text):
        # dances.append("none")
        return "none"

    if re.search("showdance", event_text):
        # dances.append("showdance")
        return "showdance"

    if re.search(r'\(\w+\)', event_text):
        # dance_initials = re.search(r'\(%w+\)$', event_text)

        # # WTFVCRSBM
        # if style in set_library.american_styles:
        #     for letter in dance_initials:
        #         if letter in set_library.american_dances:
        #             dances.append(set_library.american_dances[letter])
        #         else:
        #             dances.append(letter)

        # # WTVFQSCRPJ
        # elif style in set_library.international_styles:
        #     for letter in dance_initials:
        #         if letter in set_library.international_dances:
        #             dances.append(set_library.international_dances[letter])
        #         else:
        #             dances.append(letter)


        # return re.search(r'\(%w+\)$', event_text)

        dances = re.search(r'\(\w+\)', event_text).group(0)
        dances = re.sub(r'\\', '', dances)
        dances = re.sub(r'[\(\)]', '', dances)
        return dances

    return event_text.split(" ")[-1]
    # dances.append("error")

    # return dances