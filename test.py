#!/usr/bin/python
import reader
import json
import sqlite3

#Read configuration
try:
    with open('./settings.json') as json_data:
        config = json.load(json_data)

    conn = sqlite3.connect(config["Database"])
    c = conn.cursor()
    sql = "INSERT INTO ReadingData VALUES ({0},{1},{2},{3})".format(, amps)
    r = reader.Reader(config)

    r.read(0)
    c.execute(sql.format(r.getLastStart(),0,r.getLastPower(),'NULL'))
    r.read(1)
    c.execute(sql.format(r.getLastStart(),1,r.getLastPower(),'NULL'))
    r.read(2)
    c.execute(sql.format(r.getLastStart(),2,r.getLastPower(),'NULL'))
    r.read(3)
    c.execute(sql.format(r.getLastStart(),3,r.getLastPower(),'NULL'))

    conn.commit()
    conn.close()
except Exception as e:
    print("An error occurred:", e)
