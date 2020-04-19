#!/usr/bin/env python3
#
# LCD - Lightweight Covid Dashboard
# 28.03.20 (v0.1.0) - initial version
# 02.04.20 (v0.2.0) - added dataframe cache and view 'Average percentage increase in the last seven days'
# 03.04.20 (v0.2.1) - changed 'Average percentage increase' to 'Average growth rate'
# 15.04.20 (v0.3.0) - totally refactored and some bug fixes
# 19.04.20 (v0.4.0) - added trend in view 'Average growth rate in the last seven days'
#
__version__ = "v0.4.0"

import pandas
import urllib.request

from flask import Flask, render_template, request
from time import time as time
from lcd_cnpop import get_country_population
from math import log10, isinf, isnan

CONFIRMED_GLOBAL_URL = "https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv"
CONFIRMED_GLOBAL_FILE = "time_series_covid19_confirmed_global.csv"
DEATHS_GLOBAL_URL = "https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv"
DEATHS_GLOBAL_FILE = "time_series_covid19_deaths_global.csv"
RECOVERED_GLOBAL_URL = "https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv"
RECOVERED_GLOBAL_FILE = "time_series_covid19_recovered_global.csv"

class CovidData:
    def __init__(self, filepath, url):
        self.filepath = filepath
        self.url = url
        self.df = None
        self.df_abs = None
        self.df_dif = None
        self.last_update_time = 0.0
    
    def _insert_pop_column(self, df):
        '''Insert population column in mn at pos 0 in dataframe.'''
        population = []
        countries = list(df.index.values)
        for country in countries:
            population.append(get_country_population(country))
        df.insert(0, 'Population', population)
        return df

    def _insert_residents_per_case_column(self, df):
        '''
        Insert residents per case column at pos 1 in dataframe.
        Population column must exist!
        '''
        residents_per_case = []
        populations = list(df['Population'])
        latest_cases = list(df[df.columns[-1]])
        for po, lc in zip(populations, latest_cases):
            try:
                residents_per_case.append(round(po * 1000000 / lc))
            except ZeroDivisionError:
                residents_per_case.append(0)
        df.insert(1, 'Residents per case', residents_per_case)
        return df

    def _insert_trend_column(self, df, distance):
        '''
        Insert trend column at pos 2 in dataframe.
        Trend means percentage rate of increase of two consecutive periods described by <distance> in days.
        '''
        diff1 = df[df.columns[-1]] - df[df.columns[-(1 + distance)]]
        diff2 = df[df.columns[-(1 + distance)]] - df[df.columns[-(1 + 2 * distance)]]
        quot = diff1 / diff2
        quot = -(1 - quot) * 100
        ql = [round(x) if not (isinf(x) or isnan(x)) else "n/a at this time" for x in list(quot)]
        df.insert(2, 'Trend', ql)
        return df

    def _drop_rows_based_on_unique_indicis(self, df_source, df_target):
        '''Drop every row in df_target where the row index is not contained in df_source'''
        set_of_source_indicis = set(df_source.index)
        set_of_target_indicis = set(df_target.index)
        list_of_indicis_in_target_but_not_in_source = [i for i in set_of_target_indicis if i not in set_of_source_indicis]
        df = df_target.drop(list_of_indicis_in_target_but_not_in_source)
        return df

    def _convert_all_floats_to_ints(self, df):
        '''Convert all float numbers to int numbers in a given dataframe.'''    
        float_col = df.select_dtypes(include=['float64']) # this will select float columns only
        for col in float_col.columns.values:
            df[col] = df[col].astype('int64')
        return df

    def _condense_and_sort_dataframe(self, df):
        '''Condense dataframe to only one country per row and sort by last column.'''
        date_columns = list(df.columns)[1:]
        col_dict = {}
        for col in date_columns: col_dict[col] = 'sum'
        df = df.groupby("Country/Region").agg(col_dict)
        df = df.sort_values(df.columns[-1], ascending = False)
        return df

    def _compute_rel_dataframe(self, df):
        '''
        Compute dataframe with relative numbers (%) from dataframe with absolute numbers.
        Relative numbers (percent values) are used for length of bargraphs.
        Negative numbers are set to zero!
        '''
        residents_per_case = list(df['Residents per case'])                     # save column
        population = list(df['Population'])                                     # save column
        trend = list(df['Trend'])                                               # save column
        df_tmp = df.drop(['Population','Residents per case', 'Trend'], axis=1)  # delete columns from dataframe
        max_value = df_tmp.max().max()                                          # compute max value
        df_rel = df_tmp.div(max_value).multiply(100).round(1)                   # compute relative values
        df_rel[df_rel < 0] = 0                                                  # set negative numbers to 0
        df_rel.insert(0, 'Population', population)                              # restore column
        df_rel.insert(1, 'Residents per case', residents_per_case)              # restore column
        df_rel.insert(2, 'Trend', trend)                                        # restore column        
        return df_rel

    def _compute_abs_dataframe(self):
        df_abs = pandas.read_csv(self.filepath)
        df_abs = df_abs.drop(["Province/State", "Lat", "Long"], axis=1)
        df_abs = self._condense_and_sort_dataframe(df_abs)
        return df_abs

    def _compute_dif_dataframe(self):
        '''
        Compute differential dataframe by substraction each col from prev col.

        First col becomes NaN and is therefore dropped.
        Sort by last column.
        '''
        df_dif = self.df_abs.diff(axis=1)
        df_dif = df_dif.sort_values(df_dif.columns[-1], ascending = False)
        df_dif = df_dif.drop(df_dif.columns[0], axis=1)
        df_dif = self._convert_all_floats_to_ints(df_dif)
        return df_dif

    def _compute_agr_dataframe(self, df):
        '''Compute dataframe with average growth rate, sorted by last column.'''
        residents_per_case = list(df['Residents per case'])                     # save column
        population = list(df['Population'])                                     # save column
        trend = list(df['Trend'])                                               # save column
        df_tmp = df.drop(['Population','Residents per case', 'Trend'], axis=1)  # delete columns from dataframe
        df_agr = df_tmp.pct_change(axis=1)                                      # compute percentage change
        df_agr = df_agr.drop(df_agr.columns[0], axis=1)                         # first column becomes NaN -> drop
        si_pct = df_agr.mean(axis=1)                                            # compute mean values (returns series, not dataframe!)
        si_pct = si_pct.multiply(100).round(1)                                  # adjust 0.1234 -> 12.3
        df_agr.insert(0, 'Population', population)                              # restore column
        df_agr.insert(1, 'Residents per case', residents_per_case)              # restore column
        df_agr.insert(2, 'Trend', trend)                                        # restore column
        df_agr.insert(3, 'AGR (mean value)', list(si_pct))                      # save mean values
        df_agr = df_agr.iloc[:, list(range(4))]                                 # drop evrything after column 'Mean Values'
        df_agr = df_agr.sort_values(df_agr.columns[-1], ascending = False)      # sort by 'Mean Values'
        return df_agr

    def _check_for_update(self):
        '''
        Return cached dataframes if last update does not exceed specified amount of secs,
        else download data from Github and parse into dataframes.
        '''        
        if time() - self.last_update_time > 4 * 3600:
            urllib.request.urlretrieve(self.url, self.filepath)
            self.df_abs = self._compute_abs_dataframe()
            self.df_dif = self._compute_dif_dataframe()
            # Insert population column at pos 0 in dataframe
            self.df_abs = self._insert_pop_column(self.df_abs)
            self.df_dif = self._insert_pop_column(self.df_dif)
            # Insert residents per case column at pos 1 in dataframe
            self.df_abs = self._insert_residents_per_case_column(self.df_abs)
            self.df_dif = self._insert_residents_per_case_column(self.df_dif)
            # Insert trend column at pos 2 in dataframe
            self.df_abs = self._insert_trend_column(self.df_abs, 6)
            self.df_dif = self._insert_trend_column(self.df_dif, 6)
            self.last_update_time = time()

    def _prune_dataframe(self, df, cases, days):
        '''
        Discard all columns before <days> and all rows with less than <cases> in last column but only if cases > 0.
        '''
        df = df.iloc[:, [0, 1, 2] + list(range(-days, 0))]
        if cases > 0:
            last_column = list(df.columns)[-1]
            df = df[df[last_column] >= cases]
        return df

    def _shrink_dataframe(self, df, country):
        '''Discard all rows before <country>'''
        try:
            row_index = df.index.get_loc(country)
        except KeyError:
            print(country, 'not found in row index')
        else:
            df = df.iloc[row_index:]
        return df

    def _append_double_rates_to_df_agr(self, df_agr):
        '''
        Compute double rates from percentage increase and append as new column.
        Last col of <df> contains percentage increase (e.g. 9.2).
        '''
        def f(x):
            try:
                fx = round(log10(2) / log10(1 + x / 100), 1)
            except ZeroDivisionError:
                fx = 0
            return fx
        double_rates = [f(x) for x in df_agr["AGR (mean value)"]]
        df_agr['double_rates'] = double_rates
        return df_agr

    def compute_abs_values(self, days, cases, country=""):
        self._check_for_update()
        df_abs_tmp = self._prune_dataframe(self.df_abs, cases, days)
        df_abs_tmp = self._shrink_dataframe(df_abs_tmp, country)
        df_rel_tmp = self._compute_rel_dataframe(df_abs_tmp)
        abs_values = df_abs_tmp.reset_index().values.tolist()
        rel_values = df_rel_tmp.reset_index().values.tolist()
        dat_start = df_abs_tmp.columns[3]
        dat_end = df_abs_tmp.columns[-1]
        return abs_values, rel_values, dat_start, dat_end

    def compute_dif_values(self, days, cases, country=""):
        self._check_for_update()
        df_abs_tmp = self._prune_dataframe(self.df_abs, cases, days)                    # Create corresponding df_abs for <cases>.
        df_dif_tmp = self._drop_rows_based_on_unique_indicis(df_abs_tmp, self.df_dif)   # Drop countries which are not in corresponding df_abs.
        df_dif_tmp = self._prune_dataframe(df_dif_tmp, 0, days)                         # Only look at last <days>. Leave cases as is.
        df_dif_tmp = self._shrink_dataframe(df_dif_tmp, country)                        # Put country on top of the list if applicable.
        df_rel_tmp = self._compute_rel_dataframe(df_dif_tmp)
        dif_values = df_dif_tmp.reset_index().values.tolist()
        rel_values = df_rel_tmp.reset_index().values.tolist()
        dat_start = df_abs_tmp.columns[3]
        dat_end = df_abs_tmp.columns[-1]
        return dif_values, rel_values, dat_start, dat_end

    def compute_agr_values(self, cases):
        self._check_for_update()
        df_abs_tmp = self._prune_dataframe(self.df_abs, cases, 8)
        df_agr_tmp = self._compute_agr_dataframe(df_abs_tmp)
        df_rel_tmp = self._compute_rel_dataframe(df_agr_tmp)
        df_agr_tmp = self._append_double_rates_to_df_agr(df_agr_tmp)
        agr_values = df_agr_tmp.reset_index().values.tolist()
        rel_values = df_rel_tmp.reset_index().values.tolist()
        dat_start = df_abs_tmp.columns[3]
        dat_end = df_abs_tmp.columns[-1]
        return agr_values, rel_values, dat_start, dat_end

