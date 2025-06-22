librarian::shelf(mapboxapi, sf, tidyverse, rjson)

api_key_path <- "/Users/andrewmurp/Documents/python/usa-swimming-transit/mapbox.env"
dot_env_data <- fromJSON(paste(readLines(api_key_path), collapse=""))

df <- st_read("/Users/andrewmurp/Documents/python/usa-swimming-transit-access/data/full_cbsa_data.geojson")
#df <- st_read("/Users/andrewmurp/Documents/python/usa-swimming-transit/data/usa_swimming_top_clubs_msa.geojson")

ver = "v7" # change incrementally

secret_token = dot_env_data$mapbox_sk
public_token = dot_env_data$mapbox_pk

# ==========================================================================
# Be very careful when running this part - can incur charges if done wrong
# ==========================================================================
map_source <-
  mts_create_source(
    data = df,
    tileset_id = paste0("usa_swim_full_", ver),
    username = "blumdrew",
    access_token = secret_token
  )

recipe <- mts_make_recipe(
  cbsa_pools =
    recipe_layer(
      source = map_source$id,
      minzoom = 0,
      # ==========================================================================
      # !!! DO NOT USE MAXZOOM > 10 !!!
      # !!! IMPORTANT !!! maxzoom = 10 will trigger a 10m mapbox processing for
      # the tileset. Anything higher will trigger 1m processing which will quickly
      # incure costs. There's a lot more monthly room to process 10m tilesets.
      # ==========================================================================
      maxzoom = 10 # or less
    )
)

mts_validate_recipe(recipe, access_token = public_token)

#
# Upload and publish maptiles
# --------------------------------------------------------------------------
mts_create_tileset(
  tileset_name = paste0("usa_swim_full_", ver),
  username = "blumdrew",
  recipe = recipe,
  access_token = secret_token
)

mts_publish_tileset(
  tileset_name = paste0("usa_swim_full_", ver),
  username = "blumdrew",
  access_token = secret_token
)