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
  private onVadStatusCallback: ((status: string) => void) | null = null;
  
  public isSynthesizing = false;
  public isListening = false;
  public isSpeakingDetected = false;
  private speechStartTime = 0;
  private lastClapTime = 0;
  private lastNoiseAlertTime = 0;
  private highNoiseCounter = 0;
  private voiceInterruptionFrames = 0;
  private lastSentTranscript = '';
  private lastTranscriptTime = 0;
  private accumulatedSpeech = '';
  private speechDebounceTimer: any = null;
  private activeUtterance: SpeechSynthesisUtterance | null = null;
  private speechKeepAliveTimer: any = null;

  public cleanTextForSpeech(text: string): string {
    if (!text) return '';
    return text
      // 1. Strip ALL emojis & pictorial symbols (Unicode Extended Pictographic, emoticons, symbols)
      .replace(/[\p{Extended_Pictographic}\u{1F300}-\u{1F9FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}\u{1F600}-\u{1F64F}\u{1F680}-\u{1F6FF}]/gu, '')
      // 2. Remove markdown asterisks, hashes, backticks
      .replace(/\*\*/g, '')
      .replace(/\*/g, '')
      .replace(/#{1,6}\s*/g, '')
      .replace(/`{1,3}[\s\S]*?`{1,3}/g, '')
      // 3. Remove bullet characters & arrows
      .replace(/[•▸►▪■]/g, '')
      .replace(/[-_]{3,}/g, '')
      // 4. Clean Markdown links [Title](url) -> Title, and strip raw URLs
      .replace(/\[(.*?)\]\([^)]*\)/g, '$1')
      .replace(/\(https?:\/\/[^)]*\)/gi, '')
      .replace(/https?:\/\/\S+/gi, '')
      // 5. Remove camera snapshot notices
      .replace(/📸\s*\*.*?\*/gi, '')
      // 6. Clean spacing and line breaks
      .replace(/[ \t]+/g, ' ')
      .replace(/\n+/g, '. ')
      .trim();
  }


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
    // Common acoustic mishearings
    cleaned = cleaned.replace(/\bmeaning\s*[yb]\b/gi, 'meaning of');
    // Mastitis phonetic corrections ("my statis", "my status", "mass titis", "mustard is", "master this")
    cleaned = cleaned.replace(/\b(my\s*statis|my\s*status|my\s*static|my\s*titis|mystatis|mystatus|mystatic|mass\s*status|mass\s*titis|masstatis|mastites|mustitis|must\s*titis|masteritis|master\s*status|master\s*this|mustard\s*is|mercedes|masturitis|masturitise|match\s*today|masturi\w*|masteri\w*|mastiti\w*|mastur\w*)\b/gi, 'mastitis');
    // Quadmastest & CMT screening device corrections
    cleaned = cleaned.replace(/\b(quad\s*master|quad\s*mast\s*test|quad\s*my\s*test|god\s*master|card\s*master|court\s*master|quad\s*test)\b/gi, 'quadmastest');
    // Farm phonetic corrections
    cleaned = cleaned.replace(/\b(in the form|the form|in form)\b/gi, 'in the farm');
    cleaned = cleaned.replace(/\bform\b/gi, 'farm');
    // Cattle phonetic corrections
    cleaned = cleaned.replace(/\b(capital|theatre|kettle|cattles)\b/gi, 'cattle');
    // Ragul name corrections
    cleaned = cleaned.replace(/\b(rahul|ravel|raghav|raghul)\b/gi, 'ragul');
    // Estrus & Heat corrections
    cleaned = cleaned.replace(/\b(extra|is\s*trust|s\s*trust|east\s*rus|es\s*truss|is\s*trust|s\s*trus|s\s*stress)\b/gi, 'estrus');
    // Silage & Fodder corrections
    cleaned = cleaned.replace(/\b(sai\s*lage|cy\s*lage|sil\s*age)\b/gi, 'silage');
    cleaned = cleaned.replace(/\b(father\s*grass|father\s*crop|further\s*grass)\b/gi, 'fodder grass');
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
          const lastResultIndex = event.results.length - 1;
          const rawTranscript = event.results[lastResultIndex][0].transcript.trim();
          if (!rawTranscript) return;

          // INSTANT BARGE-IN INTERRUPTION: If user speaks during AI playback, immediately halt Ragul's voice!
          if (this.isSynthesizing) {
            console.log('[AudioController] User voice query detected during AI speech! Cutting off AI immediately:', rawTranscript);
            this.stopSpeaking();
            if (this.onInterruptionCallback) {
              this.onInterruptionCallback();
            }
            this.accumulatedSpeech = '';
          }

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

          // Filter out isolated single filler sounds/noise and ambient mic pops
          const NOISE_FILLERS = new Set(["um", "uh", "ah", "eh", "er", "mm", "hmm", "shh", "huh", "oh", "ha"]);
          const cleanChars = transcript.replace(/[^a-zA-Z0-9\u0B80-\u0BFF\u0900-\u097F]/g, '');
          if (NOISE_FILLERS.has(lower) || cleanChars.length < 3) {
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
              const cleanFinal = finalQuery.toLowerCase().replace(/[^a-z0-9]/g, '');
              const cleanLast = this.lastSentTranscript.toLowerCase().replace(/[^a-z0-9]/g, '');
              const isDuplicate = cleanLast && (
                cleanLast === cleanFinal ||
                (cleanLast.length > 5 && cleanFinal.length > 5 && (cleanLast.includes(cleanFinal) || cleanFinal.includes(cleanLast)))
              );

              // Prevent firing if this exact query or an overlapping subset was dispatched in the last 5.5s
              if (isDuplicate && (now - this.lastTranscriptTime < 5500)) {
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
          // Continuous Duplex Speech: Keep recognition alive whenever listening is active (even during synthesis for instant barge-in!)
          if (this.isListening) {
            setTimeout(() => {
              if (this.isListening) {
                try {
                  this.recognition.start();
                } catch (e) {}
              }
            }, 120);
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
    onVadStatus?: (status: string) => void;
  }) {
    this.onInterruptionCallback = callbacks.onInterruption;
    this.onTranscriptCallback = callbacks.onTranscript;
    this.onAssistantResponseCallback = callbacks.onAssistantResponse;
    this.onClapWakeCallback = callbacks.onClapWake || null;
    this.onSilenceEndCallback = callbacks.onSilenceEnd || null;
    this.onSpeechEndCallback = callbacks.onSpeechEnd || null;
    this.onNoiseAlertCallback = callbacks.onNoiseAlert || null;
    this.onVadStatusCallback = callbacks.onVadStatus || null;
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

      this.socket.onerror = (e) => {
        // Quietly absorb socket errors
        console.warn('[AudioController] WebSocket notice:', e);
      };

      this.socket.onclose = () => {
        this.isSpeakingDetected = false;
        if (this.onVadStatusCallback) {
          this.onVadStatusCallback('idle');
        }
      };

      this.socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          if (data.type === 'vad_status') {
            this.isSpeakingDetected = (data.status === 'speech');
            if (this.onVadStatusCallback) {
              this.onVadStatusCallback(data.status);
            }
          } else if (data.type === 'interrupt') {
            // Guard: Allow intentional barge-in after 300ms of speech
            if (this.isSynthesizing && (Date.now() - this.speechStartTime > 300)) {
              console.log('[AudioController] Valid User Barge-in from backend! Halting AI speech.');
              this.stopSpeaking();
              if (this.onInterruptionCallback) {
                this.onInterruptionCallback();
              }
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

        // Acoustic Voice Activity Barge-In:
        // Reject ambient noise and room echo; require real vocal presence (rms > 0.14 for 3 consecutive frames)
        if (this.isSynthesizing) {
          const now = Date.now();
          if (now - this.speechStartTime > 400 && rms > 0.14) {
            this.voiceInterruptionFrames = (this.voiceInterruptionFrames || 0) + 1;
            if (this.voiceInterruptionFrames >= 3) {
              console.log('[AudioController] Loud user voice confirmed during playback. Halting speech synthesis.');
              this.voiceInterruptionFrames = 0;
              this.stopSpeaking();
              if (this.onInterruptionCallback) {
                this.onInterruptionCallback();
              }
            }
          } else {
            this.voiceInterruptionFrames = 0;
          }
          return;
        }

        if (!this.socket || this.socket.readyState !== WebSocket.OPEN) return;

        // Front-end Noise Gate:
        // Do not flood WebSocket with low-energy background mic hiss / room silence (rms < 0.012)
        // unless active speech is underway
        if (rms < 0.012 && !this.isSpeakingDetected) {
          return;
        }

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
        this.socket.onopen = null;
        this.socket.onmessage = null;
        this.socket.onerror = null;
        this.socket.onclose = null;
        if (this.socket.readyState === WebSocket.OPEN) {
          this.socket.close(1000, 'User stopped streaming');
        }
      } catch (e) {}
      this.socket = null;
    }
  }

  public stopSpeaking(): void {
    if (this.speechKeepAliveTimer) {
      clearInterval(this.speechKeepAliveTimer);
      this.speechKeepAliveTimer = null;
    }
    if (this.activeUtterance) {
      this.activeUtterance.onend = null;
      this.activeUtterance.onerror = null;
      this.activeUtterance = null;
    }
    if (typeof window !== 'undefined' && window.speechSynthesis) {
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

    // Clean text: strip emojis, markdown, URLs, and symbols so voice is 100% natural
    const cleanText = this.cleanTextForSpeech(text);
    if (!cleanText) {
      this.isSynthesizing = false;
      return;
    }

    // Keep speech recognition armed so the user can interrupt Ragul at any moment
    if (this.recognition && this.isListening) {
      try {
        this.recognition.start();
      } catch (e) {}
    }

    const doSpeak = () => {
      this.speechStartTime = Date.now();
      const utterance = new SpeechSynthesisUtterance(cleanText);
      this.activeUtterance = utterance;
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

      // Chrome SpeechSynthesis keep-alive watchdog (prevents Chrome from silently cutting off speech > 15s)
      if (this.speechKeepAliveTimer) {
        clearInterval(this.speechKeepAliveTimer);
      }
      this.speechKeepAliveTimer = setInterval(() => {
        if (!window.speechSynthesis || !window.speechSynthesis.speaking) {
          if (this.speechKeepAliveTimer) {
            clearInterval(this.speechKeepAliveTimer);
            this.speechKeepAliveTimer = null;
          }
        } else {
          window.speechSynthesis.pause();
          window.speechSynthesis.resume();
        }
      }, 4500);

      utterance.onend = () => {
        if (this.speechKeepAliveTimer) {
          clearInterval(this.speechKeepAliveTimer);
          this.speechKeepAliveTimer = null;
        }
        this.activeUtterance = null;
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
        }, 300);
      };

      utterance.onerror = (e: any) => {
        if (this.speechKeepAliveTimer) {
          clearInterval(this.speechKeepAliveTimer);
          this.speechKeepAliveTimer = null;
        }
        this.activeUtterance = null;
        this.isSynthesizing = false;
        // If canceled by user interruption, do NOT trigger onSpeechEndCallback
        if (e && (e.error === 'canceled' || e.error === 'interrupted')) {
          console.log('[AudioController] Speech playback canceled by user barge-in.');
          return;
        }
        setTimeout(() => {
          if (this.onSpeechEndCallback) {
            this.onSpeechEndCallback();
          }
          if (this.isListening && this.recognition) {
            try {
              this.recognition.start();
            } catch (err) {}
          }
        }, 300);
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

