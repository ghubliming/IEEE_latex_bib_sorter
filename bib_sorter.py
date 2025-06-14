import re
import sys
from collections import OrderedDict


class CitationTracker:
    """Track citations and their first appearance order in the document"""

    def __init__(self):
        self.citations = OrderedDict()  # citation_key -> first_position
        self.citation_positions = []  # list of (position, citation_key) tuples

    def add_citation(self, position, citation_key):
        """Add a citation at a specific position"""
        citation_key = citation_key.strip()

        # Track all positions for debugging
        self.citation_positions.append((position, citation_key))

        # Only record first appearance
        if citation_key not in self.citations:
            self.citations[citation_key] = position

    def get_ordered_citations(self):
        """Get citations ordered by first appearance"""
        # Sort by first appearance position
        sorted_citations = sorted(self.citations.items(), key=lambda x: x[1])
        return [citation for citation, position in sorted_citations]

    def print_debug_info(self, tex_content):
        """Print debug information about found citations"""
        print("\nDEBUG: All citations found (first 15):")
        for i, (pos, cite) in enumerate(self.citation_positions[:15]):
            # Get context around citation
            start = max(0, int(pos) - 20)
            end = min(len(tex_content), int(pos) + 40)
            context = tex_content[start:end].replace('\n', ' ').strip()
            first_appearance = pos == self.citations[cite]
            marker = " [FIRST]" if first_appearance else ""
            print(f"  {i + 1:2d}. {cite:8s} at pos {int(pos):6d}{marker}: ...{context}...")

        print(f"\nUnique citations in order of first appearance:")
        for i, cite in enumerate(self.get_ordered_citations(), 1):
            print(f"  {i:2d}. {cite} (first at position {self.citations[cite]})")


def find_all_citations(tex_content):
    """Find all citations in the document and track their order"""
    tracker = CitationTracker()

    # Pattern to match \cite{...} and \cite[...]{...}
    cite_pattern = r'\\cite(?:\[[^\]]*\])?\{([^}]+)\}'

    for match in re.finditer(cite_pattern, tex_content):
        position = match.start()
        cite_keys_str = match.group(1)

        # Handle multiple citations: \cite{c1,c2,c3}
        if ',' in cite_keys_str:
            cite_keys = [key.strip() for key in cite_keys_str.split(',')]
            # For multiple citations, add small offset to maintain order
            for i, cite_key in enumerate(cite_keys):
                tracker.add_citation(position + i * 0.001, cite_key)
        else:
            tracker.add_citation(position, cite_keys_str.strip())

    return tracker


def extract_bibliography_entries(tex_content):
    """Extract all \bibitem entries from the bibliography section"""
    # Find bibliography boundaries
    bib_start_match = re.search(r'\\begin\{thebibliography\}', tex_content)
    bib_end_match = re.search(r'\\end\{thebibliography\}', tex_content)

    if not bib_start_match or not bib_end_match:
        print("ERROR: Could not find \\begin{thebibliography} or \\end{thebibliography}")
        return None, None, None

    bib_start = bib_start_match.start()
    bib_end = bib_end_match.end()

    # Extract the full bibliography section
    bib_section = tex_content[bib_start:bib_end]

    # Extract the opening line (e.g., \begin{thebibliography}{99})
    opening_line_match = re.search(r'\\begin\{thebibliography\}[^\n]*', bib_section)
    opening_line = opening_line_match.group(0) if opening_line_match else '\\begin{thebibliography}'

    # Find all \bibitem entries
    bibitem_pattern = r'\\bibitem\{([^}]+)\}(.*?)(?=\\bibitem\{|\\end\{thebibliography\})'
    entries = {}

    for match in re.finditer(bibitem_pattern, bib_section, re.DOTALL):
        cite_key = match.group(1).strip()
        content = match.group(2).strip()

        # Clean up the content
        content = re.sub(r'\n\s*\n+', '\n', content)  # Remove multiple empty lines
        content = content.strip()

        entries[cite_key] = content

    return entries, (bib_start, bib_end), opening_line


