# Press Umschalt+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

from PIL import Image, ImageDraw
import reverse_geocoder as rg

import json

from shapely.geometry import mapping, shape
from shapely.prepared import prep
from shapely.geometry import Point


def autocrop_image(image, border=0):
    # Get the bounding box
    bbox = image.getbbox()

    # Crop the image to the contents of the bounding box
    image = image.crop(bbox)

    # Determine the width and height of the cropped image
    (width, height) = image.size

    # Add border
    width += border * 2
    height += border * 2

    # Create a new image object for the output image
    cropped_image = Image.new("RGBA", (width, height), (0, 0, 0, 0))

    # Paste the cropped image onto the new image
    cropped_image.paste(image, (border, border))

    # Done!
    return cropped_image


def get_unicode(code):
    subchars = []
    for c in code:
        res = ord(c.capitalize()) - ord('A') + 127462
        subchars.append(hex(res).upper()[2:])
    return (subchars[0] + '-' + subchars[1] + '.png')


def get_country(coordinates):
    res3 = []
    for pon in coordinates:
        point = Point(pon[1], pon[0])  # lon, lat
        found = False
        for country, geom in countries.items():
            if geom.contains(point):
                res3.append(get_unicode(country))
                found = True
                break
        if not found:
            res3.append(None)
    return res3


if __name__ == '__main__':

    blueprint_flag = Image.open(f'openmoji-618x618-color/1F1E6-1F1E8.png')
    blueprint_flag = autocrop_image(blueprint_flag)

    flag_width = 32
    scale_factor = flag_width / blueprint_flag.width
    flag_height = int(blueprint_flag.height * scale_factor)

    blueprint_flag = blueprint_flag.resize((flag_width, flag_height), resample=Image.NEAREST)

    latitude_start = 73.0  # 90
    longitude_start = -13.0  # -180
    step_lat = 0.5
    step_lon = (flag_width / flag_height) * step_lat

    latitude_div = 40  # 180
    longitude_div = 55  # 360

    draw_offset_x = 100
    draw_offset_y = 100

    map_width = int(flag_width * longitude_div / step_lon + draw_offset_x * 2)
    map_height = int(flag_height * latitude_div / step_lat + draw_offset_y * 2)
    back_ground_color = (255, 255, 255)
    im = Image.new("RGBA", (map_width, map_height), back_ground_color)
    draw = ImageDraw.Draw(im)

    pos_arr2 = []
    pos_arr = []

    with open('countries.geojson') as f:
        data = json.load(f)

    countries = {}
    for feature in data["features"]:
        geom = feature["geometry"]
        country = feature["properties"]["ISO_A2"]
        countries[country] = prep(shape(geom))

    latitude_steps = 0
    while latitude_steps < latitude_div:
        longitude_steps = 0
        while longitude_steps < longitude_div:
            pos_arr.append((latitude_start - latitude_steps, longitude_start + longitude_steps))
            longitude_steps += step_lon
        latitude_steps += step_lat
    pos_arr2 = get_country(pos_arr)

    flag_dict = {}

    array_pos = 0

    latitude_steps = 0
    while latitude_steps < latitude_div:
        longitude_steps = 0
        while longitude_steps < longitude_div:
            country = pos_arr2[array_pos]
            if country is not None:
                if country in flag_dict:
                    chosen_flag = flag_dict[country]
                else:
                    chosen_flag = Image.open(f'openmoji-618x618-color/{country}')
                    chosen_flag = autocrop_image(chosen_flag)
                    chosen_flag = chosen_flag.resize((flag_width, flag_height), resample=Image.NEAREST)
                    flag_dict[country] = chosen_flag
                draw_x = int(draw_offset_x + longitude_steps * flag_width * 1 / step_lon - flag_width / 2)
                draw_y = int(draw_offset_y + latitude_steps * flag_height * 1 / step_lat - flag_height / 2)
                im.paste(chosen_flag, (draw_x, draw_y))
            array_pos += 1
            longitude_steps += step_lon
        latitude_steps += step_lat

    # im.save('data/dst/rocket_pillow_paste_pos.jpg', quality=95)

    im.show()
