# LaTeX Bibliography Reorder Tool

A Python tool that automatically reorders `\bibitem{}` entries in LaTeX documents to match the order of first citation appearance in the text.

## Features

- **Smart Citation Tracking**: Finds all `\cite{}` and `\cite[...]{...}` commands and tracks when each citation first appears
- **Preserves Original Keys**: Maintains original citation keys (e.g., `c18` stays `c18`, not renumbered)
- **Handles Multiple Citations**: Properly processes commands like `\cite{ref1,ref2,ref3}`
- **Maintains Formatting**: Preserves exact formatting of bibliography entries
- **Detailed Debugging**: Shows comprehensive information about citation order and processing
- **Error Handling**: Robust error handling with clear error messages

## Requirements

- Python 3.6 or higher
- No external dependencies (uses only standard library)

## Installation

1. Download the `bib_sorter.py` file
2. Make sure you have Python 3.6+ installed
3. No additional packages need to be installed

## Usage

### Basic Usage

```bash
python bib_sorter.py input.tex
```

This will create a new file `input_reordered.tex` with the reordered bibliography.

### Specify Output File

```bash
python bib_sorter.py input.tex output.tex
```

This will save the reordered version to `output.tex`.

### Help

```bash
python bib_sorter.py
```

Shows usage information and feature description.

## How It Works

The tool works in three main steps:

1. **Citation Discovery**: Scans the entire LaTeX document to find all `\cite{}` commands and records the position of each citation's first appearance
2. **Bibliography Extraction**: Extracts all `\bibitem{}` entries from the `\begin{thebibliography}...\end{thebibliography}` section
3. **Bibliography Reordering**: Reorders the bibliography entries to match the order of first citation appearance

## Example

### Before (Original Document)

```latex
\documentclass{article}
\begin{document}

First we cite \cite{jones2019}, then \cite{smith2020}, 
and later \cite{jones2019} again, followed by \cite{wilson2021}.

\begin{thebibliography}{99}
\bibitem{smith2020}
Smith, J. "Important Paper." Journal of Science, 2020.

\bibitem{wilson2021}
Wilson, K. "Another Study." Nature, 2021.

\bibitem{jones2019}
Jones, A. "Foundational Work." IEEE Trans, 2019.
\end{thebibliography}

\end{document}
```

### After (Reordered)

```latex
\documentclass{article}
\begin{document}

First we cite \cite{jones2019}, then \cite{smith2020}, 
and later \cite{jones2019} again, followed by \cite{wilson2021}.

\begin{thebibliography}{99}
\bibitem{jones2019}
Jones, A. "Foundational Work." IEEE Trans, 2019.

\bibitem{smith2020}
Smith, J. "Important Paper." Journal of Science, 2020.

\bibitem{wilson2021}
Wilson, K. "Another Study." Nature, 2021.
\end{thebibliography}

\end{document}
```

## Supported Citation Formats

The tool recognizes these citation formats:

- `\cite{key}` - Basic citation
- `\cite[page]{key}` - Citation with optional argument
- `\cite{key1,key2,key3}` - Multiple citations in one command
- `\cite[see][p. 123]{key}` - Citation with pre and post text

## Output Information

The tool provides detailed output including:

- **Step-by-step processing**: Clear indication of what's happening at each stage
- **Citation discovery**: Shows all citations found with their positions
- **First appearance tracking**: Indicates which citations are first appearances
- **Bibliography mapping**: Shows how citations map to bibliography entries
- **Warnings**: Alerts about missing bibliography entries or unused entries
- **Final result**: Displays the complete reordered bibliography section

## Error Handling

The tool handles various error conditions:

- **File not found**: Clear error message if input file doesn't exist
- **No citations found**: Warning if no `\cite{}` commands are found
- **No bibliography section**: Error if `\begin{thebibliography}` is missing
- **Missing entries**: Warnings for citations without corresponding `\bibitem{}`
- **Unused entries**: Information about `\bibitem{}` entries that aren't cited

## Limitations

- Only works with `\bibitem{}` style bibliographies (not BibTeX)
- Requires `\begin{thebibliography}...\end{thebibliography}` structure
- Does not modify the citation commands themselves, only reorders bibliography entries
- Assumes UTF-8 encoding for input files

## Common Use Cases

1. **Academic Papers**: Reorder references to match citation order for journal submissions
2. **Thesis Writing**: Organize bibliography in order of appearance
3. **IEEE Style**: Comply with IEEE citation numbering requirements
4. **Document Cleanup**: Organize references in existing LaTeX documents

## Troubleshooting

### No Citations Found
- Check that you're using `\cite{}` commands (not `\ref{}` or other commands)
- Ensure citations are in the main document text, not just in comments

### No Bibliography Section Found
- Verify you have `\begin{thebibliography}` and `\end{thebibliography}` in your document
- Check for typos in the bibliography environment names

### Missing Bibliography Entries
- Ensure every `\cite{key}` has a corresponding `\bibitem{key}`
- Check for typos in citation keys

### Encoding Issues
- Save your LaTeX file with UTF-8 encoding
- If you have special characters, ensure they're properly encoded

## Contributing

Feel free to submit issues or pull requests if you find bugs or want to add features.

## License

This tool is provided as-is for academic and research purposes.
