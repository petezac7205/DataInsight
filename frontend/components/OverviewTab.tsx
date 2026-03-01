'use client';

import { Lightbulb, Loader2 } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

interface OverviewTabProps {
  data: { insights: string } | null;
  loading: boolean;
}

export default function OverviewTab({ data, loading }: OverviewTabProps) {
  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
      </div>
    );
  }

  if (!data) {
    return (
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <p className="text-yellow-800">No overview data available</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg border p-6">
      <div className="flex items-center mb-4">
        <Lightbulb className="h-5 w-5 text-blue-600 mr-2" />
        <h2 className="text-lg font-semibold text-gray-900">AI Insights</h2>
      </div>
      
      <div className="prose prose-slate max-w-none">
        <ReactMarkdown
          components={{
            h1: ({node, ...props}) => <h1 className="text-xl font-bold text-gray-900 mb-3" {...props} />,
            h2: ({node, ...props}) => <h2 className="text-lg font-bold text-gray-900 mb-2" {...props} />,
            h3: ({node, ...props}) => <h3 className="text-base font-bold text-gray-900 mb-2" {...props} />,
            p: ({node, ...props}) => <p className="text-gray-800 mb-3 leading-relaxed" {...props} />,
            strong: ({node, ...props}) => <strong className="font-bold text-gray-900" {...props} />,
            ul: ({node, ...props}) => <ul className="list-disc pl-5 mb-3 space-y-1" {...props} />,
            ol: ({node, ...props}) => <ol className="list-decimal pl-5 mb-3 space-y-1" {...props} />,
            li: ({node, ...props}) => <li className="text-gray-800" {...props} />,
          }}
        >
          {data.insights}
        </ReactMarkdown>
      </div>
    </div>
  );
}