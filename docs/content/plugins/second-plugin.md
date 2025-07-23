# Literature Footnote Classification

An intelligent automated system for matching footnotes to literature entries in academic documents using LLM-powered analysis with strict formal validation criteria.

## Overview

The Literature Footnote Classification plugin (originally named "dkuzwekce") is a sophisticated analysis tool designed to automatically match footnotes with their corresponding literature entries in academic documents. This plugin leverages Large Language Models (LLMs) with carefully crafted prompts to ensure accurate bibliographic matching based on strict formal criteria rather than semantic similarity.

The plugin performs automated metadata validation for academic citations, focusing exclusively on formal matching criteria such as author surnames and publication years, making it an essential tool for academic document verification and citation consistency checking.

## Features

### Core Functionality

- **Automated Footnote-Literature Matching** - Intelligent matching of footnotes to literature entries using formal criteria
- **LLM-Powered Analysis** - Utilizes configurable Language Models for accurate bibliographic analysis
- **Strict Validation Criteria** - Matches based on author surnames and publication years only
- **Disambiguation Logic** - Handles cases where multiple literature entries might match a single footnote
- **JSON Data Processing** - Processes literature entries in structured JSON format
- **HTML Footnote Parsing** - Extracts and processes footnotes from HTML documents
- **Response Caching** - Saves all LLM responses for analysis and debugging

### Advanced Analysis Features

- **Multi-Author Handling** - Proper processing of "et al." citations and multiple author scenarios
- **Year Validation** - Exact publication year matching between footnotes and literature entries
- **Conflict Resolution** - Automated disambiguation when multiple matches are found
- **Progress Tracking** - Real-time status monitoring and logging throughout the matching process
- **Error Recovery** - Robust error handling with detailed logging and status reporting

### Configuration & Customization

- **Flexible LLM Integration** - Support for various LLM providers (OpenAI, custom models)
- **Configurable Parameters** - Adjustable temperature, token limits, and request intervals
- **Custom Prompt Templates** - Modifiable prompt templates for different matching scenarios
- **Rate Limiting** - Built-in request interval controls to avoid API limitations
- **Dummy Mode** - Fallback to dummy client when no API key is provided

## Installation

### Automatic Setup

This plugin is automatically cloned when you run the ReViewPoint plugin setup task:

1. Open VS Code in the ReViewPoint workspace
2. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on macOS)
3. Type "Tasks: Run Task" and select it
4. Choose "ReViewPoint: Setup Plugin Repositories"

### Manual Installation

```bash
cd ReViewPoint/plugin_prototypes
git clone https://github.com/Swabble/literature_footnote_classification.git
cd literature_footnote_classification
pip install -r requirements.txt
```

### Dependencies

Required Python packages (from `requirements.txt`):

- **Python 3.9+** - Core runtime environment
- **requests** - HTTP client for LLM API calls
- **beautifulsoup4** - HTML parsing for footnote extraction
- **pytest** - Testing framework (for development)

## Configuration

### Basic Configuration

Create or modify the `config.json` file in the plugin directory:

```json
{
  "api_key": "YOUR_API_KEY",
  "model": "gpt-4o-mini",
  "max_tokens": 500,
  "temperature": 0.3,
  "request_interval": 1.0,
  "responses_dir": "responses"
}
```

### Configuration Parameters

| Parameter          | Description                        | Default        | Required |
| ------------------ | ---------------------------------- | -------------- | -------- |
| `api_key`          | LLM API key (OpenAI, etc.)         | None           | No\*     |
| `model`            | LLM model identifier               | `gpt-4.1-nano` | No       |
| `max_tokens`       | Maximum tokens per request         | `500`          | No       |
| `temperature`      | LLM temperature setting            | `0.3`          | No       |
| `request_interval` | Delay between API calls (seconds)  | `1.0`          | No       |
| `responses_dir`    | Directory for LLM response storage | `responses`    | No       |

**Note:** When no `api_key` is provided, the plugin automatically uses a `DummyAPIClient` for testing and development.

### Prompt Template Customization

The plugin uses customizable prompt templates located in `prompt_templates/`:

- **`basic_prompt.txt`** - Main matching prompt for standard cases
- **`disambiguation_prompt.txt`** - Disambiguation prompt for multiple matches

You can modify these templates to adjust the matching behavior and criteria.

