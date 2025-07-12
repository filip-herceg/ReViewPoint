# errorHandling

## Purpose

Consistent error handling for network, 4xx, 5xx, and unknown errors. Integrates with logger and provides helpers for API and UI error handling.

## API

- `handleApiError(error: unknown): HandledError` — Handles API/network errors and returns a normalized error object.
- `getErrorMessage(error: unknown): string` — Returns a user-friendly error message from any error value.

## Usage Example

```ts
import { handleApiError } from "@/lib/api/errorHandling";
import { getErrorMessage } from "@/lib/utils/errorHandling";

try {
  // ...
} catch (err) {
  const handled = handleApiError(err);
  // handled.type, handled.status, handled.message
}

const msg = getErrorMessage(err);
```

## Related Files

- [Test file](../../../tests/lib/api/errorHandling.test.ts)
- [Test file](../../../tests/lib/utils/errorHandling.test.ts)

---

_Replace placeholders as you implement utilities._
