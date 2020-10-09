#!/usr/bin/python

# Various sets referenced by multiple functions
dances = {
    "waltz", "tango", "foxtrot", "viennese", "quickstep", "samba",
    "cha", "rumba", "paso", "paso-doble", "jive", "bolero", "mambo", "swing"
}

# Style
dance_styles = {
    "latin", "rhythm", "smooth", "standard",
    "american", "international", "intl",
    "social", "fun", "club", "night club", "nightclub", "nc", "country", "other", "none"
}

american_styles = { "american", "am", "smooth", "rhythm", "nine dance" }

international_styles = {
    "latin", "ballroom", "standard", "intl", "international"
}

# Dances
american_dances = {
    "w": "waltz",
    "t": "tango",
    "f": "foxtrot",
    "v": "viennese",

    "c": "cha",
    "r": "rumba",
    "s": "swing",
    "b": "bolero",
    "m": "mambo"
}

international_dances = {
    "w": "waltz",
    "t": "tango",
    "v": "viennese",
    "f": "foxtrot",
    "q": "quickstep",

    "s": "samba",
    "c": "cha",
    "r": "rumba",
    "p": "paso",
    "j": "jive"
}

smooth_dances = { "waltz", "tango", "foxtrot", "viennese", "viennese waltz" }

standard_dances = {
    "waltz", "tango", "viennese", "viennese waltz", "foxtrot", "quickstep"
}

rhythm_dances = { "cha", "cha-cha", "rumba", "swing", "bolero", "mambo" }

latin_dances = {
    "samba", "cha", "cha-cha", "rumba", "paso", "paso-doble", "jive"
}

other_dances = {
    "argentine tango", "bachata", "hustle", "lindy hop", "merengue", "polka",
    "salsa", "west coast swing",
}

# Level
all_skill_levels = {
    "none",
    "mixed proficiency", "mixed-proficiency newcomer",
    "newcomer", "pre-bronze", "pre bronze",
    "newcomer - bronze",
    "bronze", "beginning bronze", "beg-bron", "beginner to bronze", "intermediate bronze", "interm bronze", "int bronze", "advanced bronze", "full bronze", "closed bronze", "open bronze",
    "bronze/silver", "bronze-silver", "bronze - silver",
    "pre-silver", "pre silver", " beginning silver", "int silver", "intermediate silver", "silver", "advanced silver", "full silver", "closed silver", "open silver",
    "silver/gold", "silver, gold", "silver-gold", "silver - gold", "silver to gold", r"silver \& gold",
    "gold", "beginning gold", "pre-gold", "pre gold", "int gold", "intermediate gold", "advanced gold", "full gold", "closed gold", "open gold",
    "beginning", "beginner", "beginners - advanced",
    "intermediate", "open intermediate",
    "intermediate/advanced", "int/adv",
    "advanced",
    "syllabus",
    "gold/open",
    "open syllabus",
    "open",
    "novice", "pre-novice", "pre-champ", "prech-ch", "championship", "pre-championship", "champ", "champion open", "advanced open",
    "rising star", "rising-star",
    "elementary school beginner", "elementary school other",
    "middle school intermediate", "middle school advanced", "middle school other",
    "high school intermediate", "high school advanced", "high school other",
    "all levels",

    # French
    "ouvert bronze", "bronze et moins",
    "argent ", "argent et plus",
    "argent et or",
    " or ", "int or",
    "ouvert",
    "preliminaire", "pre-amateur", "debutant",
    "intermediaire", "intermediaire moderne"
}

general_skill_levels = {
    "newcomer",
    "bronze",
    "silver",
    "gold",
    "beginner", "beginning",
    "intermediate",
    "advanced",
    "syllabus",
    "open",
    "novice",
    "championship",

    # French
    "argent ", # silver
    " or ",    # gold
    "ouvert",  # open
}

level_prefixes = {
    "pre", "pre-", "pre ", "open", "beginning", "beginner", "intermediate",
    "int", "interm", "advanced", ""
}

# Age
age_groups = {
    "adult", "adulte", "senior", "youth", "juvenile", "junior", "jr", "pre-teen", r"40\+", r"50\+"
}

