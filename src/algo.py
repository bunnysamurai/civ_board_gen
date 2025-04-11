#!/usr/bin/env python

from PIL import Image
from enum import Enum
import numpy as np
import json
import random
import copy
import matplotlib.pyplot as plt
import sys
import argparse
import skimage

DEBUG_RUN_TESTS = False
DEBUG_PLOTS = False

# ================================================================================= #
#                    _____                _____            
#                   |  ___| __ ___  ___  |  ___|   _ _ __  
#                   | |_ | '__/ _ \/ _ \ | |_ | | | | '_ \ 
#                   |  _|| | |  __/  __/ |  _|| |_| | | | |
#                   |_|  |_|  \___|\___| |_|   \__,_|_| |_|
#
# ================================================================================= #
def get_4adj_neighbors(xyloc):
    # we'll go in the same order as edges
    #
    #               TOP
    #      +-------------------+
    #      |                   |
    #      |                   |
    #  LFT |         X         |  RHT
    #      |                   |
    #      |                   |
    #      +-------------------+
    #               BOT


    # top -> xyloc + [0, -1]
    # rht -> xyloc + [ 1, 0]
    # bot -> xyloc + [0,  1]
    # lft -> xyloc + [-1, 0]

    x, y = xyloc
    top = x,     y - 1
    rht = x + 1, y
    bot = x,     y + 1
    lft = x - 1, y
    return [top, rht, bot, lft]

def clamp_location(xyloc, width, height):
    return min(max(0, xyloc[0]), width-1), min(max(0, xyloc[1]), height-1)

def expand_to_8bit(mask4b):
    expnded = ""
    for ii in range(0,4):
        expnded += "11" if ( mask4b >> ii & 0b1 ) else "00"
    return int(expnded,2)

# ================================================================================= #
#                             _____ _ _           
#                            |_   _(_) | ___  ___ 
#                              | | | | |/ _ \/ __|
#                              | | | | |  __/\__ \
#                              |_| |_|_|\___||___/
#
# ================================================================================= #
class TileRotation(Enum):
    NONE = 1
    CW = 2
    CCW = 3
    TURN180 = 4

class TileSide(Enum):
    TOP = 1
    RHT = 2
    BOT = 3
    LFT = 4

class TileVertex:
    def __init__(self, pt, edge_id_mask):
        self.pt = pt
        self.eid = edge_id_mask

class TileEdge:
    def __init__(self, vert1: TileVertex, vert2: TileVertex):
        self.verts = (vert1, vert2)
        self.eid = self.determine_edge_mask()
        self.border_mask = None
        self.sflgs = None

    def determine_edge_mask(self):
        # if they are both land, then this is a land edge
        if all([v.eid == 1 for v in self.verts]):
            return 1
        # ocean otherwise
        return 0

    def contains(self, pt1, pt2):
        v1 = self.verts[0]
        v2 = self.verts[1]
        return ( v1.pt == pt1 and v2.pt == pt2 ) or ( v1.pt == pt2 and v2.pt == pt1)

class TileElement:
    def __init__(self, border_point_mask, edge_id_mask, special_flags, imgfile: str):
        self.border_point_mask = border_point_mask
        self.edge_id_mask = edge_id_mask
        self.special_flags = special_flags
        self.imgfile = imgfile

    def edge_id(self, side: TileSide):
        if side == TileSide.TOP:
            return self.edge_id_mask & 1
        if side == TileSide.RHT:
            return (self.edge_id_mask >> 1) & 1
        if side == TileSide.BOT:
            return (self.edge_id_mask >> 2) & 1
        if side == TileSide.LFT:
            return (self.edge_id_mask >> 3) & 1
    
    def border_id(self, side: TileSide):
        if side == TileSide.TOP:
            return self.border_point_mask & 0b11
        if side == TileSide.RHT:
            return (self.border_point_mask >> 2) & 0b11
        if side == TileSide.BOT:
            return (self.border_point_mask >> 4) & 0b11
        if side == TileSide.LFT:
            return (self.border_point_mask >> 6) & 0b11

    def ismatching(self, other, edgemask=int("1111",2)):
        # edgemask removes ALL constraints on this edge
        # edges must ALWAYS match, unless masked out
        # borders are a bit harder, as we sometimes want to ignore this
        other_border_ignore_mask = (other.special_flags ^ 0b1111) & 0b1111
        self_border_ignore_mask = (self.special_flags ^ 0b1111) & 0b1111
        border_ignore_mask = self_border_ignore_mask & other_border_ignore_mask
        def shrink(mask8b):
            # 'or' each pair of bits together
            acc = 0
            for n in range(0,4):
                acc |= ( ( mask8b >> 2*n ) & 0b1 | ( mask8b >> (2*n + 1) ) & 0b1 ) << n
            return acc
        border_match = shrink(self.border_point_mask ^ other.border_point_mask) & border_ignore_mask 
        edge_match = self.edge_id_mask ^ other.edge_id_mask
        return (border_match | edge_match) & edgemask == 0

    def ignore_border_flag(self, side: TileSide):
        if side == TileSide.TOP:
            return self.special_flags & 1
        if side == TileSide.RHT:
            return (self.special_flags >> 1) & 1
        if side == TileSide.BOT:
            return (self.special_flags >> 2) & 1
        if side == TileSide.LFT:
            return (self.special_flags >> 3) & 1

    def render(self):
        if self.imgfile is not None:
            return np.asarray(Image.open(self.imgfile))
        else:
            return np.zeros((1,1,3), dtype=np.uint8)

