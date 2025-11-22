import re

from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_text_splitters import MarkdownHeaderTextSplitter


def estimate_tokens(text):
    """
    Simple token estimation without tiktoken
    Rule of thumb: 1 token ≈ 4 characters for English text
    For Vietnamese: 1 token ≈ 3 characters (more dense)
    """
    # Count characters and estimate tokens
    char_count = len(text)

    # Adjust for Vietnamese vs English content
    vietnamese_chars = len(
        re.findall(
            r"[àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]",
            text.lower(),
        )
    )

    if vietnamese_chars > char_count * 0.1:  # More than 10% Vietnamese
        estimated_tokens = char_count // 3
    else:
        estimated_tokens = char_count // 4

    # Add adjustment for special characters and formatting
    pipe_count = text.count("|")
    number_count = len(re.findall(r"\d+[,.]?\d*", text))

    # Tables and numbers are more token-dense
    estimated_tokens += (pipe_count + number_count) * 0.2

    return int(estimated_tokens)


def split_table_content(table_text, max_tokens=1024):
    """
    Split table content while preserving header structure
    Uses character-based token estimation
    """
    lines = table_text.strip().split("\n")

    # Find table lines (lines with |)
    table_lines = []
    header_line = None
    separator_line = None

    for line in lines:
        if "|" in line:
            table_lines.append(line)
            if header_line is None:
                header_line = line
            elif separator_line is None and "---" in line:
                separator_line = line

    if not table_lines or len(table_lines) < 3:
        return [table_text]

    # Check if table fits in token limit
    if estimate_tokens(table_text) <= max_tokens:
        return [table_text]

    # Extract context
    context_before = ""
    context_after = ""

    first_table_idx = -1
    last_table_idx = -1

    for i, line in enumerate(lines):
        if "|" in line:
            if first_table_idx == -1:
                first_table_idx = i
            last_table_idx = i

    if first_table_idx > 0:
        context_before = "\n".join(lines[:first_table_idx]).strip()
    if last_table_idx < len(lines) - 1:
        context_after = "\n".join(lines[last_table_idx + 1 :]).strip()

    # Calculate token overhead
    header_tokens = estimate_tokens(header_line + "\n" + (separator_line or ""))
    context_tokens = estimate_tokens(context_before + context_after)

    available_tokens = max_tokens - header_tokens - context_tokens - 50  # buffer

    if available_tokens < 100:
        # Not enough space, skip context
        available_tokens = max_tokens - header_tokens - 30
        context_before = ""
        context_after = ""

    # Get data rows
    data_rows = []
    for line in table_lines:
        if "|" in line and "---" not in line and line != header_line:
            data_rows.append(line)

    # Split rows into chunks
    chunks = []
    current_rows = []
    current_tokens = 0

    for row in data_rows:
        row_tokens = estimate_tokens(row)

        if current_tokens + row_tokens > available_tokens and current_rows:
            # Create chunk
            chunk_lines = []

            if context_before and len(chunks) == 0:
                chunk_lines.append(context_before)
                chunk_lines.append("")

            chunk_lines.append(header_line)
            if separator_line:
                chunk_lines.append(separator_line)
            chunk_lines.extend(current_rows)

            chunks.append("\n".join(chunk_lines))

            # Start new chunk
            current_rows = [row]
            current_tokens = row_tokens
        else:
            current_rows.append(row)
            current_tokens += row_tokens

    # Add final chunk
    if current_rows:
        chunk_lines = []

        if context_before and len(chunks) == 0:
            chunk_lines.append(context_before)
            chunk_lines.append("")

        chunk_lines.append(header_line)
        if separator_line:
            chunk_lines.append(separator_line)
        chunk_lines.extend(current_rows)

        if context_after:
            chunk_lines.append("")
            chunk_lines.append(context_after)

        chunks.append("\n".join(chunk_lines))

    return chunks


def count_characters_and_estimate(text):
    """
    Provide both character count and token estimation for debugging
    """
    chars = len(text)
    tokens = estimate_tokens(text)
    return {
        "characters": chars,
        "estimated_tokens": tokens,
        "char_per_token_ratio": chars / max(tokens, 1),
    }


