# Press Umschalt+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

from PIL import Image, ImageDraw
from geopy.geocoders import Nominatim


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


def give_country(Latitude="25.594095", Longitude="85.137566"):
    # initialize Nominatim API
    geolocator = Nominatim(user_agent="emoji-map")

    location = geolocator.reverse(Latitude + "," + Longitude)

    if location != None:
        address = location.raw['address']

        # traverse the data
        city = address.get('city', '')
        state = address.get('state', '')
        country = address.get('country', '')
        code = address.get('country_code')
        zipcode = address.get('postcode')
        # print('City : ', city)
        # print('State : ', state)
        print('Country : ', country)
        # print('Zip Code : ', zipcode)

        subchars = []
        for c in code:
            res = ord(c.capitalize()) - ord('A') + 127462
            subchars.append(hex(res).upper()[2:])

        res3 = subchars[0] + '-' + subchars[1] + '.png'

        return res3

    return None

    # print(ord(flag.flag("IL")[0]))


if __name__ == '__main__':

    im1 = Image.open(f'openmoji-618x618-color/1F1E6-1F1E8.png')
    im1 = autocrop_image(im1)

    flag_width = 32
    scale_factor = flag_width / im1.width
    flag_height = int(im1.height * scale_factor)

    im1 = im1.resize((flag_width, flag_height), resample=Image.NEAREST)

    latitude_start = 53.0
    longitude_start = 3.0
    step = 1

    latitude_div = 10
    longitude_div = 2 * latitude_div

    draw_offset_x = 100
    draw_offset_y = 100

    map_width = int(flag_width * longitude_div / step + draw_offset_x * 2)
    map_height = int(flag_height * latitude_div / step + draw_offset_y * 2)
    back_ground_color = (255, 255, 255)
    im = Image.new("RGBA", (map_width, map_height), back_ground_color)
    draw = ImageDraw.Draw(im)

    flag_dict = {}

    latitude_steps = 0
    while latitude_steps < latitude_div:
        longitude_steps = 0
        while longitude_steps < longitude_div:
            country = give_country(str(latitude_start - latitude_steps), str(longitude_start + longitude_steps))
            if country is not None:
                if country in flag_dict:
                    chosen_flag = flag_dict[country]
                else:
                    chosen_flag = Image.open(f'openmoji-618x618-color/{country}')
                    chosen_flag = autocrop_image(chosen_flag)
                    chosen_flag = chosen_flag.resize((flag_width, flag_height), resample=Image.NEAREST)
                    flag_dict[country] = chosen_flag
                draw_x = int(draw_offset_x + longitude_steps * flag_width * 1 / step - flag_width / 2)
                draw_y = int(draw_offset_y + latitude_steps * flag_height * 1 / step - flag_height / 2)
                im.paste(chosen_flag, (draw_x, draw_y))
            longitude_steps += step
        latitude_steps += step
    # im.save('data/dst/rocket_pillow_paste_pos.jpg', quality=95)

    im.show()
