'use client';

import { useState } from 'react';
import { askQuery, QueryResponse } from '@/lib/api';
import { Send, Copy, Check, Loader2, AlertCircle } from 'lucide-react';

export default function QueryInterface() {
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<QueryResponse | null>(null);
  const [copied, setCopied] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim()) return;

    setLoading(true);
    setResult(null);

    try {
      const data = await askQuery(question);
      setResult(data);
    } catch (err: any) {
      setResult({
        structured_query: {},
        pandas_code: '',
        explanation: '',
        answer: null,
        clarification_needed: true,
        question: err.response?.data?.detail || 'Failed to process query',
      });
    } finally {
      setLoading(false);
    }
  };

  const copyCode = () => {
    if (result?.pandas_code) {
      navigator.clipboard.writeText(result.pandas_code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="space-y-6">
      {/* Query Input */}
      <div className="bg-white rounded-lg border p-6">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Ask a question about your data
            </label>
            <div className="flex gap-2">
              <input
                type="text"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="e.g., What is the average age by passenger class?"
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 placeholder-gray-400"
                disabled={loading}
              />
              <button
                type="submit"
                disabled={loading || !question.trim()}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center"
              >
                {loading ? (
                  <Loader2 className="h-5 w-5 animate-spin" />
                ) : (
                  <>
                    <Send className="h-4 w-4 mr-2" />
                    Ask
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Example Questions */}
          <div className="flex flex-wrap gap-2">
            <span className="text-sm text-gray-600">Examples:</span>
            {[
              'How many records are there?',
              'What is the average age?',
              'Count by gender',
            ].map((example) => (
              <button
                key={example}
                type="button"
                onClick={() => setQuestion(example)}
                className="text-xs px-3 py-1 bg-gray-100 text-gray-700 rounded-full hover:bg-gray-200 transition-colors"
              >
                {example}
              </button>
            ))}
          </div>
        </form>
      </div>

      {/* Results */}
      {result && (
        <div className="space-y-4">
          {/* Clarification Needed */}
          {result.clarification_needed && (
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 flex items-start">
              <AlertCircle className="h-5 w-5 text-yellow-600 mr-3 flex-shrink-0 mt-0.5" />
              <div>
                <p className="font-medium text-yellow-900">Clarification Needed</p>
                <p className="text-sm text-yellow-800 mt-1">{result.question}</p>
              </div>
            </div>
          )}

          {/* Answer */}
          {!result.clarification_needed && result.answer !== null && (
            <div className="bg-white rounded-lg border p-6">
              <h3 className="text-sm font-medium text-gray-700 mb-3">Answer</h3>
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <pre className="text-lg font-semibold text-green-900 whitespace-pre-wrap">
                  {typeof result.answer === 'object'
                    ? JSON.stringify(result.answer, null, 2)
                    : result.answer}
                </pre>
              </div>
            </div>
          )}

          {/* Explanation */}
          {!result.clarification_needed && result.explanation && (
            <div className="bg-white rounded-lg border p-6">
              <h3 className="text-sm font-medium text-gray-700 mb-3">Explanation</h3>
              <p className="text-gray-900">{result.explanation}</p>
            </div>
          )}

          {/* Pandas Code */}
          {!result.clarification_needed && result.pandas_code && (
            <div className="bg-white rounded-lg border p-6">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-sm font-medium text-gray-700">
                  Copy & Paste to Jupyter/Colab
                </h3>
                <button
                  onClick={copyCode}
                  className="flex items-center px-3 py-1.5 text-sm text-white bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors"
                >
                  {copied ? (
                    <>
                      <Check className="h-4 w-4 mr-1 text-white" />
                      Copied!
                    </>
                  ) : (
                    <>
                      <Copy className="h-4 w-4 mr-1" />
                      Copy Code
                    </>
                  )}
                </button>
              </div>
              <pre className="bg-gray-900 text-gray-100 rounded-lg p-4 overflow-x-auto text-sm font-mono">
                <code>{result.pandas_code}</code>
              </pre>
              <p className="text-xs text-gray-500 mt-2">
                💡 This code assumes your DataFrame is loaded as 'df' in your environment
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}