def print_tile(tile: TileElement, mask, figid=1):
    def to_string(value, n):
        result = ""
        for i in range(0, n):
            result += "1" if (value >> i)& 0b1 == 1 else "0"
        return result # lsb is on the left

    brd = to_string(tile.border_point_mask, 8)
    edge = to_string(tile.edge_id_mask, 4)
    sflg = to_string(tile.special_flags, 4)

    plt.figure(figid)
    plt.subplot(2,2,1)
    plt.imshow(tile.render())
    plt.title(f"neighbour_edge_mask: {mask:04b}")

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

    plt.subplot(2,2,4)
    plt.text(0.5, 0.8, "TOP")
    plt.text(0.5, 0.7, sflg[0])
    plt.text(0.8, 0.5, "RHT")
    plt.text(0.7, 0.5, sflg[1])
    plt.text(0.5, 0.2, "BOT")
    plt.text(0.5, 0.3, sflg[2])
    plt.text(0.2, 0.5, "LFT")
    plt.text(0.33, 0.5, sflg[3])
    plt.title('ignore border constraint')


class TileSet:
    def __init__(self, my_json_file):
        self.tile_width, self.tile_height = self._parse_tile_width_height(my_json_file)
        self.tile_dtype = np.uint8
        self.tile_channels = 3
        self.tiles = self._parse_tiles(my_json_file) # a list of TileElement

    def init_copy_with_new_tiles(self, new_tiles):
        result = copy.deepcopy(self)
        result.tiles = new_tiles
        return result

    def find_tile(self, tile: TileElement, select_mask = int("1111", 2)):
        def MatchTileMask(candidate):
            return tile.ismatching(candidate, select_mask)
        matches = [tile for tile, match in zip(self.tiles, map(MatchTileMask, self.tiles)) if match is True] 
        return matches

    def find_border_mask(self, brdmask, selectmask = int("1111", 2)):
        def MatchBorderMask(tile):
            # clear any selectmask bits if this tile doesn't care about them
            tmpselect = selectmask & ( ~(tile.special_flags) & 0b1111 )
            return (tile.border_point_mask ^ brdmask) & expand_to_8bit(tmpselect) == 0
        matches = [tile for tile, match in zip(self.tiles, map(MatchBorderMask, self.tiles)) if match is True] 
        return matches

    def find_edge_mask(self, edgemask, selectmask = int("1111", 2)):
        def MatchEdgeMask(tile):
            return ( tile.edge_id_mask ^ edgemask ) & selectmask == 0
        matches = [tile for tile, match in zip(self.tiles, map(MatchEdgeMask, self.tiles)) if match is True] 
        return matches

    def create_numpy_array_for_tile_map(self, map_width, map_height):
        full_width = self.tile_width * map_width
        full_height = self.tile_height * map_height
        return np.zeros((full_height, full_width, self.tile_channels), dtype=self.tile_dtype)
    
    def insert_tile(self, dataimg, x, y, element: TileElement):
        ys = y*self.tile_height
        ye = (y+1)*self.tile_height
        xs = x*self.tile_width
        xe = (x+1)*self.tile_width
        dataimg[ys:ye,xs:xe,:] = np.asarray(Image.fromarray(element.render()).resize((self.tile_height, self.tile_width)))
        return dataimg

    def _parse_tile_width_height(self, json_file: str):
        with open(json_file, 'r') as fid:
            obj = json.load(fid)
            return obj["tile_width"], obj["tile_height"]

    def _parse_tiles(self, json_file: str):
        with open(json_file, 'r') as fid:
            obj = json.load(fid)
            result = []
            for c in obj["tile_list"]:
                result.append(TileElement(border_point_mask=int(c["bordermask"][::-1], 2), edge_id_mask=int(c["edgemask"][::-1],2), special_flags=int(c["sflg"][::-1],2), imgfile=c["file"]))
            return result

