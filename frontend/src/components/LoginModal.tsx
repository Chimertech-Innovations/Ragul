import React, { useState, useEffect } from 'react';
import { X, Lock, Phone, User, CheckCircle2, AlertCircle, Building2, Eye, EyeOff, KeyRound } from 'lucide-react';
import { useRagulStore, UserProfile } from '../store/useRagulStore';
import { audioController } from '../services/audioEngine';

interface LoginModalProps {
  isOpen: boolean;
  onClose: () => void;
  onLoginSuccess?: (user: UserProfile) => void;
}

export const LoginModal: React.FC<LoginModalProps> = ({ isOpen, onClose, onLoginSuccess }) => {
  const { setCurrentUser, addMessage, setSpeaking } = useRagulStore();
  const [phone, setPhone] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isResetMode, setIsResetMode] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const [demoAccounts, setDemoAccounts] = useState<Array<{ phone: string; full_name: string; farm_code: string; farm_name: string }>>([]);

  useEffect(() => {
    if (isOpen) {
      setError(null);
      setSuccessMsg(null);
      fetch('/api/auth/demo-accounts')
        .then((res) => res.json())
        .then((data) => {
          if (Array.isArray(data)) setDemoAccounts(data);
        })
        .catch(() => {});
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!phone.trim() || !password.trim()) {
      setError('Please enter both phone number and password.');
      return;
    }

    setLoading(true);
    setError(null);
    setSuccessMsg(null);

    if (isResetMode) {
      // Password Reset
      try {
        const res = await fetch('/api/auth/reset-password', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ phone: phone.trim(), new_password: password.trim() })
        });
        const data = await res.json();
        setLoading(false);

        if (!res.ok) {
          setError(data.detail || 'Password reset failed.');
          return;
        }

        setSuccessMsg('Password updated successfully! You can now log in.');
        setIsResetMode(false);
      } catch (err) {
        setLoading(false);
        setError('Cannot connect to server to update password.');
      }
      return;
    }

    // Standard Login
    try {
      const res = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phone: phone.trim(), password: password.trim() })
      });

      const data = await res.json();
      setLoading(false);

      if (!res.ok) {
        setError(data.detail || 'Login failed. Please check your credentials or reset your password below.');
        return;
      }

      const user: UserProfile = data.user;
      setCurrentUser(user);

      // Welcome voice message
      const welcomeText = `Welcome back, ${user.full_name}! Connected to ${user.farm_name}. I have loaded your live vision detections from the cameras. What details do you need, Sir?`;
      addMessage({ role: 'assistant', content: welcomeText });
      audioController.speakText(welcomeText, 'en-US');
      setSpeaking(true);
      setTimeout(() => setSpeaking(false), 4500);

      if (onLoginSuccess) onLoginSuccess(user);
      onClose();
    } catch (err) {
      setLoading(false);
      setError('Cannot connect to server. Please ensure FastAPI backend is running on port 8000.');
    }
  };

  const handleSelectDemo = (demoPhone: string) => {
    setPhone(demoPhone);
    setPassword('');
    setError(null);
    setSuccessMsg(null);
  };

  return (
    <div className="login-modal-overlay" onClick={onClose}>
      <div className="login-modal-card" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close-btn" onClick={onClose} aria-label="Close">
          <X size={18} />
        </button>

        <div className="login-modal-header">
          <div className="login-avatar-badge">
            <Building2 size={24} className="text-cyan-400" />
          </div>
          <h2 className="login-modal-title">
            {isResetMode ? 'Reset Farm Password' : 'Farm Account Login'}
          </h2>
          <p className="login-modal-sub">
            {isResetMode
              ? 'Enter your registered phone and set a new password for your farm.'
              : 'Log in with your registered PashuX phone & password to access your real cattle, cameras, and AI telemetry.'}
          </p>
        </div>

        {error && (
          <div className="login-error-badge">
            <AlertCircle size={15} />
            <span>{error}</span>
          </div>
        )}

        {successMsg && (
          <div className="login-error-badge" style={{ background: 'rgba(16, 185, 129, 0.15)', borderColor: 'rgba(16, 185, 129, 0.4)', color: '#34d399' }}>
            <CheckCircle2 size={15} />
            <span>{successMsg}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="login-form">
          <div className="input-group">
            <label className="input-label">
              <Phone size={14} /> Phone Number
            </label>
            <input
              type="text"
              className="login-input"
              placeholder="e.g. 8667262586 or 8667262585"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              autoFocus
              required
            />
          </div>

          <div className="input-group">
            <label className="input-label">
              <Lock size={14} /> {isResetMode ? 'New Password' : 'Password'}
            </label>
            <div className="password-input-wrap">
              <input
                type={showPassword ? 'text' : 'password'}
                className="login-input"
                placeholder={isResetMode ? 'Enter new password' : 'Enter farm password'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
              <button
                type="button"
                className="pw-toggle-btn"
                onClick={() => setShowPassword(!showPassword)}
                tabIndex={-1}
              >
                {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '-6px' }}>
            <button
              type="button"
              onClick={() => {
                setIsResetMode(!isResetMode);
                setError(null);
                setSuccessMsg(null);
              }}
              style={{
                background: 'none',
                border: 'none',
                color: 'var(--accent-cyan)',
                fontSize: '0.74rem',
                cursor: 'pointer',
                textDecoration: 'underline'
              }}
            >
              {isResetMode ? 'Back to Login' : 'Forgot / Reset Password?'}
            </button>
          </div>

          <button type="submit" className="login-submit-btn" disabled={loading}>
            {loading ? (
              <span className="spinner" />
            ) : isResetMode ? (
              <>
                <KeyRound size={16} /> Update Password
              </>
            ) : (
              <>
                <CheckCircle2 size={16} /> Connect to Farm
              </>
            )}
          </button>
        </form>

        {demoAccounts.length > 0 && (
          <div className="demo-accounts-section">
            <div className="demo-accounts-title">Registered PashuX Accounts:</div>
            <div className="demo-accounts-grid">
              {demoAccounts.map((acc, idx) => (
                <button
                  key={idx}
                  type="button"
                  className={`demo-account-chip ${phone === acc.phone ? 'selected' : ''}`}
                  onClick={() => handleSelectDemo(acc.phone)}
                >
                  <User size={13} />
                  <span>
                    <strong>{acc.full_name}</strong> • {acc.phone} ({acc.farm_code})
                  </span>
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
