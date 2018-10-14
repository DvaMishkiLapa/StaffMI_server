#!bin/sh
cd /site
gunicorn --workers=3 --bind=unix:/site/pms.sock app:app
