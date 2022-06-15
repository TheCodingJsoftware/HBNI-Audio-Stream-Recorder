import json
import random
from datetime import datetime

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import themepy
from git import Repo
from scipy.interpolate import make_interp_spline

from GlobalVariables import FOLDER_LOCATION, Colors

theme = themepy.Theme()
theme.set_theme("sample-dark")


# > This class is a graph of listeners
class ListenersGraph:
    def __init__(self, listeners_count: dict):
        """
        This function takes a dictionary as an argument and assigns it to the listeners_count attribute
        of the class.

        Args:
          listeners_count (dict): dict
        """
        self.listeners_count = listeners_count

        self.fig, self.ax = plt.subplots(1, 1)
        plt.grid(axis="y", color="0.5")
        plt.grid(axis="x", color="0.5")
        self.fig.subplots_adjust(bottom=0.2)

    def update(self) -> None:
        """
        It takes the data from the listeners_count dictionary and plots it on a graph
        """
        colonies = list(self.listeners_count.keys())
        for colony in colonies:
            values = []
            dates = []
            # indexes = []
            for i, _ in enumerate(self.listeners_count[colony]["listeners"]):
                try:
                    date = list(self.listeners_count[colony]["listeners"][i].keys())[0]
                except Exception:
                    continue
                dates.append(date)
                # indexes.append(i)
                values.append(int(self.listeners_count[colony]["listeners"][i][date]))

            # Smooth interpretation of data
            # indexes = np.array(indexes)
            # smooth = make_interp_spline(indexes, values)

            # smooth_x = np.linspace(indexes.min(), indexes.max(), 500)
            # smooth_y = smooth(smooth_x)

            # self.ax.plot(smooth_x, smooth_y, color=(0.5, 0.5, 0.5), alpha=0.6)

            self.ax.plot(
                dates,
                values,
                "-",
                color=self.listeners_count[colony]["color"],
                label=colony,
            )
            self.ax.set_xticklabels(dates, rotation=45, ha="right")
        locator = mticker.MultipleLocator(15)
        self.ax.xaxis.set_major_locator(locator)
        plt.legend()
        self.fig.savefig(f"{FOLDER_LOCATION}/graph.png")
        self.__upload_graph()

    def archive(self, host: str) -> None:
        """
        It takes a hostname, and saves the data in a JSON file, and then plots the data in a PNG file

        Args:
          host (str): Hostname of broadcast
        """
        title = host.replace("/", "").title()
        with open(
            f'{FOLDER_LOCATION}/logs/{datetime.now().strftime("%Y-%m-%d-%H-%M")} - {title}.json',
            "w",
        ) as f:
            json.dump(self.listeners_count[host], f, ensure_ascii=False, indent=4)

        values = []
        dates = []
        for i, _ in enumerate(self.listeners_count[host]["listeners"]):
            date = list(self.listeners_count[host]["listeners"][i].keys())[0]
            dates.append(date)
            values.append(int(self.listeners_count[host]["listeners"][i][date]))
        self.ax.plot(
            dates, values, color=self.listeners_count[host]["color"], label=title
        )
        self.ax.set_xticklabels(dates, rotation=45, ha="right")
        locator = mticker.MultipleLocator(15)
        self.ax.xaxis.set_major_locator(locator)
        plt.legend()
        self.fig.savefig(
            f"{FOLDER_LOCATION}/logs/{datetime.now().strftime('%Y-%m-%d-%H-%M')} - {title}.png"
        )

    def __upload_graph(self, message: str = "Updated graph.png") -> None:
        """
        It adds the file to the git index, commits it, and pushes it to the remote origin
        """
        repo = Repo(".")  # if repo is CWD just do '.'
        repo.index.add(["graph.png"])
        repo.index.commit(message)
        origin = repo.remote("origin")
        origin.push()
        print(
            f"{Colors.ENDC}{Colors.BOLD}{datetime.now()}{Colors.ENDC} - {Colors.OKGREEN}{message}{Colors.ENDC}"
        )
