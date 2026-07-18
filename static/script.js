let currentGocharString = "";

// PHASE 1: ASTRONOMY
document.getElementById('calculate-btn').addEventListener('click', async () => {
    const btn = document.getElementById('calculate-btn');
    const loading = document.getElementById('loading');
    const results = document.getElementById('results');
    const grid = document.getElementById('planets-grid');
    const phase2Section = document.getElementById('phase2-section');
    
    // UI State
    btn.disabled = true;
    btn.textContent = "Calculating...";
    results.classList.add('hidden');
    phase2Section.style.display = 'none';
    loading.classList.remove('hidden');
    
    try {
        const response = await fetch('/api/phase1/calculate');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        
        // Save globally for Phase 2
        currentGocharString = data.gochar_string;
        
        // Populate Summary
        document.getElementById('gochar-string').textContent = data.gochar_string;
        
        // Populate Meta
        const dateObj = new Date(data.timestamp);
        const options = { timeZone: 'Asia/Kolkata', timeZoneName: 'short', year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit', second: '2-digit' };
        document.getElementById('utc-time').textContent = `Local (IST): ${dateObj.toLocaleString('en-IN', options)}`;
        document.getElementById('julian-day').textContent = `Julian Day: ${data.julian_day.toFixed(4)}`;
        
        // Populate Grid
        grid.innerHTML = '';
        data.planets.forEach(planet => {
            const card = document.createElement('div');
            card.className = 'planet-card glass';
            
            card.innerHTML = `
                <div class="planet-name">${planet.planet}</div>
                <div class="planet-degree">${planet.degree.toFixed(2)}° Sidereal</div>
                <div class="planet-rasi">${planet.rasi}</div>
            `;
            grid.appendChild(card);
        });
        
        // Show Results
        loading.classList.add('hidden');
        results.classList.remove('hidden');
        
        // Reveal Phase 2 section
        phase2Section.style.display = 'block';
        
    } catch (error) {
        console.error("Error fetching Phase 1 data:", error);
        alert("Failed to calculate astronomical data. Make sure the Flask server is running.");
        loading.classList.add('hidden');
    } finally {
        btn.disabled = false;
        btn.textContent = "1. Calculate Daily Gochar";
    }
});

// PHASE 2: AI GENERATOR
document.getElementById('generate-ai-btn').addEventListener('click', async () => {
    const btn = document.getElementById('generate-ai-btn');
    const loadingAI = document.getElementById('loading-ai');
    const resultsAI = document.getElementById('ai-results');
    const grid = document.getElementById('predictions-grid');
    
    // UI State
    btn.disabled = true;
    btn.textContent = "Pandit Ji is writing...";
    resultsAI.classList.add('hidden');
    loadingAI.classList.remove('hidden');
    
    try {
        const response = await fetch('/api/phase2/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ gochar_string: currentGocharString })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || `HTTP error! status: ${response.status}`);
        }
        
        // Populate Grid
        grid.innerHTML = '';
        const predictions = data.predictions;
        
        // Iterate over the JSON keys (12 Rasis)
        Object.keys(predictions).forEach(rasi => {
            const card = document.createElement('div');
            card.className = 'prediction-card glass';
            
            card.innerHTML = `
                <div class="prediction-rasi">${rasi}</div>
                <div class="prediction-text">${predictions[rasi]}</div>
            `;
            grid.appendChild(card);
        });
        
        // Show Results
        loadingAI.classList.add('hidden');
        resultsAI.classList.remove('hidden');
        
        // Reveal Phase 3 section
        const phase3Section = document.getElementById('phase3-section');
        phase3Section.style.display = 'block';
        
    } catch (error) {
        console.error("Error in AI Generation:", error);
        alert("Pandit Ji encountered an issue: " + error.message + "\\n\\nPlease check your GEMINI_API_KEY.");
        loadingAI.classList.add('hidden');
    } finally {
        btn.disabled = false;
        btn.textContent = "2. Invoke Pandit Ji AI (Generate Horoscopes)";
    }
});

// PHASE 3: AUDIO GENERATOR
document.getElementById('generate-audio-btn').addEventListener('click', async () => {
    const btn = document.getElementById('generate-audio-btn');
    const loadingAudio = document.getElementById('loading-audio');
    const resultsAudio = document.getElementById('audio-results');
    const grid = document.getElementById('audio-grid');
    
    // UI State
    btn.disabled = true;
    btn.textContent = "Recording Audio...";
    resultsAudio.classList.add('hidden');
    loadingAudio.classList.remove('hidden');
    
    try {
        const response = await fetch('/api/phase3/generate', { method: 'POST' });
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || `HTTP error! status: ${response.status}`);
        }
        
        // Populate Grid
        grid.innerHTML = '';
        const audioFiles = data.audio_files;
        
        audioFiles.forEach(item => {
            const card = document.createElement('div');
            card.className = 'audio-card glass';
            
            // Add a cache-busting query string so browser reloads audio if regenerated
            const timestamp = new Date().getTime();
            
            card.innerHTML = `
                <h4>${item.rasi}</h4>
                <audio controls preload="metadata">
                    <source src="${item.url}?t=${timestamp}" type="audio/mpeg">
                    Your browser does not support the audio element.
                </audio>
            `;
            grid.appendChild(card);
        });
        
        // Show Results
        loadingAudio.classList.add('hidden');
        resultsAudio.classList.remove('hidden');
        
        // Reveal Phase 4 section
        const phase4Section = document.getElementById('phase4-section');
        phase4Section.style.display = 'block';
        
    } catch (error) {
        console.error("Error in Audio Generation:", error);
        alert("Failed to generate audio files: " + error.message);
        loadingAudio.classList.add('hidden');
    } finally {
        btn.disabled = false;
        btn.textContent = "3. Generate Pandit Ji Audio (Voice: hi-IN-MadhurNeural)";
    }
});

