# Build
## Open-access eBible.org Corpus
1. Ensure OntoNotes is located at `data/ontonotes`.

2. Download source USFX files. Please contact Luke Gessler (lukegessler@gmail.com) for the file.

3. Convert the USFX files into PrOnto's TSV format:

```bash
mkdir data/tsv
# Option 1: run in serial
for x in `cut -f1 data/languages.tsv`; do
  python -m pronto.scripts.usfx_to_tsv data/usfx/${x}_usfx.xml data/tsv/${x}-bible.tsv;
done
# Option 2: run in parallel
for x in `cut -f1 data/languages.tsv`; do
  echo "python -m pronto.scripts.usfx_to_tsv data/usfx/${x}_usfx.xml data/tsv/${x}-bible.tsv;" >> commands.txt
done
parallel < commands.txt
```

4. Construct datasets:

```bash
rm -f commands.txt
mkdir output_log
# Allow one run to go to completion first
LANGUAGE=gulNT tango run conf/main.jsonnet > output_log/gulNT
for x in `cut -f1 data/languages.tsv`; do 
  echo "LANGUAGE=$x tango run conf/main.jsonnet > output_log/$x" >> commands.txt; 
done
parallel < commands.txt
```
