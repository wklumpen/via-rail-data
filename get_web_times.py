import urllib.request
import urllib.error
from datetime import datetime, date, timedelta

from bs4 import BeautifulSoup
import pandas as pd

# This is the list of ALL the trains.
"""TRAINS = [
    48,87,84,88,72,85,71,97,73,83,75,79,70,76,98,78,82,2,80,81,50,52,40,42,644,
    44,46,646,54,26,60,62,28,64,38,66,68,668,61,63,65,67,69,669,22,24,34,41,43,
    51,45,53,47,645,55,647,59,33,35,635,37,39,651,655,643,15,14,20,25,29,622,
    624,633,637,639,641,650
]"""
# Here you can specify specific trains to look up. Not all trins are running on
# a given date or have very good data.
TRAINS = [70, 71, 72, 75, 76, 78, 79]
# The starting and ending date to analyze (non-inclusive of the end date). 
# Replace with Year, Month, and Date (no leading zeroes)
START_DATE = date(2022, 10, 23)
END_DATE = date(2022, 10, 26)


def daterange(start_date, end_date):
    """An iterator over dates

    This iterator function will return a date over the range start_date
    to end_date, not inclusive of the end date.

    Parameters
    ----------
    start_date : `datetime.date`
        The start date to iterate from
    end_date : `datetime.date`
        The end date (non-inclusive) to iterate to

    Yields
    ------
    `datetime.date`
        The next date in the iteration
    """
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(n)

def get_times(train_number, day):
    """Get all arrival and departure times for a given train on a given day

    Parameters
    ----------
    train_number : int
        The train number to fetch
    day : `datetime.date`
        The service date to look up
    """
    
    # Assemble header data which makes the code less suceptible to errors
    user_agent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'
    values = {'name': 'Hawkeye Pierce',
          'location': '4077 MASH',
          'language': 'Python' }
    headers = { 'User-Agent' : user_agent }
    data = urllib.parse.urlencode(values)
    data = data.encode('ascii')
    day_str = day.strftime("%Y-%m-%d")

    # Let the user know what's going on
    print("Fetching train {} times for {}.".format(train_number, day_str))

    # If you need to get around a proxy, you can specify the proxy ports here
    # to help make it easier.
    # Uncomment the next two variable assignments (proxy_support and opener)
    # And comment the simpler opener assignment following these two
    # proxy_support = urllib.request.ProxyHandler({
    #     'http': '<your_http_proxy_ip:port>',
    #     'https': '<your_https_proxy_ip:port>'
    #     })
    # opener = urllib.request.build_opener(proxy_supporyt)
    
    # If you used a proxy above, comment this line out
    opener = urllib.request.build_opener()

    urllib.request.install_opener(opener)
    url = r'https://reservia.viarail.ca/tsi/GetTrainStatus.aspx?l=en&TsiCCode=VIA&TsiTrainNumber={}&TrainInstanceDate={}'.format(train_number, day_str)
    req = urllib.request.Request(url, data, headers)
    
    # Fetch the webpage and read it into the parser
    with urllib.request.urlopen(req) as u:
        data = u.read()
        soup = BeautifulSoup(data, 'html.parser')
        links = soup.find_all('a')

    first = False
    first_real = False

    data_out = {
        'train': [],
        'station': [],
        'schedArr': [],
        'realArr': [],
        'schedDep': [],
        'realDep': []
    }
    # Iterate through the items and parse the code on the webpage to extract
    # the data we need
    for link in links:
        station = link.text
        # Fetch the station row
        row = link.parent.parent
        # Fetch all the cells in that row
        cols = row.find_all('td', recursive=False)

        # Column 2 is the scheduled arrival and departure times
        for time_cols in cols[2]:
            arr_dep = [c.text for c in time_cols.children] # Arrival and departure information
            if len(arr_dep) == 1:
                # Account for a departure having no arrival time
                if not first:
                    arr_dep = [None, arr_dep[0]]
                    first = True
                # Otherwise we're at the end of the list and therefore have an arrival but no departure
                else:
                    arr_dep = [arr_dep[0], None]
            # Either way we tack on a station name
            arr_dep.insert(0, station)

        # Real time data is stored in this column        
        for real_time_cols in cols[4]:
            real_arr_dep = [c.text for c in real_time_cols.children] # Real time arrival and departure information
            if len(real_arr_dep) == 1:
                if not first_real:
                    real_arr_dep = [None, real_arr_dep[0]]
                    first_real = True
                else:
                    real_arr_dep = [real_arr_dep[0], None]

        arr_dep.extend(real_arr_dep)
        for idx, t in enumerate(arr_dep):
            if t == '\xa0' or t == '':
                arr_dep[idx] = None

        # Fix some datetime stuff
        for i in range(1,5):
            if arr_dep[i]:
                time = datetime.strptime(arr_dep[i], "%H:%M")
                arr_dep[i] = datetime.combine(day, time.time())

        data_out['train'].append(train_number)
        data_out['station'].append(arr_dep[0])
        data_out['schedArr'].append(arr_dep[1])
        data_out['schedDep'].append(arr_dep[2])
        data_out['realArr'].append(arr_dep[3])
        data_out['realDep'].append(arr_dep[4])

    return pd.DataFrame(data_out)

if __name__ == "__main__":
    print(f"You are looking for train times for {len(TRAINS)} trains: {', '.join([str(t) for t in TRAINS])}")
    print(f"For the dates from {START_DATE} up to but not including {END_DATE}")
    confirm = input(f"Enter y to proceed, n to exit: ")
    if confirm.lower() == 'y':
        dfs = []
        for t_n in TRAINS:
            for single_date in daterange(START_DATE, END_DATE):
                dfs.append(get_times(t_n, single_date))
        out_df = pd.concat(dfs, axis='index')
        stations = pd.read_csv('station_names.csv')
        out_df = pd.merge(out_df, stations, on='station')

        # Write to file
        out_df[["train", "station", "pretty_name", "schedArr", "realArr", "schedDep", "realDep"]].to_csv(
            f"via_data_{START_DATE.strftime('%Y-%m-%d')}_{END_DATE.strftime('%Y-%m-%d')}.csv", 
            index=False
        )
    else:
        print('Did not receive confirmation. Exiting...')