This dir contains dockerised elasticsearch.
It relies on a file `location_labels.jsonl` that has a TSV of format of
`<uri> <label>`.

Users should then run the following to stand up a local instance of ES at port 9200
```
$ docker-compose up -d
```

Users should then run the following to process `location_labels.jsonl`
into smaller files and in a format that ES can accept as a bulk upload
```
$ ./process.sh
$ ./upload.sh
```

