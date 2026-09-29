/**
 * Chapter 02 Practical Lab: Type-Safe Async Data Fetcher & State Machine
 */

export type FetchState<T> =
  | { status: 'idle' }
  | { status: 'loading' }
  | { status: 'success'; data: T; timestamp: number }
  | { status: 'error'; error: Error };

export class AsyncDataLoader<T> {
  private state: FetchState<T> = { status: 'idle' };

  /**
   * Returns the current state of the fetcher
   */
  public getState(): FetchState<T> {
    return this.state;
  }

  /**
   * Executes an asynchronous task and manages state transitions
   */
  public async load(fetcherFn: () => Promise<T>): Promise<FetchState<T>> {
    this.state = { status: 'loading' };

    try {
      const data = await fetcherFn();
      this.state = {
        status: 'success',
        data,
        timestamp: Date.now(),
      };
    } catch (err) {
      this.state = {
        status: 'error',
        error: err instanceof Error ? err : new Error(String(err)),
      };
    }

    return this.state;
  }
}

// ==========================================
// Example Usage / Verification
// ==========================================

interface UserProfile {
  id: string;
  username: string;
  email: string;
}

async function mockApiCall(): Promise<UserProfile> {
  // Simulate network latency
  await new Promise((resolve) => setTimeout(resolve, 500));

  return {
    id: 'usr_01hq7z8',
    username: 'dev_alex',
    email: 'alex@example.com',
  };
}

async function runLab() {
  const loader = new AsyncDataLoader<UserProfile>();

  console.log('Initial state:', loader.getState());

  const resultPromise = loader.load(mockApiCall);
  console.log('State while fetching:', loader.getState());

  const finalState = await resultPromise;
  console.log('Final state after fetch:', finalState);
}

// Uncomment to test locally with Node/ts-node:
// runLab();
