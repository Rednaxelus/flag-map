# Flag-Map

A Python script that creates a map made of (emoji-)flags for the countries in the desired region.

## Requirements

- The images for the flags you want to use must be PNG and in a folder called "flags" in the same directory as the script.
- The name for the flag-images have the format: `Unicode1 + "-" + Unicode2` Example: "1F1E6-1F1FA.png" for Australia. [Regional indicator symbol](https://en.wikipedia.org/wiki/Regional_indicator_symbol), [Enclosed Alphanumeric Supplement](https://en.wikipedia.org/wiki/Enclosed_Alphanumeric_Supplement)
- [countries.geojson](https://github.com/datasets/geo-countries/tree/master/data) needs to be in the same directory as the script. This is the offline geometric dataset used to determine what country a given geolocation belongs to.

## How to run

Execute the function "do_it()" inside "main.py" through the Python interpreter.
You can give these additional arguments:

    latitude_start: float
    longitude_start: float
    latitude_div: float
    longitude_div: float
    step_lat: float; the smaller it is the more precise but larger the map gets. A good range is  0.1 to 1.0
    background_color: RGBA
    save: bool; if the created map should be saved automatically. Will never overwrite a file but instead tries to save under a new filename up to the number 99.
    
## How it works

1. The script checks the country(-code) that is present at a given geolocation (latitude, longitude). It does this for a given region defined by its starting geolocation, the number of steps, and the step-size.
2. It loads the images of the flag for the given countrycode.
3. It prints those images on a base image and exports it.

## References

- [Openmoji (PNG 618x618 Color)](https://github.com/hfg-gmuend/openmoji): used for the flag-emojis.
- [Natural Earth](https://www.naturalearthdata.com/): creators of the country-data-set.
- [odyniec/gist:3470977](https://gist.github.com/odyniec/3470977) a function I copied to autocrop the images.

## Notes

- Open for feedback. I am a Python amateur and don't know the coding conventions that well yet.
- The reason I don't use an online API is because it was too slow and I didn't want to spam thousands of requests each run. https://github.com/thampiman/reverse-geocoder worked amazingly fast, but I couldn't filter out the water-locations that well.
