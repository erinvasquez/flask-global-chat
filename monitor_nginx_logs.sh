#!/bin/bash

# Tail the Nginx error and access logs
tail -f /var/log/nginx/error.log /var/log/nginx/access.log
