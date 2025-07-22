# Module Development Guide

> **Comprehensive guide for creating, integrating, testing, and deploying analysis modules in the ReViewPoint platform.**

---

## Overview

ReViewPoint's modular architecture allows developers to create custom analysis modules for scientific paper review. Each module is an independent microservice that can be developed, tested, and deployed separately while integrating seamlessly with the core platform.

### Module Architecture

- **Containerized Services**: Each module runs as a Docker container
- **REST API Interface**: Standardized HTTP endpoints for communication
- **Async Processing**: Non-blocking integration with the main platform
- **Independent Deployment**: Modules can be deployed and updated independently
- **Scalable Design**: Multiple instances can run in parallel

---

## Module Structure

### Standard Module Template

```
my-analysis-module/
├── Dockerfile              # Container configuration
├── requirements.txt         # Python dependencies
├── src/
│   ├── main.py             # FastAPI application entry point
│   ├── analysis.py         # Core analysis logic
│   ├── models.py           # Data models and validation
│   └── utils.py            # Helper functions
├── tests/
│   ├── test_analysis.py    # Unit tests
│   └── test_integration.py # Integration tests
├── config/
│   └── config.yaml         # Module configuration
└── README.md               # Module documentation
```

### Required API Endpoints

Each module must implement these standardized endpoints:

```python
@app.post("/analyze")
async def analyze_document(document: DocumentInput) -> AnalysisResult:
    """Main analysis endpoint"""
    pass

@app.get("/health")
async def health_check() -> HealthStatus:
    """Health check for monitoring"""
    pass

@app.get("/info")
async def module_info() -> ModuleInfo:
    """Module metadata and capabilities"""
    pass
```

---

## Creating Your First Module

### Step 1: Set Up the Module Structure

```bash
# Create module directory
mkdir my-analysis-module
cd my-analysis-module

# Copy template files (if available)
cp -r ../templates/module-template/* .

# Or create from scratch using the structure above
```

### Step 2: Implement Core Analysis Logic

```python
# src/analysis.py
from typing import Dict, List, Any
import asyncio

class DocumentAnalyzer:
    """Core analysis logic for your module"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
    async def analyze(self, document_content: str, metadata: Dict) -> Dict:
        """
        Implement your analysis logic here
        
        Args:
            document_content: Raw text content of the document
            metadata: Document metadata (title, authors, etc.)
            
        Returns:
            Analysis results in standardized format
        """
        # Your analysis implementation
        results = {
            "score": 85,
            "status": "success",
            "feedback": ["Document structure is clear", "Citations are properly formatted"],
            "details": {
                "word_count": len(document_content.split()),
                "section_count": document_content.count('\n\n'),
                # Add your specific metrics
            }
        }
        
        return results
```

### Step 3: Create FastAPI Application

```python
# src/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional
import logging

from .analysis import DocumentAnalyzer
from .models import DocumentInput, AnalysisResult, ModuleInfo

app = FastAPI(
    title="My Analysis Module",
    description="Custom analysis module for ReViewPoint",
    version="1.0.0"
)

# Initialize analyzer
analyzer = DocumentAnalyzer(config={})

@app.post("/analyze", response_model=AnalysisResult)
async def analyze_document(document: DocumentInput) -> AnalysisResult:
    """Analyze a document and return results"""
    try:
        results = await analyzer.analyze(
            document.content, 
            document.metadata
        )
        
        return AnalysisResult(
            module_name="my-analysis-module",
            version="1.0.0",
            **results
        )
    except Exception as e:
        logging.error(f"Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "module": "my-analysis-module"}

@app.get("/info", response_model=ModuleInfo)
async def module_info() -> ModuleInfo:
    """Return module information and capabilities"""
    return ModuleInfo(
        name="my-analysis-module",
        version="1.0.0",
        description="Custom document analysis module",
        capabilities=["structure_analysis", "citation_check"],
        input_formats=["text", "pdf"],
        output_format="json"
    )
```

### Step 4: Define Data Models

```python
# src/models.py
from pydantic import BaseModel
from typing import Dict, List, Optional, Any

class DocumentInput(BaseModel):
    """Input document for analysis"""
    content: str
    metadata: Dict[str, Any]
    format: str = "text"

class AnalysisResult(BaseModel):
    """Standardized analysis result format"""
    module_name: str
    version: str
    score: int  # 0-100
    status: str  # success, warning, error
    feedback: List[str]
    details: Optional[Dict[str, Any]] = None
    execution_time: Optional[float] = None

class ModuleInfo(BaseModel):
    """Module metadata and capabilities"""
    name: str
    version: str
    description: str
    capabilities: List[str]
    input_formats: List[str]
    output_format: str
```

