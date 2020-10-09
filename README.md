# LevelUp 0.1.0

A web app that pulls Dancesport results from O2CM & Ballroom Comp Express and calulates proficiency points based on three popular proficiency points systems:

    - [Fair Level](http://www.collegiatedancesport.org/fairlevel/)
    - [Amateur Points System](http://www.dcdancesportinferno.com/amateur-points-system/)
    - [USA Dance's proficiency points system](https://usadance.org/general/custom.asp?page=Rules)

Results are updated weekly on Saturday.

## Table Builders
Each table is built/updated individually.

lib -> table_builders
    competitions:
        comp_id, comp_name, date

    events:
        comp_id, heat_id, pro/am/etc. status, age, style, level, number of couples, number of rounds, dances, misc. string(?)

    placements:
        heat_id, placement, competitor_number, couple/lead/follow id

    partnerships:
        partnership_id, lead_id, lead_firstname, lead_lastname, follow_id, follow_firstname, follow_lastname, earliest_record?


## Requirements

    Need to figure out whether running virtual environment and how installing libs will work.

    - Python (version?)

    - Pip? version?

    - Pipenv? version?

    - BeautifulSoup4
        - version?
        - HTML parsing

    - Selenium
        - interacting with o2cm page elements to get full results pages