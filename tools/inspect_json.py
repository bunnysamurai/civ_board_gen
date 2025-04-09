#!/usr/bin/env python

import argparse
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import json

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="merp")
    parser.add_argument("JSON", type=str, help="A tile record json")

    args = parser.parse_args()

    with open(args.JSON, 'r') as fid:
        obj = json.load(fid)

        for tile in obj["tile_list"]:
            brd = tile["bordermask"]
            img = Image.open(tile["file"])
            edge = tile["edgemask"]
            sflg = tile["sflg"]

            plt.subplot(2,2,1)
            plt.imshow(img)
            plt.title(tile["file"])

            plt.subplot(2,2,2)
            plt.text(0.5, 0.8, "TOP")
            plt.text(0.5, 0.7, brd[0:2])
            plt.text(0.8, 0.5, "RHT")
            plt.text(0.7, 0.5, brd[2:4])
            plt.text(0.5, 0.2, "BOT")
            plt.text(0.5, 0.3, brd[4:6])
            plt.text(0.2, 0.5, "LFT")
            plt.text(0.33, 0.5, brd[6:8])

            plt.subplot(2,2,3)
            plt.text(0.5, 0.8, "TOP")
            plt.text(0.5, 0.7, edge[0])
            plt.text(0.8, 0.5, "RHT")
            plt.text(0.7, 0.5, edge[1])
            plt.text(0.5, 0.2, "BOT")
            plt.text(0.5, 0.3, edge[2])
            plt.text(0.2, 0.5, "LFT")
            plt.text(0.33, 0.5, edge[3])
            plt.title('edge')

            plt.show()