coviddata_confirmed = CovidData(CONFIRMED_GLOBAL_FILE, CONFIRMED_GLOBAL_URL)
coviddata_deaths = CovidData(DEATHS_GLOBAL_FILE, DEATHS_GLOBAL_URL) 
coviddata_recovered = CovidData(RECOVERED_GLOBAL_FILE, RECOVERED_GLOBAL_URL) 

app = Flask(__name__)

@app.route("/confirmed/")
def confirmed():
    days = request.args.get('days', default=7, type=int)
    cases = request.args.get('cases', default=2000, type=int)
    country = request.args.get('country', default="", type=str)    
    absval, relval, dat_start, dat_end = coviddata_confirmed.compute_abs_values(days, cases, country)
    header = "Total Confirmed Cases (" + dat_start + ' - ' + dat_end + ').'
    context = ["confirmed", header, days, cases, "cases", country, __version__]
    return render_template('lcd.html', title='confirmed', absval=absval, relval=relval, context=context)

@app.route("/confirmed_dif/")
def confirmed_dif():
    days = request.args.get('days', default=7, type=int)
    cases = request.args.get('cases', default=2000, type=int)
    country = request.args.get('country', default="", type=str)
    absval, relval, dat_start, dat_end = coviddata_confirmed.compute_dif_values(days, cases, country)
    header = "Daily New Cases (" + dat_start + ' - ' + dat_end + ').'
    context = ["confirmed_dif", header, days, cases, "cases", country, __version__]
    return render_template('lcd.html', title='confirmed (differential)', absval=absval, relval=relval, context=context)