def create_reordered_bibliography(citation_order, bib_entries, opening_line):
    """Create the reordered bibliography section"""
    if not bib_entries:
        return None

    reordered_entries = []
    used_citations = set()

    # Add entries in citation order (maintaining original keys)
    print(f"\nProcessing {len(citation_order)} citations in order:")
    for i, cite_key in enumerate(citation_order, 1):
        if cite_key in bib_entries:
            entry_content = bib_entries[cite_key]
            full_entry = f"\\bibitem{{{cite_key}}}\n{entry_content}"
            reordered_entries.append(full_entry)
            used_citations.add(cite_key)
            print(f"  {i:2d}. {cite_key} -> added to bibliography")
        else:
            print(f"  {i:2d}. {cite_key} -> WARNING: No bibliography entry found!")

    # Add any unused bibliography entries at the end
    unused_entries = [key for key in bib_entries.keys() if key not in used_citations]
    if unused_entries:
        print(f"\nAdding {len(unused_entries)} unused bibliography entries:")
        for cite_key in unused_entries:
            entry_content = bib_entries[cite_key]
            full_entry = f"\\bibitem{{{cite_key}}}\n{entry_content}"
            reordered_entries.append(full_entry)
            print(f"      {cite_key} -> added as unused entry")

    # Construct the complete bibliography section
    bib_content = opening_line + '\n\n'
    bib_content += '\n\n'.join(reordered_entries)
    bib_content += '\n\\end{thebibliography}'

    return bib_content


def reorder_latex_bibliography(input_file, output_file=None):
    """Main function to reorder bibliography based on citation appearance"""

    # Read input file
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        print(f"Successfully read {len(content)} characters from {input_file}")
    except FileNotFoundError:
        print(f"ERROR: File '{input_file}' not found!")
        return False
    except Exception as e:
        print(f"ERROR: Could not read file '{input_file}': {e}")
        return False

    # Find all citations and track their order
    print("\n" + "=" * 60)
    print("STEP 1: FINDING CITATIONS")
    print("=" * 60)

    citation_tracker = find_all_citations(content)

    if not citation_tracker.citations:
        print("No citations found in the document!")
        return False

    citation_tracker.print_debug_info(content)
    citation_order = citation_tracker.get_ordered_citations()

    # Extract bibliography entries
    print("\n" + "=" * 60)
    print("STEP 2: EXTRACTING BIBLIOGRAPHY")
    print("=" * 60)

    bib_entries, bib_bounds, opening_line = extract_bibliography_entries(content)

    if bib_entries is None:
        return False

    print(f"Found {len(bib_entries)} bibliography entries:")
    for key in bib_entries.keys():
        print(f"  - {key}")

    # Create reordered bibliography
    print("\n" + "=" * 60)
    print("STEP 3: REORDERING BIBLIOGRAPHY")
    print("=" * 60)

    new_bib_section = create_reordered_bibliography(citation_order, bib_entries, opening_line)

    if new_bib_section is None:
        print("Failed to create reordered bibliography!")
        return False

    # Replace bibliography in content
    bib_start, bib_end = bib_bounds
    new_content = content[:bib_start] + new_bib_section + content[bib_end:]

    # Write output file
    if output_file is None:
        output_file = input_file.replace('.tex', '_reordered.tex')

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"\n✓ Successfully saved reordered file to: {output_file}")
    except Exception as e:
        print(f"ERROR: Could not write output file '{output_file}': {e}")
        return False

    # Display the reordered bibliography
    print("\n" + "=" * 60)
    print("REORDERED BIBLIOGRAPHY SECTION")
    print("=" * 60)
    print(new_bib_section)
    print("=" * 60)

    return True


def main():
    """Command line interface"""
    if len(sys.argv) < 2:
        print("LaTeX Bibliography Reorder Tool")
        print("=" * 40)
        print("Usage: python script.py input.tex [output.tex]")
        print("\nExample:")
        print("  python script.py paper.tex")
        print("  python script.py paper.tex paper_sorted.tex")
        print("\nThis tool will:")
        print("• Find all \\cite{} commands in order of appearance")
        print("• Reorder \\bibitem{} entries to match citation order")
        print("• Keep original citation keys (e.g., c18 stays c18)")
        print("• Handle multiple citations like \\cite{c1,c2,c3}")
        print("• Preserve exact formatting of bibliography entries")
        return

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    print("LaTeX Bibliography Reorder Tool")
    print("=" * 40)
    print(f"Input file:  {input_file}")
    print(f"Output file: {output_file if output_file else input_file.replace('.tex', '_reordered.tex')}")

    success = reorder_latex_bibliography(input_file, output_file)

    if success:
        print("\n✓ Bibliography reordering completed successfully!")
    else:
        print("\n✗ Bibliography reordering failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()