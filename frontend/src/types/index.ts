export interface Campaign {
  id: number;
  name: string;
  project_id: number;
  identity_id?: string;
  objective?: string;
  tone?: string;
  status: 'DRAFT' | 'ACTIVE' | 'PAUSED' | 'COMPLETED';
  start_date: string;
  end_date?: string;
  created_at: string;
  posts?: Post[];
}

export interface Post {
  id: number;
  campaign_id: number;
  title?: string;
  content_text?: string;
  content: string; // Legacy support
  scheduled_for?: string; // Backend field
  scheduled_date?: string; // Legacy field
  status: 'DRAFT' | 'APPROVED' | 'SCHEDULED' | 'PUBLISHED' | 'FAILED' | 'PENDING' | 'GENERATED' | 'READY_MANUAL' | 'PUBLISHED_AUTO' | 'FAILED_AUTO_MANUAL_AVAILABLE';
  platform: 'linkedin';
}

export interface CreateCampaignRequest {
  project_id: number;
  name: string;
  objective: string;
  tone: string;
  identity_id?: string;
  start_date: string;
  end_date?: string;
  status?: string;
}

export interface AutomationStatus {
  id: number;
  project_id: number;
  status: 'active' | 'paused';
  autonomy_status: 'autonomous_active' | 'autonomous_paused' | 'autonomous_blocked';
  is_manually_overridden: boolean;
  override_reason?: string;
  last_error?: string;
  error_at?: string;
}
