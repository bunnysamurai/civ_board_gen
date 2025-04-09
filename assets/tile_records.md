# Constraints

Rotations of tiles are allowed

Border points don't have to perfectly align.  Maybe at least 2 or 3 do?  Or we can constrain certain tiles to rotate or not.  Ocean boarder points can be ignored.

Edge identifiers do have to perfectly align.

I shouldn't have to be limited to the count of tiles provided via the original image files.  I can generate more if needed?


# Tile Descriptors

```
    Border Points bit encoding: 8 bits to describe if there's a border crossing the edge or not.
      0 = border is not crossing edge
      1 = border is crossing edge

  |-------|-------|-------|-------|-------|-------|-------|-------|
  |   7   |   6   |   5   |   4   |   3   |   2   |   1   |   0   |
  |-------|-------|-------|-------|-------|-------|-------|-------|
  | upper | lower | left  | right | lower | upper | right | left  |
  | LEFT  | LEFT  |BOTTOM |BOTTOM | RIGHT | RIGHT |  TOP  |  TOP  |
  |-------|-------|-------|-------|-------|-------|-------|-------|

                TOP

              0       1
        +-------------------+
        |     |       |     |
        |    /         \    |
      7 |---+           +---| 2
LEFT    |                   |      RIGHT
        |                   |
      6 |---+           +---| 3
        |    \         /    |
        |     |       |     |
        +-------------------+
              5       4

               BOTTOM
```

```
    Edge Encodings: 0 == ocean, 1 = land


  |-------|-------|-------|-------|
  |   3   |   2   |   1   |   0   |
  |-------|-------|-------|-------|
  | LEFT  |BOTTOM | RIGHT |  TOP  |
  |-------|-------|-------|-------|

                TOP

                Edge 0
        +-------------------+
        |                   |
      E |                   | E
      d |                   | d
LEFT  g |                   | g    RIGHT
      e |                   | e
      3 |                   | 1
        |                   |
        |                   |
        +-------------------+
                Edge 2

               BOTTOM
```

