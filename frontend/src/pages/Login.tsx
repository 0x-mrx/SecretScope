import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { authService } from '../services/api';
import { ShieldAlert, KeyRound, Mail, AlertTriangle, HelpCircle } from 'lucide-react';

export const Login: React.FC = () => {
  const { login } = useAuth();
  const navigate = useNavigate();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isResetMode, setIsResetMode] = useState(false);
  const [resetToken, setResetToken] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [resetStep, setResetStep] = useState(1); // 1 = request, 2 = confirm
  
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const formData = new FormData();
      formData.append('username', email);
      formData.append('password', password);

      const data = await authService.login(formData);
      login(data.access_token, data.role, data.email);
      navigate('/');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Invalid email or password');
    } finally {
      setLoading(false);
    }
  };

  const handleRequestReset = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);

    try {
      const res = await authService.requestReset(email);
      setSuccess("Reset token generated! (Displayed below for testing)");
      // Inject token for ease of testing
      if (res.debug_token) {
        setResetToken(res.debug_token);
      }
      setResetStep(2);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to request reset');
    } finally {
      setLoading(false);
    }
  };

  const handleConfirmReset = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);

    try {
      await authService.confirmReset({ token: resetToken, new_password: newPassword });
      setSuccess("Password changed successfully! You can now log in.");
      setIsResetMode(false);
      setResetStep(1);
      setPassword('');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to reset password');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#090d16] flex items-center justify-center p-6 relative overflow-hidden">
      {/* Background Cyber Glow Grid */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#1f2937_1px,transparent_1px),linear-gradient(to_bottom,#1f2937_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)] opacity-30"></div>
      
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-96 h-96 bg-indigo-500/10 rounded-full blur-[100px] pointer-events-none"></div>
      <div className="absolute bottom-1/4 left-1/3 w-96 h-96 bg-red-500/5 rounded-full blur-[120px] pointer-events-none"></div>

      <div className="w-full max-w-md bg-gray-900/80 backdrop-blur-md border border-gray-800 rounded-2xl shadow-2xl p-8 relative z-10">
        
        {/* Logo / Badge */}
        <div className="flex flex-col items-center mb-8">
          <div className="bg-red-500/10 p-3.5 rounded-2xl border border-red-500/20 mb-4 shadow-[0_0_20px_rgba(239,68,68,0.1)]">
            <ShieldAlert className="w-9 h-9 text-red-500" />
          </div>
          <h2 className="text-2xl font-bold text-white tracking-tight">SecretScope</h2>
          <p className="text-sm text-cyber-muted mt-1 font-mono text-center">
            Enterprise Secret Discovery & Remediation
          </p>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-500/10 border border-red-500/20 rounded-xl flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 text-red-500 shrink-0 mt-0.5" />
            <p className="text-sm text-red-400 font-medium leading-tight">{error}</p>
          </div>
        )}

        {success && (
          <div className="mb-6 p-4 bg-emerald-500/10 border border-emerald-500/20 rounded-xl flex items-start gap-3">
            <ShieldAlert className="w-5 h-5 text-emerald-500 shrink-0 mt-0.5" />
            <p className="text-sm text-emerald-400 font-medium leading-tight">{success}</p>
          </div>
        )}

        {/* Login Form */}
        {!isResetMode ? (
          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-xs font-semibold tracking-wider text-cyber-muted uppercase mb-2 font-mono">
                Email Address
              </label>
              <div className="relative">
                <Mail className="absolute left-3.5 top-3.5 w-5 h-5 text-cyber-muted" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  placeholder="admin@secretscope.local"
                  className="w-full bg-gray-950/60 border border-gray-800 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 rounded-xl py-3 pl-11 pr-4 text-white text-sm outline-none transition duration-200"
                />
              </div>
            </div>

            <div>
              <div className="flex justify-between items-center mb-2">
                <label className="block text-xs font-semibold tracking-wider text-cyber-muted uppercase font-mono">
                  Password
                </label>
                <button
                  type="button"
                  onClick={() => setIsResetMode(true)}
                  className="text-xs text-indigo-400 hover:text-indigo-300 font-medium"
                >
                  Forgot Password?
                </button>
              </div>
              <div className="relative">
                <KeyRound className="absolute left-3.5 top-3.5 w-5 h-5 text-cyber-muted" />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  placeholder="••••••••••••"
                  className="w-full bg-gray-950/60 border border-gray-800 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 rounded-xl py-3 pl-11 pr-4 text-white text-sm outline-none transition duration-200"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-indigo-600 hover:bg-indigo-500 text-white font-semibold py-3 px-4 rounded-xl shadow-lg transition duration-200 disabled:opacity-50"
            >
              {loading ? 'Authenticating...' : 'Sign In'}
            </button>
          </form>
        ) : (
          /* Password Reset Flow */
          <form onSubmit={resetStep === 1 ? handleRequestReset : handleConfirmReset} className="space-y-5">
            <div className="border-b border-gray-800 pb-4 mb-4">
              <h3 className="text-white font-semibold flex items-center gap-2">
                <HelpCircle className="w-5 h-5 text-indigo-400" />
                Reset Security Key
              </h3>
              <p className="text-xs text-cyber-muted mt-1">
                Enter your registered email to request a temporary reset code.
              </p>
            </div>

            {resetStep === 1 ? (
              <div>
                <label className="block text-xs font-semibold tracking-wider text-cyber-muted uppercase mb-2 font-mono">
                  Registered Email
                </label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  placeholder="admin@secretscope.local"
                  className="w-full bg-gray-950/60 border border-gray-800 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 rounded-xl py-3 px-4 text-white text-sm outline-none transition duration-200"
                />
              </div>
            ) : (
              <div className="space-y-4">
                <div>
                  <label className="block text-xs font-semibold tracking-wider text-cyber-muted uppercase mb-2 font-mono">
                    Reset Token
                  </label>
                  <textarea
                    rows={2}
                    value={resetToken}
                    onChange={(e) => setResetToken(e.target.value)}
                    required
                    className="w-full bg-gray-950/60 border border-gray-800 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 rounded-xl py-2 px-3 text-white text-xs font-mono outline-none transition"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold tracking-wider text-cyber-muted uppercase mb-2 font-mono">
                    New Security Key
                  </label>
                  <input
                    type="password"
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    required
                    placeholder="Min 8 characters"
                    className="w-full bg-gray-950/60 border border-gray-800 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 rounded-xl py-3 px-4 text-white text-sm outline-none transition"
                  />
                </div>
              </div>
            )}

            <div className="flex gap-3">
              <button
                type="button"
                onClick={() => {
                  setIsResetMode(false);
                  setResetStep(1);
                  setError('');
                  setSuccess('');
                }}
                className="flex-1 border border-gray-800 hover:bg-gray-800 text-cyber-text font-semibold py-3 px-4 rounded-xl transition duration-200 text-center text-sm"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={loading}
                className="flex-1 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold py-3 px-4 rounded-xl shadow-lg transition duration-200 disabled:opacity-50 text-sm"
              >
                {loading ? 'Processing...' : resetStep === 1 ? 'Get Code' : 'Update Key'}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
};
