// Test frontend API call simulation
// Use a browser-compatible way to set the API URL
const API_URL = 'http://localhost:8001';

async function testFrontendAPICall() {
    try {
        // Simulate selecting a file (using fetch to get the test file)
        console.log('🔍 Testing frontend API call...');
        
        // Create a proper FormData just like the frontend does
        const formData = new FormData();
        
        // Use fetch to get the test audio file as a blob
        const fileResponse = await fetch('/test_audio.wav');
        const audioBlob = await fileResponse.blob();
        const audioFile = new File([audioBlob], 'test_audio.wav', { type: 'audio/wav' });
        
        formData.append('audio', audioFile);
        formData.append('session_id', 'test-session-123');

        console.log('📤 Sending request to:', `${API_URL}/analyze`);
        console.log('📦 FormData contents:');
        for (let [key, value] of formData.entries()) {
            console.log(`  ${key}:`, value);
        }

        const response = await fetch(`${API_URL}/analyze`, {
            method: 'POST',
            body: formData,
        });

        console.log('📨 Response status:', response.status);
        console.log('📨 Response ok:', response.ok);

        if (!response.ok) {
            const errData = await response.json();
            console.error('❌ API Error:', errData);
            return null;
        }
        
        const analysisResult = await response.json();
        console.log('✅ Analysis results from API:', analysisResult);
        console.log('📊 Analysis result structure:');
        console.log('  - transcript:', !!analysisResult.transcript);
        console.log('  - speaker_transcripts:', !!analysisResult.speaker_transcripts);
        console.log('  - credibility_score:', analysisResult.credibility_score);
        console.log('  - audio_analysis:', !!analysisResult.audio_analysis);
        console.log('  - emotion_analysis:', !!analysisResult.emotion_analysis);
        
        return analysisResult;
        
    } catch (err) {
        console.error('💥 Error in testFrontendAPICall:', err);
        return null;
    }
}

// Run the test
testFrontendAPICall();
