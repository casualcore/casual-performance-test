import os
from pathlib import Path
import time
from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import ConsoleMetricExporter, PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter

# todo: handle shutdown gracefully
# todo: handle log rotation

def read_file(path: Path):
    now = int(time.time_ns() / 1000)
    with path.open('r') as file:
        while True:
            lines = file.readlines(10 * 1024)
            # print(f"read {len(lines)} lines")

            if len(lines) == 0:
                # print("end of file reached, sleeping...")
                time.sleep(0.1)
                continue

            metrics = []
            for line in lines:
                if len(line) > 0:
                    # split line into columns
                    metric = line.split('|')
                    if float(metric[6]) < now:
                        # print("skipping metric: ", line)
                        continue
                    metrics.append(metric)
            
            # print(f"returning block of {len(metrics)} metrics")
            yield metrics


def create_metrics(filepath: str):
    # http_exporter = OTLPMetricExporter()
    metric_reader = PeriodicExportingMetricReader(ConsoleMetricExporter(), export_interval_millis=5000, export_timeout_millis=1000)
    provider = MeterProvider(metric_readers=[metric_reader])
    meter = provider.get_meter("casual.service")

    # pseudo exponential buckets
    predefined_buckets = [ 0.001, 0.002, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1, 2, 5, 10, 20, 100]

    duration_histogram = meter.create_histogram("casual.service.duration", "s", "Service duration", explicit_bucket_boundaries_advisory=predefined_buckets)
    # pending_histogram = meter.create_histogram("casual.service.duration", "s", "Service duration")

    path = Path(filepath)
    while not path.exists():
        time.sleep(0.3)

    while True:
        for block in read_file(path):
            for metric in block:
                # print("metric: ", metric)
                duration = (int(metric[6]) - int(metric[5])) / 1e6
                duration_histogram.record(duration, {"casual.service.name": metric[0], "casual.service.result": metric[8], "casual.service.order": metric[9]})


def main():
    domain_home = os.environ["CASUAL_DOMAIN_HOME"]
    create_metrics(f"{domain_home}/logs/statistics.log")


if __name__ == "__main__":
    main()
