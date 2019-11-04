from flask import Flask
from flask import request
import cv2
import urllib.request
import numpy as np
import webcolors
from flask import request, jsonify
from sklearn.cluster import KMeans
from collections import Counter
app = Flask(__name__)
app.config["DEBUG"] = True


@app.route('/', methods=['GET'])
def upload_file():
    image = request.args.get('img')
    req = urllib.request.urlopen(image)
    c = get_colors(get_image(req), 10, True)
    colors = []
    for i in c:
        actual_name, closest_name = get_colour_name(i)
        colors.append(closest_name)
    col = colors
    results = []
    for i in col:
        results.append(i)
    return jsonify(results)


def RGB2HEX(color):
    return "#{:02x}{:02x}{:02x}".\
        format(int(color[0]), int(color[1]), int(color[2]))


def get_image(image_path):
    arr = np.asarray(bytearray(image_path.read()), dtype=np.uint8)
    image = cv2.imdecode(arr, -1)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    return image


def get_colors(image, number_of_colors, show_chart):
    modified_image = cv2.\
        resize(image, (600, 400), interpolation=cv2.INTER_AREA)
    modified_image = modified_image.\
        reshape(modified_image.shape[0] * modified_image.shape[1], 3)

    clf = KMeans(n_clusters=number_of_colors)
    labels = clf.fit_predict(modified_image)

    counts = Counter(labels)

    center_colors = clf.cluster_centers_
    # We get ordered colors by iterating through the keys
    ordered_colors = [center_colors[i] / 255 for i in counts.keys()]
    hex_colors = [RGB2HEX(ordered_colors[i] * 255) for i in counts.keys()]

    rgb_colors = [ordered_colors[i] * 255 for i in counts.keys()]
    return rgb_colors


def closest_colour(requested_colour):
    min_colours = {}
    for key, name in webcolors.css3_hex_to_names.items():
        r_c, g_c, b_c = webcolors.hex_to_rgb(key)
        rd = (r_c - requested_colour[0]) ** 2
        gd = (g_c - requested_colour[1]) ** 2
        bd = (b_c - requested_colour[2]) ** 2
        min_colours[(rd + gd + bd)] = name
    return min_colours[min(min_colours.keys())]


def get_colour_name(requested_colour):
    try:
        closest_name = actual_name = webcolors.rgb_to_name(requested_colour)
    except ValueError:
        closest_name = closest_colour(requested_colour)
        actual_name = None
    return actual_name, closest_name


if __name__ == '__main__':
    app.run()
