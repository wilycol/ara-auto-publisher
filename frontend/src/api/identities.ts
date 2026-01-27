import { apiClient } from './client';

export interface Identity {
  id: string;
  project_id?: number;
  name: string;
  purpose?: string;
  tone?: string;
  preferred_platforms?: string | string[]; // Can be JSON string or array
  communication_style?: string;
  content_limits?: string;
  status: 'active' | 'draft' | 'archived';
  role?: string;
  created_at?: string;
}

export interface CreateIdentityRequest {
  name: string;
  purpose?: string;
  tone?: string;
  preferred_platforms?: string[];
  communication_style?: string;
  content_limits?: string;
  role?: string;
  status?: string;
}

export const identitiesApi = {
  getAll: async (projectId: number = 1): Promise<Identity[]> => {
    const response = await apiClient.get<Identity[]>(`/identities/?project_id=${projectId}`);
    return response.data;
  },

  create: async (data: CreateIdentityRequest): Promise<Identity> => {
    const response = await apiClient.post<Identity>('/identities/', data);
    return response.data;
  },

  update: async (id: string, data: Partial<CreateIdentityRequest>): Promise<Identity> => {
    const response = await apiClient.put<Identity>(`/identities/${id}`, data);
    return response.data;
  }
};
