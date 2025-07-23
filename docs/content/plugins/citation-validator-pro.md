# Citation Validator Pro

Citation Validator Pro is a comprehensive, AI-powered tool for validating academic citations in HTML documents. This marketplace plugin leverages Large Language Models (LLMs) to ensure citation accuracy, relevance, and academic integrity in research papers.

## Primary Goal

Provide researchers, academic publishers, and content creators with an intelligent system to validate citations against their source materials, ensuring accuracy, relevance, and proper academic formatting while maintaining the highest standards of scholarly integrity.

## Overview

Citation Validator Pro combines advanced HTML parsing with sophisticated AI analysis to examine citations in context, verify their accuracy against source materials, and generate detailed validation reports. The plugin offers both simplified validation with simulated sources and comprehensive verification with actual source content.

## Input and Output Specifications

### Input Requirements

**Required Input Files:**

1. **`content.html`** - HTML document containing citations to be validated
   - Academic papers in HTML format
   - Documents with properly formatted citations
   - Support for various citation styles and formats

2. **`footnotes.json`** - Citation metadata file
   - Structured citation information
   - Source details and references
   - Bibliographic data in JSON format

**Input Directory Structure:**

```
input/
├── content.html     # Main document with citations
└── footnotes.json   # Citation metadata
```

### Output Generation

**Primary Outputs:**

1. **Validation Report (`content_reviewed.html`)**
   - Detailed HTML report with citation analysis
   - Color-coded validation results
   - Interactive citation assessments
   - Professional formatting for academic review

2. **Processing Logs**
   - Detailed validation process logs
   - Error reports and debugging information
   - Processing timestamps and statistics

**Output Features:**

- Customizable output directory and file naming
- Professional HTML report formatting
- Comprehensive citation analysis results
- Integration-ready data structures

## How It Works: Validation Pipeline

The plugin follows a sophisticated 4-step validation pipeline:

### Step 1: Document Processing

**HTML Content Analysis:**

- Parses HTML documents using BeautifulSoup
- Extracts text content and citation contexts
- Identifies citation markers and references
- Maintains document structure and formatting

**Citation Metadata Processing:**

- Loads and validates JSON citation data
- Maps citations to source materials
- Processes bibliographic information
- Structures data for LLM analysis

### Step 2: Source Content Preparation

**Simplified Mode (Default):**

- Generates simulated source content based on metadata
- Creates realistic academic abstracts and summaries
- Provides cost-effective validation for development
- Enables testing without API costs

**Comprehensive Mode:**

- Integrates with actual source materials
- Performs deep source content analysis
- Provides maximum validation accuracy
- Requires full source document access

### Step 3: AI-Powered Citation Analysis

**LLM-Based Validation:**

- Uses OpenAI GPT models for intelligent analysis
- Evaluates citation accuracy and relevance
- Assesses proper academic formatting
- Identifies potential citation issues

**Multi-Criteria Assessment:**

- **Accuracy**: Verifies citation details against sources
- **Relevance**: Ensures citations support stated claims
- **Context**: Evaluates proper citation usage
- **Formatting**: Checks academic style compliance

### Step 4: Report Generation

**Interactive HTML Reports:**

- Color-coded validation results
- Detailed citation assessments
- Clickable citation analysis
- Professional academic formatting

**Comprehensive Analysis:**

- Individual citation scoring
- Overall document assessment
- Improvement recommendations
- Export-ready results

## Technical Architecture

### Core Components

**CitationValidator Core (`core.py`)**

- Main validation pipeline orchestration
- Configuration management and setup
- Output directory and file management
- Integration with all processing components

**HTML Processor (`html_processor.py`)**

- BeautifulSoup-based HTML parsing
- Citation extraction and context analysis
- Document structure preservation
- Text content processing

**Citation Data Processor (`citation_processor.py`)**

- JSON metadata loading and validation
- Citation data structure management
- Bibliographic information processing
- Data integrity verification

**LLM Provider System (`llm/`)**

- **Base Provider Interface**: Extensible LLM abstraction
- **OpenAI Provider**: Production-grade GPT integration
- **Mock Provider**: Development and testing support
- **Provider Factory**: Dynamic provider selection

### AI Integration Features

**Advanced Prompt Engineering:**

- Specialized prompts for citation analysis
- Context-aware evaluation templates
- Multi-criteria assessment instructions
- Academic standard compliance checking

**Flexible LLM Support:**

- OpenAI GPT-3.5-turbo and GPT-4 integration
- Configurable model parameters
- Rate limiting and error handling
- Cost optimization features

**Mock LLM for Development:**

- Simulated AI responses for testing
- No API costs during development
- Realistic validation behavior
- Comprehensive testing scenarios

## Installation and Configuration

### Prerequisites

```bash
# Required Python packages
beautifulsoup4>=4.12.0  # HTML parsing
openai>=1.0.0          # LLM integration
python-dotenv>=1.0.0   # Environment management

# Development dependencies (optional)
pytest>=7.0.0          # Testing framework
black>=22.0.0          # Code formatting
mypy>=0.991           # Type checking
```

### Installation Methods

#### From Source (Recommended)

