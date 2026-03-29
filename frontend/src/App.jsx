import React, { useState, useEffect } from 'react';
import DrawingBoard from './components/DrawingBoard';
import Toolbar from './components/Toolbar';
import { supabase } from './lib/supabase';
import { aiService } from './services/api';

function App() {
    const [transcribedText, setTranscribedText] = useState('');
    const [isProcessing, setIsProcessing] = useState(false);
    const [user, setUser] = useState(null);
    const [dyslexicMode, setDyslexicMode] = useState(false);

    useEffect(() => {
        // Check active session
        supabase.auth.getSession().then(({ data: { session } }) => {
            setUser(session?.user ?? null);
        });

        const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
            setUser(session?.user ?? null);
        });

        return () => subscription.unsubscribe();
    }, []);

    const handleProcessImage = async (base64Image) => {
        setIsProcessing(true);
        try {
            const result = await aiService.recognizeHandwriting(base64Image);
            // Result contains raw_text from FastAPI endpoint
            setTranscribedText((prev) => prev ? prev + ' ' + result.raw_text : result.raw_text);
        } catch (error) {
            console.error(error);
            alert('Failed to process handwriting. Check console for details.');
        } finally {
            setIsProcessing(false);
        }
    };

    const handleClear = () => {
        setTranscribedText('');
    };

    const handleSaveToDatabase = async () => {
        if (!user) {
            alert("You must be logged in to save.");
            return;
        }
        if (!transcribedText) return;

        // Example implementation for saving to `answers` table. In a real app,
        // we would need exam_id and question_number from routing/state.
        try {
            const { data, error } = await supabase
                .from('answers')
                .insert([
                    {
                        student_id: user.id,
                        raw_text: transcribedText,
                        exam_id: '00000000-0000-0000-0000-000000000000', // Placeholder
                        question_number: 1 // Placeholder
                    }
                ]);

            if (error) throw error;
            alert("Answer saved successfully!");
        } catch (error) {
            console.error(error);
            alert("Error saving answer.");
        }
    };

    const login = async () => {
        // For demo purposes, we will use a dummy login if no auth setup
        // You should use standard supabase auth processes here.
        const { error } = await supabase.auth.signInWithPassword({
            email: 'student@example.com',
            password: 'password123'
        });
        if (error) alert("Error: " + error.message);
    };

    return (
        <div className={`min-h-screen ${dyslexicMode ? 'font-dyslexic bg-yellow-50' : 'bg-scribe-bg'} text-slate-800`}>
            <header className="bg-white shadow">
                <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8 flex justify-between items-center">
                    <h1 className="text-3xl font-bold text-scribe-primary">Digital Scribe</h1>
                    <div className="flex gap-4 items-center">
                        <button
                            onClick={() => setDyslexicMode(!dyslexicMode)}
                            className="px-4 py-2 border rounded text-sm hover:bg-slate-50"
                        >
                            Toggle Dyslexic Font
                        </button>
                        {!user ? (
                            <button onClick={login} className="px-4 py-2 bg-scribe-primary text-white rounded">Login</button>
                        ) : (
                            <span className="text-sm">Logged in</span>
                        )}
                    </div>
                </div>
            </header>

            <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
                <div className="flex flex-col lg:flex-row gap-6">
                    <div className="w-full lg:w-2/3 bg-white p-4 rounded-xl shadow-sm border border-slate-100">
                        <h2 className="text-lg font-semibold mb-4 text-slate-700">Exam Canvas</h2>
                        <DrawingBoard onProcess={handleProcessImage} />
                    </div>

                    <div className="w-full lg:w-1/3 flex flex-col gap-4">
                        <Toolbar
                            isProcessing={isProcessing}
                            onClear={handleClear}
                            onSave={handleSaveToDatabase}
                            hasText={transcribedText.length > 0}
                        />

                        <div className="bg-white p-4 rounded-xl shadow-sm border border-slate-100 flex-grow">
                            <h2 className="text-lg font-semibold mb-2 text-slate-700">Transcription</h2>
                            {isProcessing && <div className="text-sm text-scribe-secondary animate-pulse mb-2">Processing handwriting...</div>}

                            <div className="w-full h-64 p-3 bg-slate-50 border rounded-lg overflow-y-auto whitespace-pre-wrap">
                                {transcribedText || <span className="text-slate-400 italic">Writing will appear here...</span>}
                            </div>
                        </div>
                    </div>
                </div>
            </main>
        </div>
    );
}

export default App;
