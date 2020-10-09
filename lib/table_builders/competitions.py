#!/usr/bin/python
import datetime
import re
import requests
import sys
import mysql.connector

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException

import lib.utils.database as database
import lib.utils.scraper_utils as scraper_utils

# Inserts comp records to db: comp_id | comp_name | is_nqe | date (YYYY-MM-DD)
def buildO2CMCompTable(comp_ids, quick):

    print("\nScraping competitions from o2cm")

    # Connect to dreamhost db
    mydb = database.getDB()

    # initialize cursor
    cursor = mydb.cursor()

    # check if comp table exists
    # create if not exist
    cursor.execute("CREATE TABLE IF NOT EXISTS competitions " +
                   "(comp_id varchar(255) NOT NULL, " +
                   "comp_name varchar(255), " +
                   "is_nqe varchar(255), " +
                   "date varchar(255), " +
                   "PRIMARY KEY (comp_id))")

    # Initialize date variables
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

        # Countdown to help sort results from same date
        counter = len(compHTMLTable.select('tr'))

        # Iterate through table of Competitions
        for row in compHTMLTable.select('tr'):

            # An anchor element with href attribute indicates link to competition
            # results page
            if row.select('a[href]'):

                # Comp ID
                href = row.select('a[href]')[0]['href']

                comp_id = re.search('(?<=event=).*?(?=&)', href).group(0)

                print(comp_id)

                if set([comp_id]).issubset(comp_ids):
                    print("competition id " + comp_id + "' already present")

                    if quick:
                        return

                else:
                    comp_ids.add(comp_id)

                    # Date
                    day_string = row.select('td')[0].get_text(strip=True)
                    month_string = scraper_utils.numericalMonth(day_string[0:3])
                    day = day_string[4:]

                    # Competition Name
                    comp_name = row.select('a[href]')[0].get_text(strip=True)

                    # NQE? If a competition's name includes the string 'NQE', we
                    # assume it's an NQE.
                    is_NQE = False

                    if re.search("nqe", scraper_utils.cleanText(comp_name)):
                        is_NQE = True

                    date = str(year) + '-' + month_string + "-" + day + "-" + str(counter)

                    # Add comp to db
                    insert = "INSERT INTO competitions (comp_id, comp_name, is_nqe, date) VALUES('" + comp_id + "', '" + comp_name + "', '" + str(is_NQE) + "', '" + date + "')"

                    print(insert)
                    cursor.execute(insert)
                    mydb.commit()

                    # # Alternatively, write to file
                    # competition = [ comp_id, comp_name, is_NQE, date ]
                    # print("competition: " + str(competition))
                    # f = open("./output/comp-table.txt", "a")
                    # f.write(str(competition))
                    # f.write("\n")
                    # f.close

            # Decrement counter
            counter = counter - 1

        # Update date variables
        month = month - 1
        if month == 0:
            month = 12
            year = year - 1

    # while comp_id != stop_point

    # close db connection
    cursor.close()


# Inserts comp records to db: comp_id | comp_name | is_nqe | date (YYYY-MM-DD)
def buildBCECompTable(comp_ids, quick):

    print("\nPulling competitions from Ballroom Comp Express")

    # Connect to dreamhost db
    mydb = database.getDB()

    # initialize cursor
    cursor = mydb.cursor()

    # check if comp table exists
    # create if not exist
    cursor.execute("CREATE TABLE IF NOT EXISTS competitions" +
                   "    (comp_id varchar(255) NOT NULL, comp_name varchar(255), is_nqe varchar(255), date varchar(255), PRIMARY KEY (comp_id))")

    # Call Ballroom Comp Express API
    apikey = {"apikey": "8OGUr7i7bxohfo16"}
    r = requests.get("https://ballroomcompexpress.com/api/competitions", params=apikey)
    competitions = r.json()

    # GET https://ballroomcompexpress.com/api/competitions?apikey=8OGUr7i7bxohfo16
    # returns JSON list of comp objects:
    # [
    #     {
    #         "compid": "13",
    #         "name": "U Dance Fest",
    #         "startdate": "2020-03-07",
    #         "enddate": "2020-03-08",
    #         "email": "info@upartnerdance.org",
    #         "website": "http://udancefest.com",
    #         "city": "St Paul",
    #         "state": "MN",
    #         "type": "1"
    #     },
    # ...
    # ]

    for competition in competitions:
        if set([competition["compid"]]).issubset(comp_ids):
            print(competition["compid"], competition["name"], "already present in DB")

            if quick:
                return

        else:

            comp_ids.add(competition["compid"])

            # Add comp to db
            is_NQE = (competition["type"] == 2)
            insert = ("INSERT INTO competitions (comp_id, comp_name, is_nqe, date) " +
                "VALUES('" + competition["compid"] + "', " +
                "'" + competition["name"] + "', " +
                "'" + str(is_NQE) + "', " +
                "'" + competition["startdate"] + "')")

            print(insert)
            cursor.execute(insert)
            mydb.commit()

    # close db connection
    cursor.close()
