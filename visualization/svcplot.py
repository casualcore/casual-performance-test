import argparse
import re
import pandas as pd
from zipfile import ZipFile
from matplotlib import pyplot

column_names=[
    'service',
    'parent',
    'pid',
    'execution',
    'trid',
    'start',
    'end',
    'pending',
    'code',
    'order'
]


def loadStatistics(zip, filename):
    series = pd.read_table(zip.open(filename), sep='|', header=None, names=column_names, usecols=['service','start','end','pending','code','order'])
    series['response_time'] = (series['end'] - series['start']) / 1000.0
    series = series.drop(columns='end')
    series['start'] = pd.to_datetime(series['start'], unit='us')
    series = series.set_index('start')
    return series


def getServiceData(series, serviceName):
    return series.loc[lambda x: x['service'] == serviceName]


def plotSeries(services, resampling_frequency):
        plot_row = 0
        fig, axes = pyplot.subplots(2 * len(services),1, sharex=True)
        for title, series in services:
            if len(series) > 0:
                series['response_time'].resample(resampling_frequency).mean().plot(title=f'{title} - Avg response time ({resampling_frequency})',ax=axes[plot_row])
                series['response_time'].resample(resampling_frequency).count().plot(title=f'{title} - Throughput ({resampling_frequency})',ax=axes[plot_row + 1])
                plot_row = plot_row + 2

        if plot_row > 0:
            pyplot.show()


def getStatisticsInfo(zip):
    return list(filter(lambda info: info.filename.endswith("statistics.log"), zip.infolist()))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('zipfile')
    parser.add_argument('-s', '--service', default='casual/example/echo', help="Name of service to plot")
    parser.add_argument('-r', '--resample', default='15s', help="Use resampling frequency. Specified as a timedelta:  '30s', '2min' etc.")

    args = parser.parse_args()

    pd.options.mode.copy_on_write = True

    with ZipFile( args.zipfile, "r") as zip:
        statistics = getStatisticsInfo(zip)
        service_series = []
        for statfile in statistics:
            # Get domainname from filename
            p = re.compile("_([^_]+)_statistics.log")
            match = p.search(statfile.filename)
            domainName = match.group(1) if match else "<unknown>"

            series = loadStatistics(zip, statfile.filename)
            svc = getServiceData(series, args.service)
            if len(svc) > 0:
                service_series.append((f'{domainName} - {args.service}', svc))

    if len(service_series) > 0:
        plotSeries(service_series, resampling_frequency=args.resample)
    else:
        print("No matching metrics found.")


if __name__ == '__main__':
    main()