```bash
# Clone the repository
git clone https://github.com/filip-herceg/ReViewPoint-CitationValidatorPro.git
cd ReViewPoint-CitationValidatorPro

# Install in development mode
pip install -e .
```

#### Direct Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Install package
pip install .
```

### Configuration Setup

#### Environment Configuration

Create `.env` file from template:

```bash
# Copy environment template
cp .env.template .env
```

Configure your settings:

```env
# LLM Configuration
OPENAI_API_KEY=your-api-key-here
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_MAX_TOKENS=1000
OPENAI_TEMPERATURE=0.7

# Processing Configuration
USE_MOCK_LLM=false
LOG_LEVEL=INFO
MODE=Simplified

# Input/Output Configuration
INPUT_DIR=input
OUTPUT_DIR=output
OUTPUT_FILE=content_reviewed.html
```

#### Configuration Options

**LLM Settings:**

- **API Key**: OpenAI API authentication
- **Model Selection**: Choose between GPT-3.5-turbo or GPT-4
- **Token Limits**: Control response length and costs
- **Temperature**: Adjust AI creativity/consistency

**Processing Options:**

- **Mock LLM**: Enable for development without API costs
- **Validation Mode**: Simplified or comprehensive analysis
- **Logging Level**: Control debug information detail
- **Output Customization**: Directory and file naming

## Usage Examples

### Basic Validation

#### Command Line Interface

```bash
# Basic validation with default settings
python main.py

# Using mock LLM (no API costs)
python main.py --mock-llm

# Custom output configuration
python main.py --output-dir results --output validation_report.html

# Debug mode with detailed logging
python main.py --log-level DEBUG
```

#### Python API

```python
from citation_validator import CitationValidator

# Create validator instance
validator = CitationValidator(
    input_dir="input",
    output_file="my_validation_report.html"
)

# Get configuration summary
summary = validator.get_validation_summary()
print(f"Output file: {summary['output_file']}")
print(f"Input directory: {summary['input_dir']}")

# Run validation pipeline
try:
    validator.run_pipeline()
    print("✅ Validation completed successfully!")
except Exception as e:
    print(f"❌ Validation failed: {e}")
```

### Advanced Usage

#### Custom Configuration

```python
import os
from citation_validator import CitationValidator

# Set environment variables programmatically
os.environ['OPENAI_MODEL'] = 'gpt-4'
os.environ['OPENAI_TEMPERATURE'] = '0.3'
os.environ['LOG_LEVEL'] = 'DEBUG'

# Create validator with custom settings
validator = CitationValidator(
    input_dir="custom_input",
    output_file="detailed_analysis.html"
)

# Run with error handling
try:
    validator.run_pipeline()
    print("Advanced validation complete!")
except FileNotFoundError as e:
    print(f"Input file missing: {e}")
except Exception as e:
    print(f"Validation error: {e}")
```

#### Batch Processing

```python
from pathlib import Path
from citation_validator import CitationValidator

# Process multiple documents
input_directories = ["paper1", "paper2", "paper3"]

for input_dir in input_directories:
    if Path(input_dir).exists():
        validator = CitationValidator(
            input_dir=input_dir,
            output_file=f"{input_dir}_validation.html"
        )

        try:
            validator.run_pipeline()
            print(f"✅ Completed: {input_dir}")
        except Exception as e:
            print(f"❌ Failed {input_dir}: {e}")
```

### Integration with ReViewPoint

```python
from citation_validator import CitationValidator
import json

# ReViewPoint integration example
class ReViewPointCitationValidator:
    def __init__(self, document_id, review_session):
        self.document_id = document_id
        self.review_session = review_session

    def validate_document_citations(self):
        # Setup validator for ReViewPoint document
        validator = CitationValidator(
            input_dir=f"documents/{self.document_id}",
            output_file=f"reviews/{self.document_id}_citations.html"
        )

        # Run validation and capture results
        validation_results = validator.run_pipeline()

        # Integrate with ReViewPoint review system
        self.review_session.add_citation_analysis(validation_results)

        return validation_results
```

## Input Data Format Specifications

### HTML Document Format

The input HTML document should contain properly structured academic content:

```html
<!DOCTYPE html>
<html>
  <head>
    <title>Research Paper Title</title>
  </head>
  <body>
    <h1>Introduction</h1>
    <p>
      This research builds on previous work <sup>[1]</sup> which demonstrated...
    </p>

    <h2>Literature Review</h2>
    <p>Recent studies <sup>[2,3]</sup> have shown that...</p>

    <!-- Additional content with citations -->
  </body>
