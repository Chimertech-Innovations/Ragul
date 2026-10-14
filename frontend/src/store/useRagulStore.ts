import { create } from 'zustand';

export interface ChatMessageItem {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  tool_meta?: any;
  timestamp: string;
}

export interface FarmOverviewData {
  farm_name: string;
  location: string;
  total_cows: number;
  high_risk_mastitis: number;
  in_estrus_cows: number;
  total_daily_yield_litres: number;
  active_health_alerts: Array<{
    id: number;
    cow_id: number;
    event_type: string;
    severity: string;
    description: string;
    action: string;
    quarter?: string;
  }>;
  urgent_tasks: Array<{
    id: number;
    cow_id?: number;
    title: string;
    priority: string;
    assigned_to: string;
  }>;
}

export interface CowSummary {
  id: number;
  tag_number: string;
  name: string;
  breed: string;
  lactation_stage: string;
  daily_average_milk: number;
  health_status: string;
  mastitis_risk: string;
  affected_quarter?: string;
  in_estrus: boolean;
  days_in_milk: number;
}

interface RagulState {
  sessionId: string;
  messages: ChatMessageItem[];
  isListening: boolean;
  isSpeaking: boolean;
  isProcessing: boolean;
  vadStatus: string;
  interrupted: boolean;
  farmOverview: FarmOverviewData | null;
  cows: CowSummary[];
  selectedCow: any | null;
  
  // Actions
  setSessionId: (sessionId: string) => void;
  addMessage: (message: Omit<ChatMessageItem, 'id' | 'timestamp'>) => void;
  setListening: (listening: boolean) => void;
  setSpeaking: (speaking: boolean) => void;
  setProcessing: (processing: boolean) => void;
  setVadStatus: (status: string) => void;
  triggerInterruption: () => void;
  setFarmOverview: (data: FarmOverviewData) => void;
  setCows: (cows: CowSummary[]) => void;
  setSelectedCow: (cow: any) => void;
  clearMessages: () => void;
}

export const useRagulStore = create<RagulState>((set) => ({
  sessionId: localStorage.getItem('ragul_session_id') || `session_${Math.random().toString(36).substring(2, 11)}`,
  messages: [
    {
      id: 'welcome-1',
      role: 'assistant',
      content: 'Hello Sir! I\'m RAGUL, your personal dairy farm AI. I\'m watching over your cattle, milk yields, mastitis risks, feed rations. What do you need, Sir?',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
  ],
  isListening: false,
  isSpeaking: false,
  isProcessing: false,
  vadStatus: 'idle',
  interrupted: false,
  farmOverview: null,
  cows: [],
  selectedCow: null,

  setSessionId: (sessionId: string) => {
    localStorage.setItem('ragul_session_id', sessionId);
    set({ sessionId });
  },

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
  triggerInterruption: () => set((state) => ({ interrupted: true, isSpeaking: false })),
  setFarmOverview: (farmOverview) => set({ farmOverview }),
  setCows: (cows) => set({ cows }),
  setSelectedCow: (selectedCow) => set({ selectedCow }),
  clearMessages: () => set({ messages: [] })
}));
