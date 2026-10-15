import glob
import json
import re
from sentence_transformers import SentenceTransformer
model = SentenceTransformer("BAAI/bge-small-en-v1.5")

def split_by_headings(text):
    parts = [""]
    in_code_block = False
    for line in text.split("\n"):
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
        if not in_code_block and re.match(r"^#{1,6} ", line):
            parts.append(line)
            parts.append("")
        else:
            parts[-1] += line + "\n"
    return parts

def split_long_chunk(text, max_tokens=200, min_tail = 30):
    lines = text.split("\n")
    sub_chunks = []
    current_lines = []
    current_token_count = 0
    in_code_block = False

    for line in lines:
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
        current_lines.append(line)
        current_token_count += len(model.tokenizer.tokenize(line))
        if current_token_count >= max_tokens and not in_code_block:
            sub_chunks.append("\n".join(current_lines))
            current_lines = []
            current_token_count = 0

    if current_lines:
        if sub_chunks and current_token_count < min_tail:
            sub_chunks[-1] += "\n" +"\n".join(current_lines)
        else:
            sub_chunks.append("\n".join(current_lines))

    return sub_chunks

 
def chunk_file(data):
    chunks =[]
    text = data["text"]
    url = data["url"]
    title = data["title"]

    parts = split_by_headings(text)
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

final_lens = [len(model.tokenizer.tokenize(c["text"])) for c in all_chunks]
too_short = sum(1 for n in final_lens if n < 20)
too_long = sum(1 for n in final_lens if n > 510)
print(too_short, too_long, len(final_lens))

with open("chunks.jsonl", "w", encoding="utf-8") as out:
    for chunk in all_chunks:
        out.write(json.dumps(chunk, ensure_ascii=False) + "\n")

print(len(all_chunks))
print(all_chunks[0])