# Dicoding Collection Dashboard ✨

## Kernel Notebook 
Python 3.10.6

## Setup Environment - Anaconda
```
conda create --name main-ds python=3.9
conda activate main-ds
pip install -r requirements.txt
```

## Setup Environment - Shell/Terminal
```
mkdir proyek_analisis_data
cd proyek_analisis_data
pipenv install
pipenv shell
pip install -r requirements.txt
```
## Setup Library yang Digunakan
```
pip install pandas numpy matplotlib seaborn

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.ticker as mtick
import seaborn as sns
import streamlit as st
import io
import urllib
from urllib.request import urlopen
from PIL import Image
from babel.numbers import format_currency
from func import DataAnalyzer, BrazilMapPlotter
```

## Run steamlit app
```
streamlit run main.py
```
