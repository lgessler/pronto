local ontonotes_path = "data/ontonotes/english/annotations/pt/";
local bible_path = "data/lat-clementine.tsv";

{
    steps: {
        ontonotes_data: {
            type: "pronto.steps::read_ontonotes",
            path: ontonotes_path,
        },
        bible_data: {
            type: "pronto.steps::read_bible_tsv",
            path: bible_path,
        },
        aligned_verses: {
            type: "pronto.steps::align_verses",
            bible_data: { type: "ref", ref: "bible_data" },
            ontonotes_data: { type: "ref", ref: "ontonotes_data" },
        }
    }
}
