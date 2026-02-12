import json
import re
from bs4 import BeautifulSoup
from typing import List, Dict

def clean_text(text: str) -> str:
    """Cleans up whitespace and newlines."""
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_links(soup_element) -> List[str]:
    """Extracts all hrefs from an element."""
    links = []
    for a in soup_element.find_all('a', href=True):
        href = a['href']
        if not href.startswith('#') and href not in links:
            links.append(href)
    return links

def get_condition_type(condition_soup) -> str:
    """Determines if it is a Licence Condition, SR Code, or Ordinary Code."""
    if condition_soup.find("div", class_="o-code"):
        return "Ordinary Code"
    elif condition_soup.find("div", class_="sr-code"):
        return "Social Responsibility Code"
    else:
        return "Licence Condition"

def extract_lccp_ready_for_rag(html_file_path: str, output_json_path: str):
    with open(html_file_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    rag_ready_chunks = []

    parts = soup.find_all("div", class_="page-part")

    for part in parts:
        part_title = part.find("h2").get_text(strip=True) if part.find("h2") else "General"

        sections = part.find_all("div", class_="page-section")
        for section in sections:
            section_title = section.find("h3").get_text(strip=True) if section.find("h3") else ""

            subsections = section.find_all("div", class_="page-subsection")
            for subsection in subsections:
                subsection_title = subsection.find("h4").get_text(strip=True) if subsection.find("h4") else ""

                conditions = subsection.find_all("section", class_="condition")
                for cond in conditions:
                    # --- 1. Extraction ---
                    h5 = cond.find("h5")
                    condition_title = h5.get_text(strip=True) if h5 else "Unknown Condition"
                    condition_id = condition_title.split("-")[0].strip()

                    applies_to_div = cond.find("div", class_="print-panel")
                    applies_to_text = ""
                    if applies_to_div:
                        applies_to_text = clean_text(applies_to_div.get_text(separator=" "))
                        applies_to_text = applies_to_text.replace("Applies to:", "").strip()

                    urls = extract_links(cond)
                    type_label = get_condition_type(cond)

                    # Prepare body text (remove headers/panels to avoid duplication)
                    content_soup = cond.__copy__()
                    if content_soup.find("h5"):
                        content_soup.find("h5").decompose()
                    if content_soup.find("div", class_="print-panel"):
                        content_soup.find("div", class_="print-panel").decompose()

                    body_text = content_soup.get_text(separator="\n", strip=True)

                    # --- 2. Build Metadata Dictionary ---
                    # This is what you will pass to `metadata={...}` in LlamaIndex later
                    metadata = {
                        "part": part_title,
                        "section": section_title,
                        "subsection": subsection_title,
                        "condition_id": condition_id,
                        "condition_name": condition_title,
                        "regulation_type": type_label,
                        "applies_to": applies_to_text,
                        "related_links": urls
                    }

                    # --- 3. Build Full Chunk Text ---
                    # This combines context + content. This is what is actually embedded.
                    # We inject the metadata into the text so the embedding model understands the context.
                    full_chunk_text = (
                        f"Part: {part_title}\n"
                        f"Section: {section_title}\n"
                        f"Subsection: {subsection_title}\n"
                        f"Regulation: {condition_title}\n"
                        f"Type: {type_label}\n"
                        f"Applies To: {applies_to_text}\n"
                        f"Content:\n{body_text}"
                    )

                    # --- 4. Append to List ---
                    rag_ready_chunks.append({
                        "full_chunk_text": full_chunk_text,
                        "metadata": metadata,
                        # We keep raw_content separate just in case you need to display
                        # just the body text in your UI without the "Part:..." headers
                        "raw_content": body_text
                    })

    # Save to JSON
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(rag_ready_chunks, f, indent=4, ensure_ascii=False)

    print(f"Successfully created {len(rag_ready_chunks)} RAG-ready chunks in {output_json_path}")

if __name__ == "__main__":
    extract_lccp_ready_for_rag("LCCP.html", "lccp_rag_dataset.json")
