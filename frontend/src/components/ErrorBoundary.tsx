import { Component } from "react";
import type { ErrorInfo, ReactNode } from "react";

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("ErrorBoundary caught an error:", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="flex h-screen items-center justify-center bg-[#050505] text-red-500">
          <div className="text-center font-mono">
            <h1 className="text-2xl font-bold mb-4">ERROR</h1>
            <p className="text-sm mb-2">{this.state.error?.message}</p>
            <pre className="text-xs bg-black/40 p-4 rounded border border-red-500 overflow-auto max-w-2xl">
              {this.state.error?.stack}
            </pre>
            <button
              onClick={() => window.location.reload()}
              className="mt-4 px-4 py-2 bg-red-500 text-black font-bold rounded"
            >
              RELOAD
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
