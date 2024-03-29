local ontonotes_path = "data/ontonotes/english/annotations/pt/";
local language = "hincv";
local bible_path = "data/tsv/" + language + "-bible.tsv";
local output_dir = "data/output/" + language;

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
        },
        process_verses: {
            type: "pronto.steps::generate_task_data",
            verses: { type: "ref", ref: "aligned_verses" },
            task_specs: [
                "ud_nonpronominal_mention",
                "ud_proper_noun_subject",
            ],
            output_dir: output_dir,
        }
    }
}
