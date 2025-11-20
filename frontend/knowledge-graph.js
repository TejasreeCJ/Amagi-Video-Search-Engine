// Knowledge Graph JavaScript
const API_BASE_URL = 'http://localhost:8000';

let network = null;
let graphData = null;
let currentVideoId = null;
let physicsEnabled = true;

// Initialize YouTube Player API
let player = null;
let tag = document.createElement('script');
tag.src = "https://www.youtube.com/iframe_api";
let firstScriptTag = document.getElementsByTagName('script')[0];
firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);

// YouTube API ready callback
function onYouTubeIframeAPIReady() {
    console.log('YouTube IFrame API is ready');
}

// Generate knowledge graph from video URL
async function generateGraph() {
    const videoUrl = document.getElementById('videoUrlInput').value.trim();
    const minDuration = parseFloat(document.getElementById('minDurationInput').value) || 30;

    if (!videoUrl) {
        alert('Please enter a YouTube video URL');
        return;
    }

    // Show loading
    document.getElementById('loadingIndicator').style.display = 'block';
    document.getElementById('generateBtn').disabled = true;
    document.getElementById('videoInfo').style.display = 'none';

    try {
        const response = await fetch(`${API_BASE_URL}/api/generate-knowledge-graph`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                video_url: videoUrl,
                min_clip_duration: minDuration
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to generate knowledge graph');
        }

        graphData = await response.json();
        console.log('Graph data received:', graphData);

        // Update video info
        updateVideoInfo(graphData.video_info);

        // Visualize the graph
        visualizeGraph(graphData);

    } catch (error) {
        console.error('Error generating graph:', error);
        alert(`Error: ${error.message}`);
    } finally {
        document.getElementById('loadingIndicator').style.display = 'none';
        document.getElementById('generateBtn').disabled = false;
    }
}

// Update video information panel
function updateVideoInfo(videoInfo) {
    currentVideoId = videoInfo.video_id;
    
    document.getElementById('videoTitle').textContent = videoInfo.title;
    document.getElementById('thumbnail').src = videoInfo.thumbnail;
    document.getElementById('infoTitle').textContent = videoInfo.title;
    document.getElementById('infoDuration').textContent = formatDuration(videoInfo.duration);
    document.getElementById('infoClips').textContent = graphData.nodes.length;
    document.getElementById('videoInfo').style.display = 'block';
}

// Visualize the knowledge graph using Vis.js
function visualizeGraph(data) {
    const container = document.getElementById('graphNetwork');

    // Prepare nodes with custom styling
    const nodes = new vis.DataSet(
        data.nodes.map(node => {
            // Determine color based on level
            let nodeColor;
            if (node.level === 0) {
                // Introduction - Red
                nodeColor = { background: '#FF6B6B', border: '#C92A2A' };
            } else if (node.level === 1) {
                // Main content - Teal
                nodeColor = { background: '#4ECDC4', border: '#087F5B' };
            } else {
                // Conclusion - Light Teal
                nodeColor = { background: '#95E1D3', border: '#0B7285' };
            }
            
            return {
                id: node.id,
                label: node.label,
                title: createNodeTooltip(node),
                group: node.level,
                level: node.level,
                color: nodeColor,
                font: {
                    size: 14,
                    color: '#ffffff',
                    face: 'Arial',
                    bold: { color: '#ffffff' }
                },
                data: node
            };
        })
    );

    // Prepare edges with custom styling
    const edges = new vis.DataSet(
        data.edges.map(edge => ({
            from: edge.from,
            to: edge.to,
            label: edge.label,
            arrows: {
                to: {
                    enabled: true,
                    scaleFactor: 0.5
                }
            },
            color: {
                color: edge.type === 'sequential' ? '#4CAF50' : '#2196F3',
                opacity: edge.strength || 0.8
            },
            width: edge.type === 'sequential' ? 2 : 1,
            dashes: edge.type !== 'sequential',
            smooth: {
                type: 'cubicBezier',
                roundness: 0.4
            },
            data: edge
        }))
    );

    // Network options
    const options = {
        nodes: {
            shape: 'box',
            margin: 10,
            widthConstraint: {
                maximum: 200
            },
            borderWidth: 2,
            borderWidthSelected: 4,
            shadow: true
        },
        edges: {
            smooth: true,
            font: {
                size: 10,
                align: 'middle',
                color: '#666'
            }
        },
        groups: {
            0: { color: { background: '#FF6B6B', border: '#C92A2A' } }, // Introduction
            1: { color: { background: '#4ECDC4', border: '#087F5B' } }, // Main content
            2: { color: { background: '#95E1D3', border: '#0B7285' } }  // Conclusion
        },
        layout: {
            hierarchical: {
                enabled: true,
                direction: 'LR', // Left to Right
                sortMethod: 'directed',
                levelSeparation: 200,
                nodeSpacing: 150,
                treeSpacing: 200
            }
        },
        physics: {
            enabled: true,
            hierarchicalRepulsion: {
                centralGravity: 0.0,
                springLength: 150,
                springConstant: 0.01,
                nodeDistance: 200,
                damping: 0.09
            },
            solver: 'hierarchicalRepulsion'
        },
        interaction: {
            hover: true,
            navigationButtons: true,
            keyboard: true,
            zoomView: true,
            dragView: true
        }
    };

    // Create network
    network = new vis.Network(container, { nodes, edges }, options);

    // Event listeners
    network.on('click', function(params) {
        if (params.nodes.length > 0) {
            const nodeId = params.nodes[0];
            const nodeData = nodes.get(nodeId).data;
            showClipDetails(nodeData);
        }
    });

    network.on('doubleClick', function(params) {
        if (params.nodes.length > 0) {
            const nodeId = params.nodes[0];
            const nodeData = nodes.get(nodeId).data;
            openVideoModal(nodeData);
        }
    });

    // Stabilization complete
    network.on('stabilizationIterationsDone', function() {
        network.setOptions({ physics: false });
        physicsEnabled = false;
        updatePhysicsButton();
    });
}

