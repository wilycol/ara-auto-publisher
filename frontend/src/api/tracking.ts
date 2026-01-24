import { apiClient } from './client';

export interface TrackingEntry {
    id: number;
    created_at: string;
    project_name: string;
    platform: string;
    type: string;
    url: string;
    status: string;
    objective: string;
    notes: string;
}

export interface TrackingReport {
    count: number;
    data: TrackingEntry[];
}

export const getTrackingReport = async (project_id?: number) => {
    const params = project_id ? { project_id } : {};
    const response = await apiClient.get<TrackingReport>('/internal/tracking', { params });
    return response.data;
};

export const downloadReport = async (format: 'json' | 'csv' | 'xlsx', project_id?: number) => {
    const params = project_id ? { format, project_id } : { format };
    const response = await apiClient.get('/internal/tracking', { 
        params,
        responseType: 'blob'
    });
    
    // Create download link
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `tracking_report.${format}`);
    document.body.appendChild(link);
    link.click();
    link.remove();
};
