#!/bin/bash

if [ -n "$1" ]; then
   for filename in *.conf; do
      locust --config $filename --csv $HOME/testResults/${filename%.*};

   done
   zip -r -j $1.zip $HOME/testResults;
else
   echo "Error: Enter output filename."
fi