// Create tooltip for node
function createNodeTooltip(node) {
    return `
        <div style="padding: 10px;">
            <strong>${node.label}</strong><br>
            <em>Time: ${formatTime(node.start_time)} - ${formatTime(node.end_time)}</em><br>
            Duration: ${Math.round(node.duration)}s<br>
            Topics: ${node.topics.join(', ')}
        </div>
    `;
}

// Show clip details in side panel
function showClipDetails(node) {
    document.getElementById('clipTitle').textContent = node.label;
    document.getElementById('clipTime').textContent = `${formatTime(node.start_time)} - ${formatTime(node.end_time)}`;
    document.getElementById('clipDuration').textContent = `Duration: ${Math.round(node.duration)}s`;
    
    // Display topics
    const topicsContainer = document.getElementById('clipTopics');
    topicsContainer.innerHTML = node.topics.map(topic => 
        `<span class="topic-tag">${topic}</span>`
    ).join('');
    
    document.getElementById('clipText').textContent = node.text;
    document.getElementById('clipDetails').style.display = 'block';

    // Store current clip for playback
    window.currentClip = node;
}

// Close clip details
function closeClipDetails() {
    document.getElementById('clipDetails').style.display = 'none';
}

// Play clip in video modal
function playClip() {
    if (window.currentClip) {
        openVideoModal(window.currentClip);
    }
}

// Open video modal with clip
function openVideoModal(clipData) {
    if (!currentVideoId) {
        alert('Video ID not available');
        return;
    }

    // Check if we're running on file:// protocol
    if (window.location.protocol === 'file:') {
        // Open in YouTube directly instead of embedded player
        const startTime = Math.floor(clipData.start_time);
        const youtubeUrl = `https://www.youtube.com/watch?v=${currentVideoId}&t=${startTime}s`;
        
        const confirmOpen = confirm(
            `YouTube player requires a web server to work.\n\n` +
            `Would you like to open this clip directly on YouTube?\n\n` +
            `Clip: ${clipData.label}\n` +
            `Time: ${formatTime(clipData.start_time)} - ${formatTime(clipData.end_time)}`
        );
        
        if (confirmOpen) {
            window.open(youtubeUrl, '_blank');
        }
        return;
    }

    document.getElementById('videoModal').style.display = 'flex';

    // Create YouTube player if not exists
    if (!player) {
        player = new YT.Player('videoPlayer', {
            height: '500',
            width: '100%',
            videoId: currentVideoId,
            playerVars: {
                start: Math.floor(clipData.start_time),
                end: Math.floor(clipData.end_time),
                autoplay: 1
            },
            events: {
                onReady: onPlayerReady
            }
        });
    } else {
        player.loadVideoById({
            videoId: currentVideoId,
            startSeconds: Math.floor(clipData.start_time),
            endSeconds: Math.floor(clipData.end_time)
        });
    }
}

// Player ready callback
function onPlayerReady(event) {
    event.target.playVideo();
}

// Close video modal
function closeVideoModal() {
    document.getElementById('videoModal').style.display = 'none';
    if (player) {
        player.stopVideo();
    }
}

// Toggle physics simulation
function togglePhysics() {
    if (!network) return;
    
    physicsEnabled = !physicsEnabled;
    network.setOptions({ physics: { enabled: physicsEnabled } });
    updatePhysicsButton();
}

// Update physics button text
function updatePhysicsButton() {
    const btn = document.getElementById('physicsBtn');
    btn.textContent = physicsEnabled ? 'Disable Physics' : 'Enable Physics';
}

// Reset view to fit all nodes
function resetView() {
    if (network) {
        network.fit({
            animation: {
                duration: 1000,
                easingFunction: 'easeInOutQuad'
            }
        });
    }
}

// Export graph as image
function exportGraph() {
    if (!network) {
        alert('No graph to export');
        return;
    }

    const canvas = document.querySelector('#graphNetwork canvas');
    if (canvas) {
        const link = document.createElement('a');
        link.download = 'knowledge-graph.png';
        link.href = canvas.toDataURL();
        link.click();
    }
}

// Go back to main search page
function goBack() {
    window.location.href = 'index.html';
}

// Format duration in seconds to readable format
function formatDuration(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);
    
    if (hours > 0) {
        return `${hours}h ${minutes}m ${secs}s`;
    } else if (minutes > 0) {
        return `${minutes}m ${secs}s`;
    } else {
        return `${secs}s`;
    }
}

// Format time in seconds to MM:SS
function formatTime(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
}

// Check if URL has video parameter
window.addEventListener('DOMContentLoaded', function() {
    // Check if running on file:// protocol
    if (window.location.protocol === 'file:') {
        const notice = document.getElementById('serverNotice');
        if (notice) {
            notice.style.display = 'flex';
        }
    }
    
    const urlParams = new URLSearchParams(window.location.search);
    const videoUrl = urlParams.get('video');
    
    if (videoUrl) {
        document.getElementById('videoUrlInput').value = decodeURIComponent(videoUrl);
        // Auto-generate after a short delay
        setTimeout(() => generateGraph(), 500);
    }
});

// Dismiss server notice
function dismissNotice() {
    const notice = document.getElementById('serverNotice');
    if (notice) {
        notice.style.display = 'none';
    }
}
