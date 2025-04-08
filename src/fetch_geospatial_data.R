library(tigris)
library(tidyverse)
library(tidycensus)
library(stringr)
library(sf)
library(rmapshaper)

# msa county map
msa_county_map <- read_csv("/Users/andrewmurp/Documents/python/usa-swimming-transit-access/data/msa_county_map.csv")
names(msa_county_map) <- c(
  "CBSA_code",
  "MSA_division_code",
  "CSA_code",
  "CBSA_title",
  "CBSA_type",
  "metropolitan_divison_title",
  "CSA_title",
  "county_name",
  "state_name",
  "STATEFP",
  "COUNTYFP",
  "central_outlying_county"
)
## list of CBSAs to use :)
cbsas <- c(
  "New York-Newark-Jersey City, NY-NJ",
  "Los Angeles-Long Beach-Anaheim, CA",
  "Chicago-Naperville-Elgin, IL-IN",
  "Dallas-Fort Worth-Arlington, TX",
  "Houston-Pasadena-The Woodlands, TX",
  "Miami-Fort Lauderdale-West Palm Beach, FL",
  "Washington-Arlington-Alexandria, DC-VA-MD-WV",
  "Atlanta-Sandy Springs-Roswell, GA",
  "Philadelphia-Camden-Wilmington, PA-NJ-DE-MD",
  "Phoenix-Mesa-Chandler, AZ",
  ## FUTURE ME: DELETE SEATTLE AND MILWAUKEE FROM THE LIST HERE HEHE
  "Seattle-Tacoma-Bellevue, WA",
  "Milwaukee-Waukesha, WI",
  ## BUT LEAVE THEM LATER ON.. just having them jump the line
  "Boston-Cambridge-Newton, MA-NH",
  "San Francisco-Oakland-Fremont, CA",
  "San Jose-Sunnyvale-Santa Clara, CA",
  "Detroit-Warren-Dearborn, MI",
  "Ann Arbor, MI",
  "Seattle-Tacoma-Bellevue, WA",
  "Minneapolis-St. Paul-Bloomington, MN-WI",
  "Tampa-St. Petersburg-Clearwater, FL",
  "North Port-Bradenton-Sarasota, FL",
  "San Diego-Chula Vista-Carlsbad, CA",
  "Denver-Aurora-Centennial, CO",
  "Boulder, CO",
  "Orlando-Kissimmee-Sanford, FL",
  "Charlotte-Concord-Gastonia, NC-SC",
  "St. Louis, MO-IL",
  "San Antonio-New Braunfels, TX",
  "Austin-Round Rock-San Marcos, TX",
  "Portland-Vancouver-Hillsboro, OR-WA",
  "Sacramento-Roseville-Folsom, CA",
  "Las Vegas-Henderson-North Las Vegas, NV",
  "Cincinnati, OH-KY-IN",
  "Kansas City, MO-KS",
  "Columbus, OH",
  "Indianapolis-Carmel-Greenwood, IN",
  "Nashville-Davidson--Murfreesboro--Franklin, TN",
  "Virginia Beach-Chesapeake-Norfolk, VA-NC",
  "Providence-Warwick, RI-MA",
  "Milwaukee-Waukesha, WI",
  "Raleigh-Cary, NC",
  "Louisville/Jefferson County, KY-IN",
  "Richmond, VA",
  "Fresno, CA"
)
cbsas <- head(cbsas, 12)
msa_county_map <- msa_county_map %>% filter(CBSA_title %in% cbsas)
# national census tract dataset that I downloaded manually since tigris hates me :(
all_ct <- sf::read_sf("/Users/andrewmurp/Downloads/cb_2023_us_tract_500k/cb_2023_us_tract_500k.shp")

ct_pop <- read_csv("/Users/andrewmurp/Downloads/acs_5y_demographics_tract.csv")

cts <- merge(all_ct,ct_pop,by=c("GEOIDFQ"),all.x=TRUE) %>% select(
  "GEOID","tract_name",
  "population","population_white","population_black","population_american_indian_ak_native",
  "population_asian","population_native_hawaiian_pacific_islander","population_other_race",
  "population_two_or_more_races","population_hispanic_latino","median_household_income",
  "STATEFP","COUNTYFP","STATE_NAME","ALAND","AWATER","geometry"
)

cts_cbsa <- merge(cts, msa_county_map, by=c("STATEFP","COUNTYFP")) %>% select(
  'STATEFP','COUNTYFP',"GEOID",'tract_name','population',
  "population_white","population_black","population_american_indian_ak_native",
  "population_asian","population_native_hawaiian_pacific_islander","population_other_race",
  "population_two_or_more_races","population_hispanic_latino","median_household_income",
  'ALAND','AWATER','CBSA_title','geometry'
)
# write to intermediate location, other geospatial stuff is happening in python
# why is it not all in python you ask? because I was going to use tigris, but then it hated me
sf::write_sf(cts_cbsa, "/Users/andrewmurp/Documents/python/usa-swimming-transit/data/tracts/msa_tracts.geojson")