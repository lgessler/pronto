# Build
## Open-access eBible.org Corpus
1. Ensure OntoNotes is located at `data/ontonotes`.

2. Download source USFX files. Please contact Luke Gessler (lukegessler@gmail.com) for the file.

3. Convert the USFX files into PrOnto's TSV format:

```
$ mkdir data/tsv

# run in serial...
$ for x in `cut -f1 data/languages.tsv`; do
  python -m pronto.scripts.usfx_to_tsv data/usfx/${x}_usfx.xml data/tsv/${x}-bible.tsv;
done

# ...or in parallel
$ for x in `cut -f1 data/languages.tsv`; do
  echo "python -m pronto.scripts.usfx_to_tsv data/usfx/${x}_usfx.xml data/tsv/${x}-bible.tsv;" >> commands.txt
done
$ parallel < commands.txt
```

4. Construct datasets:

```
$ rm -f commands.txt
$ mkdir output_log
# Allow one run to go to completion first
$ LANGUAGE=gulNT tango run conf/main.jsonnet > output_log/gulNT
$ for x in `cut -f1 data/languages.tsv`; do 
  echo "LANGUAGE=$x tango run conf/main.jsonnet > output_log/$x" >> commands.txt; 
done
$ parallel < commands.txt
```
