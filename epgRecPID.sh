#!/bin/bash
ps aux | grep python | grep epgRec | tr -s " " | cut -d " " -f2
