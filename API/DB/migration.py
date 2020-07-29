from mysql import connector
import boto3, sys, mysql

ENDPOINT = "ls-dec1d5133329eca3f8522daadb38ee487e90a1eb.c4bmr14mp8ah.us-east-1.rds.amazonaws.com"
PORT = "3306"
REGION="us-east-1"
USR = "dbmasteruser"
DBNAME="mysql"
passwd = "11111111" # password since db is public

client = boto3.client('rds')
# token = client.generate_db_auth_token(DBHostname=ENDPOINT, Port=PORT, DBUsername=USR, Region= REGION) # passwd from AWS

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
        cur.execute(q)
        res = cur.fetchall()
        return f"Table {tableName} was created successfully with the following columns and data types: {colInfo}."

    def insertData(self, q):
        """
        Insert data into mySQL table.
        """


if __name__ == "__main__":
    conn =  connector.connect(host=ENDPOINT, user=USR, passwd= passwd, port=PORT, database=DBNAME)
    db = DataMigration(conn)
    cols = {"day" : "INT NOT NULL", "month" : "VARCHAR(30)", "year":"INT NOT NULL", "date" : "VARCHAR(100)", 
            "photoresistor":"INT NOT NULL", "digital_button": "INT NOT NULL", "temp":"INT NOT NULL", "humidity":"INT NOT NULL"}  
    db.createTable(tableName = "readings", colInfo = cols)
    # print(``' '.join([list(cols.keys())[i]` + ' ' +list(cols.values())[i]+',' for i in range(len(cols.keys()))]))


