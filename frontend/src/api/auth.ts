import client from './client';

export interface ConnectedAccount {
    id: number;
    provider: string;
    provider_name: string | null;
    active: boolean;
    created_at: string;
}

export const authApi = {
    // List all connected accounts
    getAccounts: async (): Promise<ConnectedAccount[]> => {
        const response = await client.get<{ data: ConnectedAccount[] }>('/auth/accounts');
        return response.data.data;
    },

    // Disconnect an account
    disconnectAccount: async (id: number): Promise<boolean> => {
        const response = await client.delete<{ data: boolean }>(`/auth/accounts/${id}`);
        return response.data.data;
    },

    // Get LinkedIn Login URL
    getLinkedInAuthUrl: async (projectId: number = 1): Promise<string> => {
        const response = await client.get<{ url: string }>('/auth/linkedin/login', {
            params: { project_id: projectId }
        });
        return response.data.url;
    }
};