age_subgroups = {
    "1", "2", "3", "4", "5", "6", "i", "ii", "iii", "iv", "v", "vi",
    "a1", "a2", "a3", "b1", "b2", "b3", "c1", "c2", "c3", "d1", "d2", "d3"
}

ages = {
    "teddy bear", "teddy-bear", "babies under 6yo", "itty-bitty", "kids",
    "juvenile",
        "juvenile i", "juvenile ii", "juvenile iii", "juvenile iv", "juvenile v", "juvenile vi",
        "juvenile 1", "juvenile 2",  "juvenile 3",   "juvenile 4",  "juvenile 5", "juvenile 6",
    "pre-teen",
        "pre-teen i", "pre-teen ii", "pre-teen iii", "pre-teen iv", "pre-teen v", "pre-teen vi",
        "pre-teen 1", "pre-teen 2",  "pre-teen 3",   "pre-teen 4",  "pre-teen 5", "pre-teen 6",
    "junior",
        "junior i", "junior ii", "junior iii", "junior iv", "junior v", "junior vi",
        "junior 1", "junior 2",  "junior 3",   "junior 4",  "junior 5", "junior 6",
    "youth",
        "youth i", "youth ii", "youth iii", "youth iv", "youth v", "youth vi",
        "youth 1", "youth 2",  "youth 3",   "youth 4",  "youth 5", "youth 6",
    "adult",
        "adult a ", "adult a1", "adult a2", "adult a3",
        "adult b ", "adult b1", "adult b2", "adult b3",
        "adult c ", "adult c1", "adult c2", "adult c3",
        "adult d ", "adult d1", "adult d2", "adult d3",
    "senior",
        "senior i", "senior ii", "senior iii", "senior iv", "senior v", "senior vi",
        "senior 1", "senior 2",  "senior 3",   "senior 4",  "senior 5", "senior 6",
    r"16\+", r"16 \+", r"18\+", r"19\+", r"30\+", r"40\+", r"40 \+", r"50\+", r"50 \+", r"65\+", r"15 yrs \& under", r"16 yrs \& older",
    "12-16", "17-29", "30-39", "under 7", "under 9", "under 14", "under 15", "15 yrs & under", "15 and under", "under 16", "over 16", "16 yrs & older", "over 18", "under 19", "under 21", "35 plus", "over 40",
    "collegiate",
    "none", "open", "all ages",

    # French
    "adulte", "jeune adulte", "jeunesse", "adulte over 40", "45 et plus",
    r"adulte 16\+", r"adulte 16 \+", r"adulte 18\+", r"adulte 19\+", r"adulte 30\+", r"adulte 40\+", r"adulte 50\+", r"adulte 65\+", "adulte 30-39",
}

# Experimental, not currently used
regex_ages = {
    "16+", "16 +", "18+", "over 18", "19+", "30+", "40+", "over 40", "50+", "65+",
    "15 yrs & under", "16 yrs & older",
    "adulte 16+", "adulte 16 +", "adulte 18+", "adulte over 18",
    "adulte 19+", "adulte 30+", "adulte 40+",
    "adulte 50+", "adulte 65+"
}

# Professional Status
am_pro_status = {
    "none",
    "collegiate",
    "amateur", "amat", "am/am", "student/student",
    "professional",
    "pro/am", "proam", "pro-am",
    "teacher/student", "teacher/am", "teach/student", "tea/stu",
    "mixed proficiency",
    "jack and jill",

    # Ladies
    "pro/am ladies", "proam ladies", "pro-am ladies", "pro/am - ladies", "proam - ladies", "pro-am - ladies",
    "teacher/student ladies", "teacher/am ladies", "teach/student ladies", "tea/stu ladies",

    # Gents
    "pro/am gents", "proam gents", "pro-am gents", "pro/am - gents", "proam - gents", "pro-am - gents",
    "teacher/student gents", "teacher/am gents", "teach/student gents", "tea/stu gents",

    "mixed ladies", "mixed prof,/ladies", "mixed gents", "mixed prof./gents"
}

basic_status = {
    "none",
    "amateur", "am/am", "student/student",
    "professional",
    "pro/am", "proam", "pro-am",
    "teacher/student", "teacher/am", "teach/student", "tea/stu",
}

additional_status = { "prof", "pa ", "t/s", "teacher/stu" }