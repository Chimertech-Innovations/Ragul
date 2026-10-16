/**
 * Native Audio Streamer, Clap Detector & Jarvis AI Voice Controller
 * Features:
 * - Total Speaker Echo Isolation (aborts recognition during speech playback to prevent self-triggering)
 * - Clap / Sharp Sound Wake-Up Detector (automatically turns on mic and wakes Ragul)
 * - Male English TTS Voice synthesis
 * - Native SpeechRecognition for natural voice dialogue
 */

export class AudioController {
  private audioContext: AudioContext | null = null;
  private mediaStream: MediaStream | null = null;
  private processorNode: ScriptProcessorNode | null = null;
  private analyserNode: AnalyserNode | null = null;
  private socket: WebSocket | null = null;
  private recognition: any = null;
  private onInterruptionCallback: (() => void) | null = null;
  private onTranscriptCallback: ((text: string, lang: string) => void) | null = null;
  private onAssistantResponseCallback: ((text: string, toolMeta: any) => void) | null = null;
  private onClapWakeCallback: (() => void) | null = null;
  private onSilenceEndCallback: (() => void) | null = null;
  private onSpeechEndCallback: (() => void) | null = null;
  private onNoiseAlertCallback: ((msg: string) => void) | null = null;
  
  public isSynthesizing = false;
  public isListening = false;
  private speechStartTime = 0;
  private lastClapTime = 0;
  private lastNoiseAlertTime = 0;
  private highNoiseCounter = 0;
  private lastSentTranscript = '';
  private lastTranscriptTime = 0;
  private accumulatedSpeech = '';
  private speechDebounceTimer: any = null;


  private cachedVoices: SpeechSynthesisVoice[] = [];

  constructor() {
    this.initSpeechRecognition();
    this.initVoices();
  }

