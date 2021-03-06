# -*- coding: utf-8 -*-
"""
Do a statistical analyis on the influence of different hyperparameters on the results.

Created on Tue Jun 26 13:44:29 2018

@author: lbechberger
"""

import argparse
import csv
import os
from scipy.stats import shapiro, normaltest, f_oneway, ttest_ind, kruskal, mannwhitneyu
from matplotlib import pyplot as plt
from configparser import RawConfigParser

parser = argparse.ArgumentParser(description='Statistical analyis')
parser.add_argument('input_file_name', help = 'the input file containing all individual runs')
parser.add_argument('config_file_name', help = 'the config file specifying the hyperparameters and metrics')
parser.add_argument('data_set', help = 'the data set to analyze')
parser.add_argument('-t', '--threshold', type = int, help = 'significance threshold', default = 0.01)
parser.add_argument('-o', '--output_folder', help = 'folder for storing the output images', default = '.')
parser.add_argument('-p', '--parameters', help = 'the configuration of hyperparameters to investigate', default = 'all_hyperparams')
parser.add_argument('-m', '--metrics', help = 'the configuration of metrics to investigate', default = 'all_metrics')
args = parser.parse_args()
             
config = RawConfigParser()
config.read(args.config_file_name)

hyperparams_mapping = config[args.parameters]
metric_mapping = config[args.metrics]

hyperparams = sorted(list(hyperparams_mapping.keys()))
bins = {}
for metric in metric_mapping.keys():
    bins[metric] = {}  
    for hyperparam in hyperparams:
        bins[metric][hyperparam] = {}           


with open(args.input_file_name, 'r') as in_file:
    reader = csv.DictReader(in_file, delimiter=',')
    
    def try_add(dictionary, key, vector):
        if key not in dictionary.keys():
            dictionary[key] = []
        dictionary[key].append(vector)
       
    for row in reader:
        
        # skip all the rows that don't belong to the data set of interest
        if row['data_set'] != args.data_set:
            continue
        
        config_name = row['config']
        
        for hyperparam in hyperparams:
            # find the position of the given hyperparameter
            start_idx = config_name.find(hyperparam)
            # find the end of the given hyperparameter
            end_idx = config_name.find('-', start_idx)

            if end_idx == -1:
                end_idx = len(config_name)
            elif config_name[end_idx + 1].isdigit():
                # need special dealing for 'di9e-05'
                end_idx = config_name.find('-', end_idx + 1)
           
            # figure out the bin name
            bin_name = config_name[(start_idx + len(hyperparam)):end_idx]
            
            # finally add the data to the corresponding bin
            for metric, dictionary in bins.items():
                try_add(dictionary[hyperparam], bin_name, float(row[metric]))



# now do some statistical tests to check for normal distribution of all the bins
for metric, dictionary in bins.items():
    for hyperparam, bins in dictionary.items():

        def is_float(string):
            try:
                float(string)
                return True
            except ValueError:
                return False

        def try_convert(string):
            if is_float(string):
                return float(string)
            return string
        
        all_bins_normal = True
        all_bins_raw = []
        
        for value, numbers in bins.items():
            shapiro_stat, shapiro_p = shapiro(numbers)
            d_agostino_stat, d_agostino_p = normaltest(numbers)
            print("Testing normality of '{0}' for {1} = {2} ...".format(metric, hyperparam, value))
            print("\tShapiro test: p = {0} (stat = {1})\t --> {2}".format(shapiro_p, shapiro_stat, (shapiro_p >= args.threshold)))
            print("\tD'Agostino test: p = {0} (stat = {1})\t --> {2}".format(d_agostino_p, d_agostino_stat, (d_agostino_p >= args.threshold)))
            
            this_bin_normal = (shapiro_p >= args.threshold) and (d_agostino_p >= args.threshold)
            all_bins_normal = all_bins_normal and this_bin_normal
            all_bins_raw.append((try_convert(value), numbers))
        
        all_bins_sorted = sorted(all_bins_raw, key = lambda y: y[0])
        all_bins = list(map(lambda x: x[1], all_bins_sorted))
        bin_names = list(map(lambda x: x[0], all_bins_sorted))      
        
        if all_bins_normal:
            # do ANOVA
            print("\nAll bins normally distributed --> conducting ANOVA")

            anova_stat, anova_p = f_oneway(*all_bins)
            print("ANOVA result: p = {0} (stat = {1})".format(anova_p, anova_stat))
            
            if anova_p < args.threshold:
                # we found significant differences! use t-test to follow up
                print("ANOVA detected significant differences, using pairwise t-tests to follow up...")
                list_of_values = list(bins.keys())
                # use Bonferroni adjustments
                number_of_comparisons = (len(list_of_values) * (len(list_of_values) - 1)) / 2
                bonferroni_threshold = args.threshold / number_of_comparisons
                for i in range(len(list_of_values)):
                    for j in range(i + 1, len(list_of_values)):
                        first_name = list_of_values[i]
                        second_name = list_of_values[j]
                        first_numbers = bins[first_name]
                        second_numbers = bins[second_name]
                        t_test_stat, t_test_p = ttest_ind(first_numbers, second_numbers)
                        significance = "SIGNIFICANT" if t_test_p < bonferroni_threshold else "NOT SIGNIFICANT"
                        print("\tDifference between {0} and {1}: p = {2} (stat: {3})\t{4}".format(first_name, second_name, t_test_p, t_test_stat, significance))
        else:
            # do something else
            print("\nAt least one bin not normally distributed --> conducting Kruskal-Wallis")
            kruskal_stat, kruskal_p = kruskal(*all_bins)
            print("Kruskal-Wallis result: p = {0} (stat = {1})".format(kruskal_p, kruskal_stat))
            
            if kruskal_p < args.threshold:
                # we found significant differences! use Mann-Whitney-U to follow up
                print("Kriskal-Wallis detected significant differences, using pairwise Mann-Whitney-U to follow up...")
                list_of_values = list(bins.keys())
                # use Bonferroni adjustments
                number_of_comparisons = (len(list_of_values) * (len(list_of_values) - 1)) / 2
                bonferroni_threshold = args.threshold / number_of_comparisons
                for i in range(len(list_of_values)):
                    for j in range(i + 1, len(list_of_values)):
                        first_name = list_of_values[i]
                        second_name = list_of_values[j]
                        first_numbers = bins[first_name]
                        second_numbers = bins[second_name]
                        mannwhitneyu_stat, mannwhitneyu_p = mannwhitneyu(first_numbers, second_numbers)
                        significance = "SIGNIFICANT" if mannwhitneyu_p < bonferroni_threshold else "NOT SIGNIFICANT"
                        print("\tDifference between {0} and {1}: p = {2} (stat: {3})\t{4}".format(first_name, second_name, mannwhitneyu_p, mannwhitneyu_stat, significance))
        print("\n")

        # now also create some box plots
        fig, ax = plt.subplots()
        ax.boxplot(all_bins, labels = bin_names)
        ax.set_title("{0}\nfor different values of {1}".format(metric_mapping[metric], hyperparams_mapping[hyperparam]))
        plt.savefig(os.path.join(args.output_folder, "{0}-{1}.png".format(metric, hyperparam)))   
        plt.close(fig)
        
    print("\n")
        
# TODO also look for interaction effects?