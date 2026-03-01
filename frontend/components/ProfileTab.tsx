'use client';

import { Loader2, TrendingUp, AlertTriangle, Target } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

interface ProfileTabProps {
  data: any | null;
  loading: boolean;
}

export default function ProfileTab({ data, loading }: ProfileTabProps) {
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
        <p className="text-yellow-800">No profile data available</p>
      </div>
    );
  }

  const profile = data;

  return (
    <div className="space-y-6">
      {/* AI Insights */}
      <div className="bg-white rounded-lg border p-6">
        <div className="flex items-center mb-4">
          <Target className="h-5 w-5 text-blue-600 mr-2" />
          <h2 className="text-lg font-semibold text-gray-900">Key Insights</h2>
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
            {profile.ai_insights}
          </ReactMarkdown>
        </div>
      </div>

      {/* Correlations */}
      {profile.raw_profile.strong_correlations?.length > 0 && (
        <div className="bg-white rounded-lg border p-6">
          <div className="flex items-center mb-4">
            <TrendingUp className="h-5 w-5 text-green-600 mr-2" />
            <h3 className="text-lg font-semibold text-gray-900">Strong Correlations</h3>
          </div>
          <div className="space-y-2">
            {profile.raw_profile.strong_correlations.map((corr: any, idx: number) => (
              <div key={idx} className="flex items-center justify-between py-2 border-b last:border-0">
                <span className="text-sm text-gray-700">
                  {corr.feature_1} ↔ {corr.feature_2}
                </span>
                <span className="text-sm font-medium text-green-600">
                  {corr.correlation.toFixed(3)}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Outliers */}
      {profile.raw_profile.outliers && Object.keys(profile.raw_profile.outliers).length > 0 && (
        <div className="bg-white rounded-lg border p-6">
          <div className="flex items-center mb-4">
            <AlertTriangle className="h-5 w-5 text-orange-600 mr-2" />
            <h3 className="text-lg font-semibold text-gray-900">Outliers Detected</h3>
          </div>
          <div className="space-y-2">
            {Object.entries(profile.raw_profile.outliers).map(([col, data]: [string, any]) => (
              <div key={col} className="flex items-center justify-between py-2 border-b last:border-0">
                <span className="text-sm text-gray-700">{col}</span>
                <div className="text-right">
                  <span className="text-sm font-medium text-orange-600 block">
                    {typeof data === 'object' ? data.count : data} outliers
                  </span>
                  {typeof data === 'object' && data.percentage && (
                    <span className="text-xs text-gray-500">
                      {data.percentage}%
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Dominant Categories */}
      {profile.raw_profile.dominant_categories && Object.keys(profile.raw_profile.dominant_categories).length > 0 && (
        <div className="bg-white rounded-lg border p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Dominant Categories</h3>
          <div className="space-y-2">
            {Object.entries(profile.raw_profile.dominant_categories).map(([col, data]: [string, any]) => (
              <div key={col} className="flex items-center justify-between py-2 border-b last:border-0">
                <div>
                  <span className="text-sm text-gray-700 block">{col}</span>
                  {typeof data === 'object' && data.dominant_value && (
                    <span className="text-xs text-gray-500">
                      Value: {data.dominant_value}
                    </span>
                  )}
                </div>
                <span className="text-sm font-medium text-blue-600">
                  {typeof data === 'object' ? data.percentage?.toFixed(1) : (data * 100).toFixed(1)}%
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Strongest Relationship */}
      {profile.raw_profile.strongest_relationship && (
        <div className="bg-white rounded-lg border p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Strongest Relationship</h3>
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-700">
                {profile.raw_profile.strongest_relationship.feature_1} ↔{' '}
                {profile.raw_profile.strongest_relationship.feature_2}
              </span>
              <span className="text-lg font-bold text-blue-600">
                {profile.raw_profile.strongest_relationship.correlation.toFixed(3)}
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}