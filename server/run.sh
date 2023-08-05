#!/bin/sh
time=$(date "+%Y%m%d-%H%M%S")
filename=$time.txt
python3 -m app.main $1 2>&1 | tee "logs/$filename"