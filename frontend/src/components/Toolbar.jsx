import React from 'react';

const Toolbar = ({ isProcessing, onClear, onSave, hasText }) => {
    return (
        <div className="bg-white p-4 rounded-xl shadow-sm border border-slate-100">
            <h2 className="text-lg font-semibold mb-4 text-slate-700">Actions</h2>

            <div className="flex flex-col gap-3">
                <button
                    onClick={onClear}
                    disabled={!hasText || isProcessing}
                    className="w-full px-4 py-2 border border-slate-200 text-slate-700 rounded-lg hover:bg-slate-50 disabled:opacity-50 transition"
                >
                    Clear Transcription
                </button>

                <button
                    onClick={onSave}
                    disabled={!hasText || isProcessing}
                    className="w-full px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 disabled:opacity-50 shadow transition"
                >
                    Save to Database
                </button>
            </div>
        </div>
    );
};

export default Toolbar;
