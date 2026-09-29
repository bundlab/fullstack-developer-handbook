# Chapter 02: HTML, CSS, JavaScript/TypeScript

Modern web development relies on a solid understanding of semantic document structure, scalable styling systems, asynchronous runtime execution, and strong type safety.

---

## 1. Semantic HTML5 & Modern Accessibility (a11y)

Semantic HTML improves SEO, readability, and accessibility by providing structural meaning to browser engines and screen readers.

### Key Semantic Elements

```html
<header>    <!-- Navigation, logos, site header -->
<nav>       <!-- Primary navigation link groups -->
<main>      <!-- Main central content of document (1 per page) -->
<article>   # Standalone, reusable content unit (e.g., blog post)
<section>   <!-- Thematic grouping of content with a heading -->
<aside>     <!-- Tangential content (sidebar, related links) -->
<footer>    <!-- Page/section level copyright, contact info -->

```

### Accessible Form Design Pattern

```html
<form aria-labelledby="form-title">
  <h2 id="form-title">User Registration</h2>

  <div class="form-group">
    <label for="user-email">Email Address</label>
    <input 
      type="email" 
      id="user-email" 
      name="email" 
      required 
      aria-describedby="email-help"
      placeholder="alex@example.com"
    />
    <small id="email-help">We'll never share your email with third parties.</small>
  </div>

  <button type="submit" aria-label="Submit registration form">Register</button>
</form>

```

---

## 2. Modern CSS Layouts & Architecture

### CSS Grid vs. Flexbox

* **Flexbox (1D):** Ideal for alignment along a single axis (row or column). Great for toolbars, navigation bars, and card components.
* **CSS Grid (2D):** Ideal for layout structures requiring simultaneous row and column coordination (page templates, dashboard widgets).

```css
/* Responsive Card Grid with Modern CSS Grid */
.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
  padding: 1rem;
}

/* Flexbox Component Centering */
.card {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  border-radius: 8px;
  padding: 1rem;
  background-color: var(--surface-color, #ffffff);
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

```

---

## 3. JavaScript Asynchronous Execution & Event Loop

JavaScript is single-threaded and executes non-blocking asynchronous operations via an **Event Loop**.

```
┌──────────────────────────────────────────┐
│                Call Stack                │
└────────────────────┬─────────────────────┘
                     │
┌────────────────────▼─────────────────────┐
│               Web APIs                   │
│   (DOM, fetch, setTimeout, Promises)     │
└────────────────────┬─────────────────────┘
                     │
         ┌───────────┴──────────┐
         ▼                      ▼
┌──────────────────┐  ┌──────────────────┐
│ Microtask Queue  │  │  Macrotask Queue │
│ (Promises,       │  │ (setTimeout,     │
│  queueMicrotask) │  │  setInterval)    │
└────────┬─────────┘  └────────┬─────────┘
         │                     │
         └───────────┬─────────┘
                     │
┌────────────────────▼─────────────────────┐
│               Event Loop                 │
└──────────────────────────────────────────┘

```

> **Execution Order:** Microtasks always execute **before** the next Macrotask in line.

### Async/Await with Robust Error Handling

```javascript
async function fetchUserData(userId) {
  try {
    const response = await fetch(`https://api.example.com/users/${userId}`, {
      headers: { 'Accept': 'application/json' }
    });

    if (!response.ok) {
      throw new Error(`HTTP Error! Status: ${response.status}`);
    }

    const userData = await response.json();
    return userData;
  } catch (error) {
    console.error('Failed to retrieve user data:', error.message);
    throw error; // Re-throw or return fallback state
  }
}

```

---

## 4. TypeScript Type Safety & Generics

TypeScript adds static typing to JavaScript, catching type errors at compile time rather than runtime.

### Interfaces, Union Types, and Generics

```typescript
// Interface contract
interface User {
  id: string;
  name: string;
  email: string;
  role: 'admin' | 'editor' | 'viewer'; // Union type
  createdAt: Date;
}

// Generic API Response Wrapper
interface ApiResponse<T> {
  data: T;
  status: number;
  message: string;
  timestamp: string;
}

// Generic Fetcher Function
async function apiGet<T>(url: string): Promise<ApiResponse<T>> {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`API Fetch Failed: ${response.statusText}`);
  }
  return await response.json() as ApiResponse<T>;
}

// Usage with strict typing
async function loadUser() {
  const result = await apiGet<User>('/api/v1/users/usr_123');
  console.log(`User ${result.data.name} is an ${result.data.role}`);
}

```

---

## 🧪 Practical Lab Exercise: Type-Safe Async Data Fetcher

### Goal

Build a lightweight, type-safe data fetcher script that handles network requests, state transitions (`idle`, `loading`, `success`, `error`), and generic responses in TypeScript.

1. Create `labs/frontend/src/lab_02_async_fetcher.ts`.
2. Define a generic state union: `FetchState<T>`.
3. Implement a reusable state container class `AsyncDataLoader<T>`.

#### Lab Implementation Code

```typescript
// labs/frontend/src/lab_02_async_fetcher.ts

export type FetchState<T> =
  | { status: 'idle' }
  | { status: 'loading' }
  | { status: 'success'; data: T }
  | { status: 'error'; error: Error };

export class AsyncDataLoader<T> {
  private state: FetchState<T> = { status: 'idle' };

  public getState(): FetchState<T> {
    return this.state;
  }

  public async load(fetcherFn: () => Promise<T>): Promise<FetchState<T>> {
    this.state = { status: 'loading' };
    try {
      const data = await fetcherFn();
      this.state = { status: 'success', data };
    } catch (err) {
      this.state = { 
        status: 'error', 
        error: err instanceof Error ? err : new Error(String(err)) 
      };
    }
    return this.state;
  }
}

```

---