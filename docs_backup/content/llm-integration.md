# LLM Integration Guide

Complete guide to Large Language Model integration patterns and provider management in ReViewPoint.

## Overview

ReViewPoint provides a flexible, extensible architecture for integrating multiple Large Language Model (LLM) providers. The system supports:

- **Multi-Provider Support**: OpenAI, Anthropic, local models, and custom providers
- **Unified API**: Consistent interface across all providers
- **Async Operations**: Non-blocking LLM calls for high performance
- **Rate Limiting**: Built-in throttling and quota management
- **Caching**: Intelligent response caching to reduce costs
- **Fallback Systems**: Automatic provider switching on failures

## Quick Start

### 1. Choose Your LLM Provider

```bash
# OpenAI (recommended for production)
REVIEWPOINT_OPENAI_API_KEY=your_openai_key
REVIEWPOINT_OPENAI_MODEL=gpt-4

# Anthropic (for long documents)
REVIEWPOINT_ANTHROPIC_API_KEY=your_anthropic_key
REVIEWPOINT_ANTHROPIC_MODEL=claude-3-opus-20240229

# Local Models (for privacy)
REVIEWPOINT_LOCAL_MODEL_URL=http://localhost:11434
REVIEWPOINT_LOCAL_MODEL_NAME=llama2
```

### 2. Configure Credentials

Add to your `.env` file:

```bash
# Never hardcode API keys in source code
REVIEWPOINT_LLM_PROVIDER=openai
REVIEWPOINT_OPENAI_API_KEY=sk-your-key-here
REVIEWPOINT_OPENAI_MODEL=gpt-4
REVIEWPOINT_OPENAI_MAX_TOKENS=4096
```

### 3. Test Integration

```python
from services.llm import LLMService

# Test basic completion
llm = LLMService()
response = await llm.complete("Test prompt")
print(response.content)
```

## Supported Providers

### OpenAI
- **Models**: GPT-4, GPT-3.5, GPT-4 Turbo
- **Best For**: General analysis, high-quality responses
- **Cost**: Variable, token-based pricing

### Anthropic
- **Models**: Claude-3 Opus, Sonnet, Haiku
- **Best For**: Long documents, complex reasoning
- **Cost**: Competitive, good for large documents

### Local Models
- **Backends**: Ollama, vLLM, LlamaCpp
- **Best For**: Privacy-sensitive applications
- **Cost**: No API costs, hardware requirements

## Configuration

### Environment Variables

```bash
# Provider Selection
REVIEWPOINT_DEFAULT_PROVIDER=openai
REVIEWPOINT_FALLBACK_PROVIDERS=anthropic,local

# OpenAI Configuration
REVIEWPOINT_OPENAI_API_KEY=your_key
REVIEWPOINT_OPENAI_MODEL=gpt-4
REVIEWPOINT_OPENAI_MAX_TOKENS=4096
REVIEWPOINT_OPENAI_TEMPERATURE=0.7

# Rate Limiting
REVIEWPOINT_LLM_RATE_LIMIT_PER_MINUTE=60
REVIEWPOINT_LLM_COST_LIMIT_PER_DAY=100.00
```

### Provider Configuration

Configure in `core/config.py`:

```python
LLM_PROVIDERS = {
    "openai": {
        "class": "OpenAIProvider",
        "api_key": os.getenv("REVIEWPOINT_OPENAI_API_KEY"),
        "model": "gpt-4",
        "max_tokens": 4096,
        "temperature": 0.7,
        "timeout": 30.0,
        "retry_attempts": 3
    }
}
```

## Usage Patterns

### Basic Text Completion

```python
from services.llm import LLMService

llm = LLMService()

# Simple completion
response = await llm.complete(
    "Analyze this research paper for methodological issues:",
    provider="openai",
    model="gpt-4"
)

print(response.content)
```

### Chat-Based Interaction

```python
messages = [
    {"role": "system", "content": "You are a scientific paper reviewer."},
    {"role": "user", "content": "Please review this paper's methodology."}
]

response = await llm.chat(
    messages=messages,
    provider="anthropic"
)
```

### Streaming Responses

```python
async for chunk in llm.stream(
    "Provide detailed analysis:",
    provider="openai"
):
    print(chunk, end="", flush=True)
```

