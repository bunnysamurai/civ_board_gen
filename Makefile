
.PHONY: prep

map: prep
	cd assets && python ../src/algo.py unique_onlymodded.json 9 6

prep: assets/unique_onlymodded.json

assets/unique_onlymodded.json:
	cd assets && tar xf files.tar.zst && python ../tools/rotate_tiles.py unique_only.json
