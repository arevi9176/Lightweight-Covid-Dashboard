#!/usr/bin/env python3
#
# LCD - Lightweight Covid Dashboard
#
# 28.03.20 (v0.1.0) - initial version
# 02.04.20 (v0.2.0) - added dataframe cache and view 'Average percentage increase in the last seven days'
# 03.04.20 (v0.2.1) - changed 'Average percentage increase' to 'Average growth rate'
#
__version__ = "v0.2.1"

import pandas
import urllib.request

from flask import Flask, render_template, request
from time import time as time
from lcd_cnpop import country_population as cp
from math import log10 as log10

CONFIRMED_GLOBAL_URL = "https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv"
CONFIRMED_GLOBAL_FILE = "time_series_covid19_confirmed_global.csv"
DEATHS_GLOBAL_URL = "https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv"
DEATHS_GLOBAL_FILE = "time_series_covid19_deaths_global.csv"

class DataFrameCache:
    def __init__(self, filepath, url):
        self.filepath = filepath
        self.url = url
        self.df = None
        self.last_update_time = 0.0

    def fetch(self):
        """Return cached dataframe if last download is younger than 1h,
           else download from Github and parse into dataframe.
        """
        if time() - self.last_update_time > 2 * 3600:
            urllib.request.urlretrieve(self.url, self.filepath)
            self.df = pandas.read_csv(self.filepath)
            self.last_update_time = time()
        return self.df

def convert_all_floats_to_ints(df):
    """Converts all float numbers to int numbers in a given dataframe.
    """    
    float_col = df.select_dtypes(include=['float64']) # This will select float columns only
    for col in float_col.columns.values:
       df[col] = df[col].astype('int64')
    return df

def compute_abs_dataframe(dfc, days, cases, country):
    """Compute dataframe with absolute numbers from cached dataframe for the last <days> days.
       Latest timeseries must have at least <cases> cases.
    """
    # fetch cached dataframe
    df = dfc.fetch()
    # reduce dataframe to 1st column (countries) and last <days> days column
    df = df.iloc[:, [1] + list(range(-days,0))]
    # condense dataframe to only one country per row
    last_columns = list(df.columns)[-days:]
    col_dict = {}
    for col in last_columns:
        col_dict[col] = 'sum'
    df = df.groupby("Country/Region").agg(col_dict)
    # sort dataframe by last column
    df = df.sort_values(df.columns[-1], ascending = False)
    # reduce dataframe to min <cases> in last coloumn
    df = df[df[last_columns[-1]] >= cases]
    # 
    if country != "":
        last_column_name = df.columns[-1]
        try:
            last_cases_at_position = df.at[country, last_column_name]
        except KeyError:
            print("Country not found")
        else:
            df = df.loc[df[last_column_name] <= last_cases_at_position]
    return df

def compute_rel_dataframe(df_abs):
    """Compute dataframe with relative numbers (%) from dataframe with absolute numbers.
       Relative numbers (percent values) are used for length of bargraphs-
    """
    max_value = df_abs.max().max()
    df_rel = df_abs.div(max_value).multiply(100).round(1)
    return df_rel

def compute_dif_dataframe(df, country):
    """Compute dataframe by substraction each col from prev col.
       First col becomes NaN and is therefore dropped.
    """
    df_dif = df.diff(axis=1)
    df_dif = df_dif.sort_values(df_dif.columns[len(df_dif.columns) - 1], ascending = False)
    df_dif = df_dif.drop(df_dif.columns[0], axis=1)
    if country != "":
            last_column_name = df_dif.columns[-1]
            try:
                last_cases_at_position = df_dif.at[country, last_column_name]
            except KeyError:
                print("Country not found")
            else:
                df_dif = df_dif.loc[df_dif[last_column_name] <= last_cases_at_position]
    df_dif = convert_all_floats_to_ints(df_dif)
    return(df_dif)

def add_pop_to_country_names(absval, info_type):
    """absval: [['US', 83836, 101657, 121478], ['Italy', 80589, 86498, 92472]]
       resval: [['US', ': 327 mio residents; 1,533 residents per case', 83836, 101657, 121478], ['Italy', ': 60 mio residents; 546 residents per case', 80589, 86498, 92472, 97689, 101739, 105792, 110574]]
    """
    resval = []
    for entry in absval:
        country = entry[0]
        country_pop = get_country_population(country)
        if country_pop > 0:
            if info_type == "ONLY_POPULATION":
                country_info = ": {:,.0f} mio residents".format(country_pop / 1000000)
            else:
                latest_confirmed_cases = entry[-1]
                residents_per_case = int(country_pop / latest_confirmed_cases)
                country_info = ": {:,.0f} mio residents; {:,} residents per case".format(
                    country_pop / 1000000,
                    residents_per_case)
        else:
            country_info = ": n/a"
        resval.append([country] + [country_info] + entry[1:])
    return(resval)

