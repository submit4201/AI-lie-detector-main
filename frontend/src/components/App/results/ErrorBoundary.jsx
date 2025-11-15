import React from 'react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="bg-red-900/20 backdrop-blur-sm border border-red-500/30 rounded-lg p-4 my-4">
          <div className="text-red-400 text-center">
            <div className="text-2xl mb-2">⚠️</div>
            <div className="font-medium">{this.props.fallback || 'Something went wrong'}</div>
            <div className="text-sm text-gray-400 mt-2">
              Please try refreshing the page or contact support if the issue persists.
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