  private initVoices() {
    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      const load = () => {
        const v = window.speechSynthesis.getVoices();
        if (v && v.length > 0) {
          this.cachedVoices = v;
          console.log('[AudioController] Pre-cached', v.length, 'system voices.');
        }
      };
      load();
      window.speechSynthesis.onvoiceschanged = load;
    }
  }

  public getStrictMaleVoice(): SpeechSynthesisVoice | null {
    if (typeof window === 'undefined' || !('speechSynthesis' in window)) return null;

    let voices = this.cachedVoices;
    if (!voices || voices.length === 0) {
      voices = window.speechSynthesis.getVoices() || [];
      if (voices.length > 0) {
        this.cachedVoices = voices;
      }
    }

    if (voices.length === 0) return null;

    const femaleBlacklist = [
      'zira', 'female', 'woman', 'susan', 'eva', 'jenny', 'aria', 'samantha',
      'victoria', 'karen', 'moira', 'veena', 'heera', 'hazel', 'catherine', 'linda', 'lucy',
      'neerja', 'anamika', 'swara', 'priya', 'shruti', 'sunita', 'radha', 'alva', 'kendra',
      'google us english', // In Chrome, 'Google US English' is female
      'google uk english female',
      'en-in-standard-a', 'en-in-standard-c', 'en-in-standard-d', 'en-in-standard-e',
      'en-us-standard-a', 'en-us-standard-c', 'en-us-standard-e', 'en-us-standard-f', 'en-us-standard-g', 'en-us-standard-h',
      'microsoft zira', 'microsoft susan', 'microsoft hazel', 'microsoft heera', 'microsoft veena', 'microsoft neerja', 'microsoft swara'
    ];

    const isBlacklisted = (name: string) => {
      const lower = name.toLowerCase();
      return femaleBlacklist.some(f => lower.includes(f));
    };

    // Priority 1: High quality explicit male voices (Microsoft David, Microsoft Mark, Google UK Male, etc.)
    const maleExplicitNames = [
      'david', 'mark', 'george', 'prabhat', 'ravi', 'hemant', 'guy', 'male',
      'uk english male', 'standard-b', 'standard-d', 'standard-j',
      'wavenet-b', 'wavenet-d', 'natural - english (india)', 'natural - english (united states)'
    ];

    let maleVoice = voices.find(v => {
      const name = v.name.toLowerCase();
      if (isBlacklisted(name)) return false;
      return maleExplicitNames.some(m => name.includes(m));
    });

    // Priority 2: Any English voice not on female blacklist
    if (!maleVoice) {
      maleVoice = voices.find(v => {
        const name = v.name.toLowerCase();
        return v.lang.toLowerCase().startsWith('en') && !isBlacklisted(name);
      });
    }

    // Priority 3: Any voice not in female blacklist
    if (!maleVoice) {
      maleVoice = voices.find(v => !isBlacklisted(v.name));
    }

    return maleVoice || null;
  }

  private normalizeDairyPhonetics(text: string): string {
    let cleaned = text;
    // Mastitis phonetic corrections
    cleaned = cleaned.replace(/\b(mercedes|masturitis|mass\s*status|masstatis|mastites|mustitis|masteritis|master\s*status|match\s*today)\b/gi, 'mastitis');
    // Farm phonetic corrections
    cleaned = cleaned.replace(/\b(in the form|the form|in form)\b/gi, 'in the farm');
    cleaned = cleaned.replace(/\bform\b/gi, 'farm');
    // Cattle phonetic corrections
    cleaned = cleaned.replace(/\b(capital|theatre|kettle|cattles)\b/gi, 'cattle');
    // Ragul name corrections
    cleaned = cleaned.replace(/\b(rahul|ravel|raghav|raghul)\b/gi, 'ragul');
    // Estrus & Heat corrections
    cleaned = cleaned.replace(/\b(extra|is\s*trust|s\s*trust)\b/gi, 'estrus');
    return cleaned;
  }

  private initSpeechRecognition() {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (SpeechRecognition) {
      try {
        this.recognition = new SpeechRecognition();
        this.recognition.continuous = true;
        this.recognition.interimResults = false;
        // en-IN accurately recognizes Indian English pronunciations
        this.recognition.lang = 'en-IN';

        this.recognition.onresult = (event: any) => {
          // STRICT ECHO ISOLATION: Discard everything if speaker is talking or just finished
          if (this.isSynthesizing) {
            console.log('[AudioController] Discarded speaker audio loop from microphone');
            return;
          }

          const lastResultIndex = event.results.length - 1;
          const rawTranscript = event.results[lastResultIndex][0].transcript.trim();
          const transcript = this.normalizeDairyPhonetics(rawTranscript);

          const GHOST_HALLUCINATIONS = [
            "i don't know how to do it",
            "thank you for watching",
            "subtitles by",
            "you",
            "thank you.",
            "i don't know",
            "hide over",
            "hide over.",
            "hide",
            "over",
            "hide for a bit",
            "i'm going to hide for a bit",
            "a ragul hot air plant histidine",
            "subscribe",
            "please subscribe",
            "translated by",
            "amara.org",
            "english subtitles",
            "the end",
            "bye bye",
            "watching video"
          ];

          const lower = transcript.toLowerCase();
          if (GHOST_HALLUCINATIONS.some(g => lower === g || lower.includes(g))) {
            console.log('[AudioController] Filtered phantom background noise:', transcript);
            return;
          }

          // Filter out isolated single filler sounds/noise
          const NOISE_FILLERS = new Set(["um", "uh", "ah", "eh", "er", "mm", "hmm", "shh"]);
          if (NOISE_FILLERS.has(lower) || transcript.length < 2) {
            console.log('[AudioController] Discarded ambient filler noise:', transcript);
            return;
          }

          // Continuous Speech Accumulator: append consecutive speech turns until user takes a full breath/pause
          if (!this.accumulatedSpeech) {
            this.accumulatedSpeech = transcript;
          } else if (!this.accumulatedSpeech.toLowerCase().includes(transcript.toLowerCase())) {
            this.accumulatedSpeech += ' ' + transcript;
          }

          console.log('[AudioController] Accumulating speech:', this.accumulatedSpeech);

          // Clear previous timer and set natural pause silence debounce (1.7s)
          if (this.speechDebounceTimer) {
            clearTimeout(this.speechDebounceTimer);
          }

          // Wait 1.7s of natural pause silence before finalizing and dispatching
          this.speechDebounceTimer = setTimeout(() => {
            const finalQuery = this.accumulatedSpeech.trim();
            this.accumulatedSpeech = '';
            
            if (finalQuery && finalQuery.length > 1) {
              const now = Date.now();
              // Prevent firing if this exact query or a subset was dispatched in the last 2.5s
              if (
                this.lastSentTranscript &&
                (this.lastSentTranscript === finalQuery || this.lastSentTranscript.includes(finalQuery)) &&
                now - this.lastTranscriptTime < 2500
              ) {
                console.log('[AudioController] Suppressing duplicate speech dispatch:', finalQuery);
                return;
              }

              this.lastSentTranscript = finalQuery;
              this.lastTranscriptTime = now;
              console.log('[AudioController] Speech Silence Trigger (1.7s). Dispatching Query:', finalQuery);
              
              if (this.onSilenceEndCallback) {
                this.onSilenceEndCallback();
              }
              if (this.onTranscriptCallback) {
                this.onTranscriptCallback(finalQuery, 'en');
              }
            }
          }, 1700);
        };


        this.recognition.onerror = (e: any) => {
          if (e.error !== 'no-speech' && e.error !== 'aborted') {
            console.warn('[AudioController] Speech recognition notice:', e.error);
          }
        };

        this.recognition.onend = () => {
          // Restart recognition if listening is active and assistant is NOT speaking
          if (this.isListening && !this.isSynthesizing) {
            setTimeout(() => {
              if (this.isListening && !this.isSynthesizing) {
                try {
                  this.recognition.start();
                } catch (e) {}
              }
            }, 100);
          }
        };
      } catch (err) {
        console.warn('SpeechRecognition initialization notice:', err);
      }
    }
  }

  public setCallbacks(callbacks: {
    onInterruption: () => void;
    onTranscript: (text: string, lang: string) => void;
    onAssistantResponse: (text: string, toolMeta: any) => void;
    onClapWake?: () => void;
    onSilenceEnd?: () => void;
    onSpeechEnd?: () => void;
    onNoiseAlert?: (msg: string) => void;
  }) {
    this.onInterruptionCallback = callbacks.onInterruption;
    this.onTranscriptCallback = callbacks.onTranscript;
    this.onAssistantResponseCallback = callbacks.onAssistantResponse;
    this.onClapWakeCallback = callbacks.onClapWake || null;
    this.onSilenceEndCallback = callbacks.onSilenceEnd || null;
    this.onSpeechEndCallback = callbacks.onSpeechEnd || null;
    this.onNoiseAlertCallback = callbacks.onNoiseAlert || null;
  }

  public async startStreaming(sessionId?: string): Promise<void> {
    try {
      this.isListening = true;

      // Reuse existing active audio stream & socket to prevent duplicate connections
      if (this.socket && this.socket.readyState === WebSocket.OPEN && this.mediaStream) {
        if (this.audioContext && this.audioContext.state === 'suspended') {
          await this.audioContext.resume();
        }
        if (this.recognition && !this.isSynthesizing) {
          try {
            this.recognition.start();
          } catch (e) {}
        }
        return;
      }

      this.mediaStream = await navigator.mediaDevices.getUserMedia({
        audio: {
          channelCount: 1,
          sampleRate: 16000,
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true
        }
      });

      this.audioContext = new (window.AudioContext || (window as any).webkitAudioContext)({
        sampleRate: 16000
      });

      const source = this.audioContext.createMediaStreamSource(this.mediaStream);
      this.processorNode = this.audioContext.createScriptProcessor(4096, 1, 1);
      
      // Analyser for Clap / Sharp Transient Sound Detection & Noise Floor
      this.analyserNode = this.audioContext.createAnalyser();
      this.analyserNode.fftSize = 512;

      // Close previous stale socket if any
      if (this.socket) {
        try { this.socket.close(); } catch (e) {}
      }

      // Connect WebSocket with unified session_id
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const host = window.location.host;
      const queryParam = sessionId ? `?session_id=${encodeURIComponent(sessionId)}` : '';
      const wsUrl = `${protocol}//${host}/ws/audio${queryParam}`;

      this.socket = new WebSocket(wsUrl);
      this.socket.binaryType = 'arraybuffer';

      this.socket.onopen = () => {
        console.log('[AudioController] WebSocket connected to /ws/audio with session:', sessionId);
      };

      this.socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          if (data.type === 'interrupt') {
            // Guard: Only allow intentional barge-in after initial speech period (> 2000ms)
            // to completely prevent speaker echo from falsely aborting the assistant's introduction
            if (this.isSynthesizing && (Date.now() - this.speechStartTime > 2000)) {
              console.log('[AudioController] Valid User Barge-in! Halting AI speech.');
              this.stopSpeaking();
              if (this.onInterruptionCallback) {
                this.onInterruptionCallback();
              }
            } else {
              console.log('[AudioController] Filtered speaker feedback interrupt echo');
            }
          } else if (data.type === 'user_transcript') {
            // STRICT SINGLE SOURCE OF TRUTH: Only use backend WS transcript if browser SpeechRecognition is not supported
            if (!this.recognition) {
              const text = (data.text || '').trim();
              const now = Date.now();
              if (text && (text.toLowerCase() !== this.lastSentTranscript.toLowerCase() || now - this.lastTranscriptTime > 2500)) {
                this.lastSentTranscript = text;
                this.lastTranscriptTime = now;
                console.log('[AudioController] High-Confidence Backend Speech:', text);
                if (this.onTranscriptCallback) {
                  this.onTranscriptCallback(text, data.language || 'en');
                }
              }
            }
          }


        } catch (e) {
          console.error('[AudioController] Error parsing WS message:', e);
        }
      };

      this.processorNode.onaudioprocess = (e) => {
        // Prevent audio loopback into local speakers
        const outputData = e.outputBuffer.getChannelData(0);
        outputData.fill(0);

        const inputData = e.inputBuffer.getChannelData(0);

        // Clap detection
        let maxVal = 0;
        let sumSq = 0;
        for (let i = 0; i < inputData.length; i++) {
          const abs = Math.abs(inputData[i]);
          if (abs > maxVal) maxVal = abs;
          sumSq += inputData[i] * inputData[i];
        }
        const rms = Math.sqrt(sumSq / inputData.length);

        // Persistent High Ambient Noise Detector (calibrated for high noise)
        if (rms > 0.45 && !this.isSynthesizing) {
          this.highNoiseCounter++;
          const now = Date.now();
          if (this.highNoiseCounter > 30 && now - this.lastNoiseAlertTime > 15000) {
            this.lastNoiseAlertTime = now;
            this.highNoiseCounter = 0;
            console.warn('[AudioController] High ambient noise detected');
            if (this.onNoiseAlertCallback) {
              this.onNoiseAlertCallback('High background noise detected. Please speak closer to the microphone or speak louder.');
            }
          }
        } else {
          this.highNoiseCounter = Math.max(0, this.highNoiseCounter - 1);
        }

        if (maxVal > 0.90 && (maxVal / (rms + 0.001) > 3.5)) {
          const now = Date.now();
          if (now - this.lastClapTime > 2000) {
            this.lastClapTime = now;
            console.log('[AudioController] Clap detected!');
            if (this.onClapWakeCallback) {
              this.onClapWakeCallback();
            }
          }
        }

        // STRICT ECHO PREVENTION: Do NOT stream microphone audio to VAD while assistant is speaking!
        // This prevents the assistant's own speaker output from triggering false barge-in interruptions.
        if (this.isSynthesizing) return;

        if (!this.socket || this.socket.readyState !== WebSocket.OPEN) return;

        const pcm16 = new Int16Array(inputData.length);
        for (let i = 0; i < inputData.length; i++) {
          const s = Math.max(-1, Math.min(1, inputData[i]));
          pcm16[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
        }

        this.socket.send(pcm16.buffer);
      };

      source.connect(this.analyserNode);
      source.connect(this.processorNode);
      this.processorNode.connect(this.audioContext.destination);

      // Ensure AudioContext is active
      if (this.audioContext.state === 'suspended') {
        await this.audioContext.resume();
      }

      // Start client speech recognition for fast voice capture
      if (this.recognition && !this.isSynthesizing) {
        try {
          this.recognition.start();
        } catch (e) {}
      }

    } catch (err) {
      this.isListening = false;
      console.error('[AudioController] Failed to access microphone:', err);
      throw err;
    }
  }

  public stopStreaming(): void {
    this.isListening = false;

    if (this.recognition) {
      try {
        this.recognition.abort();
      } catch (e) {}
    }

    if (this.processorNode) {
      try {
        this.processorNode.disconnect();
      } catch (e) {}
      this.processorNode = null;
    }

    if (this.analyserNode) {
      try {
        this.analyserNode.disconnect();
      } catch (e) {}
      this.analyserNode = null;
    }

    if (this.mediaStream) {
      try {
        this.mediaStream.getTracks().forEach((t) => t.stop());
      } catch (e) {}
      this.mediaStream = null;
    }

    if (this.audioContext) {
      try {
        this.audioContext.close();
      } catch (e) {}
      this.audioContext = null;
    }

    if (this.socket) {
      try {
        if (this.socket.readyState === WebSocket.OPEN) {
          this.socket.close(1000, 'User stopped streaming');
        }
      } catch (e) {}
      this.socket = null;
    }
  }

  public stopSpeaking(): void {
    if (window.speechSynthesis) {
      window.speechSynthesis.cancel();
    }
    this.isSynthesizing = false;
  }

  public speakText(text: string, lang = 'en-US'): void {
    if (typeof window === 'undefined' || !window.speechSynthesis) return;

    this.stopSpeaking();
    this.isSynthesizing = true;

    // Reset backend VAD audio buffer
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      try {
        this.socket.send(JSON.stringify({ type: 'reset_vad' }));
      } catch (e) {}
    }

    // Abort speech recognition so it cannot hear the speaker output
    if (this.recognition) {
      try {
        this.recognition.abort();
      } catch (e) {}
    }

    // Clean text: strip markdown asterisks and bullet symbols
    const cleanText = text
      .replace(/\*\*/g, '')
      .replace(/\*/g, '')
      .replace(/#/g, '')
      .replace(/\[.*?\]\(.*?\)/g, '')
      .trim();

    const doSpeak = () => {
      this.speechStartTime = Date.now();
      const utterance = new SpeechSynthesisUtterance(cleanText);
      utterance.lang = lang;

      const maleVoice = this.getStrictMaleVoice();
      if (maleVoice) {
        utterance.voice = maleVoice;
        console.log('[AudioController] Active Strict Male Voice:', maleVoice.name);
      } else {
        console.warn('[AudioController] No explicit male profile found yet; using deep masculine pitch lock.');
      }
      
      // Strict masculine pitch & high volume calibration
      utterance.volume = 1.0; // Loud and clear audio output
      utterance.pitch = 0.72; // Deep resonant male pitch
      utterance.rate = 1.0;

      utterance.onend = () => {
        // Safety grace period to ensure speaker echo is completely dissipated
        setTimeout(() => {
          this.isSynthesizing = false;
          if (this.onSpeechEndCallback) {
            this.onSpeechEndCallback();
          }
          if (this.isListening && this.recognition) {
            try {
              this.recognition.start();
            } catch (e) {}
          }
        }, 400);
      };

      utterance.onerror = () => {
        setTimeout(() => {
          this.isSynthesizing = false;
          if (this.onSpeechEndCallback) {
            this.onSpeechEndCallback();
          }
          if (this.isListening && this.recognition) {
            try {
              this.recognition.start();
            } catch (e) {}
          }
        }, 400);
      };

      window.speechSynthesis.speak(utterance);
    };

    // If voices are not yet cached, ensure voices are loaded first
    if (this.cachedVoices.length === 0 && window.speechSynthesis.getVoices().length === 0) {
      window.speechSynthesis.onvoiceschanged = () => {
        this.cachedVoices = window.speechSynthesis.getVoices();
        doSpeak();
      };
      // Fallback timeout in case onvoiceschanged does not fire
      setTimeout(() => {
        if (this.isSynthesizing) {
          doSpeak();
        }
      }, 150);
    } else {
      doSpeak();
    }
  }
}

export const audioController = new AudioController();

