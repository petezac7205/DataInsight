'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Database, FileText, Activity } from 'lucide-react';
import QueryInterface from '@/components/QueryInterface';
import OverviewTab from '@/components/OverviewTab';
import ProfileTab from '@/components/ProfileTab';
import { getOverview, getProfile } from '@/lib/api';

export default function AnalysisPage() {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<'query' | 'overview' | 'profile'>('overview');
  const [datasetInfo, setDatasetInfo] = useState<any>(null);
  
  // Cache the data at parent level
  const [overviewData, setOverviewData] = useState<any>(null);
  const [profileData, setProfileData] = useState<any>(null);
  const [loadingOverview, setLoadingOverview] = useState(false);
  const [loadingProfile, setLoadingProfile] = useState(false);

  useEffect(() => {
    const info = sessionStorage.getItem('datasetInfo');
    if (!info) {
      router.push('/');
      return;
    }
    setDatasetInfo(JSON.parse(info));
  }, [router]);

  // Fetch overview data when tab is first opened
  useEffect(() => {
    if (activeTab === 'overview' && !overviewData && !loadingOverview) {
      setLoadingOverview(true);
      getOverview()
        .then(data => setOverviewData(data))
        .catch(err => console.error('Overview error:', err))
        .finally(() => setLoadingOverview(false));
    }
  }, [activeTab, overviewData, loadingOverview]);

  // Fetch profile data when tab is first opened
  useEffect(() => {
    if (activeTab === 'profile' && !profileData && !loadingProfile) {
      setLoadingProfile(true);
      getProfile()
        .then(data => setProfileData(data))
        .catch(err => console.error('Profile error:', err))
        .finally(() => setLoadingProfile(false));
    }
  }, [activeTab, profileData, loadingProfile]);

  if (!datasetInfo) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading dataset...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                {datasetInfo.filename}
              </h1>
              <p className="text-sm text-gray-600">
                {datasetInfo.rowCount.toLocaleString()} rows × {datasetInfo.columns.length} columns
              </p>
            </div>
            <button
              onClick={() => router.push('/')}
              className="px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
            >
              Upload New File
            </button>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex space-x-8">
            <button
              onClick={() => setActiveTab('overview')}
              className={`py-4 px-2 border-b-2 font-medium text-sm transition-colors flex items-center ${
                activeTab === 'overview'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              }`}
            >
              <FileText className="h-4 w-4 mr-2" />
              Overview
            </button>
            <button
              onClick={() => setActiveTab('query')}
              className={`py-4 px-2 border-b-2 font-medium text-sm transition-colors flex items-center ${
                activeTab === 'query'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              }`}
            >
              <Database className="h-4 w-4 mr-2" />
              Query
            </button>
            <button
              onClick={() => setActiveTab('profile')}
              className={`py-4 px-2 border-b-2 font-medium text-sm transition-colors flex items-center ${
                activeTab === 'profile'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              }`}
            >
              <Activity className="h-4 w-4 mr-2" />
              Profile
            </button>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 py-8">
        {activeTab === 'overview' && (
          <OverviewTab data={overviewData} loading={loadingOverview} />
        )}
        {activeTab === 'query' && <QueryInterface />}
        {activeTab === 'profile' && (
          <ProfileTab data={profileData} loading={loadingProfile} />
        )}
      </div>
    </div>
  );
}