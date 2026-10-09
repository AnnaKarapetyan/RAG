import glob
import json
import re

lens = []
def split_long_chunk(text, max_words=360, min_tail = 30):
    lines = text.split("\n")
    sub_chunks = []
    current_lines = []
    current_word_count = 0
    in_code_block = False

    for line in lines:
        if line.strip().startswith("```"):
            in_code_block = not in_code_block

        current_lines.append(line)
        current_word_count += len(line.split())

        if current_word_count >= max_words and not in_code_block:
            sub_chunks.append("\n".join(current_lines))
            current_lines = []
            current_word_count = 0

    if current_lines:
        if sub_chunks and current_word_count < min_tail:
            sub_chunks[-1] += "\n" +"\n".join(current_lines)
        else:
            sub_chunks.append("\n".join(current_lines))

    return sub_chunks

 
def chunk_file(data):
    chunks =[]
    text = data["text"]
    url = data["url"]
    title = data["title"]

    parts = re.split(r"(^#{1,6} .*)", text, flags=re.MULTILINE)
    intro = parts[0].strip()
    if intro:
        chunks.append({
            "text": intro,
            "heading": title,
            "url": url,
            "title": title,
            "chunk_part":0
        })
    chunk = ""
    headings = ""

    for i in range(1, len(parts), 2):
        global lens

        heading = parts[i].strip()
        content = parts[i + 1].strip() if i + 1 < len(parts) else ""
        
        if content:
            chunk = f"{chunk}\n{content}"
            headings = f"{headings}/ {heading}"
            if len(chunk.split()) < 30:
                continue
            else:
                split_chunk = split_long_chunk(chunk)
                for chunk_part,element in enumerate(split_chunk):
                    lens.append(len(element.split()))
                    chunks.append({
                        "text": f"{headings}\n\n{element}",
                        "heading": headings,
                        "url": url,
                        "title": title,
                        "chunk_part": chunk_part
                    })
                chunk = ""
                headings = ""
            
    if chunk.strip():
        if chunks:
            chunks[-1]["text"] += f"\n\n{headings}\n\n{chunk.strip()}"
        else:
            chunks.append({
                "text": f"{headings}\n\n{chunk.strip()}",
                "heading": headings,
                "url": url,
                "title": title,
                "chunk_part": 0
                })
    return chunks

files  = sorted(glob.glob("*.json"))
all_chunks = []
for file_name in files:
    with open(file_name, encoding="utf-8") as f:
        data = json.load(f)
        chunks = chunk_file(data)
        all_chunks.extend(chunks)
for idx, c in enumerate(all_chunks):
    c["id"] = f"chunk_{idx}"
print(sorted(lens))
too_short = sum(1 for n in lens if n < 20)
too_long = sum(1 for n in lens if n > 400)
print(too_short, too_long, len(lens))

with open("chunks.jsonl", "w", encoding="utf-8") as out:
    for chunk in all_chunks:
        out.write(json.dumps(chunk, ensure_ascii=False) + "\n")

print(len(all_chunks))
print(all_chunks[0])