@app.route("/deaths/")
def deaths():
    days = request.args.get('days', default=7, type=int)
    cases = request.args.get('cases', default=100, type=int)
    country = request.args.get('country', default="", type=str)
    absval, relval, dat_start, dat_end = coviddata_deaths.compute_abs_values(days, cases, country)
    header = "Total Deaths (" + dat_start + ' - ' + dat_end + ').'
    context = ["deaths", header, days, cases, "deaths", country, __version__] 
    return render_template('lcd.html', title='deaths', absval=absval, relval=relval, context=context)

@app.route("/deaths_dif/")
def deaths_dif():
    days = request.args.get('days', default=7, type=int)
    cases = request.args.get('cases', default=100, type=int)
    country = request.args.get('country', default="", type=str)
    absval, relval, dat_start, dat_end = coviddata_deaths.compute_dif_values(days, cases, country)
    header = "Daily New Deaths (" + dat_start + ' - ' + dat_end + ').'
    context = ["deaths_dif", header, days, cases, "deaths", country, __version__]
    return render_template('lcd.html', title='deaths (differential)', absval=absval, relval=relval, context=context)

@app.route("/recovered/")
def recovered():
    days = request.args.get('days', default=7, type=int)
    cases = request.args.get('cases', default=100, type=int)
    country = request.args.get('country', default="", type=str)
    absval, relval, dat_start, dat_end = coviddata_recovered.compute_abs_values(days, cases, country)
    header = "Total Recovered (" + dat_start + ' - ' + dat_end + ').'
    context = ["recovered", header, days, cases, "recovered", country, __version__] 
    return render_template('lcd.html', title='recovered', absval=absval, relval=relval, context=context)

@app.route("/recovered_dif/")
def recovered_dif():
    days = request.args.get('days', default=7, type=int)
    cases = request.args.get('cases', default=100, type=int)
    country = request.args.get('country', default="", type=str)
    absval, relval, dat_start, dat_end = coviddata_recovered.compute_dif_values(days, cases, country)
    header = "Daily New Recovered (" + dat_start + ' - ' + dat_end + ').'
    context = ["recovered_dif", header, days, cases, "recovered", country, __version__]
    return render_template('lcd.html', title='recovered (differential)', absval=absval, relval=relval, context=context)

@app.route("/av_growth_rate/")
def average_percentage_increase():
    days = request.args.get('days', default=7, type=int)
    cases = request.args.get('cases', default=1000, type=int)
    absval, relval, dat_start, dat_end = coviddata_confirmed.compute_agr_values(cases)
    header = ""
    context = ["av_growth_rate", header, days, cases, "", "", __version__]
    return render_template('lcd.html', title='Average growth rate in the last seven days', absval=absval, relval=relval, context=context)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)