const API_BASE_URL = 'http://localhost:8000';

let currentVideoData = null;
let youtubePlayer = null;

// Initialize YouTube IFrame API
function loadYouTubeAPI() {
    if (window.YT && window.YT.Player) {
        return Promise.resolve();
    }
    
    return new Promise((resolve) => {
        if (window.YT && window.YT.Player) {
            resolve();
            return;
        }
        
        // Set up callback
        window.onYouTubeIframeAPIReady = function() {
            console.log('YouTube API ready');
            resolve();
        };
        
        // Load script if not already loading
        if (!document.querySelector('script[src*="youtube.com/iframe_api"]')) {
            const tag = document.createElement('script');
            tag.src = 'https://www.youtube.com/iframe_api';
            const firstScriptTag = document.getElementsByTagName('script')[0];
            firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);
        } else {
            // Script already loading, wait for callback
            const checkReady = setInterval(() => {
                if (window.YT && window.YT.Player) {
                    clearInterval(checkReady);
                    resolve();
                }
            }, 100);
        }
    });
}

// Perform search
async function performSearch() {
    const query = document.getElementById('searchInput').value.trim();
    
    if (!query) {
        alert('Please enter a search query');
        return;
    }
    
    const searchButton = document.getElementById('searchButton');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const resultsContainer = document.getElementById('resultsContainer');
    
    // Show loading
    searchButton.disabled = true;
    loadingIndicator.style.display = 'flex';
    resultsContainer.innerHTML = '';
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/search`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                query: query,
                top_k: 5
            })
        });
        
        if (!response.ok) {
            throw new Error('Search failed');
        }
        
        const data = await response.json();
        displayResults(data.clips, data.query);
    } catch (error) {
        console.error('Error:', error);
        resultsContainer.innerHTML = `
            <div class="no-results">
                <h3>Error searching videos</h3>
                <p>${error.message}</p>
                <p>Make sure the backend server is running on ${API_BASE_URL}</p>
            </div>
        `;
    } finally {
        searchButton.disabled = false;
        loadingIndicator.style.display = 'none';
    }
}

// Display search results
function displayResults(clips, query) {
    const resultsContainer = document.getElementById('resultsContainer');
    
    if (!clips || clips.length === 0) {
        resultsContainer.innerHTML = `
            <div class="no-results">
                <h3>No results found</h3>
                <p>Try a different search query or process a playlist first.</p>
            </div>
        `;
        return;
    }
    
    resultsContainer.innerHTML = clips.map((clip, index) => `
        <div class="result-card" onclick="openVideoModal(${index})" data-clip-index="${index}">
            <h3>${clip.video_title}</h3>
            <div class="video-meta">
                Video ID: ${clip.video_id}
            </div>
            <div class="clip-info">
                <div class="clip-time">
                    Clip: ${formatTime(clip.clip_start)} - ${formatTime(clip.clip_end)}
                </div>
                <div class="clip-text">
                    ${clip.transcript.substring(0, 200)}${clip.transcript.length > 200 ? '...' : ''}
                </div>
                <div class="relevance-score">
                    Relevance: ${(clip.relevance_score * 100).toFixed(1)}%
                </div>
            </div>
        </div>
    `).join('');
    
    // Store clips data
    window.searchResults = clips;
}

// Format time in seconds to MM:SS format
function formatTime(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
}

// Open video modal
function openVideoModal(index) {
    const clip = window.searchResults[index];
    if (!clip) return;
    
    currentVideoData = clip;
    const modal = document.getElementById('videoModal');
    const videoTitle = document.getElementById('videoTitle');
    const clipTranscript = document.getElementById('clipTranscript');
    const clipStartTime = document.getElementById('clipStartTime');
    const clipEndTime = document.getElementById('clipEndTime');
    const clipMarker = document.getElementById('clipMarker');
    const videoPlayerContainer = document.getElementById('videoPlayerContainer');
    
    // Set video info
    videoTitle.textContent = clip.video_title;
    clipTranscript.textContent = clip.transcript;
    clipStartTime.textContent = formatTime(clip.clip_start);
    clipEndTime.textContent = formatTime(clip.clip_end);
    
    // Extract video ID from URL
    const videoId = extractVideoId(clip.video_url);
    
    if (!videoId) {
        alert('Invalid video URL');
        return;
    }
    
    // Create YouTube player container
    videoPlayerContainer.innerHTML = `
        <div id="youtube-player"></div>
    `;
    
    // Load YouTube API and initialize player
    loadYouTubeAPI().then(() => {
        initializeYouTubePlayer(videoId, clip);
    }).catch((error) => {
        console.error('Error loading YouTube API:', error);
        alert('Failed to load YouTube player. Please refresh the page.');
    });
    
    // Show modal
    modal.style.display = 'block';
    
    // Update timeline marker
    updateTimelineMarker(clip);
}

// Extract video ID from YouTube URL
function extractVideoId(url) {
    const regExp = /^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|&v=)([^#&?]*).*/;
    const match = url.match(regExp);
    return (match && match[2].length === 11) ? match[2] : null;
}

// Initialize YouTube player
function initializeYouTubePlayer(videoId, clip) {
    if (youtubePlayer) {
        youtubePlayer.destroy();
    }
    
    youtubePlayer = new YT.Player('youtube-player', {
        height: '100%',
        width: '100%',
        videoId: videoId,
        playerVars: {
            'autoplay': 0,
            'controls': 1,
            'rel': 0,
            'modestbranding': 1,
            'enablejsapi': 1,
            'origin': window.location.origin
        },
        events: {
            'onReady': function(event) {
                // Player is ready
                console.log('Player ready');
                // Update timeline marker after video is ready
                updateTimelineMarker(clip);
            },
            'onStateChange': function(event) {
                // Monitor playback to stop at clip end
                if (event.data === YT.PlayerState.PLAYING && clip) {
                    const checkTime = setInterval(() => {
                        try {
                            const currentTime = youtubePlayer.getCurrentTime();
                            if (currentTime >= clip.clip_end) {
                                youtubePlayer.pauseVideo();
                                clearInterval(checkTime);
                            }
                        } catch (e) {
                            clearInterval(checkTime);
                        }
                    }, 500);
                }
            }
        }
    });
}

// Update timeline marker
function updateTimelineMarker(clip) {
    const clipMarker = document.getElementById('clipMarker');
    // Wait for video to load to get duration
    if (youtubePlayer && youtubePlayer.getDuration) {
        setTimeout(() => {
            try {
                const duration = youtubePlayer.getDuration();
                if (duration > 0) {
                    const clipStartPercent = (clip.clip_start / duration) * 100;
                    const clipEndPercent = (clip.clip_end / duration) * 100;
                    const clipWidth = clipEndPercent - clipStartPercent;
                    
                    clipMarker.style.left = `${clipStartPercent}%`;
                    clipMarker.style.width = `${clipWidth}%`;
                }
            } catch (e) {
                console.log('Could not get video duration:', e);
                // Fallback: show approximate marker
                clipMarker.style.width = '10%';
                clipMarker.style.left = '5%';
            }
        }, 1000);
    } else {
        // Fallback: show approximate marker
        clipMarker.style.width = '10%';
        clipMarker.style.left = '5%';
    }
}

// Jump to clip
function jumpToClip() {
    if (!youtubePlayer || !currentVideoData) return;
    
    const startTime = currentVideoData.clip_start;
    youtubePlayer.seekTo(startTime, true);
    youtubePlayer.playVideo();
    
    // Stop at end of clip (approximate)
    setTimeout(() => {
        if (youtubePlayer && youtubePlayer.getCurrentTime) {
            const checkTime = setInterval(() => {
                const currentTime = youtubePlayer.getCurrentTime();
                if (currentTime >= currentVideoData.clip_end) {
                    youtubePlayer.pauseVideo();
                    clearInterval(checkTime);
                }
            }, 100);
        }
    }, 100);
}

// Close video modal
function closeVideoModal() {
    const modal = document.getElementById('videoModal');
    modal.style.display = 'none';
    
    if (youtubePlayer) {
        youtubePlayer.stopVideo();
    }
    
    currentVideoData = null;
}

// Process playlist
async function processPlaylist() {
    const playlistUrl = document.getElementById('playlistInput').value.trim();
    
    if (!playlistUrl) {
        alert('Please enter a playlist URL');
        return;
    }
    
    const processButton = document.getElementById('processButton');
    const playlistLoading = document.getElementById('playlistLoading');
    const resultsContainer = document.getElementById('resultsContainer');
    
    // Show loading
    processButton.disabled = true;
    playlistLoading.style.display = 'flex';
    resultsContainer.innerHTML = '<div class="no-results"><p>Processing playlist... This may take several minutes. Please keep this window open.</p><p>Check the backend server terminal for progress updates.</p></div>';
    
    try {
        console.log('Sending request to process playlist:', playlistUrl);
        const response = await fetch(`${API_BASE_URL}/api/process-playlist`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                playlist_url: playlistUrl
            })
        });
        
        const responseData = await response.json();
        
        if (!response.ok) {
            // Handle error response
            const errorMessage = responseData.detail || responseData.message || 'Failed to process playlist';
            console.error('Error response:', responseData);
            
            // Display detailed error message
            resultsContainer.innerHTML = `
                <div class="no-results">
                    <h3>❌ Error Processing Playlist</h3>
                    <p style="white-space: pre-wrap; text-align: left; background: #ffe6e6; padding: 15px; border-radius: 5px; margin: 10px 0;">${errorMessage}</p>
                    <h4>Common Solutions:</h4>
                    <ul style="text-align: left; display: inline-block;">
                        <li>Make sure the playlist is <strong>public</strong> or <strong>unlisted</strong></li>
                        <li>Ensure videos have <strong>automatic captions</strong> or subtitles enabled</li>
                        <li>Check your <strong>internet connection</strong></li>
                        <li>Try updating yt-dlp: <code>pip install --upgrade yt-dlp</code></li>
                        <li>Check the backend server terminal for detailed error messages</li>
                    </ul>
                </div>
            `;
            throw new Error(errorMessage);
        }
        
        // Success
        console.log('Success response:', responseData);
        resultsContainer.innerHTML = `
            <div class="no-results" style="background: #e6ffe6; border: 2px solid #4caf50;">
                <h3>✅ Playlist Processed Successfully!</h3>
                <p><strong>Videos processed:</strong> ${responseData.videos_processed}</p>
                <p><strong>Chunks created:</strong> ${responseData.chunks_created}</p>
                <p>You can now search for video clips using the search box above.</p>
            </div>
        `;
        
        // Show success message
        alert(`Playlist processed successfully!\n\nVideos: ${responseData.videos_processed}\nChunks: ${responseData.chunks_created}\n\nYou can now search for video clips!`);
        
    } catch (error) {
        console.error('Error processing playlist:', error);
        
        // Check if it's a network error
        if (error.name === 'TypeError' && error.message.includes('fetch')) {
            resultsContainer.innerHTML = `
                <div class="no-results">
                    <h3>❌ Connection Error</h3>
                    <p>Cannot connect to the backend server.</p>
                    <p><strong>Solution:</strong> Make sure the backend server is running on ${API_BASE_URL}</p>
                    <p>Start it with: <code>python run_server.py</code></p>
                </div>
            `;
        } else {
            // Error already displayed in the try block, but show alert too
            if (!error.message.includes('Failed to process')) {
                alert(`Error: ${error.message}\n\nCheck the browser console (F12) and backend server logs for more details.`);
            }
        }
    } finally {
        processButton.disabled = false;
        playlistLoading.style.display = 'none';
    }
}

// Allow Enter key to trigger search
document.getElementById('searchInput').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        performSearch();
    }
});

document.getElementById('playlistInput').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        processPlaylist();
    }
});

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('videoModal');
    if (event.target == modal) {
        closeVideoModal();
    }
}

// Load YouTube API on page load
loadYouTubeAPI();

