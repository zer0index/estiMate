def add_chunk_markers_and_save(input_path="input/device_order_app_prd.md"):
    """Reads the PRD, inserts chunk markers before each H2 heading, and writes to memory/1_tagged.md."""
    output_path = "memory/1_tagged.md"
    try:
        with open(input_path, "r", encoding="utf-8") as infile:
            lines = infile.readlines()
    except FileNotFoundError:
        print(f"[Error] Input file not found: {input_path}")
        return
    output_lines = []
    chunk_count = 1
    for line in lines:
        if line.strip().startswith("## "):
            output_lines.append(f"<!-- CHUNK_H2_{chunk_count} -->\n")
            chunk_count += 1
        output_lines.append(line)
    with open(output_path, "w", encoding="utf-8") as outfile:
        outfile.writelines(output_lines)
    print(f"[Prechunker] Tagged PRD written to {output_path} with {chunk_count-1} chunk markers.") 