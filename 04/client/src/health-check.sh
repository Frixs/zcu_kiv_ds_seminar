#!/bin/bash

if [ $( ps aux | grep -c "client.py") -gt 1 ]; 
then exit 0; 
else exit 1; 
fi
