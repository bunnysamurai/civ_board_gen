#!/usr/bin/env python

import argparse
import json
from PIL import Image
from enum import Enum
import os
import copy
import sys

class Rot(Enum):
    CW = 1
    CCW = 2
    FULL180 = 3

def to_angle(direction: Rot):
    if direction == Rot.CW:
        return -90
    if direction == Rot.CCW:
        return 90
    if direction == Rot.FULL180:
        return 180
    return 0

def read_json(filepath):
    with open(filepath, 'r') as fid:
        return json.load(fid)

def rotate_image_file(elem, direct: Rot, outdir):
    if os.path.isdir(outdir) is False:
        os.mkdir(outdir)
    
    origfile = elem

    img = Image.open(origfile).rotate(to_angle(direct))

    name, ext = os.path.splitext(os.path.basename(origfile))
    newfilename = os.path.join(outdir, name) + '_' + direct.name + '.png'
    img.save(newfilename)

    return newfilename

def __rotate_string(string, n):
    ''' 
        n < 0 is rotate right
        n > 0 is rotate left
    '''
    return string[n:] + string[:n]

def rotate_edge_mask(elem, direct: Rot):
    if direct == Rot.CW:
        elem = __rotate_string(elem, -1)
    if direct == Rot.CCW:
        elem = __rotate_string(elem, 1)
    if direct == Rot.FULL180:
        elem = __rotate_string(elem, 2)
    return elem

def rotate_sflgs(elem, direct: Rot):
    return rotate_edge_mask(elem, direct)

def rotate_border_mask(elem, direct: Rot):
    if direct == Rot.CW:
        elem = __rotate_string(elem, -2)
    if direct == Rot.CCW:
        elem = __rotate_string(elem, 2)
    if direct == Rot.FULL180:
        elem = __rotate_string(elem, 4)
    return elem

def rotate_tile(elem, direct: Rot, outdir):
    result = copy.deepcopy(elem)
    
    result["file"] = rotate_image_file(result["file"], direct, outdir)
    result["bordermask"] = rotate_border_mask(result["bordermask"], direct)
    result["edgemask"] = rotate_edge_mask(result["edgemask"], direct)
    result["sflg"] = rotate_sflgs(result["sflg"], direct)

    return result

def run_tests():
    test_str = "0011"
    print(f"rotate string {test_str}:")
    for n in range(0,5):
        print(f"{n}: {__rotate_string(test_str, n)}")
    test_str = "1100"
    print(f"-rotate string {test_str}:")
    for n in range(0,5):
        print(f"{-n}: {__rotate_string(test_str, -n)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="create new json with rotated equivalents")
    parser.add_argument("FILE", type=str, help="json tile set")
    parser.add_argument("--test", action="store_true", help="dry run, just run tests")
    parser.add_argument("--outdir", type=str, default="rotated_tiles", help="Output directory.  Default is 'rotated_tiles'")

    args = parser.parse_args()

    if args.test is True:
        run_tests()
        sys.exit(0)

    obj = read_json(args.FILE)
    tile_list = obj["tile_list"]

    rotated_results = []
    for elem in tile_list:
        # don't rotate all ocean tiles, since they don't look as good
        if elem["edgemask"] == "0000":
            continue
        for direction in [Rot.CW, Rot.CCW, Rot.FULL180]:
            rotated_results.append(rotate_tile(elem, direction, args.outdir))
    
    obj["tile_list"] += rotated_results

    newfile, ext = os.path.splitext(args.FILE)
    with open(newfile + "modded" + ext, 'w') as fid:
        json.dump(obj, fid, indent=4)


