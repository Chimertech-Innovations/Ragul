import { create } from 'zustand';

export interface ProofImageItem {
  activity_id?: string;
  cattle_id?: string;
  camera_id?: string;
  time?: string;
  confidence?: string;
  description?: string;
  image_url: string;
}

export interface ChatMessageItem {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  tool_meta?: any;
  proof_images?: ProofImageItem[];
  timestamp: string;
}

export interface EstrusAlert {
  cattle_id: string;
  camera: string;
  time: string;
  confidence: string;
  description: string;
}

export interface FarmOverviewData {
  source?: string;
  farm_id?: string;
  farm_name: string;
  farm_code: string;
  owner_name: string;
  location: string;
  monitored_cattle_count: number;
  cattle_list: string[];
  total_activities_detected: number;
  active_estrus_count: number;
  active_estrus_alerts: EstrusAlert[];
  feeding_activity_count: number;
  cameras_connected: number;
  cameras: Array<{
    id: string;
    camera_name: string;
    location_description?: string;
    is_active: boolean;
  }>;
}

interface RagulState {
  sessionId: string;
  farmId: string;
  messages: ChatMessageItem[];
  isListening: boolean;
  isSpeaking: boolean;
  isProcessing: boolean;
  vadStatus: string;
  interrupted: boolean;
  farmOverview: FarmOverviewData | null;

  // Actions
  setSessionId: (sessionId: string) => void;
  setFarmId: (farmId: string) => void;
  addMessage: (message: Omit<ChatMessageItem, 'id' | 'timestamp'>) => void;
  setListening: (listening: boolean) => void;
  setSpeaking: (speaking: boolean) => void;
  setProcessing: (processing: boolean) => void;
  setVadStatus: (status: string) => void;
  triggerInterruption: () => void;
  setFarmOverview: (data: FarmOverviewData) => void;
  clearMessages: () => void;
}

export const useRagulStore = create<RagulState>((set) => ({
  sessionId: localStorage.getItem('ragul_session_id') || `session_${Math.random().toString(36).substring(2, 11)}`,
  farmId: localStorage.getItem('ragul_farm_id') || '584cab92-d75d-4aa0-824a-c07423aa6453',
  messages: [
    {
      id: 'welcome-1',
      role: 'assistant',
      content: "Hello Sir! I am **RAGUL**, your PashuX AI Dairy Farm Supervisor. How can I help you and your herd today, Sir?",
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
  ],
  isListening: false,
  isSpeaking: false,
  isProcessing: false,
  vadStatus: 'idle',
  interrupted: false,
  farmOverview: null,

  setSessionId: (sessionId: string) => {
    localStorage.setItem('ragul_session_id', sessionId);
    set({ sessionId });
  },

  setFarmId: (farmId: string) => {
    localStorage.setItem('ragul_farm_id', farmId);
    set({ farmId });
  },

  addMessage: (msg) => {
    set((state) => ({
      messages: [
        ...state.messages,
        {
          ...msg,
          id: Math.random().toString(36).substring(2, 9),
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }
      ]
    }));
  },

  setListening: (isListening) => set({ isListening }),
  setSpeaking: (isSpeaking) => set({ isSpeaking }),
  setProcessing: (isProcessing) => set({ isProcessing }),
  setVadStatus: (vadStatus) => set({ vadStatus }),
  triggerInterruption: () => set(() => ({ interrupted: true, isSpeaking: false })),
  setFarmOverview: (farmOverview) => set({ farmOverview }),
  clearMessages: () => set({ messages: [] })
}));