def compute_abs_values(dfc, days, cases, country):
    df_abs = compute_abs_dataframe(dfc, days, cases, country)
    df_rel = compute_rel_dataframe(df_abs)
    absval = df_abs.reset_index().values.tolist()
    info_type = "ONLY_POPULATION" if "death" in dfc.filepath else "FULL"
    absval = add_pop_to_country_names(absval, info_type)
    relval = df_rel.reset_index().values.tolist()
    datval = list(df_abs.columns)
    return absval, relval, datval

def compute_dif_values(dfc, days, cases, country):
    df_abs = compute_abs_dataframe(dfc, days, cases, "")
    df_dif = compute_dif_dataframe(df_abs, country)
    df_rel = compute_rel_dataframe(df_dif)
    absval = df_dif.reset_index().values.tolist()
    absval = add_pop_to_country_names(absval, "ONLY_POPULATION")    
    relval = df_rel.reset_index().values.tolist()
    datval = list(df_abs.columns)
    return absval, relval, datval

def get_country_population(country):
    try:
        pop = cp[country][1]
    except KeyError:
        pop = 0
    return pop

dfc_confirmed = DataFrameCache(CONFIRMED_GLOBAL_FILE, CONFIRMED_GLOBAL_URL)
dfc_deaths = DataFrameCache(DEATHS_GLOBAL_FILE, DEATHS_GLOBAL_URL) 

app = Flask(__name__)

@app.route("/confirmed/")
def confirmed():
    days = request.args.get('days', default=7, type=int)
    cases = request.args.get('cases', default=2000, type=int)
    country = request.args.get('country', default="", type=str)    
    absval, relval, datval = compute_abs_values(dfc_confirmed, days, cases, country)
    header = ["Total Confirmed Cases (" + datval[0] + ' - ' + datval[-1] + ').', days, cases, "cases", "1", country, __version__]
    return render_template('lcd.html', title='confirmed', absval=absval, relval=relval, header=header)

@app.route("/confirmed_dif/")
def confirmed_dif():
    days = request.args.get('days', default=7, type=int)
    cases = request.args.get('cases', default=2000, type=int)
    country = request.args.get('country', default="", type=str)
    absval, relval, datval = compute_dif_values(dfc_confirmed, days, cases, country)
    header = ["Daily New Cases (" + datval[0] + ' - ' + datval[-1] + ').', days, cases, "cases", "1", country, __version__]
    return render_template('lcd.html', title='confirmed (differential)', absval=absval, relval=relval, header=header)

@app.route("/deaths/")
def deaths():
    days = request.args.get('days', default=7, type=int)
    cases = request.args.get('cases', default=100, type=int)
    country = request.args.get('country', default="", type=str)
    absval, relval, datval = compute_abs_values(dfc_deaths, days, cases, country)
    header = ["Total Deaths (" + datval[0] + ' - ' + datval[-1] + ').', days, cases, "deaths", "1", country, __version__]
    return render_template('lcd.html', title='deaths', absval=absval, relval=relval, header=header)

@app.route("/deaths_dif/")
def deaths_dif():
    days = request.args.get('days', default=7, type=int)
    cases = request.args.get('cases', default=100, type=int)
    country = request.args.get('country', default="", type=str)
    absval, relval, datval = compute_dif_values(dfc_deaths, days, cases, country)
    header = ["Daily New Deaths (" + datval[0] + ' - ' + datval[-1] + ').', days, cases, "deaths", "1", country, __version__]
    return render_template('lcd.html', title='deaths (differential)', absval=absval, relval=relval, header=header)

def append_double_rates(df):
    """Last col of <df> contains percentage increase.
       Compute double rates from percentage increase and append as new column
    """
    def f(x):
        try:
            fx = round(log10(2) / log10(1 + x / 100), 1)
        except ZeroDivisionError:
            fx = 0
        return fx
    double_rates = [f(x) for x in df[0]]
    df['double_rates'] = double_rates
    return df

@app.route("/av_growth_rate/")
def average_percentage_increase():
    days = request.args.get('days', default=7, type=int)
    cases = request.args.get('cases', default=1000, type=int)
    print("cases:", cases)
    df_abs = compute_abs_dataframe(dfc_confirmed, 8, cases, "")
    df_abs = df_abs.pct_change(axis=1)
    df_abs = df_abs.drop(df_abs.columns[0], axis=1)
    # compute growth rate change, sorted
    df_abs = df_abs.mean(axis=1)
    df_abs = df_abs.multiply(100).round(1)
    df_rel = compute_rel_dataframe(df_abs)
    df_rel = df_rel.reset_index()
    df_rel = df_rel.sort_values(df_rel.columns[-1], ascending = False)
    df_abs = df_abs.reset_index()
    df_abs = df_abs.sort_values(df_abs.columns[-1], ascending = False)
    df_abs = append_double_rates(df_abs)
    absval = df_abs.values.tolist()
    relval = df_rel.values.tolist()
    header = ["", days, cases, "", "2", "", __version__]
    return render_template('lcd.html', title='Average growth rate in the last seven days', absval=absval, relval=relval, header=header)

if __name__ == '__main__':
    #app.run(debug=True)
    app.run(host='0.0.0.0', debug=True)