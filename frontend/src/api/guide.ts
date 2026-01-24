import client from './client';

export type GuideMode = 'guided' | 'collaborator' | 'expert';

export interface GuideOption {
  label: string;
  value: string;
}

export interface GuideState {
  step: number;
  objective?: string;
  audience?: string;
  platform?: "linkedin" | "instagram" | "facebook" | "twitter";
  tone?: string;
  topics?: string[];
  postsPerDay?: number;
  scheduleStrategy?: "distributed" | "morning_evening";
  extra_context?: string;
  conversation_summary?: string;
}

export interface GuideNextRequest {
  current_step: number;
  mode: GuideMode;
  state: GuideState;
  user_input?: string;
  user_value?: string;
  guide_session_id: string;
}

export interface GuideNextResponse {
  assistant_message: string;
  options: GuideOption[];
  next_step: number;
  state_patch: Partial<GuideState>;
  status?: 'success' | 'blocked' | 'error';
}

export const guideApi = {
  nextStep: async (request: GuideNextRequest): Promise<GuideNextResponse> => {
    console.log("➡️ [API] guide.nextStep REQUEST:", request);
    try {
      const response = await client.post('/guide/next', request);
      console.log("⬅️ [API] guide.nextStep RESPONSE:", response.data);
      return response.data;
    } catch (error) {
      console.error("❌ [API] guide.nextStep ERROR:", error);
      throw error;
    }
  }
};
