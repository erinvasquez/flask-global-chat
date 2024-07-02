#!/bin/bash
source /home/erin_vasquez/flask-global-chat/fresnoenv/bin/activate
exec /home/erin_vasquez/flask-global-chat/fresnoenv/bin/python /home/erin_vasquez/flask-global-chat/app.py > /home/erin_vasquez/flask-global-chat/app.log 2>&1
