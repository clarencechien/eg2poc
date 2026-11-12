# Blind review instructions

You are an independent annotator. Each line of your batch files is one item:
{"rid", "lang", "question", "options" {A,B,C,D}, "text"}.

For every item:
1. Read `question` (it contains the judging rules), the four `options`, and `text`
   (its first line is "今天：…" / "Today: …", the reference date).
2. Choose the single option (A, B, C or D) that the text best supports under those rules
   and option definitions. Use only that item; do not let other items influence you
   (some items look alike on purpose).
3. Write a one-sentence reason naming the deciding fact (any language).

Read and judge every item yourself. Do not use keyword matching, scripts or any other
model to classify. A short script is allowed only to serialise answers you decided.

Output: for each batch bXX.jsonl write answers/bXX.jsonl with one line per item, same order:
{"rid": "r0001", "answer": "C", "reason": "..."}

Read only the files in your own folder and this file. Do not open anything under
/home/user/eg2poc or other folders.
