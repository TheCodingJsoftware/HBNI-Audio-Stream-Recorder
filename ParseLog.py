import random
import re

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import themepy
from rich import print

from Graph import ListenersGraph

plt.rcParams["figure.figsize"] = [7.50, 3.50]
plt.rcParams["figure.autolayout"] = True
theme = themepy.Theme()
theme.set_theme("sample-dark")


def parse(path_to_file: str) -> dict:
    valid_regex = (
        r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d{6} - Host:(.*?)Recording stopped)"
    )
    get_listeners_regex = r"((\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d{6}) - Changes: {1,} Listeners Current: (\d{1,}))"
    host_regex = r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d{6} - (Host: ([\W|\w\S\s]{1,})) Description)"
    with open(path_to_file, "r") as f:
        text = f.read()

    matches = re.finditer(valid_regex, text, re.DOTALL | re.MULTILINE)

    data = {}

    for match in matches:
        stream_data = match.group(1)

        listener_matches = re.finditer(get_listeners_regex, stream_data, re.MULTILINE)
        host_matches = re.finditer(host_regex, stream_data, re.MULTILINE)

        for host_match in host_matches:
            host = host_match.group(3)
            # data[host] = []
            r: float = random.random()
            b: float = random.random()
            g: float = random.random()
            color: tuple = (r, g, b)
            data[host] = {"listeners": [], "color": color}

            for listener_match in listener_matches:
                time = listener_match.group(2)
                listners = listener_match.group(3)
                data[host]["listeners"].append({time: listners})

    return data


graph = ListenersGraph(parse(path_to_file="log.txt"))
graph.update()
