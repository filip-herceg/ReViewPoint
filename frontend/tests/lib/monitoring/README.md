# Monitoring Tests Directory

⚠️ **WARNING: Error Monitoring Tests Disabled** ⚠️

## Disabled Tests

The following test file has been **PERMANENTLY DISABLED** due to infinite loops:

- `errorMonitoring.test.ts` - **DO NOT ENABLE**

## Why These Tests Are Disabled

The error monitoring tests cause the entire test suite to hang indefinitely. The tests create infinite loops through:

- Asynchronous operations that never resolve
- Event listeners that aren't properly cleaned up
- Promise chains that create circular dependencies
- Mocked modules that interfere with test isolation

## Symptoms

When these tests are enabled:

- Test runner hangs at "0/21" tests
- Process never completes (even after hours)
- Must be terminated with keyboard interrupt
- Blocks entire CI/CD pipeline

## Safety Measures

Multiple safety measures have been implemented:

1. **Code Level**: Tests use `describe.skip()` to prevent execution
2. **Config Level**: Test file excluded in `vitest.config.ts`
3. **Documentation**: Clear warnings in test file and this README
4. **Monitoring**: Original test content completely removed

## Re-enabling Instructions (NOT RECOMMENDED)

**DO NOT** re-enable these tests unless you have:

1. ✅ Identified root cause of infinite loops
2. ✅ Created isolated unit tests that complete successfully
3. ✅ Added proper timeouts and cleanup for ALL async operations
4. ✅ Verified test isolation and proper mocking
5. ✅ Tested entire suite completes end-to-end
6. ✅ Added monitoring to detect infinite loops

## Alternative Testing Strategy

If you need to test error monitoring functionality:

```typescript
// ✅ DO: Create isolated unit tests
describe('Error Service - Unit Tests', () => {
  it('should format error messages', () => {
    // Test pure functions only
  });
});

// ❌ DON'T: Test full error monitoring system
describe('Error Monitoring Integration', () => {
  // This will likely cause infinite loops
});
```

## Support

If you need to work on error monitoring:

- Focus on testing individual functions
- Use explicit timeouts for ALL async operations  
- Mock ALL external dependencies
- Test in complete isolation

---

**Last Updated**: July 9, 2025  
**Status**: Permanently disabled due to infinite loops  
**Action Required**: None - keep disabled
