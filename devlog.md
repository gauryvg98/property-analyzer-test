# Dev Log - 
## Documenting my thoughts during development

## First look at the data csv - 
1. Data doesnt seem to be clean. Some rows seem to be missing fields such as price, bedrooms, bathrooms, sq.ft. 
Will need to not load rows into SQL which do not seem to have price attached to them. 

### Better - To load all the data into SQL, and only use valid rows for analysis 
###### Definition of valid rows : rows which do not have a missing price

### Quick Analysis of the data to drive some development decisions :
###### Total rows (total) : 464,889 
###### Total unique rows: 388,006
###### Number of rows with conflicting (duplicate) property IDs: 577
###### Number of rows with missing data points (excluding the DateListed column) (at_least_one_missing_data_point): 115,115 
###### Number of rows with missing price (missing_price): 83,429 
###### Rows with bathroom data but no bedroom data (and have a price): 6,361
###### Rows with bedroom data but no bathroom data (and have a price): 2,114
###### Price value but no squarefeet - 6,157

###### Rows with all columns present = (total - at_least_one_missing_data_point) = 464,889 - 115,115  ~= 350,000
###### Rows with no missing price data (rows which fit my "valid" definition) = total - missing_price ~= 380,000
###### Rows we wont be able to use for deeper analysis (price present but missing bedrooms/bathrooms/area) ~= 31,686

#### Raw dump from analysis
###### Total rows: 464,889
###### Total unique rows: 464,431
###### Rows with conflicting property IDs: 577
###### Rows with missing data (excluding DateListed): 115,115
###### Rows with a price but missing some other data (excluding DateListed):
###### Total: 31,686
###### Unique: 31,339
###### Missing data breakdown (unique rows):
###### Missing bathrooms: 34,557
###### Missing bedrooms: 40,108
###### Missing square feet: 9,484
###### Missing price: 83,337
###### (Columns address, city, geometry, propertyid, state, zipcode have no missing values)
###### Rows with a price but no square feet: 6,157
###### Rows with bathroom data but no bedroom data (and with price): 6,361
###### Rows with bedroom data but no bathroom data (and with price): 2,114

### Even Better - To remove garbage outliers in the data (price > 1B / ppsf > 1M)

Looking at historic data now, 
Number of rows with conflicting (duplicate) property IDs: 577 
No variation in prices across duplicate properties across datetime listed found

## Starting development : 
#### 1. Define response models and table schema. 
#### 2. Expose API for filtering properties.
#### 3. Simple load script : load into pandas, and then write row by row to sql
#### Add some extra fields during load (is_valid and is_historic)
#### Load price == 0 as price = null, because zero price makes no sense (null price means missing price, which makes more sense and it wouldnt skew our analysis)
#### 4. Expose API to calculate statistics
#### 5. Refactor code - Extract out common query params as injectable classes and filter database objects based on them
#### 6. Add pagination as an injectable param
#### 7. Write tests with a smaller data set of 100 properties for the APIs and statistics functions
#### 8. Use plotly for visualizations.

#### Note - Use the common filter property query function which can effectively filter the `properties` table as per query params, as these query params are consistent across all APIs exposed (including visualization APIs).
#### Avoid visualizations which pass non-aggregated data to the plots, due to network and performance concerns (see box plot performance)
#### Improvements to outlier detection can be done.