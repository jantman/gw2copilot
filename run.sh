#!/bin/bash

WINEPID=$(pgrep wineserver)
cd '/home/jantman/.PlayOnLinux/wineprefix/guildwars2/drive_c'
/home/jantman/.PlayOnLinux/wine/linux-x86/1.7.49-staging/bin/wine Python27/python.exe readmumble.py
