# Casual performance test

1. Clone repo
2. Run all tests with `run.sh path/to/output/filename`

The output is stored in a zip archive containing metrics from locust, casual and telegraf.
`path/to/output/filename.zip`

---
## Configuration

- host2 and host3 needs to be set on the machine running the tests.
- Each test case has a locust config file.
- Each test case has its own domain configured, and some tests uses multiple domains.
- Each domain is configured with its own user, cas201, cas202, cas303...

Example cas`2`0`1`:
- `2` corresponds to the host
- `1` corresponds to the test case.

### Telegraf

We use telegraf to gather system information from the machines.

A config file for telegraf must be found on each machine.

---

## Visualization

The output from locust can be visualized with `plot.py output1.zip output2.zip ... outputN.zip`

The output from remote casual domains can be visualized with [`svcplot.py`](visualization/readme.md)

No visualization for other metrics yet.