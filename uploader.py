import mysql.connector

cnx = mysql.connector.connect(user='EnergyMonitor', password='Energy4All!',
                              host='192.168.1.2',
                              database='EnergyMonitor')
cnx.close()