// PHASE 4: VIDEO GENERATOR (STREAMING QUEUE)
document.getElementById('generate-video-btn').addEventListener('click', async () => {
    const btn = document.getElementById('generate-video-btn');
    const loadingVideo = document.getElementById('loading-video');
    const resultsVideo = document.getElementById('video-results');
    const grid = document.getElementById('video-grid');
    
    // UI State
    btn.disabled = true;
    btn.textContent = "Rendering Videos sequentially...";
    resultsVideo.classList.remove('hidden'); // Show grid immediately
    loadingVideo.classList.remove('hidden');
    grid.innerHTML = '';
    
    const rasis = ["मेष", "वृषभ", "मिथुन", "कर्क", "सिंह", "कन्या", "तुला", "वृश्चिक", "धनु", "मकर", "कुंभ", "मीन"];
    let successCount = 0;
    
    for (const rasi of rasis) {
        try {
            // Update loading text
            loadingVideo.querySelector('p').textContent = `Rendering ${rasi}... (This takes ~10 seconds)`;
            
            const response = await fetch('/api/phase4/generate_single', { 
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ rasi: rasi })
            });
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || `HTTP error! status: ${response.status}`);
            }
            
            // Build Video Card and append it to the grid IMMEDIATELY
            const item = data.video_file;
            const card = document.createElement('div');
            card.className = 'video-card glass';
            const timestamp = new Date().getTime();
            
            card.innerHTML = `
                <h4>${item.rasi}</h4>
                <video controls preload="metadata">
                    <source src="${item.url}?t=${timestamp}" type="video/mp4">
                    Your browser does not support the video element.
                </video>
            `;
            grid.appendChild(card);
            successCount++;
            
        } catch (error) {
            console.error(`Error rendering video for ${rasi}:`, error);
            // Append an error card so the user knows it failed, but keep processing the rest
            const errorCard = document.createElement('div');
            errorCard.className = 'video-card glass';
            errorCard.innerHTML = `<h4 style="color:red">${rasi} Failed</h4><p>${error.message}</p>`;
            grid.appendChild(errorCard);
        }
    }
    
    // Final UI State
    loadingVideo.classList.add('hidden');
    btn.disabled = false;
    btn.textContent = `4. Render Final Videos (${successCount}/12 completed)`;
    
    // Reveal Phase 6 Section
    const phase6Section = document.getElementById('phase6-section');
    phase6Section.style.display = 'block';
});

// PHASE 6: COMBINE VIDEOS
document.getElementById('combine-video-btn').addEventListener('click', async () => {
    const btn = document.getElementById('combine-video-btn');
    const loading = document.getElementById('loading-phase6');
    const results = document.getElementById('phase6-results');
    const output = document.getElementById('phase6-output');
    const statusText = document.getElementById('phase6-status-text');
    
    btn.disabled = true;
    statusText.textContent = "Combining all 12 videos into a Master File... (takes 1-3 mins)";
    loading.classList.remove('hidden');
    results.classList.add('hidden');
    
    try {
        const response = await fetch('/api/phase4/combine_videos', { method: 'POST' });
        const data = await response.json();
        
        if (!response.ok) throw new Error(data.error || "Unknown Error");
        
        output.innerHTML = `
            <h3 style="color:#10b981">Master Video Combined!</h3>
            <video controls style="width:100%; max-width:400px; margin-top:1rem; border-radius:12px;">
                <source src="${data.url}?t=${new Date().getTime()}" type="video/mp4">
            </video>
        `;
        results.classList.remove('hidden');
    } catch (e) {
        alert("Failed to combine videos: " + e.message);
    } finally {
        loading.classList.add('hidden');
        btn.disabled = false;
    }
});

