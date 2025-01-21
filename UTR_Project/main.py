from scraper import *
import pandas as pd

df = pd.read_csv('uscities.csv')

get_utr_rating(df)