## Error Handling

### Comprehensive Error Management

```python
from exceptions import LLMProviderError, RateLimitError

try:
    response = await llm.complete(prompt)
except RateLimitError:
    # Wait and retry or switch providers
    await asyncio.sleep(60)
    response = await llm.complete(prompt, provider="anthropic")
except LLMProviderError as e:
    # Log error and use fallback
    logger.error(f"Provider error: {e}")
    response = await llm.complete(prompt, provider="fallback")
```

## Testing

### Mock Providers for Testing

```python
from testing.llm_mocks import MockLLMProvider

llm = LLMService()
llm.register_provider("mock", MockLLMProvider({
    "default_response": "Test response",
    "response_time": 0.1
}))

# Test with predictable responses
response = await llm.complete("Test prompt", provider="mock")
assert response.content == "Test response"
```

## Security Best Practices

### API Key Management
- **Environment Variables**: Store keys securely
- **Key Rotation**: Support for rotating API keys
- **Access Control**: Role-based access to providers
- **Audit Logging**: Track all API usage

### Data Privacy
```python
# Keep sensitive data local
response = await llm.complete(
    prompt,
    provider="local",  # Use local model
    privacy_mode=True,  # Strip PII from logs
    retention_policy="delete_after_processing"
)
```

## Performance Optimization

### Connection Pooling
```python
llm.configure_provider("openai", {
    "connection_pool_size": 20,
    "max_connections": 100,
    "keep_alive": True
})
```

### Caching Strategy
```python
# Cache responses for identical requests
cached_response = await llm.complete(
    "Standard review prompt",
    cache_key="standard_review",
    cache_ttl=3600  # 1 hour
)
```

## Monitoring and Metrics

### Built-in Metrics
- **Request Volume**: Requests per provider
- **Response Time**: Latency by provider and model
- **Cost Tracking**: Real-time cost monitoring
- **Error Rates**: Success/failure rates
- **Cache Hit Rates**: Caching effectiveness

### Custom Dashboards
```python
llm.configure_metrics_export(
    prometheus_endpoint="/metrics",
    datadog_tags={"service": "reviewpoint", "env": "production"}
)
```

## Advanced Features

### Cost Optimization
```python
# Estimate costs before requests
cost_estimate = llm.estimate_cost(
    prompt="Long document analysis",
    provider="openai",
    model="gpt-4"
)

if cost_estimate > budget_threshold:
    # Switch to cheaper provider
    response = await llm.complete(
        prompt,
        provider="anthropic",
        model="claude-3-haiku-20240307"
    )
```

### Function Calling
```python
# OpenAI function calling
functions = [
    {
        "name": "extract_methodology",
        "description": "Extract methodology information",
        "parameters": {
            "type": "object",
            "properties": {
                "research_design": {"type": "string"},
                "sample_size": {"type": "integer"}
            }
        }
    }
]

response = await llm.complete(
    "Extract methodology from this paper:",
    provider="openai",
    functions=functions,
    function_call="auto"
)
```

## Integration Tips

- **Store secrets securely** (never hardcode API keys)
- **Use environment variables** for configuration
- **Add integration tests** for new adapters
- **Monitor costs** and set budgets
- **Implement fallback strategies** for reliability
- **Cache responses** when appropriate
- **Use local models** for sensitive data

## Troubleshooting

### Common Issues

1. **API Key Errors**: Check environment variables
2. **Rate Limiting**: Implement exponential backoff
3. **High Costs**: Monitor usage and implement budgets
4. **Slow Responses**: Use appropriate model sizes
5. **Connection Issues**: Implement retry logic

### Debug Mode

```python
# Enable debug logging
llm.configure_logging(
    level="DEBUG",
    log_requests=True,
    log_responses=True
)
```

## Contributing

Add your integration notes and tips! See [Contributing to Docs](contributing-docs.md) for guidelines.

## Related Documentation

- [Module Guide](module-guide.md) - Creating analysis modules that use LLMs
- [API Reference](api-reference.md) - LLM service API documentation
- [Configuration](setup.md) - Environment setup and configuration
- [Testing](test-instructions.md) - Testing LLM integrations
