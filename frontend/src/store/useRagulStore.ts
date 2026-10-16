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

export interface UserProfile {
  id: string;
  phone: string;
  full_name: string;
  role: string;
  farm_id: string;
  farm_code: string;
  farm_name: string;
  owner_name?: string;
  location?: string;
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
  currentUser: UserProfile | null;
  messages: ChatMessageItem[];
  isListening: boolean;
  isSpeaking: boolean;
  isProcessing: boolean;
  vadStatus: string;
  interrupted: boolean;
  farmOverview: FarmOverviewData | null;
  isLoginModalOpen: boolean;

  // Actions
  setSessionId: (sessionId: string) => void;
  setCurrentUser: (user: UserProfile | null) => void;
  setLoginModalOpen: (open: boolean) => void;
  addMessage: (message: Omit<ChatMessageItem, 'id' | 'timestamp'>) => void;
  setListening: (listening: boolean) => void;
  setSpeaking: (speaking: boolean) => void;
  setProcessing: (processing: boolean) => void;
  setVadStatus: (status: string) => void;
  triggerInterruption: () => void;
  setFarmOverview: (data: FarmOverviewData) => void;
  clearMessages: () => void;
}

const getInitialUser = (): UserProfile | null => {
  try {
    const raw = localStorage.getItem('ragul_user');
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
};

export const useRagulStore = create<RagulState>((set) => ({
  sessionId: localStorage.getItem('ragul_session_id') || `session_${Math.random().toString(36).substring(2, 11)}`,
  currentUser: getInitialUser(),
  isLoginModalOpen: false,
  messages: [
    {
      id: 'welcome-1',
      role: 'assistant',
      content: 'Hello Sir! I\'m RAGUL, your PashuX AI Dairy Farm Supervisor. Please log in with your phone number and password to view and discuss your live farm cameras, estrus detection, and cattle activities.',
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

  setCurrentUser: (currentUser: UserProfile | null) => {
    if (currentUser) {
      localStorage.setItem('ragul_user', JSON.stringify(currentUser));
    } else {
      localStorage.removeItem('ragul_user');
    }
    set({ currentUser });
  },

  setLoginModalOpen: (isLoginModalOpen) => set({ isLoginModalOpen }),

  addMessage: (msg) => set((state) => ({
    messages: [
      ...state.messages,
      {
        ...msg,
        id: Math.random().toString(36).substring(2, 9),
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }
    ]
  })),

  setListening: (isListening) => set({ isListening }),
  setSpeaking: (isSpeaking) => set({ isSpeaking }),
  setProcessing: (isProcessing) => set({ isProcessing }),
  setVadStatus: (vadStatus) => set({ vadStatus }),
  triggerInterruption: () => set(() => ({ interrupted: true, isSpeaking: false })),
  setFarmOverview: (farmOverview) => set({ farmOverview }),
  clearMessages: () => set({ messages: [] })
}));