def chunk_the_extracted_report_enhanced(file_path, year, max_tokens=1024):
    """
    Your enhanced function using local token estimation
    """
    with open(file_path, "r", encoding="utf-8") as f:
        markdown_text = f.read()

    headers_to_split_on = [
        ("###", "BÁO CÁO TÌNH HÌNH TÀI CHÍNH HỢP NHẤT"),
        ("###", "BÁO CÁO LƯU CHUYỂN TIỀN TỆ HỢP NHẤT"),
        ("###", "CÁC CHỈ TIÊU NGOÀI BÁO CÁO TÌNH HÌNH TÀI CHÍNH HỢP NHẤT"),
        ("###", "BÁO CÁO KẾT QUẢ HOẠT ĐỘNG HỢP NHẤT"),
    ]

    semantic_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1500,  # Increased since we're using char count
        chunk_overlap=50,
        length_function=len,  # Use character length
    )
    final_chunks = []

    md_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
    hierarchical_docs = md_splitter.split_text(markdown_text)

    for doc in hierarchical_docs:
        content = doc.page_content
        sections = extract_tables_and_text(content)

        for section_content, is_table in sections:
            if not section_content.strip():
                continue

            if is_table:
                # Split oversized tables
                table_chunks = split_table_content(section_content, max_tokens)

                print(
                    f"Table section ({len(section_content)} chars) split into {len(table_chunks)} chunks"
                )

                for i, chunk in enumerate(table_chunks):
                    stats = count_characters_and_estimate(chunk)
                    print(
                        f"  Chunk {i + 1}: {stats['characters']} chars ≈ {stats['estimated_tokens']} tokens"
                    )

                    final_chunks.append(
                        Document(
                            page_content=chunk,
                            metadata={
                                **doc.metadata,
                                "year": year,
                                "content_type": "table",
                                "estimated_tokens": stats["estimated_tokens"],
                                "character_count": stats["characters"],
                                "table_part": i + 1 if len(table_chunks) > 1 else None,
                            },
                        )
                    )
            else:
                # Regular text chunking
                sub_chunks = semantic_splitter.split_text(section_content)
                for chunk_text in sub_chunks:
                    if chunk_text.strip():
                        stats = count_characters_and_estimate(chunk_text)
                        final_chunks.append(
                            Document(
                                page_content=chunk_text,
                                metadata={
                                    **doc.metadata,
                                    "year": year,
                                    "content_type": "text",
                                    "estimated_tokens": stats["estimated_tokens"],
                                    "character_count": stats["characters"],
                                },
                            )
                        )

    print(f"Total chunks created: {len(final_chunks)}")

    # Check for oversized chunks
    oversized = 0
    for i, chunk in enumerate(final_chunks):
        tokens = estimate_tokens(chunk.page_content)
        if tokens > max_tokens:
            oversized += 1
            print(
                f"⚠️  Chunk {i + 1}: {tokens} estimated tokens (over {max_tokens} limit)"
            )

    if oversized == 0:
        print("✅ All chunks estimated within token limit!")
    else:
        print(f"ℹ️  Note: {oversized} chunks may still be over limit (estimation only)")

    return final_chunks


def extract_tables_and_text(content):
    """
    Simple table detection
    """
    lines = content.split("\n")
    sections = []
    current_section = []
    in_table = False
    consecutive_table_lines = 0

    for line in lines:
        has_pipe = "|" in line
        has_numbers = bool(re.search(r"\d+[\.,]\d+", line))
        has_multiple_spaces = len(re.findall(r"\s{2,}", line)) > 2

        is_table_line = has_pipe or (has_numbers and has_multiple_spaces)

        if is_table_line:
            consecutive_table_lines += 1
        else:
            if consecutive_table_lines >= 3 and current_section and not in_table:
                # We just finished a table-like section
                in_table = True
            consecutive_table_lines = 0

        if is_table_line and not in_table and consecutive_table_lines >= 2:
            # Starting table section
            if current_section:
                sections.append(("\n".join(current_section), False))
                current_section = []
            in_table = True
            current_section.append(line)
        elif is_table_line and in_table:
            current_section.append(line)
        elif not is_table_line and in_table:
            if line.strip() == "" or len(line.split()) <= 1:
                current_section.append(line)  # Keep empty lines or single words
            else:
                # End table
                sections.append(("\n".join(current_section), True))
                current_section = [line]
                in_table = False
        else:
            current_section.append(line)

    # Add final section
    if current_section:
        sections.append(("\n".join(current_section), in_table))

    return sections
