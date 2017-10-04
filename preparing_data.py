#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Oct  3 16:58:45 2017

Preparing data (Analysing & filteration)

@author: LiuQianKevin
"""
from pandas_datareader import data
import numpy as np
import csv, json
import pandas as pd

################################################################################################
## Preparing DJI data
dates = pd.date_range('2006-12-29', '2016-12-31')
df = pd.DataFrame(index=dates)

panel_data = data.DataReader(name = 'DJI',start = '2006-12-29',end = '2016-12-31',data_source = 'yahoo');
df = df.join(panel_data, how = 'outer')
df.fillna(method='ffill', inplace=True)
df.fillna(method='bfill', inplace=True)

interpolated_df = df[['Close','Adj Close']]
# Removing extra date rows added in data for calculating interpolation
interpolated_df = interpolated_df[3:]


###############################################################################################  
## Preparing NYTimes data
# Function to parse and convert date format
date_format = ["%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S+%f"]
def try_parsing_date(text):
    for fmt in date_format:
        #return datetime.strptime(text, fmt)
        try:
            return datetime.strptime(text, fmt).strftime('%Y-%m-%d')
        except ValueError:
            pass
    raise ValueError('no valid date format found')
    
years = [2016, 2015, 2014, 2013, 2012, 2011, 2010, 2009, 2008, 2007]
#years = [2016]
months = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
#months = [12]
dict_keys = ['pub_date', 'headline'] #, 'lead_paragraph']
articles_dict = dict.fromkeys(dict_keys)
# Filtering list for type_of_material
type_of_material_list = ['blog', 'brief', 'news', 'editorial', 'op-ed', 'list','analysis']
# Filtering list for section_name
section_name_list = ['business', 'national', 'world', 'u.s.' , 'politics', 'opinion', 'tech', 'science',  'health']
news_desk_list = ['business', 'national', 'world', 'u.s.' , 'politics', 'opinion', 'tech', 'science',  'health', 'foreign']

current_date = '2016-01-01'
from datetime import datetime
current_article_str = ''      

## Adding article column to dataframe
interpolated_df["articles"] = ''
count_articles_filtered = 0
count_total_articles = 0
count_main_not_exist = 0               
count_unicode_error = 0     
count_attribute_error = 0   

print 12
for year in years:
    for month in months:
        file_str = '/Users/LiuQianKevin/Documents/Git-repository/MachineLearningForTrading/data/nytimes/' + str(year) + '-' + '{:02}'.format(month) + '.json'
        with open(file_str) as data_file:    
            NYTimes_data = json.load(data_file)
        count_total_articles = count_total_articles + len(NYTimes_data["response"]["docs"][:])
        for i in range(len(NYTimes_data["response"]["docs"][:])):
            try:
                if any(substring in NYTimes_data["response"]["docs"][:][i]['type_of_material'].lower() for substring in type_of_material_list):
                    if any(substring in NYTimes_data["response"]["docs"][:][i]['section_name'].lower() for substring in section_name_list):
                        #count += 1
                        count_articles_filtered += 1
                        #print 'i: ' + str(i)
                        articles_dict = { your_key: NYTimes_data["response"]["docs"][:][i][your_key] for your_key in dict_keys }
                        articles_dict['headline'] = articles_dict['headline']['main'] # Selecting just 'main' from headline
                        #articles_dict['headline'] = articles_dict['lead_paragraph'] # Selecting lead_paragraph
                        date = try_parsing_date(articles_dict['pub_date'])
                        #print 'article_dict: ' + articles_dict['headline']
                        if date == current_date:
                            current_article_str = current_article_str + '. ' + articles_dict['headline']
                        else:  
                            interpolated_df.set_value(current_date, 'articles', interpolated_df.loc[current_date, 'articles'] + '. ' + current_article_str)
                            current_date = date
                            #interpolated_df.set_value(date, 'articles', current_article_str)
                            #print str(date) + current_article_str
                            current_article_str = articles_dict['headline']
                        # For last condition in a year
                        if (date == current_date) and (i == len(NYTimes_data["response"]["docs"][:]) - 1): 
                            interpolated_df.set_value(date, 'articles', current_article_str)   
                        
             #Exception for section_name or type_of_material absent
            except AttributeError:
                #print 'attribute error'
                #print NYTimes_data["response"]["docs"][:][i]
                count_attribute_error += 1
                # If article matches news_desk_list if none section_name found
                try:
                    if any(substring in NYTimes_data["response"]["docs"][:][i]['news_desk'].lower() for substring in news_desk_list):
                            #count += 1
                            count_articles_filtered += 1
                            #print 'i: ' + str(i)
                            articles_dict = { your_key: NYTimes_data["response"]["docs"][:][i][your_key] for your_key in dict_keys }
                            articles_dict['headline'] = articles_dict['headline']['main'] # Selecting just 'main' from headline
                            #articles_dict['headline'] = articles_dict['lead_paragraph'] # Selecting lead_paragraph
                            date = try_parsing_date(articles_dict['pub_date'])
                            #print 'article_dict: ' + articles_dict['headline']
                            if date == current_date:
                                current_article_str = current_article_str + '. ' + articles_dict['headline']
                            else:  
                                interpolated_df.set_value(current_date, 'articles', interpolated_df.loc[current_date, 'articles'] + '. ' + current_article_str)
                                current_date = date
                                #interpolated_df.set_value(date, 'articles', current_article_str)
                                #print str(date) + current_article_str
                                current_article_str = articles_dict['headline']
                            # For last condition in a year
                            if (date == current_date) and (i == len(NYTimes_data["response"]["docs"][:]) - 1): 
                                interpolated_df.set_value(date, 'articles', current_article_str)   
                
                except AttributeError:
                    pass
                pass
            except KeyError:
                print 'key error'
                #print NYTimes_data["response"]["docs"][:][i]
                count_main_not_exist += 1
                pass   
            except TypeError:
                print "type error"
                #print NYTimes_data["response"]["docs"][:][i]
                count_main_not_exist += 1
                pass
         

              
print count_articles_filtered 
print count_total_articles                     
print count_main_not_exist
print count_unicode_error


## Putting all articles if no section_name or news_desk not found
for date, row in interpolated_df.T.iteritems():   
    if len(interpolated_df.loc[date, 'articles']) <= 400:
        #print interpolated_df.loc[date, 'articles']
        print date
        month = date.month
        year = date.year
        file_str = '/Users/LiuQianKevin/Documents/Git-repository/MachineLearningForTrading/data/nytimes/' + str(year) + '-' + '{:02}'.format(month) + '.json'
        with open(file_str) as data_file:    
            NYTimes_data = json.load(data_file)
        count_total_articles = count_total_articles + len(NYTimes_data["response"]["docs"][:])
        interpolated_df.set_value(date.strftime('%Y-%m-%d'), 'articles', '')
        for i in range(len(NYTimes_data["response"]["docs"][:])):
            try:
                
                articles_dict = { your_key: NYTimes_data["response"]["docs"][:][i][your_key] for your_key in dict_keys }
                articles_dict['headline'] = articles_dict['headline']['main'] # Selecting just 'main' from headline
                #articles_dict['headline'] = articles_dict['lead_paragraph'] # Selecting lead_paragraph       
                pub_date = try_parsing_date(articles_dict['pub_date'])
                #print 'article_dict: ' + articles_dict['headline']
                if date.strftime('%Y-%m-%d') == pub_date: 
                    interpolated_df.set_value(pub_date, 'articles', interpolated_df.loc[pub_date, 'articles'] + '. ' + articles_dict['headline'])  
                
            except KeyError:
                print 'key error'
                #print NYTimes_data["response"]["docs"][:][i]
                #count_main_not_exist += 1
                pass   
            except TypeError:
                print "type error"
                #print NYTimes_data["response"]["docs"][:][i]
                #count_main_not_exist += 1
                pass


#>>> print count_articles_filtered 
#440770
#>>> print count_total_articles 
#1073132


## Filtering the whole data for a year
#filtered_data = interpolated_df.ix['2016-01-01':'2016-12-31']
#filtered_data.to_pickle('/Users/Dinesh/Documents/Project Stock predictions/data/pickled_ten_year_all.pkl')  


# Saving the data as pickle file
interpolated_df.to_pickle('/Users/LiuQianKevin/Documents/Git-repository/MachineLearningForTrading/data/pickled_ten_year_filtered_lead_para.pkl')  


# Save pandas frame in csv form
interpolated_df.to_csv('/Users/LiuQianKevin/Documents/Git-repository/MachineLearningForTrading/data/sample_interpolated_df_10_years_filtered_lead_para.csv',
                       sep='\t', encoding='utf-8')



# Reading the data as pickle file
dataframe_read = pd.read_pickle('/Users/LiuQianKevin/Documents/Git-repository/MachineLearningForTrading/data/pickled_ten_year_filtered_lead_para.pkl')




#################################################################################

# Filtering rows
#filtered_data = interpolated_df.ix['2016-01-01':'2016-12-31']

# Syntax for accessing the data
#NYTimes_data["response"]["docs"][1:2][:]['headline']['main']
#NYTimes_data["response"]["docs"][1:2][0]['pub_date']
     

#    articles_dict = { your_key: NYTimes_data["response"]["docs"][:][i][your_key] for your_key in dict_keys }
#    try:
#        articles_dict['headline'] = articles_dict['headline']['main'] # Selecting just 'main' from headline
#    except KeyError:
#        count_main_not_exist += 1
#        pass   
#    except TypeError:
#        count_main_not_exist += 1
#        pass


        
# Find out articles with less number of articles
# for date, row in interpolated_df.T.iteritems():   
#     if len(interpolated_df.loc[date, 'articles']) < 300:
#         print interpolated_df.loc[date, 'articles']
#         print date
           
            
