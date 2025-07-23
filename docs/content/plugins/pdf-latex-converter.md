# PDF LaTeX Converter

# PDF LaTeX Converter

The PDF LaTeX Converter is ReViewPoint's flagship document processing plugin, designed to intelligently extract, analyze, and structure content from PDF documents using advanced parsing techniques and AI-assisted analysis.

## Primary Goal

Transform unstructured PDF documents into well-organized, machine-readable formats that facilitate automated review workflows, content analysis, and citation processing. The plugin serves as the foundation for ReViewPoint's document understanding capabilities.

## Overview

This plugin combines sophisticated PDF parsing with Large Language Model (LLM) integration to extract document structure, identify key components, and generate multiple output formats. It's specifically designed for academic papers and research documents, maintaining the integrity of complex formatting while making content accessible for further processing.

## Input and Output Specifications

### Input Requirements

**Supported Input Formats:**

- PDF documents (all versions)
- Multi-page academic papers
- Research documents with complex formatting
- Papers with footnotes, citations, and bibliographies

**Input Requirements:**

- Readable PDF files (not image-only scans)
- Documents with identifiable text content
- Academic or research paper format

### Output Generation

**Primary Outputs:**

1. **Structured Text (`structured_trimmed.txt`)**
   - Hierarchically organized content with LaTeX-style formatting
   - Preserved section numbering and clean, machine-readable format

2. **HTML Document (`structured_trimmed.html`)**
   - Web-ready formatted content with proper heading hierarchy
   - Validated citation links and navigation-friendly structure

3. **Bibliography JSON (`bibliography_entries.json`)**
   - Structured reference data with extractable citation information
   - Searchable bibliography entries in integration-ready format

4. **Processing Artifacts**
   - `parsed.txt` - Raw extracted text
   - `heading_candidates.txt` - Debug information for heading detection
   - `structured_cite.txt` - Content with converted citations
   - `status.json` - Real-time processing status

## How It Works: Processing Pipeline

The plugin follows an intelligent 8-step processing pipeline:

### Step 1: PDF Parsing and Text Extraction

- **Line-by-line parsing** with font size and style detection
- **Font change recognition** to preserve superscripts and formatting
- **Page break tracking** for accurate document navigation
- **Character-level analysis** for precise text extraction

### Step 2: AI-Powered Structure Detection

- **Heading extraction** using LLM analysis of document structure
- **Table of contents identification** and hierarchical mapping
- **Section and subsection recognition** with numbering preservation
- **Chapter boundary detection** for academic documents

### Step 3: Footnote Processing

- **Automatic footnote detection** and marker identification
- **Cross-reference matching** between in-text markers and footnotes
- **Footnote text extraction** from page footers
- **Citation conversion** from numeric markers to `\cite{}` format

### Step 4: Bibliography Analysis

- **Bibliography section identification** and page range detection
- **Reference entry extraction** with structure preservation
- **Bibliography splitting** for large reference sections
- **Metadata extraction** from individual citations

### Step 5: Structure Matching and Validation

- **Heading-to-text alignment** using intelligent matching algorithms
- **Structure validation** against extracted table of contents
- **Content organization** into hierarchical sections
- **Quality assurance** for extracted structure

### Step 6: Content Trimming and Optimization

- **Main content isolation** from auxiliary sections
- **Structure refinement** to focus on core chapters
- **Noise reduction** to remove processing artifacts
- **Content validation** for completeness

### Step 7: Format Conversion

- **HTML generation** with proper heading hierarchy
- **LaTeX structure** creation for academic formatting
- **Citation validation** and cross-reference checking
- **Multi-format output** generation

### Step 8: Status Tracking and Monitoring

- **Real-time progress tracking** via JSON status files
- **Error logging** and debugging information
- **Processing timestamps** for workflow coordination
- **External monitoring** capabilities for integration

## Installation and Configuration

### Prerequisites

```bash
# Required Python packages
pdfminer.six>=20221105  # PDF parsing
openai                  # LLM integration
PyPDF2>=3.0.1          # PDF manipulation
validators>=0.20.0      # Data validation
isbnlib>=3.10.14       # ISBN processing
```

### Basic Setup

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. **Manual Mode (No API Key Required):**

   ```bash
   python -m src.pipeline --manual
   ```

