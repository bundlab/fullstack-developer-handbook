# Chapter 03: React / Flutter / Modern Frontend Development

Modern frontend engineering relies on component-driven architectures, unidirectional data flow, reactive state management, and optimized rendering engines across web and native mobile platforms.

---

## 1. Web Frontend: Modern React 18+ Architecture

React structures UIs into composable components using declarative JSX, state hooks, and side-effect controls.

### React Component Lifecycle & Essential Hooks

* **`useState`**: Local component state persistence across renders.
* **`useEffect`**: Encapsulates side effects (data fetching, subscriptions, DOM mutations).
* **`useMemo` & `useCallback**`: Memoization primitives to optimize render cycles.
* **`useContext`**: Avoids prop-drilling by providing global scope trees.

### Production React Pattern: Custom Hook + Declarative State

```tsx
import React, { useState, useEffect, useCallback } from 'react';

interface Post {
  id: number;
  title: string;
  body: string;
}

// Custom Hook for Encapsulated Data Fetching
function useFetchPosts(url: string) {
  const [posts, setPosts] = useState<Post[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const refetch = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(url);
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      const data: Post[] = await response.json();
      setPosts(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  }, [url]);

  useEffect(() => {
    refetch();
  }, [refetch]);

  return { posts, loading, error, refetch };
}

// Presentation Component
export const PostList: React.FC = () => {
  const { posts, loading, error, refetch } = useFetchPosts(
    'https://jsonplaceholder.typicode.com/posts?_limit=5'
  );

  if (loading) return <div className="spinner">Loading posts...</div>;
  if (error) return <div className="error-banner">Error: {error}</div>;

  return (
    <div className="post-container">
      <div className="header-actions">
        <h2>Latest Articles</h2>
        <button onClick={refetch} className="btn-primary">Refresh</button>
      </div>
      <ul className="post-list">
        {posts.map((post) => (
          <li key={post.id} className="post-card">
            <h3>{post.title}</h3>
            <p>{post.body}</p>
          </li>
        ))}
      </ul>
    </div>
  );
};

```

---

## 2. Cross-Platform Mobile: Flutter & Dart Architecture

Flutter renders pixel-perfect UIs compiled directly to native ARM code using its Impeller/Skia rendering engine, using Dart for type-safe asynchronous execution.

### Flutter Widget Tree: `StatelessWidget` vs. `StatefulWidget`

```
┌───────────────────────────────────────────────┐
│                Widget Tree                    │
└───────────────────────┬───────────────────────┘
                        │
         ┌──────────────┴──────────────┐
         ▼                             ▼
┌──────────────────┐          ┌──────────────────┐
│ StatelessWidget  │          │ StatefulWidget   │
│ Immutable UI     │          │ Mutable State    │
│ (Text, Icon,     │          │ (TextField,      │
│  Container)      │          │  Form, Slider)   │
└──────────────────┘          └──────────────────┘

```

### Flutter Production Pattern: Clean State & Service Layer

```dart
import 'package:flutter/material.dart';

// Model
class UserProfile {
  final String id;
  final String name;
  final String email;

  const UserProfile({
    required this.id,
    required this.name,
    required this.email,
  });
}

// Widget
class UserProfileCard extends StatelessWidget {
  final UserProfile profile;
  final VoidCallback onEditPressed;

  const UserProfileCard({
    super.key,
    required this.profile,
    required this.onEditPressed,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Card(
      elevation: 2.0,
      margin: const EdgeInsets.all(12.0),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Row(
          children: [
            CircleAvatar(
              backgroundColor: theme.colorScheme.primary,
              child: Text(
                profile.name[0].toUpperCase(),
                style: const TextStyle(color: Colors.white),
              ),
            ),
            const SizedBox(width: 16.0),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    profile.name,
                    style: theme.textTheme.titleMedium,
                  ),
                  Text(
                    profile.email,
                    style: theme.textTheme.bodyMedium?.copyWith(
                      color: Colors.grey[600],
                    ),
                  ),
                ],
              ),
            ),
            IconButton(
              icon: const Icon(Icons.edit),
              onPressed: onEditPressed,
              tooltip: 'Edit Profile',
            ),
          ],
        ),
      ),
    );
  }
}

```

---

## 3. Web vs. Mobile Architecture Comparison

| Dimension | React (Web) | Flutter (Mobile / Multi-platform) |
| --- | --- | --- |
| **Language** | TypeScript / JavaScript | Dart |
| **Rendering Primitive** | Virtual DOM $\rightarrow$ HTML DOM Nodes | Direct Canvas Engine (Impeller / Skia) |
| **Styling** | CSS / Tailwind / CSS-in-JS | Encapsulated Widget parameters |
| **State Management** | Redux, Zustand, Context API | BLoC, Provider, Riverpod |
| **Target Output** | Web Browsers (SPA/SSR) | iOS, Android, Desktop, Web |

---

## 🧪 Practical Lab Exercise: React Dashboard Component (`labs/frontend/src/App.tsx`)

### Goal

Implement a responsive dashboard widget in React with TypeScript that handles real-time metric updates, loading states, and user actions.

#### Save this code to `labs/frontend/src/App.tsx`:

```tsx
import React, { useState, useEffect } from 'react';

interface Metric {
  id: string;
  label: string;
  value: string | number;
  status: 'healthy' | 'warning' | 'critical';
}

export const DashboardWidget: React.FC = () => {
  const [metrics, setMetrics] = useState<Metric[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    // Simulate initial telemetry API fetch
    const timer = setTimeout(() => {
      setMetrics([
        { id: 'm1', label: 'API Latency', value: '42ms', status: 'healthy' },
        { id: 'm2', label: 'Memory Usage', value: '78%', status: 'warning' },
        { id: 'm3', label: 'Active Sessions', value: 1420, status: 'healthy' },
        { id: 'm4', label: 'Error Rate', value: '0.02%', status: 'healthy' },
      ]);
      setLoading(false);
    }, 600);

    return () => clearTimeout(timer);
  }, []);

  const getStatusColor = (status: Metric['status']) => {
    switch (status) {
      case 'healthy': return '#10B981';
      case 'warning': return '#F59E0B';
      case 'critical': return '#EF4444';
      default: return '#6B7280';
    }
  };

  if (loading) {
    return <div style={{ padding: '20px', fontFamily: 'sans-serif' }}>Loading Telemetry Dashboard...</div>;
  }

  return (
    <div style={{
      maxWidth: '800px',
      margin: '20px auto',
      padding: '24px',
      borderRadius: '12px',
      backgroundColor: '#1E293B',
      color: '#F8FAFC',
      fontFamily: 'system-ui, sans-serif'
    }}>
      <h2 style={{ marginTop: 0, borderBottom: '1px solid #334155', pb: '12px' }}>
        System Telemetry
      </h2>
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
        gap: '16px',
        marginTop: '16px'
      }}>
        {metrics.map((m) => (
          <div key={m.id} style={{
            backgroundColor: '#0F172A',
            padding: '16px',
            borderRadius: '8px',
            borderLeft: `4px solid ${getStatusColor(m.status)}`
          }}>
            <div style={{ fontSize: '12px', color: '#94A3B8' }}>{m.label}</div>
            <div style={{ fontSize: '24px', fontWeight: 'bold', marginTop: '8px' }}>{m.value}</div>
          </div>
        ))}
      </div>
    </div>
  );
};

```