## Usage

### Basic Usage

Run the plugin directly from its directory:

```bash
cd plugin_prototypes/literature_footnote_classification
python run.py
```

### Input Data Format

#### Literature Entries (`data/literature.json`)

```json
[
  {
    "author": "Smith, John",
    "title": "Academic Writing Principles",
    "year": "2023",
    "publisher": "Academic Press"
  },
  {
    "author": "Johnson, Mary",
    "title": "Citation Standards in Research",
    "year": "2022",
    "journal": "Research Methods Quarterly"
  }
]
```

#### Footnotes (`data/footnotes.html`)

```html
<html>
  <body>
    <div class="footnote">
      1. Smith, J. (2023). Academic Writing Principles.
    </div>
    <div class="footnote">2. Johnson et al. (2022). Citation Standards.</div>
  </body>
</html>
```

### Output and Results

The plugin generates several types of output:

1. **Status File** (`status.json`) - Current processing status and progress
2. **Log File** (`app.log`) - Detailed execution logs
3. **LLM Responses** (`responses/` directory) - All LLM API responses for analysis
4. **Console Output** - Real-time progress and status information

### Integration with ReViewPoint

The plugin is designed to integrate with ReViewPoint's document processing pipeline:

```python
# Example integration (conceptual)
from plugins.literature_footnote_classification import FootnoteAnalyzer

analyzer = FootnoteAnalyzer(config_path="config.json")
results = analyzer.process_document(
    literature_entries=literature_data,
    footnotes_html=footnotes_data
)

# Access results
matches = results.get_matches()
unmatched_footnotes = results.get_unmatched()
disambiguation_cases = results.get_disambiguation_cases()
```

## Technical Architecture

### Module Structure

The plugin follows a modular architecture with clear separation of concerns:

```
src/
├── __init__.py              # Package initialization and exports
├── data_ingestion.py        # Literature and footnote data loading
├── llm_client.py           # LLM API client and communication
├── logging_manager.py      # Centralized logging configuration
├── matching_logic.py       # Core matching and disambiguation logic
└── status_manager.py       # Progress tracking and status management
```

### Key Components

#### Data Ingestion (`data_ingestion.py`)

- **Literature Loading** - Parses JSON literature entries with unique IDs (`L00001`, `L00002`, ...)
- **Footnote Extraction** - Processes HTML footnotes with unique IDs (`F00001`, `F00002`, ...)
- **Data Validation** - Ensures proper format and required fields

#### LLM Client (`llm_client.py`)

- **API Integration** - Handles communication with LLM providers
- **Rate Limiting** - Implements configurable request intervals
- **Error Handling** - Robust error recovery and retry logic
- **Dummy Mode** - Fallback client for testing without API access

#### Matching Logic (`matching_logic.py`)

- **Core Matching** - Implements formal validation criteria (author/year matching)
- **Disambiguation** - Resolves conflicts when multiple matches are found
- **Result Validation** - Ensures LLM responses meet expected format requirements

#### Status Management (`status_manager.py`)

- **Progress Tracking** - Real-time processing status updates
- **Error Recovery** - State preservation for interrupted processing
- **Performance Metrics** - Processing statistics and timing information

### Data Flow

1. **Initialization** - Load configuration and initialize components
2. **Data Loading** - Read literature entries and footnotes from input files
3. **Processing Loop** - For each footnote, attempt to find matching literature entries
4. **LLM Analysis** - Query LLM with structured prompts for matching decisions
5. **Result Processing** - Validate LLM responses and handle disambiguation
6. **Output Generation** - Save results, logs, and status information

## Validation Criteria

The plugin uses strict formal criteria for matching footnotes to literature entries:

### Primary Matching Rules

1. **Author Surname Match**
   - Footnote must include exact same surname as literature entry author
   - For "et al." citations, first listed surname must match exactly
   - Single author entries do not match multi-author footnotes (unless "et al.")

2. **Year Match**
   - Publication year in footnote must exactly match literature entry year
   - No fuzzy matching or year ranges accepted

### Excluded Criteria

The plugin explicitly **does not** consider:

- Topic similarity or subject matter overlap
- Semantic relationships between content
- Title matching or partial title overlap
- Publisher or journal information
- Page numbers or other citation details

This strict approach ensures high precision in bibliographic matching while avoiding false positives from content similarity.

