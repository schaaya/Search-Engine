SEARCH_KEY = "AIzaSyC6PBRl69lpHUu2OzPnaIjSeyRCWA7UPSg"
SEARCH_ID = "43c41defef3244457"
COUNTRY = "us"
SEARCH_URL = "https://www.googleapis.com/customsearch/v1?key={key}&cx={cx}&q={query}&start={start}&num=10&gl=" + COUNTRY
RESULT_COUNT = 20

import os

if os.path.exists("private.py"):
    from private import *
