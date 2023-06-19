#!/bin/bash
cd db
touch gamedata.db
sqlite3 gamedata.db < import-sqlite-script.txt
