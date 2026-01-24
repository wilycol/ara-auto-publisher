import { apiClient } from './client';
import type { Campaign, CreateCampaignRequest } from '../types';

export const campaignsApi = {
  getAll: async (projectId: number = 1): Promise<Campaign[]> => {
    const response = await apiClient.get<Campaign[]>(`/campaigns/?project_id=${projectId}`);
    return response.data;
  },
  
  getOne: async (id: number): Promise<Campaign> => {
    const response = await apiClient.get<Campaign>(`/campaigns/${id}`);
    return response.data;
  },

  create: async (data: CreateCampaignRequest): Promise<Campaign> => {
    const response = await apiClient.post<Campaign>('/campaigns/', data);
    return response.data;
  },

  delete: async (id: number): Promise<void> => {
    await apiClient.delete(`/campaigns/${id}`);
  },

  generatePosts: async (id: number, count: number = 3, platform: string = 'linkedin'): Promise<any> => {
    const response = await apiClient.post(`/campaigns/${id}/generate`, { count, platform });
    return response.data;
  },

  update: async (id: number, data: Partial<Campaign>): Promise<Campaign> => {
    const response = await apiClient.put<Campaign>(`/campaigns/${id}`, data);
    return response.data;
  }
};
