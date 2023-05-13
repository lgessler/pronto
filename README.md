# PrOnto
PrOnto is a resource intended for pretrained language model evaluation that is extensible to any language with a 
New Testament translation. **No manual annotation required**!

PrOnto v0.1 comes with 1051 datasets from all of ebible.org's permissively-licensed Bible translations, which span
859 distinct languages. Each dataset is created by aligning verses from the target language's translation
with the New Testament verses included in English OntoNotes, and then projecting annotations from English to the
target language. Currently, each dataset includes data for 5 different sequence classification tasks.

In addition to these premade datasets, you may also provide your own Bible translation and run our dataset
generation code in order to generate a dataset for your own target language. No annotation required!
See [BUILD](./BUILD.md) for details.

For a full description of this resource, see [our paper](./pronto.pdf).

# Download
Please see [our registry](RELEASE_v0.1.md) for a list of Bibles included in the PrOnto release.
As of version 0.1, this includes 1051 Bible translations in 859 distinct languages.

# Usage
You may use the datasets however you like, though we do include 
[a sequence classification module](./pronto/eval/sequence_classifier.py) which is ready to use with the data for our
5 tasks. You may invoke it with `python -m pronto.eval.sequence_classifier`. See 
[here](https://github.com/lgessler/pronto/blob/master/pronto/eval/paper_eval.py#L44L131) for sensible defaults on
each task for its options.

# Development
For information on how to build a PrOnto dataset, see [BUILD](./BUILD.md).
