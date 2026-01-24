import client from './client';

export interface DashboardStats {
    global_autonomy_enabled: boolean;
    campaigns: {
        total: number;
        active_status: number;
        paused_status: number;
    };
    autonomy_states: {
        active: number;
        paused: number;
        manually_overridden: number;
        errors: number;
    };
    last_human_action?: {
        decision: string;
        reason: string;
        created_at: string;
    } | null;
}

export interface Recommendation {
    id: number;
    automation_id: number;
    automation_name: string;
    type: string;
    suggested_value: any;
    reasoning: string;
    status: string;
    created_at: string;
}

export const controlApi = {
    getDashboardStats: async (): Promise<DashboardStats> => {
        const response = await client.get('/internal/control/dashboard/stats');
        return response.data;
    },
    
    getRecommendations: async (status: string = 'PENDING'): Promise<Recommendation[]> => {
        const response = await client.get('/internal/control/recommendations', { params: { status } });
        return response.data;
    },
    
    actOnRecommendation: async (id: number, action: 'APPROVE' | 'REJECT' | 'ARCHIVE'): Promise<any> => {
        const response = await client.post(`/internal/control/recommendation/${id}/${action}`);
        return response.data;
    },
    
    emergencyStop: async (): Promise<any> => {
        const response = await client.post('/internal/control/emergency-stop');
        return response.data;
    },
    
    // Per-campaign override
    manualOverride: async (id: number, action: string, reason: string): Promise<any> => {
        const response = await client.post(`/internal/control/campaign/${id}/override/${action}`, { reason });
        return response.data;
    },

    setupAutomation: async (payload: {
        project_id: number;
        name: string;
        status: string;
        autonomy_status: string;
        style_locked: boolean;
    }): Promise<any> => {
        const response = await client.post('/internal/control/setup', payload);
        return response.data;
    }
};
