"""
Usage:
    plotter_v2.py (peak|line|euclidean) <id>... --timeunit=<UNIT> [options]

Arguments:
    -t --timeunit=<UNIT>    Time unit of the x axis. Units: day, week, month, year
Options:
    -h --help           Show this screen.
    --hide           Hide the diagram / Don't show the diagram
    -o --out=<file>     Path to output file. You can specify the file format by using the desired file extension (e.g. png, pdf)
    --shift=<direction> Shift the dates of projects [values: left, right]
    --norm              Normalises all y values to be between 0 and 1
    --acc               Accumulate y values
"""
from docopt import docopt
import data_provider as provider
import data_processor as processor
import matplotlib.pyplot as pyplot
import numpy

if __name__ == '__main__':
    args = docopt(__doc__)
    # Validate command line arguments ----------------------------------------------------------------------------------
    valid_timeunits = ["day", "week", "month", "year"]
    if not args['--timeunit'] in valid_timeunits:
        print("Invalid timeunit. Use --help to get more information.")
        exit(1)

    valid_shift_values = ["left", "right", None]
    if not args['--shift'] in valid_shift_values:
        print("Invalid shift value. Use --help to get more information.")
        exit(1)

    # Process command line arguments -----------------------------------------------------------------------------------
    convert_date_functions = {
        "day": provider.DateUtil.date_to_day,
        "week": provider.DateUtil.date_to_week,
        "month": provider.DateUtil.date_to_month,
        "year": provider.DateUtil.date_to_year,
    }

    arg_ids = args['<id>']
    arg_time_unit = args['--timeunit']
    arg_acc = args['--acc']
    arg_norm = args['--norm']
    arg_shift = args['--shift']
    arg_out_file= args['--out']
    arg_hide = args['--hide']

    # Get the data -----------------------------------------------------------------------------------------------------
    data = provider.get_commit_frequencies(arg_ids, convert_date_functions[arg_time_unit])
    
    # Process the data -------------------------------------------------------------------------------------------------
    data = processor.process(data, accumulate=arg_acc, normalise=arg_norm, shift=arg_shift)

    # Plot the specified graph -----------------------------------------------------------------------------------------

    fig, ax = pyplot.subplots()
    plot_fun = ax.plot_date
    if not arg_shift is None:
        plot_fun = ax.plot

    for (idx, row) in enumerate(data):
        plot_fun(row[0], row[1], '-', label=arg_ids[idx])

    if (args['peak']):
        peaks = provider.find_peaks(data)
        for (idx, row) in enumerate(data):
            ups = numpy.where(numpy.array(peaks[idx][1]) == 1)[0]
            downs = numpy.where(numpy.array(peaks[idx][1]) == -1)[0]
            ups_data = (numpy.array(row[0])[ups], numpy.array(row[1])[ups])
            downs_data = (numpy.array(row[0])[downs], numpy.array(row[1])[downs])
            ax.plot(ups_data[0], ups_data[1], '^', label="Up" if idx == 0 else "", color='green')
            ax.plot(downs_data[0], downs_data[1], 'v', label="Down" if idx == 0 else "", color='red')
    elif args['euclidean']:
        pass
    # Adjust title and format ------------------------------------------------------------------------------------------
    pyplot.title('Number of commits over time (' + arg_time_unit + 's)')
    fig.autofmt_xdate()
    pyplot.legend(loc='upper left')
    # Display and save figure ------------------------------------------------------------------------------------------
    if not arg_out_file is None:
        print "Save figure to ", arg_out_file
        pyplot.savefig(arg_out_file)
    if not arg_hide:
        pyplot.show()