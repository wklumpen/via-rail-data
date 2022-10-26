# VIA Rail Data Fetcher
Fetch scheduled and actual arrival times from VIA Rail

This script pulls historical real and actual arrival and departure time from
VIA's public reporting website. For an example of the data format, visit

https://reservia.viarail.ca/tsi/GetTrainStatus.aspx?l=en&TsiCCode=VIA&TsiTrainNumber=78&TrainInstanceDate=2022-10-25

You may have to replace the TrainInstanceDate in the URL with a more recent
date, and the train number with a specified train number.

## Set Up
This script makes use of the Beautiful Soup HTML parser. You will need to install
both this library and Pandas. This can be done with `pip` or with `conda`.

## With `pip`

    pip install beautifulsoup4 pandas

# With `conda`

    conda install -c conda-forge beautifulsoup4 pandas

Usage
-----
To fetch the data you would like, you need to specify both a date range and
a list of trains. You will need to update the following variables in the script

*  `TRAINS` - A list of integers representing train numbers
*  `START_DATE` - A `datetime.date` object with the starting service date
*  `END_DATE` - A `datetime.date` object with the ending service date (not included in the fetch!)

Note that not all times are reported, and this script does no quality checking
on the validity of the data. Post-analysis is required to clean the dataset
to capture missing times or dates.




