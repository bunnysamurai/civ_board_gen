
.PHONY: prep

map: prep
	cd assets && python ../src/algo.py trimmed-uniquemodded.json 13 9

prep: assets/unique_onlymodded.json assets/trimmed-uniquemodded.json

assets/unique_onlymodded.json:
	cd assets && tar xf files.tar.zst && python ../tools/rotate_tiles.py unique_only.json

assets/trimmed-uniquemodded.json:
	cd assets && tar xf files.tar.zst && python ../tools/rotate_tiles.py trimmed-unique.json