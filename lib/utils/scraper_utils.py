#!/usr/bin/python
import datetime
import re
import os

from bs4 import BeautifulSoup
from requests import get
from contextlib import closing
from requests import RequestException
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException

import lib.utils.set_library as set_library

# Formats Month as number
def numericalMonth(month):
    months = [ 'not_a_month', 'Jan', 'Feb', 'Mar', 'Apr', 'May',
               'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec' ]

    numerical_month = months.index(month)
    if numerical_month < 10:
        numerical_month = '0' + str(numerical_month)
    else:
        numerical_month = str(numerical_month)

    return numerical_month


# Attempts to discern age level of an event from result tag, returns empty
# string if unable
def getAge(event_text):

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


# Attempts to discern the level of an event (standardized format), returns empty string if it fails
def getLevel(event_text):
    skill_level = []

    clean_event_text = cleanText(event_text)

    for level in (set_library.all_skill_levels - set_library.general_skill_levels):
        if re.search(level, clean_event_text):
            skill_level.append(level)

    if len(skill_level) == 0:
        for level in set_library.all_skill_levels - { "open", "ouvert" }:
            if re.search(level, clean_event_text):
                skill_level.append(level)


    if skill_level == [] and re.search("open", clean_event_text):
        skill_level.append("open")
    elif skill_level == [] and re.search("ouvert", clean_event_text):
        skill_level.append("ouvert")

    return skill_level


# Attemps to classify event based on professional/amateur status. Returns empty
# list if unsuccesful.
def getStatus(event_text):

    status = []

    for status_type in set_library.am_pro_status:
        if re.search(status_type, cleanText(event_text)):
            status.append(status_type)

    if len(status) == 0:
        for status_type in set_library.additional_status:
            if re.search(status_type, cleanText(event_text)):
                status.append(status_type)

    if len(status) == 0 and re.search(cleanText(event_text), "pro"):
        status.append("pro")

    if len(status) == 0:
        status.append("none")

    return status


# Attempts to discern whether event was International or American Style, returns
# empty string if it fails
def getStyle(text):

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

    print(am_or_intl)
    if am_or_intl == "":
        for dance in set_library.other_dances:
            if re.search(dance, cleanText(text)):
                return "fun"
        for dance_style in set_library.dance_styles:
            if re.search(dance_style, cleanText(text)):
                return dance_style
        return "none"
    else:
        return am_or_intl
        # print("failed to determine style")
        # os._exit(10)


# Determine dances danced in dance event. Dance.
def getDances(event_text):

    if re.search("showdance", cleanText(event_text)):
        return "showdance"

    # if re.search(r'\(%w+\)', cleanText(event_text)):

    return event_text.split(" ")[-1]


# Cleans up text string to make parsing/interpretation easier
def cleanText(text):

    # clean_text = re.sub(r'[\.\*\(\)\[\]]', '', text)
    clean_text = re.sub(r'[\.\*\[\]]', '', text)
    clean_text = clean_text.lower()

    return clean_text


def subSpace(text):

    sub = ""

    for _ in range(0, len(text)):
        sub = sub + " "

    return sub