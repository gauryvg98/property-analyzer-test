## Property Analyzer
### Live url - https://property-analyzer-411cc23a6077.herokuapp.com/

### Devlog is at `devlog.md` in the root of the repository. Check it for more detailed design decisions.

### Essential Endpoints :
##### 1. /docs/ - Link to the FastAPI docs
##### 2. /property - Routes to Property (filter, statistics, outliers) endpoints
##### 3. /visualization/ - Link to the visualizations
##### 4. /load/ - Loads the data from the default csv into sqlite-db (Support for additional data)

### Setup :

##### 1. Ensure you have python3 installed. 
##### 2. Run `pip3 install requirements.txt` to install all the required dependencies.
##### 3. Start the server with `python main.py`
##### 4. After the server has started up, hit this curl to load the data - `curl localhost:8000/load/`
##### 5. You're done!

### APIs : 
##### 1. `/property/` - 
###### Gets a paginated list of Properties on filter criterias such as min/max price, min/max price_per_square_feet, min/max square feet, bedrooms, bathrooms, zipcode, city, state.
```
Sample Request : 
curl -X 'GET' \
  'http://localhost:8000/property/?price_max=1000000&squarefeet_max=100000&bedrooms=3&bathrooms=2&city=Miami&state=FL&page=1&page_size=10' \
  -H 'accept: application/json'

Sample Response : 
{
  "total": 464437,
  "page": 1,
  "page_size": 10,
  "results": [
    {
      "propertyid": 38522891,
      "address": "12327 SW 148TH TER",
      "city": "Miami",
      "state": "FL",
      "zipcode": "33186",
      "price": 115000,
      "bedrooms": 3,
      "bathrooms": 2,
      "squarefeet": 1464,
      "price_per_square_feet": 78.55191256830601,
      "datelisted": null
    },
    ....
  ]
}
```
##### 2. `/property/statistics/` - 
###### Gets some basic property statistics such as average price, average_price_per_sqft, percentiles, along with a number of outliers detected (based on simple IQR ranges)
```
Sample Request : 
curl -X 'GET' \
  'http://localhost:8000/property/statistics/?price_max=1000000&squarefeet_max=100000&bedrooms=3&bathrooms=2&city=Miami&state=FL&page=1&page_size=10' \
  -H 'accept: application/json'

Sample Response : 
{
  "average_price": 554757.4955481003,
  "median_price": 235000,
  "average_price_per_sqft": 846.4466804395497,
  "total_properties": 368719,
  "percentiles": {
    "percentile_25_price": 125000,
    "percentile_50_price": 235000,
    "percentile_75_price": 410000,
    "percentile_90_price": 715000,
    "percentile_99_price": 5650000
  },
  "outlier_properties_count": 28936
}
```
##### 3. `/property/outliers/price/` - 
###### Gets a paginated list of Properties whose prices are outliers (based on simple IQR ranges) on the filter criterias (same as above APIs). These outliers could be simply due to wrong data, or can be legitimate (which can be a good marker for say, property flip-ers)
```
Sample Request : 
curl -X 'GET' \
  'http://localhost:8000/property/outliers/price/?price_max=1000000&squarefeet_max=100000&bedrooms=3&bathrooms=2&city=Miami&state=FL&page=1&page_size=10' \
  -H 'accept: application/json'

Sample Response : 
{
  "total": 464437,
  "page": 1,
  "page_size": 10,
  "results": [
    {
      "propertyid": 38167625,
      "address": "10631 N KENDALL DR STE 280",
      "city": "Miami",
      "state": "FL",
      "zipcode": "33176",
      "price": 25000,
      "bedrooms": 0,
      "bathrooms": null,
      "squarefeet": null,
      "price_per_square_feet": null,
      "datelisted": null
    },
    ....
  ]
}
```
##### 4. `/property/statistics/` - 
###### Gets a paginated list of Properties whose prices per square feets are outliers (based on simple IQR ranges) on the filter criterias (same as above APIs)
```
Sample Request : 
curl -X 'GET' \
  'http://localhost:8000/property/outliers/price/?squarefeet_max=100000&bedrooms=3&bathrooms=2&city=Miami&state=FL&page=1&page_size=10' \
  -H 'accept: application/json'

Sample Response : 
{
  "total": 464437,
  "page": 1,
  "page_size": 10,
  "results": [
    {
      "propertyid": 38167625,
      "address": "10631 N KENDALL DR STE 280",
      "city": "Miami",
      "state": "FL",
      "zipcode": "33176",
      "price": 25000,
      "bedrooms": 0,
      "bathrooms": null,
      "squarefeet": null,
      "price_per_square_feet": null,
      "datelisted": null
    },
    ....
  ]
}
```
### Bugs - APIs take longer when curled without any filters. This is typically very observable on the basic heroku dyno.

### Visualizations :

##### Features in the webpage `/visualization` and correspondingly built into the API - 
###### 1. All visualizations support a variety of filters - city, state, zipcode, bedrooms, bathrooms
###### 2. Every visualization has a button at the top of the webpage which needs to be pressed to render it. 
###### 3. HTML code can be found in the static/visualization.html file (Please excuse my html :)

###### All these visualizations are served from the backend through APIs of response - text/html format and the divs returned are rendered using plotly.js

##### 1. Price Distribution - `/visualization/property/price/`
###### A simple histogram which shows the count of properties within predefined price ranges

##### 2. Historical Price Distribution - `/visualization/property/historical-price/`
###### A line plot which shows the trend of average property prices across time.

##### 3. Bedrooms Distribution - `/visualization/property/rooms/`
###### A simple histogram which shows the count of properties within predefined price ranges

##### 4. Price vs Zipcode Box Plots - `/visualization/property/price-zipcode-box/`
###### A box plot which shows the distribution of property price grouped by zipcodes. It is good for seeing outliers and getting a general trend across different areas. 
###### Bug - This takes a little longer to load (~30 secs). Due to certain extreme outliers in data (properties which cost upwards of 1B USD), the plot is not very clear when viewed without any filters. Need to zoom to see the actual trends. Better to just clean them off, but for the time being, they are there in the data. 

##### 5. Geographical Heatmap - `/visualization/property/zipcode-heatmaps/`
###### A heatmap which shows the distribution of average price, number of properties, average area, average price ranges, average price per square feet across different zipcodes in Miami. Similar colored zipcodes have similar characteristics.

##### 6. Historical Geo-Heatmap - `/visualization/property/historical-zipcode-heatmaps/`
###### Shows all of the same characteristics as the visualization in point 5, but additonally supports a slider which these stats across time. There's a play button which shows the trends across time sequentially. This was generated by forward filling existing price data across future months to rightfully consider old prices as latest as well, to show a general trend. 

### Running tests - 
#### Use this command to run tests - `python3 -m unittest discover -s tests` 
##### 1. Tests are pretty basic. They test all "service layer" functions called from the router for all 4 of the APIs.
##### 2. Spins up an in-memory sqlite instance which is used for all database operations.
##### 3. These can extended to use MagicMocks to mock db operations, so that each function can be independently tested without prepopulating db data.

### Known Bugs - 
###### 1. Box plot seems to sometimes blow up the heroku "basic" dyno, causing the pod to provision more memory, or just go down. Please confirm the same through dev console on your browser.
###### 2. Box plot takes sometime to load, so dont panic and overload the baby heroku server with more button clicks xD