</html>
```

### Citation Metadata Format

The `footnotes.json` file should follow this structure:

```json
{
  "1": {
    "title": "Original Research Paper Title",
    "authors": ["Smith, J.", "Doe, A."],
    "journal": "Journal of Academic Research",
    "year": 2023,
    "volume": "15",
    "pages": "123-145",
    "doi": "10.1000/journal.2023.12345"
  },
  "2": {
    "title": "Comparative Analysis Study",
    "authors": ["Johnson, M."],
    "conference": "International Conference on Research",
    "year": 2022,
    "pages": "67-89"
  }
}
```

## Performance and Optimization

### Processing Performance

**Validation Speed:**

- Small documents (< 50 citations): 2-5 minutes
- Medium documents (50-200 citations): 5-15 minutes
- Large documents (> 200 citations): 15-45 minutes

**API Usage Optimization:**

- Configurable request delays for rate limiting
- Batch processing for multiple citations
- Mock LLM mode for development efficiency
- Token usage optimization for cost control

### Resource Management

**Memory Usage:**

- Base processing: ~100MB
- LLM response caching: ~50MB per document
- HTML parsing: ~25MB for large documents

**Cost Optimization:**

```env
# Cost-effective settings
OPENAI_MODEL=gpt-3.5-turbo  # Lower cost than GPT-4
OPENAI_MAX_TOKENS=500       # Limit response length
OPENAI_TEMPERATURE=0.3      # More consistent, focused responses
USE_MOCK_LLM=true          # Development without API costs
```

## Troubleshooting and Support

### Common Issues and Solutions

#### Missing Input Files

**Symptoms:** FileNotFoundError during validation

**Solutions:**

- Verify `content.html` exists in input directory
- Check `footnotes.json` is properly formatted
- Ensure input directory path is correct
- Validate file permissions and accessibility

#### API Authentication Issues

**Symptoms:** OpenAI API authentication errors

**Solutions:**

- Verify OPENAI_API_KEY in `.env` file
- Check API key validity and quota
- Use `--mock-llm` for development testing
- Confirm network connectivity

#### Invalid Citation Metadata

**Symptoms:** JSON parsing errors or incomplete validation

**Solutions:**

- Validate JSON syntax in `footnotes.json`
- Ensure all required citation fields are present
- Check character encoding (use UTF-8)
- Review citation data structure format

#### Memory or Performance Issues

**Symptoms:** Slow processing or out-of-memory errors

**Solutions:**

- Reduce `OPENAI_MAX_TOKENS` setting
- Process documents in smaller batches
- Enable debug logging to identify bottlenecks
- Increase system memory allocation

### Debug and Monitoring

#### Enable Debug Logging

```bash
# Command line debug mode
python main.py --log-level DEBUG

# Environment variable
export LOG_LEVEL=DEBUG
```

#### Validation Summary

```python
from citation_validator import CitationValidator

validator = CitationValidator()
summary = validator.get_validation_summary()

print("Configuration Summary:")
for key, value in summary.items():
    print(f"  {key}: {value}")
```

## Development and Contributing

### Development Setup

```bash
# Clone and setup development environment
git clone https://github.com/filip-herceg/ReViewPoint-CitationValidatorPro.git
cd ReViewPoint-CitationValidatorPro

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install in development mode
pip install -e .
pip install -r requirements.txt
```

### Running Tests and Examples

```bash
# Test with mock LLM (no API costs)
python main.py --mock-llm

# Run example scripts
python examples/basic_usage_mock.py
python examples/advanced_usage.py

# Test different configurations
python examples/basic_usage.py
```

### Architecture Overview

The codebase follows clean architecture principles:

- **Core Layer**: Business logic in `CitationValidator`
- **Application Layer**: CLI interface and configuration
- **Infrastructure Layer**: LLM providers and processors
- **Utilities Layer**: Prompts, source simulation, and helpers

### Adding New Features

**Extending LLM Providers:**

1. Create new provider class inheriting from `LLMProvider`
2. Implement `generate_response()` method
3. Add to `LLMFactory` provider creation logic
4. Update configuration options

**Custom Citation Formats:**

1. Extend `CitationDataProcessor` for new formats
2. Update prompt templates for format-specific analysis
3. Add validation rules for new citation styles
4. Update documentation and examples

### Contributing Guidelines

1. **Code Quality**: Follow PEP 8 and include type hints
2. **Testing**: Add comprehensive tests for new features
3. **Documentation**: Update docs for API changes
4. **Examples**: Provide usage examples for new functionality

## License and Support

### License

Citation Validator Pro is licensed under the MIT License, making it free for both academic and commercial use.

### Support Channels

- **Repository**: [ReViewPoint-CitationValidatorPro](https://github.com/filip-herceg/ReViewPoint-CitationValidatorPro)
- **Issues**: GitHub issue tracker for bugs and feature requests
- **Documentation**: Repository wiki and README files
- **Examples**: Comprehensive usage examples in `/examples` directory

### Version History

#### v2.0.0 (Current)

- Complete modular architecture refactor
- Output directory support and management
- Enhanced LLM provider system
- Improved error handling and logging
- Professional HTML report generation

#### v1.0.0

- Initial release with basic citation validation
- OpenAI GPT integration
- Simple HTML processing
- Basic validation pipeline

### Roadmap

#### Planned Enhancements

- **Multi-format Support**: PDF, Word, and LaTeX document processing
- **Advanced Citation Styles**: Support for more academic citation formats
- **Batch Processing**: Enhanced multi-document validation
- **Real-time Integration**: Live validation during document editing
- **Cloud Processing**: Scalable cloud-based validation services
- **Machine Learning**: Custom models for citation-specific analysis
