#!/bin/bash

sqlite3 gamedata < import-sqlite-script.txt
# sqlite3 'DROP TABLE IF EXISTS cities; CREATE TABLE cities("name" TEXT NOT NULL, "population" TEXT NOT NULL); .mode csv .import city.csv'


