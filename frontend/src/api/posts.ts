import { apiClient } from './client';
import type { Post } from '../types';

export const postsApi = {
  update: async (id: number, data: Partial<Post>): Promise<Post> => {
    // Backend expects 'scheduled_for'. Ensure we send it.
    const payload = {
        ...data,
        // If scheduled_date is passed but not scheduled_for, map it.
        ...(data.scheduled_date && !data.scheduled_for && { scheduled_for: data.scheduled_date })
    };
    
    const response = await apiClient.put<{ data: Post }>(`/posts/${id}`, payload);
    return response.data.data;
  },

  publishNow: async (id: number): Promise<Post> => {
    const response = await apiClient.post<{ data: Post }>(`/posts/${id}/publish`);
    return response.data.data;
  }
};
