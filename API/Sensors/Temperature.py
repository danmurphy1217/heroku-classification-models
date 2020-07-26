from Sensors.Photoresistor import Photoresistor
import pandas as pd 
import numpy as np
import mysql, mysql.connector as connector
class Temperature(Photoresistor):
    def __init__(self, connection):
        self.connection = connection
        