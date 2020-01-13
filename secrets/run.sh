#!/bin/sh
env $(gpg -d secrets.env.gpg | grep -v '^#') ./example.sh