// PHASE 6: UPLOAD MASTER TO YOUTUBE
document.getElementById('upload-master-youtube-btn').addEventListener('click', async () => {
    const btn = document.getElementById('upload-master-youtube-btn');
    const loading = document.getElementById('loading-phase6');
    const results = document.getElementById('phase6-results');
    const output = document.getElementById('phase6-output');
    const statusText = document.getElementById('phase6-status-text');
    
    btn.disabled = true;
    statusText.textContent = "Uploading Master to YouTube (Check terminal for OAuth if needed)...";
    loading.classList.remove('hidden');
    
    try {
        const response = await fetch('/api/phase6/upload', { 
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ type: 'master', platform: 'youtube' })
        });
        const data = await response.json();
        
        if (!response.ok) throw new Error(data.error || "Unknown Error");
        
        output.innerHTML += `
            <h3 style="color:#ef4444; margin-top:1rem;">Master Uploaded to YouTube!</h3>
            <p>Video ID: <strong>${data.youtube_video_id}</strong> (Private Status)</p>
            <a href="https://studio.youtube.com/video/${data.youtube_video_id}/edit" target="_blank" style="color:#3b82f6; text-decoration:underline;">Edit in YouTube Studio</a>
        `;
        results.classList.remove('hidden');
    } catch (e) {
        alert("Failed to upload: " + e.message);
    } finally {
        loading.classList.add('hidden');
        btn.disabled = false;
    }
});

// PHASE 6: UPLOAD SHORTS TO YOUTUBE
document.getElementById('upload-shorts-youtube-btn').addEventListener('click', async () => {
    const btn = document.getElementById('upload-shorts-youtube-btn');
    const loading = document.getElementById('loading-phase6');
    const results = document.getElementById('phase6-results');
    const output = document.getElementById('phase6-output');
    const statusText = document.getElementById('phase6-status-text');
    
    btn.disabled = true;
    loading.classList.remove('hidden');
    
    const rasis = ["मेष", "वृषभ", "मिथुन", "कर्क", "सिंह", "कन्या", "तुला", "वृश्चिक", "धनु", "मकर", "कुंभ", "मीन"];
    
    for (const rasi of rasis) {
        try {
            statusText.textContent = `Uploading ${rasi} Short to YouTube...`;
            
            const response = await fetch('/api/phase6/upload', { 
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ type: 'single', rasi: rasi, platform: 'youtube' })
            });
            const data = await response.json();
            
            if (!response.ok) throw new Error(data.error || "Unknown Error");
            
            output.innerHTML += `
                <div style="margin-top: 0.5rem; padding-top: 0.5rem; border-top: 1px solid #ccc;">
                    <strong>${rasi} Short uploaded!</strong> YouTube ID: <a href="https://studio.youtube.com/video/${data.youtube_video_id}/edit" target="_blank" style="color:#3b82f6;">${data.youtube_video_id}</a>
                </div>
            `;
            results.classList.remove('hidden');
        } catch (e) {
            console.error(`Failed to upload ${rasi}:`, e);
            output.innerHTML += `<div style="color:red;">Failed to upload ${rasi}: ${e.message}</div>`;
        }
    }
    
    loading.classList.add('hidden');
    btn.disabled = false;
});

// PHASE 6: UPLOAD SHORTS TO META (FB/IG)
document.getElementById('upload-shorts-meta-btn').addEventListener('click', async () => {
    const btn = document.getElementById('upload-shorts-meta-btn');
    const loading = document.getElementById('loading-phase6');
    const results = document.getElementById('phase6-results');
    const output = document.getElementById('phase6-output');
    const statusText = document.getElementById('phase6-status-text');
    
    btn.disabled = true;
    loading.classList.remove('hidden');
    
    const rasis = ["मेष", "वृषभ", "मिथुन", "कर्क", "सिंह", "कन्या", "तुला", "वृश्चिक", "धनु", "मकर", "कुंभ", "मीन"];
    
    for (const rasi of rasis) {
        try {
            statusText.textContent = `Uploading ${rasi} Short to Meta (FB/IG)...`;
            
            const response = await fetch('/api/phase6/upload', { 
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ type: 'single', rasi: rasi, platform: 'meta' })
            });
            const data = await response.json();
            
            if (!response.ok) throw new Error(data.error || "Unknown Error");
            
            output.innerHTML += `
                <div style="margin-top: 0.5rem; padding-top: 0.5rem; border-top: 1px solid #ccc;">
                    <strong>${rasi} Short uploaded to Meta!</strong> FB ID: ${data.facebook_video_id}, IG ID: ${data.instagram_video_id}
                </div>
            `;
            results.classList.remove('hidden');
        } catch (e) {
            console.error(`Failed to upload ${rasi} to Meta:`, e);
            output.innerHTML += `<div style="color:red;">Failed to upload ${rasi} to Meta: ${e.message}</div>`;
        }
    }
    
    loading.classList.add('hidden');
    btn.disabled = false;
});
