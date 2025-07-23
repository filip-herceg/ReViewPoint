# ReViewPoint Plugins

ReViewPoint is designed with modularity in mind, allowing for powerful extensions through our plugin ecosystem. Our official plugins enhance the platform's capabilities for scientific paper review and analysis.

## Quick Setup

### Automatic Installation (Recommended)

The easiest way to set up all plugin repositories is using our VS Code task:

1. Open VS Code in the ReViewPoint workspace
2. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on macOS)
3. Type "Tasks: Run Task" and select it
4. Choose "ReViewPoint: Setup Plugin Repositories"

This will automatically clone all plugin repositories into the `plugin_prototypes/` directory if they don't already exist.

### Manual Installation

If you prefer to set up plugins manually:

```bash
# Navigate to the ReViewPoint root directory
cd ReViewPoint

# Create plugin directory if it doesn't exist
mkdir -p plugin_prototypes
cd plugin_prototypes

# Clone the plugin repositories
git clone https://github.com/Swabble/pdf_latex_converter.git
git clone https://github.com/Swabble/literature_footnote_classification.git
git clone https://github.com/filip-herceg/ReViewPoint-CitationValidatorPro.git
```

## Official Plugins

### 1. PDF LaTeX Converter

**Status:** In Development (Built-in)  
**Repository:** [pdf_latex_converter](https://github.com/Swabble/pdf_latex_converter.git)

The PDF LaTeX Converter is ReViewPoint's primary document processing plugin, designed to intelligently extract and structure content from PDF documents using advanced parsing and AI-assisted analysis. This plugin transforms unstructured PDF content into well-organized, machine-readable formats suitable for academic review workflows.

**Key Features:**

- Intelligent PDF parsing with font and structure recognition
- AI-powered heading and section extraction
- Automatic footnote detection and processing
- Bibliography extraction and structuring
- HTML and structured text output generation
- Citation format conversion and validation

**Use Cases:**

- Converting submitted research papers to structured review format
- Extracting document hierarchy for automated analysis
- Preparing papers for citation analysis and validation
- Generating structured content for review workflow integration
- Creating searchable and navigable document versions

[Learn more about PDF LaTeX Converter →](plugins/pdf-latex-converter.md)

### 2. Literature Footnote Classification

**Status:** In Development (Built-in)  
**Repository:** [literature_footnote_classification](https://github.com/Swabble/literature_footnote_classification.git)

The Literature Footnote Classification plugin is an intelligent analysis tool designed to automatically categorize and analyze footnotes within academic literature. This plugin enhances the review process by providing structured insights into citation patterns, reference types, and footnote usage across scientific documents.

**Key Features:**

- Automated footnote detection and extraction
- Machine learning-based footnote classification
- Citation pattern analysis and insights
- Reference type categorization
- Statistical reporting on footnote usage
- Integration with citation validation workflows

**Use Cases:**

- Analyzing citation patterns in academic papers during review
- Quality assessment of reference usage and documentation
- Automated categorization of footnote types for consistency checking
- Supporting reviewers with structured footnote analysis
- Generating reports on citation and reference practices

[Learn more about Literature Footnote Classification →](plugins/second-plugin.md)

### 3. Citation Validator Pro

**Status:** In Development (Marketplace)  
**Repository:** [ReViewPoint-CitationValidatorPro](https://github.com/filip-herceg/ReViewPoint-CitationValidatorPro)

The Citation Validator Pro is a comprehensive tool for validating and analyzing citations in scientific papers. It helps ensure citation accuracy, completeness, and adherence to academic standards.

**Key Features:**

- Advanced citation format validation
- Cross-reference verification
- Citation completeness analysis
- Multiple citation style support
- Integration with academic databases

**Use Cases:**

- Automated citation checking during paper review
- Quality assurance for academic publications
- Citation style consistency verification
- Reference list validation

[Learn more about Citation Validator Pro →](plugins/citation-validator-pro.md)

## Plugin Development

### Creating Custom Plugins

ReViewPoint's plugin architecture allows developers to create custom extensions. Our plugin system is designed to be:

- **Modular:** Each plugin operates independently
- **Extensible:** Easy to add new functionality
- **Standardized:** Consistent API and integration patterns
- **Maintainable:** Clear separation of concerns

### Plugin Requirements

All ReViewPoint plugins should:

1. Follow our coding standards and conventions
2. Include comprehensive documentation
3. Provide unit tests with good coverage
4. Use appropriate error handling
5. Support configuration through environment variables

### Contributing

We welcome contributions to our official plugins and encourage the development of community plugins. Please see our [contributing guidelines](../resources/guidelines.md) for more information.

## Support and Documentation

- **Plugin Issues:** Report issues in the respective plugin repositories
- **General Support:** Use the main [ReViewPoint repository](https://github.com/filip-herceg/ReViewPoint) for general questions
- **Development Questions:** Check our [developer documentation](developer-overview.md)

## Plugin Integration

Each plugin is designed to integrate seamlessly with the ReViewPoint platform:

- **API Integration:** Plugins can interact with ReViewPoint's REST API
- **Database Access:** Shared database access for data persistence
- **Event System:** Plugin hooks for common workflow events
- **Configuration Management:** Centralized configuration through the main platform

For detailed integration instructions, see the individual plugin documentation pages.