3. **API Mode with OpenAI:**

   ```bash
   python -m src.pipeline --api-key YOUR_OPENAI_KEY
   ```

### Advanced Configuration

Create `config.ini` for detailed settings:

```ini
[openai]
api_key = YOUR_OPENAI_KEY
model = gpt-4                # LLM model selection
max_tokens = 500            # Response length limit
temperature = 0.3           # Response creativity
request_interval = 1.0      # Rate limiting (seconds)

[processing]
pages_for_analysis = 1-10   # Page range for LLM analysis
debug_logging = true        # Enable detailed logs
preserve_formatting = true  # Maintain original formatting
```

## Usage Examples

### Basic Document Processing

```bash
# Process all PDFs in input directory
python -m src.pipeline --manual

# Process with OpenAI integration
python -m src.pipeline --config config.ini

# Process specific file with custom output
python -m src.pipeline --input-dir ./papers --output-dir ./processed
```

### Advanced Usage

```bash
# Debug mode with detailed logging
python -m src.pipeline --log-level DEBUG --log-file detailed.log

# Extract titles only (no full processing)
python -m src.pipeline --print-extract-titles research_paper.pdf

# Custom page range for analysis
python -m src.pipeline --analysis-pages 1-15 --config config.ini
```

### Integration with ReViewPoint

```python
from pdf_latex_converter import PDFProcessor

# Initialize processor
processor = PDFProcessor(config_path="config.ini")

# Process uploaded document
result = processor.process_document(
    pdf_path="uploaded_paper.pdf",
    output_dir="./processed",
    include_bibliography=True
)

# Access structured results
structured_content = result.structured_text
bibliography = result.bibliography_entries
html_output = result.html_document
```

## Technical Architecture

### Core Components

**PDF Reader (`pdf_reader.py`)**

- PDFMiner integration for robust PDF parsing
- LineInfo dataclass for structured text representation
- Font analysis with size, bold, and italic detection
- Character-level processing for precision extraction

**LLM Client (`llm_client.py`)**

- OpenAI API integration with configurable models
- Rate limiting and error handling
- Manual mode support for testing without API costs
- Response caching for development efficiency

**Structure Tools (`structure_tools.py`)**

- HTML conversion utilities
- LaTeX formatting preservation
- Content trimming algorithms
- Structure validation functions

**Bibliography Processing (`bibliography.py`)**

- Bibliography detection using pattern matching
- Page range identification for reference sections
- PDF splitting for targeted analysis
- Entry extraction and structuring

### AI Integration

The plugin leverages Large Language Models for intelligent document analysis:

**Extract Titles Prompt:**

- Analyzes document structure to identify headings
- Returns hierarchical JSON with chapters, sections, and subsections
- Supports both English and German document formats
- Preserves original numbering and formatting

**Footnote Detection:**

- Identifies footnote markers and corresponding text
- Extracts precise footnote content from page footers
- Maintains reference accuracy for citation processing

**Bibliography Processing:**

- Extracts structured bibliography entries
- Identifies reference formatting patterns
- Supports multiple citation styles

## Performance and Troubleshooting

### Processing Performance

- **Small Documents (< 20 pages):** 30-60 seconds
- **Medium Documents (20-50 pages):** 1-3 minutes
- **Large Documents (> 50 pages):** 3-10 minutes
- **API Rate Limiting:** Configurable delays between LLM calls

### Common Issues and Solutions

#### PDF Reading Errors

**Symptoms:** "Failed to read PDF" errors

**Solutions:**

- Verify PDF is not corrupted or password-protected
- Check file permissions and accessibility
- Try re-saving PDF with different settings

#### LLM API Issues

**Symptoms:** API timeout or rate limit errors

**Solutions:**

- Increase `request_interval` in configuration
- Verify API key validity and quota
- Use manual mode for testing without API costs

#### Poor Structure Detection

**Symptoms:** Missing headings or incorrect hierarchy

**Solutions:**

- Enable debug logging to analyze detection process
- Adjust page range for LLM analysis
- Verify document has clear structural formatting

### Debug and Monitoring

Monitor processing progress via status files:

```json
{
  "status": "extracting_bibliography",
  "timestamp": "2025-07-23T14:30:15.123456",
  "current_step": 7,
  "total_steps": 8,
  "estimated_completion": "2025-07-23T14:32:00"
}
```

Enable comprehensive logging:

