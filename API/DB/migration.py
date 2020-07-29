from mysql import connector
import boto3, sys, mysql

ENDPOINT = "database-1.cqr3wactoekt.us-east-1.rds.amazonaws.com"
PORT = "3306"
REGION="us-east-1"
USR = "dan"
DBNAME="api"

session = boto3.Session(profile_name="dan")
client = boto3.client('rds', region_name=REGION)
token = client.generate_db_auth_token(DBHostname=ENDPOINT, Port=PORT, DBUsername=USR, Region=REGION)

class DataMigration:
    def __init__(self, cnx):
        self.cnx = cnx
    def establishConnection(self):        
        cur = self.cnx.cursor()
        cur.execute("""SELECT now();""")
        res = cur.fetchall()
        return res
    def createTable(self, tableName, colInfo):
        """
        Create a table in mySQL with the specified name.

        Parameters
        ----------
        tableName : (str)
            name of the table to create.
        conInfo : (dict)
            a dictionary containing column names as keys and data types as values.

        Returns
        ----------
        Statement of success if query was successful, error message otherwise.
        """
        cnx = self.cnx
        cur = cnx.cursor()        
        q = f"CREATE TABLE {tableName} (day INT NOT NULL,\
                month VARCHAR(30), year INT NOT NULL, date VARCHAR(100),\
                photoresistor INT NOT NULL, digital_button INT NOT NULL,\
                temp DECIMAL(4, 2), humidity DECIMAL(4, 2));"
        
        try:
            cur.execute(q)
            return f"Table {tableName} was created successfully with the following columns and data types: {colInfo}."            
        except:
            return "Table already exists."

    def insertData(self, q):
        """
        Insert data into mySQL table.
        """

conn =  connector.connect(host=ENDPOINT, user=USR, passwd= "Dpm#1217", port=PORT, database=DBNAME)
db = DataMigration(conn)    
_ =db.establishConnection()

# CREATE TABLE
cols = {"day" : "INT NOT NULL", "month" : "VARCHAR(30)", "year":"INT NOT NULL", "date" : "VARCHAR(100)", 
        "photoresistor":"INT NOT NULL", "digital_button": "INT NOT NULL", "temp":"INT NOT NULL", "humidity":"INT NOT NULL"}  
print(db.createTable(tableName = "readings", colInfo = cols))