| File name | Border Point Mask(lsb on the left, it's reversed, I know) | Edge Identifier Mask(lsb on the left, it's reversed, I know) | Special Flags (bit 0:3 -> if 1, this edge always matches a candidate border from another tile.  In other words, always set border match result to 1) |
| --- | --- | --- | --- |
| Tile_01_0.png | 11001100 | 1010 | 1111 |
| Tile_01_1.png | 11001100 | 1010 | 1111 |
| Tile_01_2.png | 10100101 | 1111 | 0000 |
| Tile_01_3.png | 10100101 | 1111 | 0000 |
| Tile_02_0.png | 10100101 | 1111 | 0000 |
| Tile_02_1.png | 10100101 | 1111 | 0000 |
| Tile_02_2.png | 10100101 | 0000 | 0000 |
| Tile_02_3.png | 10100101 | 0000 | 0000 |
| Tile_03_0.png | 10100101 | 1111 | 0000 |
| Tile_03_1.png | 10100101 | 1111 | 0000 |
| Tile_03_2.png | 10100101 | 0000 | 0000 |
| Tile_03_3.png | 10100101 | 0000 | 0000 |
| Tile_04_0.png | 10100101 | 1111 | 0000 |
| Tile_04_1.png | 10100101 | 1111 | 0000 |
| Tile_04_2.png | 10100101 | 0000 | 0000 |
| Tile_04_3.png | 10100101 | 0000 | 0000 |
| Tile_05_0.png | 10100101 | 1111 | 0000 |
| Tile_05_1.png | 10100101 | 1111 | 0000 |
| Tile_05_2.png | 10100101 | 0000 | 0000 |
| Tile_05_3.png | 10100101 | 0000 | 0000 |
| Tile_06_0.png | 10100101 | 1111 | 0000 |
| Tile_06_1.png | 10100101 | 1111 | 0000 |
| Tile_06_2.png | 10100101 | 0000 | 0000 |
| Tile_06_3.png | 10100101 | 0000 | 0000 |
| Tile_07_0.png | 10100101 | 1111 | 0000 |
| Tile_07_1.png | 10100101 | 1111 | 0000 |
| Tile_07_2.png | 10100101 | 0000 | 0000 |
| Tile_07_3.png | 10100101 | 0000 | 0000 |
| Tile_08_0.png | 10100101 | 1111 | 0000 |
| Tile_08_1.png | 10100101 | 1111 | 0000 |
| Tile_08_2.png | 10100101 | 0000 | 0000 |
| Tile_08_3.png | 10100101 | 0000 | 0000 |
| Tile_09_0.png | 10100101 | 1111 | 0000 |
| Tile_09_1.png | 10100101 | 1111 | 0000 |
| Tile_09_2.png | 10100101 | 0000 | 0000 |
| Tile_09_3.png | 10100101 | 0000 | 0000 |
| Tile_10_0.png | 10100101 | 1111 | 0000 |
| Tile_10_1.png | 10100101 | 1111 | 0000 |
| Tile_10_2.png | 10100101 | 0000 | 0000 |
| Tile_10_3.png | 10100101 | 0000 | 0000 |
| Tile_11_0.png | 10100101 | 1111 | 0000 |
| Tile_11_1.png | 10100101 | 1111 | 0000 |
| Tile_11_2.png | 10100101 | 0000 | 0000 |
| Tile_11_3.png | 10100101 | 0000 | 0000 |
| Tile_12_0.png | 01000000 | 1000 | 0111 |
| Tile_12_1.png | 10100101 | 1111 | 0000 |
| Tile_12_2.png | 00001000 | 0010 | 1101 |
| Tile_12_3.png | 10000000 | 1000 | 0111 |
| Tile_13_0.png | 00010010 | 0101 | 1010 |
| Tile_13_1.png | 00000100 | 0010 | 1101 |
| Tile_13_2.png | 00011010 | 0111 | 1000 |
| Tile_13_3.png | 00100001 | 0101 | 1010 |
| Tile_14_0.png | 00101001 | 0111 | 1000 |
| Tile_14_1.png | 00010110 | 0111 | 1000 |
| Tile_14_2.png | 00100101 | 0111 | 1000 |
| Tile_14_3.png | 01010010 | 1101 | 0010 |
| Tile_15_0.png | 10010010 | 1101 | 0010 |
| Tile_15_1.png | 01100001 | 1101 | 0010 |
| Tile_15_2.png | 10100001 | 1101 | 0010 |
| Tile_15_3.png | 01010010 | 1101 | 0010 |
| Tile_16_0.png | 10010010 | 1101 | 0010 |
| Tile_16_1.png | 01100001 | 1101 | 0010 |
| Tile_16_2.png | 00011010 | 0111 | 1000 |
| Tile_16_3.png | 10100001 | 0111 | 1000 |
| Tile_17_0.png | 00101001 | 0111 | 1000 |
| Tile_17_1.png | 00010110 | 0111 | 1000 |
| Tile_17_2.png | 00100101 | 0111 | 1000 |
| Tile_17_3.png | 00001010 | 0011 | 1100 |
| Tile_18_0.png | 00001010 | 0011 | 1100 |
| Tile_18_1.png | 00000110 | 0011 | 1100 |
| Tile_18_2.png | 00001010 | 0011 | 1100 |
| Tile_18_3.png | 00000110 | 0011 | 1100 |
| Tile_19_0.png | 00000110 | 0011 | 1100 |
| Tile_19_1.png | 00000110 | 0011 | 1100 |
| Tile_19_2.png | 00001001 | 0011 | 1100 |
| Tile_19_3.png | 00000110 | 0011 | 1100 |
| Tile_20_0.png | 00001001 | 0011 | 1100 |
| Tile_20_1.png | 00000101 | 0011 | 1100 |
| Tile_20_2.png | 00000101 | 0011 | 1100 |
| Tile_20_3.png | 00001001 | 0011 | 1100 |
| Tile_21_0.png | 00000101 | 0011 | 1100 |
| Tile_21_1.png | 00001010 | 0011 | 1100 |
| Tile_21_2.png | 00000110 | 0011 | 1100 |
| Tile_21_3.png | 00001010 | 0011 | 1100 |
| Tile_22_0.png | 00000110 | 0011 | 1100 |
| Tile_22_1.png | 00001001 | 0011 | 1100 |
| Tile_22_2.png | 00000101 | 0011 | 1100 |
| Tile_22_3.png | 00001001 | 0011 | 1100 |
| Tile_23_0.png | 00000000 | 0010 | 1111 |
| Tile_23_1.png | 00000101 | 0011 | 1100 |
| Tile_23_2.png | 00000000 | 0010 | 1111 |
| Tile_23_3.png | 00000000 | 0010 | 1111 |
| Tile_24_0.png | 10100101 | 0000 | 0000 |
| Tile_24_1.png | 00000000 | 0010 | 1111 |
| Tile_24_2.png | 10100101 | 0000 | 0000 |
| Tile_24_3.png | 10100101 | 0000 | 0000 |
| Tile_25_0.png | 10100101 | 0000 | 0000 |
| Tile_25_1.png | 10100101 | 0000 | 0000 |
| Tile_25_2.png | 10100101 | 0000 | 0000 |
| Tile_25_3.png | 10100101 | 0000 | 0000 |
| Tile_26_0.png | 10100101 | 0000 | 0000 |
| Tile_26_1.png | 10100101 | 0000 | 0000 |
| Tile_26_2.png | 10100101 | 0000 | 0000 |
| Tile_26_3.png | 10100101 | 0000 | 0000 |
