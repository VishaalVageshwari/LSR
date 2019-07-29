#!/bin/sh

pkill -f Lsr.py
sleep 2
python3 -u /mnt/c/Users/Vishaal/Desktop/LSR/Lsr.py /mnt/c/Users/Vishaal/Desktop/LSR/configA.txt > configA.out 2>&1 &
python3 -u /mnt/c/Users/Vishaal/Desktop/LSR/Lsr.py /mnt/c/Users/Vishaal/Desktop/LSR/configB.txt > configB.out 2>&1 &
python3 -u /mnt/c/Users/Vishaal/Desktop/LSR/Lsr.py /mnt/c/Users/Vishaal/Desktop/LSR/configC.txt > configC.out 2>&1 &
python3 -u /mnt/c/Users/Vishaal/Desktop/LSR/Lsr.py /mnt/c/Users/Vishaal/Desktop/LSR/configD.txt > configD.out 2>&1 &
python3 -u /mnt/c/Users/Vishaal/Desktop/LSR/Lsr.py /mnt/c/Users/Vishaal/Desktop/LSR/configE.txt > configE.out 2>&1 &
python3 -u /mnt/c/Users/Vishaal/Desktop/LSR/Lsr.py /mnt/c/Users/Vishaal/Desktop/LSR/configF.txt > configF.out 2>&1 &