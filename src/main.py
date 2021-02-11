import json

from PIL import Image
from shapely.geometry import Point
from shapely.geometry import shape
from shapely.prepared import prep


def __prepare_country_data(json_file):
    with open(json_file) as f:
        data = json.load(f)

    countries = {}
    for feature in data["features"]:
        geom = feature["geometry"]
        country_code = feature["properties"]["ISO_A2"]
        countries[country_code] = prep(shape(geom))
    return countries


def __calc_flag_height(flag_width, folder_name):
    blueprint_flag = Image.open(f'{folder_name}/1F1E6-1F1E8.png')
    blueprint_flag = __autocrop_image(blueprint_flag)
    scale_factor = flag_width / blueprint_flag.width
    flag_height = int(blueprint_flag.height * scale_factor)
    return flag_height


def __autocrop_image(image, border=0):
    """
    @author odyniec https://gist.github.com/odyniec/3470977
    """
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


def __create_coordinate_list(latitude_start, latitude_div, step_lat, longitude_start, longitude_div, step_lon):
    coordinates = []
    latitude_steps = 0
    while latitude_steps < latitude_div:
        longitude_steps = 0
        while longitude_steps < longitude_div:
            coordinates.append((latitude_start - latitude_steps, longitude_start + longitude_steps))
            longitude_steps += step_lon
        latitude_steps += step_lat
    return coordinates


def __create_coordinate_to_country_code_dict(coord_list, all_countries_data):
    pos_country_dict = {}
    for pos in coord_list:
        point = Point(pos[1], pos[0])  # lon, lat
        found_country = None
        for country_code, geom in all_countries_data.items():
            if geom.contains(point):
                found_country = country_code
                break
        pos_country_dict[pos] = found_country
    return pos_country_dict


def __calc_flag_unicode(country_iso2):
    if country_iso2 is None:
        return None
    subchars = []
    for c in country_iso2:
        res = ord(c.capitalize()) - ord('A') + 127462
        subchars.append(hex(res).upper()[2:])
    return subchars[0] + '-' + subchars[1]


def __load_flags_for_country_codes(country_code_list, flag_width, flag_height, folder_name):
    flag_dict = {}
    for country_code in country_code_list:
        if country_code not in flag_dict and country_code is not None:
            flag_code = __calc_flag_unicode(country_code)
            if flag_code is not None:
                try:
                    flag = Image.open(f'{folder_name}/{flag_code}.png')
                    flag = __autocrop_image(flag)
                    flag = flag.resize((flag_width, flag_height), resample=Image.NEAREST)
                    flag_dict[country_code] = flag
                except Exception:
                    pass
    return flag_dict


def __draw_images_on_base(base, images, draw_offset_x, draw_offset_y):
    for image in images:
        draw_x = int(draw_offset_x + image["offset_x"])
        draw_y = int(draw_offset_y + image["offset_y"])
        base.paste(image["image"], (draw_x, draw_y))
    return base


def __save_map_safely(created_map):
    print('saving map...')
    name = 'cool_map'
    counter = 1
    while counter < 100:
        full_name = f'{name}_{counter}.png'
        try:
            with open(f'{name}_{counter}.png'):
                counter += 1
        except IOError:
            created_map.save(full_name)
            return full_name
    return ''


def do_it(latitude_start=90.0, longitude_start=-180.0, latitude_div=180, longitude_div=360, step_lat=1.0,
          background_color=(255, 255, 255, 255), save=False, folder_name='flags'):
    """
    Creates a map made of flag-emojis on a given area with a given precision.
    @param latitude_start: float
    @param longitude_start: float
    @param latitude_div: float
    @param longitude_div: float
    @param step_lat: float; the smaller it is the more precise but larger the map gets. A good range is  0.1 to 1.0
    @param background_color: RGBA
    @param save: bool; if the created map should be saved automatically.
    Will never overwrite a file but instead tries to save under a new filename up to the number 99.
    @param folder_name: the name of the folder where you have your flag-images stored
    @author Rednaxelus
    """
    all_countries_data = __prepare_country_data('countries.geojson')

    draw_offset_x = 100
    draw_offset_y = 100

    flag_width = 32
    flag_height = __calc_flag_height(flag_width, folder_name)

    step_lon = (flag_width / flag_height) * step_lat

    coord_list = __create_coordinate_list(latitude_start, latitude_div, step_lat, longitude_start, longitude_div,
                                          step_lon)

    pos_to_country_dict = __create_coordinate_to_country_code_dict(coord_list, all_countries_data)

    existing_country_codes = pos_to_country_dict.values()

    flag_dict = __load_flags_for_country_codes(existing_country_codes, flag_width, flag_height, folder_name)

    image_array = []
    for position in coord_list:
        country_code = pos_to_country_dict[position]
        if country_code in flag_dict:
            country_flag = flag_dict[country_code]
            image_data = {"image": country_flag,
                          "offset_x": abs(longitude_start - position[1]) * flag_width * 1 / step_lon - flag_width / 2,
                          "offset_y": abs(latitude_start - position[0]) * flag_height * 1 / step_lat - flag_height / 2}
            image_array.append(image_data)

    map_width = int(flag_width * longitude_div / step_lon + draw_offset_x * 2)
    map_height = int(flag_height * latitude_div / step_lat + draw_offset_y * 2)
    base_image = Image.new("RGBA", (map_width, map_height), background_color)

    created_map = __draw_images_on_base(base_image, image_array, draw_offset_x, draw_offset_y)

    if save:
        map_file_name = __save_map_safely(created_map)
        if map_file_name == '':
            print("saving the map failed")
        else:
            print("saved the map successfully as: " + map_file_name)

    created_map.show()


if __name__ == '__main__':
    do_it()  # do_it(73.0, -13.0, 40, 55, 0.5, (255, 255, 255, 0), save=True, 'flags')