## Development and Testing

### Running Tests

```bash
cd plugin_prototypes/literature_footnote_classification
pytest -q
```

### Development Setup

1. **Clone the Repository**

   ```bash
   git clone https://github.com/Swabble/literature_footnote_classification.git
   cd literature_footnote_classification
   ```

2. **Create Virtual Environment**

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/macOS
   # or
   .venv\Scripts\activate     # Windows
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure for Development**
   ```bash
   # Copy config template and add your API key
   cp config.json.example config.json
   # Edit config.json with your settings
   ```

### Adding Custom Validation Logic

To extend the matching criteria or add custom validation logic:

1. **Modify Prompt Templates** - Update `prompt_templates/basic_prompt.txt` with new criteria
2. **Extend Matching Logic** - Add custom validation in `src/matching_logic.py`
3. **Update Configuration** - Add new parameters to `config.json` schema
4. **Test Changes** - Ensure all existing functionality continues to work

## Repository Information

- **Repository:** [https://github.com/Swabble/literature_footnote_classification](https://github.com/Swabble/literature_footnote_classification)
- **Status:** Production Ready (Built-in)
- **Language:** Python 3.9+
- **License:** [Check repository for license details]
- **Maintainer:** Swabble

## ReViewPoint Platform Integration

### Plugin Registration

The plugin integrates with ReViewPoint through the standard plugin architecture:

- **Discovery** - Automatically detected in `plugin_prototypes/` directory
- **Configuration** - Uses ReViewPoint's centralized configuration system
- **API Integration** - Exposes endpoints for footnote analysis
- **Data Flow** - Integrates with document processing pipeline

### Usage in Review Workflow

1. **Document Upload** - Academic papers uploaded to ReViewPoint
2. **Content Extraction** - PDF processing extracts footnotes and bibliography
3. **Plugin Execution** - Literature Footnote Classification analyzes citations
4. **Report Generation** - Results integrated into review reports
5. **Reviewer Interface** - Citation analysis available to human reviewers

## Performance Considerations

### Optimization Tips

- **Batch Processing** - Group similar footnotes for efficient LLM queries
- **Caching** - Leverage response caching for repeated analyses
- **Rate Limiting** - Adjust `request_interval` based on API quotas
- **Model Selection** - Choose appropriate LLM model for speed vs. accuracy trade-offs

### Scalability

- **Concurrent Processing** - Plugin supports parallel processing of multiple documents
- **Memory Management** - Efficient handling of large literature databases
- **API Quota Management** - Built-in rate limiting prevents quota exhaustion

## Troubleshooting

### Common Issues

1. **API Key Problems**
   - Ensure valid API key in `config.json`
   - Check API quota and rate limits
   - Verify model availability

2. **Data Format Issues**
   - Validate JSON structure for literature entries
   - Ensure HTML footnotes are properly formatted
   - Check character encoding (UTF-8)

3. **Performance Issues**
   - Increase `request_interval` for rate limiting
   - Reduce `max_tokens` for faster processing
   - Use lighter LLM models for better performance

### Debug Mode

Enable detailed logging by modifying the logging level in `src/logging_manager.py`:

```python
logging.basicConfig(level=logging.DEBUG)
```

### Support Resources

- **Plugin Issues:** [GitHub Issues](https://github.com/Swabble/literature_footnote_classification/issues)
- **ReViewPoint Integration:** [Main Repository](https://github.com/filip-herceg/ReViewPoint)
- **Documentation:** Plugin README and source code comments

## Future Enhancements

### Planned Features

- **Multi-language Support** - Citation analysis in multiple languages
- **Enhanced Disambiguation** - Improved conflict resolution algorithms
- **Performance Optimization** - Faster processing for large document sets
- **API Integration** - Direct integration with academic databases
- **Machine Learning** - Custom ML models for citation pattern recognition

### Contribution Opportunities

- **Algorithm Improvements** - Enhance matching accuracy and performance
- **Data Format Support** - Add support for additional bibliography formats
- **Integration Features** - Improve ReViewPoint platform integration
- **Testing Coverage** - Expand test suite and validation scenarios
- **Documentation** - Improve user guides and API documentation

---

This plugin represents a sophisticated approach to automated bibliographic analysis, providing essential functionality for academic document review and citation validation within the ReViewPoint ecosystem.
