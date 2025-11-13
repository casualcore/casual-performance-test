#!/usr/bin/env python3

import importlib.util
import sys
import yaml


# load/import python testcase file
if (spec := importlib.util.spec_from_file_location('testcase', '/home/casual/python/testcase.py')) is not None:
    testcase = importlib.util.module_from_spec(spec)
    sys.modules['testcase'] = testcase
    spec.loader.exec_module(testcase)

with open('/home/casual/test/parameters.yaml') as parameter_file:
    parameters = yaml.safe_load(parameter_file)
    testcase.test_setup()
    testcase.test_run(parameters)
    testcase.test_shutdown()
