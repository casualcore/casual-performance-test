#!/bin/bash

for filename in *.py; do
   locust -f $filename --headless
done