### Step 5: Create Dockerfile

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY config/ ./config/

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1

# Run the application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

---

## Integration with ReViewPoint

### Module Registration

To integrate your module with the main ReViewPoint platform:

1. **Add Module Configuration**:
```yaml
# backend/config/modules.yaml
modules:
  - name: "my-analysis-module"
    endpoint: "http://my-module:8080"
    enabled: true
    timeout: 30
    retry_count: 3
```

2. **Update Module Dispatcher**:
```python
# backend/src/services/module_dispatcher.py
async def dispatch_analysis(document_id: str, modules: List[str]):
    """Dispatch document to specified analysis modules"""
    tasks = []
    for module_name in modules:
        if module_name in REGISTERED_MODULES:
            task = analyze_with_module(document_id, module_name)
            tasks.append(task)
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results
```

### Docker Compose Integration

```yaml
# backend/deployment/docker-compose.yml
services:
  my-analysis-module:
    build: 
      context: ./modules/my-analysis-module
      dockerfile: Dockerfile
    ports:
      - "8080:8080"
    environment:
      - MODULE_CONFIG_PATH=/app/config/config.yaml
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - reviewpoint-network
```

---

## Testing Your Module

### Unit Testing

```python
# tests/test_analysis.py
import pytest
from src.analysis import DocumentAnalyzer

@pytest.fixture
def analyzer():
    return DocumentAnalyzer(config={})

@pytest.mark.asyncio
async def test_basic_analysis(analyzer):
    """Test basic document analysis"""
    content = "This is a test document with multiple sections."
    metadata = {"title": "Test Document", "authors": ["Test Author"]}
    
    result = await analyzer.analyze(content, metadata)
    
    assert "score" in result
    assert "status" in result
    assert "feedback" in result
    assert isinstance(result["feedback"], list)
    assert 0 <= result["score"] <= 100

@pytest.mark.asyncio
async def test_empty_document(analyzer):
    """Test handling of empty documents"""
    content = ""
    metadata = {}
    
    result = await analyzer.analyze(content, metadata)
    
    assert result["status"] in ["warning", "error"]
    assert len(result["feedback"]) > 0
```

### Integration Testing

```python
# tests/test_integration.py
import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_analyze_endpoint():
    """Test the main analysis endpoint"""
    document_data = {
        "content": "Sample document content for analysis.",
        "metadata": {"title": "Test", "authors": ["Author"]},
        "format": "text"
    }
    
    response = client.post("/analyze", json=document_data)
    
    assert response.status_code == 200
    result = response.json()
    assert "module_name" in result
    assert "score" in result
    assert "status" in result

def test_health_endpoint():
    """Test health check endpoint"""
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

def test_info_endpoint():
    """Test module info endpoint"""
    response = client.get("/info")
    
    assert response.status_code == 200
    info = response.json()
    assert "name" in info
    assert "version" in info
    assert "capabilities" in info
```

### Load Testing

```python
# tests/test_performance.py
import asyncio
import pytest
from concurrent.futures import ThreadPoolExecutor
from fastapi.testclient import TestClient
from src.main import app

def test_concurrent_requests():
    """Test module performance under load"""
    client = TestClient(app)
    
    def make_request():
        document_data = {
            "content": "Test content for load testing.",
            "metadata": {"title": "Load Test"},
            "format": "text"
        }
        return client.post("/analyze", json=document_data)
    
    # Test with multiple concurrent requests
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(make_request) for _ in range(50)]
        results = [future.result() for future in futures]
    
    # Verify all requests succeeded
    success_count = sum(1 for r in results if r.status_code == 200)
    assert success_count >= 45  # Allow for some failures under load
```

---

## Deployment & Operations

### Local Development

```bash
# Build and run locally
docker build -t my-analysis-module .
docker run -p 8080:8080 my-analysis-module

# Test the endpoints
curl http://localhost:8080/health
curl -X POST http://localhost:8080/analyze \
  -H "Content-Type: application/json" \
  -d '{"content": "test", "metadata": {}, "format": "text"}'
```

### Production Deployment

