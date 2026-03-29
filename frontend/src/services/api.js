const API_BASE_URL = import.meta.env.VITE_AI_SERVICE_URL || 'http://localhost:8000';

export const aiService = {
    async recognizeHandwriting(base64Image) {
        try {
            // Strip out the data:image/png;base64, prefix if present
            const base64Data = base64Image.replace(/^data:image\/(png|jpeg);base64,/, '');

            const response = await fetch(`${API_BASE_URL}/api/handwriting`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ image_base64: base64Data }),
            });

            if (!response.ok) {
                throw new Error(`Error: ${response.statusText}`);
            }

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Handwriting Recognition Error:', error);
            throw error;
        }
    },
};
