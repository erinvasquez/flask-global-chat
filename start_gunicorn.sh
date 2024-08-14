#!/bin/bash

/home/erin_vasquez/flask-global-chat/fresnoenv/bin/gunicorn --workers 3 --bind unix:gunicorn.sock -m 007 wsgi:app &
sleep 5
sudo chown www-data:www-data /home/erin_vasquez/flask-global-chat/gunicorn.sock
sudo chmod 660 /home/erin_vasquez/flask-global-chat/gunicorn.sock
