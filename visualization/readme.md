# Service plotting

svcplot.py is a simple tool for visualizing response times and througputs based on data gathered from remote casual domains

Current features:
- Show data from multiple domains, but restricted to a single service name
- Custom sampling frequency
- Display: average response time
- Display: throughput 

# Install

Use virtual environment (recommended) and install prerequisites

    %> source <venv directory>/bin/activate.sh
    %> pip install -r requirements.txt

# Usage

    %> python3 svcplot.py -s <servicename> -r <resampling frequency> zipfile
