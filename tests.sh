#!/bin/sh

for file in tests/*.input; do
    echo Running test $file
    ./server.py < $file > output
    diff -w output tests/`basename $file .input`.output
    if [ $? == 0 ]; then
        echo    Passed
    else
        echo    Failed
    fi
done
