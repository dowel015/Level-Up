#!/usr/bin/python
import mysql.connector
import os

def getDB():

    # connect to db
    # MYSQL Connection class https://dev.mysql.com/doc/connector-python/en/connector-python-api-mysql-connector.html
    mydb = mysql.connector.connect(
        host="mysql.danoc14.dreamhosters.com",
        user="danoc14dreamhost",
        passwd="QPdwbeL*",
        database="danoc14_dreamhosters_com"
    )

    return mydb