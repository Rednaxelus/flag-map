# Press Umschalt+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import json

from PIL import Image, ImageDraw
from shapely.geometry import Point
from shapely.geometry import shape
from shapely.prepared import prep


def prepare_country_data(json_file):
    with open(json_file) as f:
        data = json.load(f)

    countries = {}
    for feature in data["features"]:
        geom = feature["geometry"]
        country_code = feature["properties"]["ISO_A2"]
        countries[country_code] = prep(shape(geom))
    return countries


def calc_flag_height(flag_width):
    blueprint_flag = Image.open(f'openmoji-618x618-color/1F1E6-1F1E8.png')
    blueprint_flag = autocrop_image(blueprint_flag)
    scale_factor = flag_width / blueprint_flag.width
    flag_height = int(blueprint_flag.height * scale_factor)
    return flag_height


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


def create_coordinate_list(latitude_start, latitude_div, longitude_start, longitude_div):
    coordinates = []
    latitude_steps = 0
    while latitude_steps < latitude_div:
        longitude_steps = 0
        while longitude_steps < longitude_div:
            coordinates.append((latitude_start - latitude_steps, longitude_start + longitude_steps))
            longitude_steps += step_lon
        latitude_steps += step_lat
    return coordinates


def create_coordinate_to_country_code_dict(coordinates):
    pos_country_dict = {}
    for pos in coordinates:
        point = Point(pos[1], pos[0])  # lon, lat
        found_country = None
        for country_code, geom in all_countries_data.items():
            if geom.contains(point):
                found_country = country_code
                break
        pos_country_dict[pos] = found_country
    return pos_country_dict


def calc_flag_unicode(country_iso2):
    if country_iso2 is None:
        return None
    subchars = []
    for c in country_iso2:
        res = ord(c.capitalize()) - ord('A') + 127462
        subchars.append(hex(res).upper()[2:])
    return subchars[0] + '-' + subchars[1] + '.png'


def load_flags_for_country_codes(country_code_list):
    flag_dict = {}
    for country_code in country_code_list:
        if country_code not in flag_dict:
            if country_code is not None:
                flag_code = calc_flag_unicode(country_code)
                if flag_code is not None:
                    try:
                        flag = Image.open(f'openmoji-618x618-color/{flag_code}')
                        flag = autocrop_image(flag)
                        flag = flag.resize((flag_width, flag_height), resample=Image.NEAREST)
                        flag_dict[country_code] = flag
                    except:
                        pass
    return flag_dict


def create_image_data_array():
    image_array = []
    for position in coord_list:
        country_code = pos_to_country_dict[position]
        if country_code in flag_dict:
            country_flag = flag_dict[country_code]
            image_data = {}
            image_data["image"] = country_flag
            image_data["offset_x"] = abs(longitude_start - position[1]) * flag_width * 1 / step_lon - flag_width / 2
            image_data["offset_y"] = abs(latitude_start - position[0]) * flag_height * 1 / step_lat - flag_height / 2
            image_array.append(image_data)
    return image_array


def create_base_image(map_width, map_height, background_color):
    im = Image.new("RGBA", (map_width, map_height), background_color)
    ImageDraw.Draw(im)
    return im


def draw_images_on_base(base, images, draw_offset_x, draw_offset_y):
    for image in images:
        draw_x = int(draw_offset_x + image["offset_x"])
        draw_y = int(draw_offset_y + image["offset_y"])
        base.paste(image["image"], (draw_x, draw_y))
    return base


if __name__ == '__main__':
    all_countries_data = prepare_country_data('countries.geojson')

    draw_offset_x = 100
    draw_offset_y = 100

    flag_width = 32
    flag_height = calc_flag_height(flag_width)

    latitude_start = 73.0  # 90
    longitude_start = -13.0  # -180
    step_lat = 1  # 0.5
    step_lon = (flag_width / flag_height) * step_lat

    latitude_div = 40  # 180
    longitude_div = 55  # 360

    coord_list = create_coordinate_list(latitude_start, latitude_div, longitude_start, longitude_div)

    pos_to_country_dict = create_coordinate_to_country_code_dict(coord_list)

    existing_country_codes = pos_to_country_dict.values()

    flag_dict = load_flags_for_country_codes(existing_country_codes)

    image_array = create_image_data_array()

    map_width = int(flag_width * longitude_div / step_lon + draw_offset_x * 2)
    map_height = int(flag_height * latitude_div / step_lat + draw_offset_y * 2)
    background_color = (255, 255, 255)
    base_image = create_base_image(map_width, map_height, background_color)

    created_map = draw_images_on_base(base_image, image_array, draw_offset_x, draw_offset_y)

    # created_map.save('cool_map.png')

    created_map.show()
