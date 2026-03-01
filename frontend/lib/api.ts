import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface UploadResponse {
  columns: string[];
  row_count: number;
  preview: Record<string, any>[];
}

export interface QueryResponse {
  structured_query: any;
  pandas_code: string;
  explanation: string;
  answer: any;
  clarification_needed?: boolean;
  question?: string;
}

export interface ProfileResponse {
  raw_profile: any;
  ai_insights: string;
}

export const uploadCSV = async (file: File): Promise<UploadResponse> => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await api.post('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  
  return response.data;
};

export const getOverview = async (): Promise<{ insights: string }> => {
  const response = await api.get('/ai/overview-insights');
  return response.data;
};

export const askQuery = async (question: string): Promise<QueryResponse> => {
  const response = await api.post('/ai/query', { question });
  return response.data;
};

export const getProfile = async (): Promise<ProfileResponse> => {
  const response = await api.get('/ai/deep-profile');
  return response.data;
};

export const exportCSV = async (): Promise<Blob> => {
  const response = await api.get('/export/csv', {
    responseType: 'blob',
  });
  return response.data;
};