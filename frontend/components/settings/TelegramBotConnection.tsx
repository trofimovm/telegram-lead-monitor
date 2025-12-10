'use client';

import { useState, useEffect } from 'react';
import { notificationsApi } from '@/lib/api/notifications';
import {
  TelegramBotInfo,
  TelegramVerificationCodeResponse,
} from '@/lib/api/notification-types';

interface TelegramBotConnectionProps {
  onConnectionChange?: (connected: boolean) => void;
}

type Step = 'idle' | 'generating' | 'verifying' | 'connected';

export default function TelegramBotConnection({
  onConnectionChange,
}: TelegramBotConnectionProps) {
  const [step, setStep] = useState<Step>('idle');
  const [botInfo, setBotInfo] = useState<TelegramBotInfo | null>(null);
  const [verificationData, setVerificationData] =
    useState<TelegramVerificationCodeResponse | null>(null);
  const [chatId, setChatId] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Загрузить статус при монтировании
  useEffect(() => {
    loadBotInfo();
  }, []);

  const loadBotInfo = async () => {
    try {
      const info = await notificationsApi.getTelegramBotInfo();
      setBotInfo(info);
      if (info.is_connected) {
        setStep('connected');
        setChatId(info.chat_id || '');
      }
    } catch (err: any) {
      console.error('Failed to load bot info:', err);
      // Ошибку показываем только если это критическая ошибка API (5xx)
      // НЕ показываем если бот просто не подключен (это нормальное состояние)
      if (err.response && err.response.status >= 500) {
        setError('Failed to load Telegram bot info. Please try again later.');
      }
    }
  };

  const handleGenerateCode = async () => {
    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const data = await notificationsApi.generateTelegramCode();
      setVerificationData(data);
      setStep('generating');
      setSuccess('Verification code generated! Follow the instructions below.');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to generate verification code');
    } finally {
      setLoading(false);
    }
  };

  const handleVerify = async () => {
    if (!verificationData || !chatId.trim()) {
      setError('Please enter your Chat ID');
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const response = await notificationsApi.verifyTelegramCode({
        verification_code: verificationData.verification_code,
        chat_id: chatId.trim(),
      });

      setSuccess(response.message);
      setStep('connected');
      await loadBotInfo();

      if (onConnectionChange) {
        onConnectionChange(true);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Verification failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleDisconnect = async () => {
    if (!confirm('Are you sure you want to disconnect Telegram bot?')) {
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      await notificationsApi.disconnectTelegramBot();
      setSuccess('Telegram bot disconnected successfully');
      setStep('idle');
      setVerificationData(null);
      setChatId('');
      await loadBotInfo();

      if (onConnectionChange) {
        onConnectionChange(false);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to disconnect');
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    setStep('idle');
    setVerificationData(null);
    setChatId('');
    setError(null);
    setSuccess(null);
  };

  return (
    <div className="space-y-4">
      {/* Error Message */}
      {error && (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-800 dark:text-red-200 px-4 py-3 rounded-lg">
          <p className="text-sm">{error}</p>
        </div>
      )}

      {/* Success Message */}
      {success && (
        <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 text-green-800 dark:text-green-200 px-4 py-3 rounded-lg">
          <p className="text-sm">{success}</p>
        </div>
      )}

      {/* Connected State */}
      {step === 'connected' && botInfo && (
        <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4">
          <div className="flex items-start justify-between">
            <div>
              <h4 className="text-sm font-medium text-green-900 dark:text-green-100">Connected</h4>
              <p className="text-sm text-green-700 dark:text-green-300 mt-1">
                Telegram bot is connected to chat ID: <code className="font-mono">{botInfo.chat_id}</code>
              </p>
              <p className="text-sm text-green-600 dark:text-green-400 mt-1">
                Bot: {botInfo.bot_username}
              </p>
            </div>
            <button
              onClick={handleDisconnect}
              disabled={loading}
              className="text-sm text-red-600 dark:text-red-400 hover:text-red-800 dark:hover:text-red-300 font-medium disabled:opacity-50"
            >
              Disconnect
            </button>
          </div>
        </div>
      )}

      {/* Not Connected - Idle State */}
      {step === 'idle' && (
        <div className="bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
          <h4 className="text-sm font-medium text-gray-900 dark:text-gray-100 mb-2">
            Connect Telegram Bot
          </h4>
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
            Receive lead notifications directly in Telegram. Click the button below to start the
            connection process.
          </p>
          <button
            onClick={handleGenerateCode}
            disabled={loading}
            className="bg-blue-600 dark:bg-blue-500 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700 dark:hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Generating...' : 'Connect Telegram Bot'}
          </button>
        </div>
      )}

      {/* Generating/Verifying State */}
      {(step === 'generating' || step === 'verifying') && verificationData && (
        <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4 space-y-4">
          <div>
            <h4 className="text-sm font-medium text-blue-900 dark:text-blue-100 mb-2">Verification Code</h4>
            <div className="bg-white dark:bg-gray-900 border border-blue-300 dark:border-blue-700 rounded-lg p-3 mb-3">
              <code className="text-xl font-mono font-bold text-blue-900 dark:text-blue-100">
                {verificationData.verification_code}
              </code>
            </div>
            <p className="text-xs text-blue-600 dark:text-blue-400">
              Expires at:{' '}
              {new Date(verificationData.expires_at).toLocaleString()}
            </p>
          </div>

          <div className="bg-white dark:bg-gray-900 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
            <h5 className="text-sm font-medium text-gray-900 dark:text-gray-100 mb-2">Instructions:</h5>
            <ol className="text-sm text-gray-700 dark:text-gray-300 space-y-2 list-decimal list-inside">
              <li>
                Open Telegram and find bot:{' '}
                <a
                  href={`https://t.me/${verificationData.bot_username.replace('@', '')}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 dark:text-blue-400 hover:underline font-medium"
                >
                  {verificationData.bot_username}
                </a>
              </li>
              <li>Send <code className="bg-gray-100 dark:bg-gray-800 px-1 py-0.5 rounded">/start</code> to the bot</li>
              <li>Copy your <strong>Chat ID</strong> from the bot's response</li>
              <li>Paste Chat ID below and click "Verify & Connect"</li>
            </ol>
            <div className="mt-3 p-2 bg-blue-50 dark:bg-blue-900/10 rounded border border-blue-200 dark:border-blue-800">
              <p className="text-xs text-blue-700 dark:text-blue-300">
                💡 <strong>Quick tip:</strong> You can also verify directly in Telegram by sending:{' '}
                <code className="bg-blue-100 dark:bg-blue-800 px-1 rounded">/verify {verificationData.verification_code}</code>
              </p>
            </div>
          </div>

          <div>
            <label htmlFor="chatId" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Your Chat ID
            </label>
            <input
              type="text"
              id="chatId"
              value={chatId}
              onChange={(e) => setChatId(e.target.value)}
              placeholder="e.g., 123456789"
              className="w-full px-3 py-2 bg-white dark:bg-gray-900 border border-gray-300 dark:border-gray-700 text-gray-900 dark:text-gray-100 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent placeholder-gray-400 dark:placeholder-gray-500"
            />
          </div>

          <div className="flex gap-2">
            <button
              onClick={handleVerify}
              disabled={loading || !chatId.trim()}
              className="flex-1 bg-blue-600 dark:bg-blue-500 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700 dark:hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Verifying...' : 'Verify & Connect'}
            </button>
            <button
              onClick={handleCancel}
              disabled={loading}
              className="px-4 py-2 border border-gray-300 dark:border-gray-700 rounded-lg text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800 disabled:opacity-50"
            >
              Cancel
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