# ================================================================================= #
#             __  __               __  __       _    _             
#            |  \/  | __ _ _ __   |  \/  | __ _| | _(_)_ __   __ _ 
#            | |\/| |/ _` | '_ \  | |\/| |/ _` | |/ / | '_ \ / _` |
#            | |  | | (_| | |_) | | |  | | (_| |   <| | | | | (_| |
#            |_|  |_|\__,_| .__/  |_|  |_|\__,_|_|\_\_|_| |_|\__, |
#                         |_|                                |___/ 
# ================================================================================= #
class MapPixel:
    def __init__(self, location_xy, element = None):
        self.location_xy = location_xy
        self.element = element
        self.neighbors = get_4adj_neighbors(self.location_xy)
        
    

class MapMaker:
    '''
    tile_set : list of dict
    map_wh : tuple of int
    '''
    def __init__(self, tile_set, map_wh):
        self.width, self.height = map_wh
        self.tile_set = tile_set
        self._map = self._create_map() # a list of MapPixels

    '''
    The business
    '''
    def _create_map(self):
        # Now the fun begins.  
        # working_map = self._the_real_random_map(self._random_strategy())
        working_map = self._the_real_random_map(self._parceled_strategy())
        return working_map

    def _init_map(self):
        result = []
        for y in range(0,self.height):
            for x in range(0, self.width):
                result.append(MapPixel(location_xy=(x,y)))
        return result

    def _random_strategy(self):
        def choose_randomly():
            return 1 if random.random() > 0.30 else 0
        def capture():
            verts = []
            for row in range(0, self.height+1):
                for col in range(0, self.width+1):
                    # initialize border verticies with 0 (ocean)
                    edge_val = 0 if row == 0 or col == 0 or row == self.height or col == self.width else choose_randomly()
                    verts.append(TileVertex(pt=(col,row), edge_id_mask=edge_val))
            return verts
        return capture

    def _parceled_strategy(self):
        def choose_randomly():
            return 1 if random.random() > 0.30 else 0
        def create_parcels(width, height):
            # divide up the possible verticies into 3 groups:
            #
            #   +--------------+
            #   |     |        |
            #   |-----*        |
            #   |     |        |
            #   +--------------+
            center_point = [width//2, height//2]
            # add noise
            center_point[0] += random.randint(-2,3)
            center_point[1] += random.randint(-2,3)
            # we can now define 3 rectangles
            rect1 = [0, 0, *center_point]
            rect2 = [0, center_point[1], center_point[0], height - center_point[1]]
            rect3 = [center_point[0], 0, width - center_point[0], height]

            result = []
            for r in (rect1, rect2, rect3):
                x, y, w, h = r
                points = []
                for yy in range(y, y+h):
                    for xx in range(x, x+w):
                        points.append([xx,yy])
                result.append(np.asarray(points))
            return result

        parcels = create_parcels(self.width+1, self.height+1)

        def capture():
            def generate(parsec):
                verts = []
                minC, minR = np.min(parsec,0)
                maxC, maxR = np.max(parsec,0)
                for col, row in parsec:
                    # initialize border verticies with 0 (ocean)
                    if row == minR or col == minC or row == maxR or col == maxC:
                        verts.append(TileVertex(pt=(col,row), edge_id_mask=0))
                    else:
                        verts.append(TileVertex(pt=(col,row), edge_id_mask=choose_randomly()))
                return verts
            verticies = []
            for p in parcels:
                for tmp in generate(p):
                    verticies.append(tmp)
            return verticies

        return capture

    def _the_real_random_map(self, vertex_assignment_strategy):
        thismap = self._init_map()

        # we're going to define the edges, instead of wholesale tiles
        # then, we'll grab a match from the tile set since we should have the edges well defined

        # apparently the way to go is to store both the verticies and the edges

        # we'll start with a vertex approach
        # IMPORTANT this is then entry point for continent creation algorithms
        verts = vertex_assignment_strategy()

        # iterate through each vertex, defining each edge ahead of it, with boundary clamping
        def find_vert(vert_list, x, y):
            result = [idx for idx, v in enumerate(vert_list) if v.pt == (x,y)]
            assert(len(result) == 1)
            return result[0]
        edges = []
        for row in range(0, self.height+1):
            for col in range(0,self.width+1):
                cur_idx = find_vert(verts, col, row)
                # at this vertex, there is one extending to the right (maybe) 
                # and one extending below (maybe)
                if col+1 < self.width+1:
                    cad_idx = find_vert(verts, col+1, row)
                    edges.append(TileEdge(vert1=verts[cur_idx], vert2=verts[cad_idx]))
                if row+1 < self.height+1:
                    rad_idx = find_vert(verts, col, row+1)
                    edges.append(TileEdge(vert1=verts[cur_idx], vert2=verts[rad_idx]))
        
        # now that we have the edges defined, let's start making matches
        # we'll define the anchor point for a tile to be the top-left vertex
        def find_edge(edge_list, pt1, pt2):
            result = [(e,idx) for idx, e in enumerate(edge_list) if e.contains(pt1, pt2)]
            assert(len(result) == 1)
            return result[0]
        def to_TileElement(top: TileEdge, lft: TileEdge, bot: TileEdge, rht: TileEdge):
            bpm = 0
            sflgs = 0
            eid = 0
            for n, itr in enumerate((top,rht,bot,lft)):
                brdmsk = itr.border_mask
                # need to switch the bits around if the edge is top or lft
                # why?  because the top edge is another tile's bottom, 
                # which, due to the encoding scheme, is backwards
                # This only applies to the top and left because of the order
                # of iteration through the edge list
                if n == 0 or n == 3:
                    if brdmsk == 1:
                        brdmsk = 2
                    elif brdmsk == 2:
                        brdmsk = 1
                bpm |= 0 if brdmsk is None else brdmsk << ( 2*n )
                sflgs |= 1<<n if itr.sflgs is None else itr.sflgs << n
                eid |= itr.eid << n
            return TileElement(bpm, eid, sflgs, None)
        def update_edges(top: TileEdge, lft: TileEdge, bot: TileEdge, rht: TileEdge, tile):
            result = []
            for e, side in zip((top, lft, bot, rht), (TileSide.TOP, TileSide.LFT, TileSide.BOT, TileSide.RHT)):
                e.eid = tile.edge_id(side)
                e.border_mask = tile.border_id(side)
                e.sflgs = tile.ignore_border_flag(side)
                result.append(e)
            return result

        for row in range(0, self.height):
            for col in range(0, self.width):
                # grab our four edges
                top, tid = find_edge(edges, (col,row), (col+1,row))
                lft, lid = find_edge(edges, (col,row),(col,row+1))
                bot, bid = find_edge(edges, (col,row+1), (col+1,row+1))
                rht, rid = find_edge(edges, (col+1,row),(col+1,row+1))
                tile_to_find = to_TileElement(top, lft, bot, rht)
                candidates = self.tile_set.find_tile(tile_to_find)
                tile_found = candidates[self._help_pick_idx(candidates)]
                thismap[row*self.width + col] = MapPixel(location_xy=(col,row), element=tile_found)
                # once we find our tile, update the edges with it's constraints, 
                # namely, border mask and special flags
                edges[tid], edges[lid], edges[bid], edges[rid] = update_edges(top,lft,bot,rht,tile_found)
        
        return thismap

    def _help_pick_idx(self, listing):
        return random.randint(0, len(listing)-1)

    '''
    returns an image of the full map
    '''
    def render(self):
        img = self.tile_set.create_numpy_array_for_tile_map(self.width, self.height)
        for pix in self._map:
            x, y = pix.location_xy
            if pix.element is None:
                pix.element = TileElement(0b0000,0b0000,0b0000,None)
            img = self.tile_set.insert_tile(img, x, y, pix.element)
        return img

def run_tests():
    record_file = "./tile_recordsmodded.json"
    tile_set = TileSet(my_json_file=record_file)

    test_tile = tile_set.tiles[0]
    print(f"expect true: {test_tile.ismatching(test_tile)}")
    print_tile(test_tile, 0b1111)
    plt.show()


    test_tile = TileElement(border_point_mask=0b1111, edge_id_mask=0b0010, special_flags=1101, imgfile=None)
    print_tile(test_tile, 0b1111)
    plt.show()


# ================================================================================= #
#         __  __       _         ____            _                     
#        |  \/  | __ _(_)_ __   | __ ) _   _ ___(_)_ __   ___  ___ ___ 
#        | |\/| |/ _` | | '_ \  |  _ \| | | / __| | '_ \ / _ \/ __/ __|
#        | |  | | (_| | | | | | | |_) | |_| \__ \ | | | |  __/\__ \__ \
#        |_|  |_|\__,_|_|_| |_| |____/ \__,_|___/_|_| |_|\___||___/___/
#
# ================================================================================= #
if __name__ == "__main__":
    if DEBUG_RUN_TESTS:
        run_tests()
    else:
        MAXTRIES = 1
        parser = argparse.ArgumentParser(description="Make a map for Civ III, the Boardgame!")
        parser.add_argument("TILESET", type=str, help=".json of the tile set to use")
        parser.add_argument("WIDTH", type=int, help="Map width, in tiles")
        parser.add_argument("HEIGHT", type=int, help="Map height, in tiles")

        args = parser.parse_args()

        MAPW = args.WIDTH
        MAPH = args.HEIGHT
        tileset = TileSet(my_json_file=args.TILESET)
        maker = MapMaker(tileset, map_wh=(MAPW, MAPH))
        plt.figure(24511)
        plt.imshow(maker.render())
        plt.show()
else:
    pass # explicitly

