import React, { useState } from 'react';
import { Send, Sparkles, AlertTriangle, CheckCircle } from 'lucide-react';
import { cn } from '../lib/utils';
import { beautifyBroadcast, sendBroadcast } from '../api/client';

const Broadcast = () => {
    const [message, setMessage] = useState('');
    const [isBeautifying, setIsBeautifying] = useState(false);
    const [isSending, setIsSending] = useState(false);
    const [showSuccess, setShowSuccess] = useState(false);
    const [error, setError] = useState(null);

    const handleBeautify = async () => {
        setIsBeautifying(true);
        setError(null);
        try {
            const result = await beautifyBroadcast(message);
            setMessage(result.improved);
        } catch (err) {
            setError("Failed to beautify message. Please try again.");
        } finally {
            setIsBeautifying(false);
        }
    };

    const handleSend = async () => {
        if (!message) return;
        setIsSending(true);
        setError(null);
        try {
            await sendBroadcast(message);
            setShowSuccess(true);
            setTimeout(() => setShowSuccess(false), 3000);
            setMessage('');
        } catch (err) {
            setError("Failed to send broadcast. Please try again.");
        } finally {
            setIsSending(false);
        }
    };

    return (
        <div className="space-y-8 animate-in fade-in duration-500 max-w-4xl mx-auto">
            <div className="text-center">
                <h2 className="text-3xl font-bold text-slate-900">Broadcast Center</h2>
                <p className="text-slate-500 mt-1">Send mass alerts to patients and staff</p>
            </div>

            <div className="bg-white rounded-2xl shadow-xl border border-slate-100 overflow-hidden">
                <div className="p-6 bg-slate-50 border-b border-slate-100 flex justify-between items-center">
                    <div className="flex items-center space-x-2">
                        <div className="w-3 h-3 rounded-full bg-red-500 animate-pulse"></div>
                        <span className="text-sm font-bold text-slate-700">Live Broadcast Channel</span>
                    </div>
                    <div className="text-xs text-slate-400">Target: All Registered Patients (Mumbai Region)</div>
                </div>

                <div className="p-8">
                    <label className="block text-sm font-medium text-slate-700 mb-2">Draft Message</label>
                    <div className="relative">
                        <textarea
                            value={message}
                            onChange={(e) => setMessage(e.target.value)}
                            placeholder="Type here to draft a patient advisory or staff alert..."
                            className="w-full h-64 p-6 text-lg rounded-xl border border-slate-200 focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none bg-slate-50 placeholder:text-slate-400"
                        />
                        {isBeautifying && (
                            <div className="absolute inset-0 bg-white/80 backdrop-blur-sm flex items-center justify-center rounded-xl z-10">
                                <div className="flex flex-col items-center animate-pulse">
                                    <Sparkles className="w-8 h-8 text-indigo-600 mb-2" />
                                    <span className="text-sm font-medium text-indigo-600">AI is refining your message...</span>
                                </div>
                            </div>
                        )}
                    </div>

                    {error && <p className="text-red-500 text-sm mt-2">{error}</p>}

                    <div className="mt-6 flex justify-between items-center">
                        <button
                            onClick={handleBeautify}
                            disabled={isBeautifying || message.length === 0}
                            className="flex items-center space-x-2 px-6 py-3 bg-indigo-50 text-indigo-600 rounded-xl font-medium hover:bg-indigo-100 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            <Sparkles className="w-5 h-5" />
                            <span>Beautify with AI</span>
                        </button>

                        <button
                            onClick={handleSend}
                            disabled={message.length === 0 || isSending}
                            className="flex items-center space-x-2 px-8 py-3 bg-blue-600 text-white rounded-xl font-bold hover:bg-blue-700 transition-all shadow-lg shadow-blue-600/20 disabled:opacity-50 disabled:cursor-not-allowed disabled:shadow-none"
                        >
                            <span>{isSending ? 'Sending...' : 'Send Broadcast'}</span>
                            <Send className="w-5 h-5" />
                        </button>
                    </div>
                </div>
            </div>

            {showSuccess && (
                <div className="fixed bottom-8 right-8 bg-emerald-600 text-white px-6 py-4 rounded-xl shadow-2xl flex items-center space-x-3 animate-in slide-in-from-bottom-5">
                    <CheckCircle className="w-6 h-6" />
                    <div>
                        <p className="font-bold">Broadcast Sent Successfully</p>
                        <p className="text-xs text-emerald-100">Delivered to 12,450 recipients</p>
                    </div>
                </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-8">
                <div className="p-4 bg-amber-50 border border-amber-100 rounded-xl flex items-start space-x-3">
                    <AlertTriangle className="w-5 h-5 text-amber-600 shrink-0" />
                    <div>
                        <p className="text-sm font-bold text-amber-800">High Urgency</p>
                        <p className="text-xs text-amber-700 mt-1">Recommended for severe weather alerts.</p>
                    </div>
                </div>
                {/* More tips or context could go here */}
            </div>
        </div>
    );
};

export default Broadcast;
