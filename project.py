import mysql.connector

def open_connection:
    '''Open connection to database cs122a using the provided autograder credentials'''
    return mysql.connector.connect(
        user='test', 
        password='password', 
        database='cs122a'
    )
