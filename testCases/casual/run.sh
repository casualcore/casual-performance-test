#!/bin/bash

for filename in *.conf; do
   locust --config $filename;
done