import sqlite3

# create database
con = sqlite3.connect("../database/stolenVehiclesDatabase.db")

# create police record database
## will hold details about the stolen vehicle
con.execute("""
CREATE TABLE IF NOT EXISTS STOLEN_VEHICLE(
    SV_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    TYPE TEXT NOT NULL,
    LICENSE_PLATE_NUMBER TEXT NOT NULL,
    COLOR TEXT NOT NULL,
    TIME_STOLEN INTEGER NOT NULL
);""")

## will hold details about the stolen vehicle incident report
con.execute("""
CREATE TABLE IF NOT EXISTS INCIDENT_REPORT(
    SV_ID INTEGER NOT NULL,
    OFFICER_ID INTEGER NOT NULL,
    TIME_FILED INTEGER NOT NULL,
    FOREIGN KEY (SV_ID) REFERENCES STOLEN_VEHICLE(SV_ID),
    FOREIGN KEY (OFFICER_ID) REFERENCES OFFICER(OFFICER_ID),
    PRIMARY KEY (SV_ID, OFFICER_ID),
);""")

## will hold details about the officer noting the stolen vehicle incident report
con.execute("""
CREATE TABLE IF NOT EXISTS OFFICER(
    OFFICER_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    NAME TEXT NOT NULL,
    DISTICT TEXT NOT NULL,
);""")


# Table to hold suspected targets when caught
## POSSIBLE_SV_ID is a string of possible stolen vehicle id (see STOLEN_VEHICLE<SV_ID>). String is joined by ';'.
con.execute("""
CREATE TABLE IF NOT EXISTS SUSPECT(
    SUSPECT_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    POSSIBLE_SV_ID TEXT NOT NULL,
    CAMERA_ID INTEGER NOT NULL,
    TIME_CAUGHT INTEGER NOT NULL,
    FOREIGN KEY (CAMERA_ID) REFERENCES CAMERA(CAMERA_ID),
);""")

# Table to hold camera details
con.execute("""
CREATE TABLE IF NOT EXISTS CAMERA(
    CAMERA_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    MODEL_NUMBER TEXT,
    TIME_INSTALLED INTEGER NOT NULL,
    LOCATION_X REAL NOT NULL,
    LOCATION_Y REAL NOT NULL,
    LOCATION_NAME TEXT NULL,
);""")

# Table to hold permission details
# camera persmission --> allows hardware access (can restrict to write only access)
con.execute("""
CREATE TABLE IF NOT EXISTS CAMERA_PERMISSION(
    CAMERA_ID INTEGER PRIMARY KEY NOT NULL,
    API TEXT NOT NULL,
    FOREIGN KEY (CAMERA_ID) REFERENCES CAMERA(CAMERA_ID),
);""")
# officer persmission --> allows officer/personel access (can permit read/write/delete access)
con.execute("""
CREATE TABLE IF NOT EXISTS OFFICER_PERMISSION(
    OFFICER_ID INTEGER PRIMARY KEY NOT NULL,
    API TEXT NOT NULL,
    FOREIGN KEY (OFFICER_ID) REFERENCES OFFICER(OFFICER_ID),
);""")

# officer login --> allows officer/personel app login
con.execute("""
CREATE TABLE IF NOT EXISTS OFFICER_PERMISSION(
    OFFICER_ID INTEGER PRIMARY KEY NOT NULL,
    API TEXT NOT NULL,
    FOREIGN KEY (OFFICER_ID) REFERENCES OFFICER(OFFICER_ID),
    FOREIGN KEY (OFFICER_ID) REFERENCES OFFICER_PERMISSION(OFFICER_ID),
);""")

# commit changes
con.commit()
# close connection
con.close()