```bash
python -m src.pipeline --log-level DEBUG --log-file converter.log
```

## Development and Support

### Development Setup

```bash
# Clone repository
git clone https://github.com/Swabble/pdf_latex_converter.git
cd pdf_latex_converter

# Development environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# Run tests
python -m pytest tests/
```

### Contributing Guidelines

1. **Code Standards:** Follow PEP 8 and type hints
2. **Testing:** Add tests for new functionality
3. **Documentation:** Update docs for API changes
4. **Performance:** Consider memory and speed impacts

### Support Channels

- **Repository:** [pdf_latex_converter](https://github.com/Swabble/pdf_latex_converter)
- **Issues:** GitHub issue tracker for bugs and features
- **Documentation:** Repository wiki for detailed guides
- **Community:** ReViewPoint discussions for general help

## License and Roadmap

### License

This plugin is open source under the MIT License.

### Current Capabilities (v1.0)

- Intelligent PDF parsing and structure extraction
- AI-powered heading and section detection
- Bibliography processing and citation conversion
- Multiple output format generation

### Planned Enhancements (v2.0)

- **Enhanced OCR Support** for scanned documents
- **Multi-language Processing** beyond German/English
- **Advanced Table Detection** and extraction
- **Real-time Collaborative Processing** capabilities
- **Cloud Processing Integration** for scalability
- **Machine Learning Models** for improved accuracy

## Overview

This plugin bridges the gap between different document formats in academic publishing, allowing reviewers and authors to work with their preferred format while maintaining document integrity and formatting.

## Installation

### Prerequisites

- Python 3.8 or higher
- LaTeX distribution (TeX Live, MiKTeX, or MacTeX)
- ReViewPoint platform installed and configured
- PDF processing libraries

### Setup

1. Ensure the plugin repository is cloned (use the "Setup Plugin Repositories" task)
2. Navigate to the plugin directory:

   ```bash
   cd plugin_prototypes/pdf_latex_converter
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Configure your LaTeX distribution path in the configuration file

## Features

### High-Quality PDF to LaTeX Conversion

- **Text Extraction:** Accurate text extraction maintaining formatting
- **Structure Preservation:** Maintains document hierarchy and sections
- **Font Handling:** Preserves text styling and font information
- **Layout Detection:** Recognizes and converts document layouts

### LaTeX to PDF Compilation

- **Multiple Engines:** Support for pdfLaTeX, XeLaTeX, and LuaLaTeX
- **Bibliography Processing:** Automatic BibTeX/Biber integration
- **Index Generation:** Support for makeindex and xindy
- **Error Handling:** Comprehensive compilation error reporting

### Mathematical Formula Preservation

- **Equation Recognition:** Advanced mathematical content detection
- **LaTeX Math Mode:** Converts to appropriate LaTeX math environments
- **Symbol Mapping:** Accurate mathematical symbol conversion
- **Complex Expressions:** Handles multi-line equations and matrices

### Table and Figure Extraction

- **Table Detection:** Identifies and converts tabular data
- **Figure Extraction:** Preserves images and diagrams
- **Caption Handling:** Maintains figure and table captions
- **Cross-references:** Preserves internal document references

### Bibliography Handling

- **Reference Extraction:** Identifies and converts reference lists
- **BibTeX Generation:** Creates structured bibliography files
- **Citation Mapping:** Maintains citation-reference relationships
- **Format Standardization:** Ensures consistent bibliography formatting

## Configuration

### Environment Variables

```bash
# LaTeX configuration
LATEX_COMPILER=pdflatex
LATEX_PATH=/usr/local/texlive/2023/bin
BIBTEX_PROCESSOR=biber

# PDF processing
PDF_DPI=300
OCR_ENABLED=true
OCR_LANGUAGE=eng

# Output settings
OUTPUT_ENCODING=utf-8
PRESERVE_COMMENTS=true
```

### Plugin Settings

- **Conversion Quality:** Configure precision vs. speed trade-offs
- **LaTeX Packages:** Specify required LaTeX packages for compilation
- **OCR Settings:** Enable/configure optical character recognition
- **Output Format:** Choose LaTeX document class and styling

## Usage

### Basic PDF to LaTeX Conversion

```python
from pdf_latex_converter import PDFConverter

converter = PDFConverter()
latex_content = converter.pdf_to_latex("input.pdf")

# Save to file
with open("output.tex", "w", encoding="utf-8") as f:
    f.write(latex_content)
```

### Advanced Conversion with Options

```python
converter = PDFConverter(
    preserve_formatting=True,
    extract_images=True,
    ocr_enabled=True
)

# Convert with custom settings
result = converter.convert(
    input_file="paper.pdf",
    output_dir="./converted",
    options={
        "document_class": "article",
        "packages": ["amsmath", "graphicx", "hyperref"],
        "bibliography_style": "ieee"
    }
)
```

### LaTeX to PDF Compilation

```python
from pdf_latex_converter import LaTeXCompiler

compiler = LaTeXCompiler()
pdf_result = compiler.compile_latex(
    tex_file="document.tex",
    engine="pdflatex",
    runs=2  # For bibliography and cross-references
)

if pdf_result.success:
    print(f"PDF generated: {pdf_result.output_file}")
else:
    print(f"Compilation failed: {pdf_result.errors}")
```

### Integration with ReViewPoint

The plugin integrates with ReViewPoint's workflow:

1. **Upload Processing:** Automatically converts uploaded PDFs
2. **Review Mode:** Allows reviewers to switch between PDF and LaTeX views
3. **Annotation Sync:** Synchronizes comments between formats
4. **Export Options:** Provides multiple output formats for authors

## API Reference

### PDFConverter Class

#### Methods

- `pdf_to_latex(pdf_path, options=None)`: Convert PDF to LaTeX
- `extract_images(pdf_path, output_dir)`: Extract images from PDF
- `extract_bibliography(pdf_path)`: Extract reference list
- `analyze_structure(pdf_path)`: Analyze document structure

### LaTeXCompiler Class

#### Compilation Methods

- `compile_latex(tex_file, engine="pdflatex")`: Compile LaTeX to PDF
- `validate_syntax(tex_file)`: Check LaTeX syntax
- `extract_dependencies(tex_file)`: List required packages
- `generate_bibliography(bib_file)`: Process bibliography

## Supported Formats

### Input Formats

- PDF (all versions)
- LaTeX (.tex files)
- BibTeX (.bib files)
- Plain text with formatting hints

### Output Formats

- LaTeX (.tex)
- PDF (via LaTeX compilation)
- HTML (experimental)
- Markdown (basic conversion)

## Troubleshooting

### Common Issues

#### LaTeX Compilation Errors

- Verify LaTeX distribution is properly installed
- Check required packages are available
- Review compilation logs for specific errors
- Ensure file paths don't contain special characters

#### Poor PDF Conversion Quality

- Increase PDF resolution settings
- Enable OCR for scanned documents
- Check source PDF quality and format
- Adjust conversion parameters

#### Missing Mathematical Content

- Enable mathematical formula detection
- Check PDF contains actual text (not just images)
- Verify LaTeX math packages are included
- Review conversion settings for math handling

### Performance Optimization

- **Large Documents:** Process in sections for better performance
- **Memory Usage:** Adjust processing chunk sizes
- **Quality vs Speed:** Configure conversion precision levels
- **Parallel Processing:** Enable multi-threading for batch operations

## Development

### Building from Source

```bash
# Clone repository
git clone https://github.com/Swabble/pdf_latex_converter.git
cd pdf_latex_converter

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest tests/

# Build documentation
sphinx-build docs/ docs/_build/
```

### Contributing

We welcome contributions to improve the PDF LaTeX Converter:

1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Add comprehensive tests
5. Update documentation
6. Submit a pull request

### Testing

The plugin includes comprehensive tests for:

- PDF parsing accuracy
- LaTeX generation quality
- Mathematical content preservation
- Bibliography extraction
- Error handling scenarios

## License

This plugin is open source and available under the MIT License. See the repository for full license details.

## Support

- **Repository:** [pdf_latex_converter](https://github.com/Swabble/pdf_latex_converter)
- **Issues:** Report bugs and feature requests on GitHub
- **Documentation:** Comprehensive guides in the repository wiki

## Roadmap

### Current Version Features

- Basic PDF to LaTeX conversion
- LaTeX compilation support
- Mathematical formula extraction
- Image and table handling

### Planned Enhancements

- Improved OCR accuracy
- Advanced table detection
- Real-time collaborative editing
- Cloud processing support
- Machine learning-enhanced conversion