```bash
# Build for production
docker build -t my-analysis-module:v1.0.0 .

# Deploy with docker-compose
docker-compose up -d my-analysis-module

# Monitor logs
docker-compose logs -f my-analysis-module
```

### Monitoring & Observability

```python
# Add logging and metrics to your module
import logging
import time
from prometheus_client import Counter, Histogram

# Metrics
ANALYSIS_REQUESTS = Counter('analysis_requests_total', 'Total analysis requests')
ANALYSIS_DURATION = Histogram('analysis_duration_seconds', 'Analysis duration')

@app.post("/analyze")
async def analyze_document(document: DocumentInput) -> AnalysisResult:
    ANALYSIS_REQUESTS.inc()
    
    start_time = time.time()
    try:
        # Perform analysis
        results = await analyzer.analyze(document.content, document.metadata)
        
        execution_time = time.time() - start_time
        ANALYSIS_DURATION.observe(execution_time)
        
        return AnalysisResult(execution_time=execution_time, **results)
    except Exception as e:
        logging.error(f"Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

---

## Best Practices

### Performance Optimization

1. **Async Operations**: Use async/await for I/O operations
2. **Connection Pooling**: Reuse database and HTTP connections
3. **Caching**: Cache expensive computations
4. **Batch Processing**: Process multiple documents together when possible
5. **Resource Limits**: Set appropriate memory and CPU limits

### Error Handling

1. **Graceful Degradation**: Return partial results when possible
2. **Detailed Logging**: Log errors with context for debugging
3. **Retry Logic**: Implement retries for transient failures
4. **Timeout Handling**: Set reasonable timeouts for operations
5. **Status Reporting**: Use consistent status codes and messages

### Security Considerations

1. **Input Validation**: Validate all input data thoroughly
2. **Rate Limiting**: Implement rate limiting to prevent abuse
3. **Authentication**: Use proper authentication for module endpoints
4. **Data Sanitization**: Sanitize user input to prevent injection attacks
5. **Container Security**: Use minimal base images and security scanning

---

## Advanced Topics

### Custom LLM Integration

```python
# Integrate with external LLM services
from openai import AsyncOpenAI

class LLMEnhancedAnalyzer(DocumentAnalyzer):
    def __init__(self, config):
        super().__init__(config)
        self.llm_client = AsyncOpenAI(api_key=config.get("openai_api_key"))
    
    async def analyze_with_llm(self, content: str) -> str:
        """Get LLM-powered analysis"""
        prompt = f"Analyze this document for clarity and structure:\n\n{content}"
        
        response = await self.llm_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500
        )
        
        return response.choices[0].message.content
```

### Multi-Format Document Processing

```python
# Handle different document formats
import fitz  # PyMuPDF
import docx
from bs4 import BeautifulSoup

class DocumentProcessor:
    @staticmethod
    async def extract_text(file_path: str, format: str) -> str:
        """Extract text from various document formats"""
        if format == "pdf":
            return await DocumentProcessor._extract_from_pdf(file_path)
        elif format == "docx":
            return await DocumentProcessor._extract_from_docx(file_path)
        elif format == "html":
            return await DocumentProcessor._extract_from_html(file_path)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    @staticmethod
    async def _extract_from_pdf(file_path: str) -> str:
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text()
        return text
```

### Module Chaining

```python
# Chain multiple analysis modules
class ModuleChain:
    def __init__(self, modules: List[str]):
        self.modules = modules
    
    async def execute(self, document: DocumentInput) -> List[AnalysisResult]:
        """Execute modules in sequence, passing results forward"""
        results = []
        current_doc = document
        
        for module_name in self.modules:
            result = await self.call_module(module_name, current_doc)
            results.append(result)
            
            # Optionally modify document for next module
            if result.status == "success":
                current_doc = self.enhance_document(current_doc, result)
        
        return results
```

---

## Resources & Support

### Documentation
- [Backend Source Guide](backend-source-guide.md) - Backend development patterns
- [API Reference](api-reference.md) - Platform API documentation
- [Test Instructions](test-instructions.md) - Testing guidelines

### Templates & Examples
- Check the `examples/modules/` directory for sample implementations
- Review existing modules in the platform for best practices
- Use the module template generator: `pnpm run create:module`

### Community & Support
- **GitHub Issues**: Report bugs and request features
- **Discussions**: Ask questions and share ideas
- **Pull Requests**: Contribute improvements and new modules

---

**Ready to build your first module?** Start with the template and follow this guide step by step. The ReViewPoint community is here to help you succeed!
