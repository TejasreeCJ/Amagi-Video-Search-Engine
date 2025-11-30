// Global variables
const API_BASE_URL = 'http://localhost:8000';
let network = null;
let graphData = { nodes: [], edges: [] };
let currentLayout = 'hierarchical'; // Default to hierarchical for clear learning path
let selectedNodeId = null;
let selectedNodeData = null;
let ytPlayer = null;
let is3DMode = false;
let scene, camera, renderer, controls, graph3D;

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('Knowledge Graph page loaded');
    loadGraphStats();
    loadKnowledgeGraph();
    updateLearningDirection(); // Show direction indicator on load

    // Setup slider value displays
    const similaritySlider = document.getElementById('similarityThreshold');
    const similarityValue = document.getElementById('similarityValue');
    const maxConnectionsSlider = document.getElementById('maxConnections');
    const maxConnectionsValue = document.getElementById('maxConnectionsValue');

    if (similaritySlider && similarityValue) {
        similaritySlider.addEventListener('input', (e) => {
            similarityValue.textContent = e.target.value;
        });
    }

    if (maxConnectionsSlider && maxConnectionsValue) {
        maxConnectionsSlider.addEventListener('input', (e) => {
            maxConnectionsValue.textContent = e.target.value;
        });
    }
});

// Toggle advanced settings panel
function toggleAdvancedSettings() {
    const panel = document.getElementById('advancedSettings');
    if (panel.style.display === 'none') {
        panel.style.display = 'block';
    } else {
        panel.style.display = 'none';
    }
}

// Build Knowledge Graph (creates relationships)
async function buildKnowledgeGraph() {
    const buildBtn = document.getElementById('buildGraphBtn');
    const loadingIndicator = document.getElementById('loadingIndicator');

    // Get user-specified parameters
    const similarityThreshold = parseFloat(document.getElementById('similarityThreshold').value) || 0.75;
    const maxConnections = parseInt(document.getElementById('maxConnections').value) || 3;

    buildBtn.disabled = true;
    buildBtn.textContent = '🔨 Building...';
    loadingIndicator.style.display = 'flex';

    try {
        const response = await fetch(
            `${API_BASE_URL}/api/knowledge-graph/build?similarity_threshold=${similarityThreshold}&max_connections=${maxConnections}`,
            {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            }
        );

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to build knowledge graph');
        }

        const data = await response.json();
        console.log('Knowledge graph built:', data);

        alert('Knowledge graph built successfully!\n\n' +
              `Total Chapters: ${data.statistics.total_chapters}\n` +
              `Total Videos: ${data.statistics.total_videos}\n` +
              `Relationships: ${JSON.stringify(data.statistics.relationships, null, 2)}`);

        // Reload the graph
        await loadKnowledgeGraph();
        await loadGraphStats();

    } catch (error) {
        console.error('Error building knowledge graph:', error);
        alert('Error building knowledge graph: ' + error.message);
    } finally {
        buildBtn.disabled = false;
        buildBtn.textContent = '🔨 Build Knowledge Graph';
        loadingIndicator.style.display = 'none';
    }
}

// Load Knowledge Graph from API
async function loadKnowledgeGraph(videoId = null) {
    const loadingIndicator = document.getElementById('loadingIndicator');
    const loadingText = loadingIndicator.querySelector('span');
    loadingIndicator.style.display = 'flex';
    loadingText.textContent = 'Loading knowledge graph...';

    try {
        const url = videoId
            ? `${API_BASE_URL}/api/knowledge-graph?video_id=${videoId}&limit=1000&auto_build=true`
            : `${API_BASE_URL}/api/knowledge-graph?limit=1000&auto_build=true`;

        const response = await fetch(url);

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to load knowledge graph');
        }

        const data = await response.json();
        console.log('Loaded graph data:', data);

        graphData = data;

        // Update stats
        document.getElementById('totalNodes').textContent = data.stats.total_nodes;
        document.getElementById('totalEdges').textContent = data.stats.total_edges;

        // Render the graph
        renderGraph();

        // Show success message if graph was auto-built
        if (data.stats.total_edges > 0 && !graphData._notified) {
            graphData._notified = true;
            console.log('Knowledge graph loaded successfully!');
        }

    } catch (error) {
        console.error('Error loading knowledge graph:', error);
        alert('Error loading knowledge graph: ' + error.message + '\n\nMake sure you have:\n1. Processed at least one playlist\n2. Neo4j database is running\n3. Backend server is running');
    } finally {
        loadingIndicator.style.display = 'none';
    }
}

// Render the graph in 3D using Three.js
function render3DGraph() {
    const container = document.getElementById('graphNetwork');
    container.innerHTML = '';

    if (!window.THREE) {
        container.innerHTML = '<div class="empty-state">3D library not loaded. Please refresh the page.</div>';
        console.error('THREE.js not loaded');
        return;
    }

    if (!THREE.OrbitControls) {
        container.innerHTML = '<div class="empty-state">3D controls not loaded. Please refresh the page.</div>';
        console.error('OrbitControls not loaded');
        return;
    }

    console.log('Starting 3D graph render...');

    // Create video-to-color mapping
    const videoColors = {};
    const colorPalette = [0xe74c3c, 0x3498db, 0x2ecc71, 0xf39c12, 0x9b59b6, 0x1abc9c, 0xe67e22, 0x16a085, 0xc0392b, 0x2980b9];
    let colorIndex = 0;

    graphData.nodes.forEach(node => {
        if (node.video_id && !videoColors[node.video_id]) {
            videoColors[node.video_id] = colorPalette[colorIndex % colorPalette.length];
            colorIndex++;
        }
    });

    // Setup scene
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0xfafafa);

    // Setup camera
    const width = container.clientWidth;
    const height = container.clientHeight;
    camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 10000);
    camera.position.z = 1000;

    // Setup renderer
    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(width, height);
    container.appendChild(renderer.domElement);

    // Setup controls
    controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.rotateSpeed = 0.5;
    controls.zoomSpeed = 1.2;
    controls.panSpeed = 0.8;

    // Create graph structure
    graph3D = {
        nodes: [],
        edges: [],
        nodeObjects: {},
        edgeObjects: []
    };

    // Force-directed layout in 3D (simplified simulation)
    const positions = {};
    const velocities = {};

    // Initialize random positions
    graphData.nodes.forEach(node => {
        positions[node.id] = {
            x: (Math.random() - 0.5) * 1000,
            y: (Math.random() - 0.5) * 1000,
            z: (Math.random() - 0.5) * 1000
        };
        velocities[node.id] = { x: 0, y: 0, z: 0 };
    });

    // Simple force-directed simulation (run for a bit to spread nodes)
    for (let iteration = 0; iteration < 100; iteration++) {
        // Repulsion between all nodes
        graphData.nodes.forEach(node1 => {
            graphData.nodes.forEach(node2 => {
                if (node1.id === node2.id) return;

                const dx = positions[node1.id].x - positions[node2.id].x;
                const dy = positions[node1.id].y - positions[node2.id].y;
                const dz = positions[node1.id].z - positions[node2.id].z;
                const distance = Math.sqrt(dx*dx + dy*dy + dz*dz) || 1;

                const force = 50000 / (distance * distance);
                velocities[node1.id].x += (dx / distance) * force;
                velocities[node1.id].y += (dy / distance) * force;
                velocities[node1.id].z += (dz / distance) * force;
            });
        });

        // Attraction along edges
        graphData.edges.forEach(edge => {
            const pos1 = positions[edge.from];
            const pos2 = positions[edge.to];
            if (!pos1 || !pos2) return;

            const dx = pos2.x - pos1.x;
            const dy = pos2.y - pos1.y;
            const dz = pos2.z - pos1.z;
            const distance = Math.sqrt(dx*dx + dy*dy + dz*dz) || 1;

            const force = distance * 0.01;
            velocities[edge.from].x += (dx / distance) * force;
            velocities[edge.from].y += (dy / distance) * force;
            velocities[edge.from].z += (dz / distance) * force;
            velocities[edge.to].x -= (dx / distance) * force;
            velocities[edge.to].y -= (dy / distance) * force;
            velocities[edge.to].z -= (dz / distance) * force;
        });

        // Update positions with damping
        graphData.nodes.forEach(node => {
            positions[node.id].x += velocities[node.id].x;
            positions[node.id].y += velocities[node.id].y;
            positions[node.id].z += velocities[node.id].z;
            velocities[node.id].x *= 0.9;
            velocities[node.id].y *= 0.9;
            velocities[node.id].z *= 0.9;
        });
    }

    // Create node spheres
    graphData.nodes.forEach(node => {
        const geometry = new THREE.SphereGeometry(15, 16, 16);
        const material = new THREE.MeshPhongMaterial({
            color: videoColors[node.video_id] || 0x95a5a6,
            shininess: 30
        });
        const sphere = new THREE.Mesh(geometry, material);

        const pos = positions[node.id];
        sphere.position.set(pos.x, pos.y, pos.z);
        sphere.userData = { nodeId: node.id, nodeData: node };

        scene.add(sphere);
        graph3D.nodeObjects[node.id] = sphere;

        // Add label (sprite with text)
        const canvas = document.createElement('canvas');
        const context = canvas.getContext('2d');
        canvas.width = 256;
        canvas.height = 64;
        context.fillStyle = 'rgba(255, 255, 255, 0.9)';
        context.fillRect(0, 0, canvas.width, canvas.height);
        context.font = '20px Arial';
        context.fillStyle = '#333333';
        context.textAlign = 'center';
        context.fillText(node.title.substring(0, 20), 128, 35);

        const texture = new THREE.CanvasTexture(canvas);
        const spriteMaterial = new THREE.SpriteMaterial({ map: texture });
        const sprite = new THREE.Sprite(spriteMaterial);
        sprite.scale.set(100, 25, 1);
        sprite.position.set(pos.x, pos.y + 30, pos.z);
        scene.add(sprite);
    });

    // Create edges as lines
    graphData.edges.forEach(edge => {
        const pos1 = positions[edge.from];
        const pos2 = positions[edge.to];
        if (!pos1 || !pos2) return;

        const geometry = new THREE.BufferGeometry();
        const positions = new Float32Array([
            pos1.x, pos1.y, pos1.z,
            pos2.x, pos2.y, pos2.z
        ]);
        geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));

        const colorMap = {
            'NEXT_TOPIC': 0x4CAF50,
            'SIMILAR_TO': 0x2196F3,
            'RELATES_TO': 0xFF9800,
            'PREREQUISITE_OF': 0x9C27B0
        };
        const edgeColor = colorMap[edge.type] || 0x999999;

        const material = new THREE.LineBasicMaterial({
            color: edgeColor,
            opacity: 0.6,
            transparent: true
        });

        const line = new THREE.Line(geometry, material);
        scene.add(line);
        graph3D.edgeObjects.push(line);
    });

    // Add lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
    scene.add(ambientLight);

    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.4);
    directionalLight.position.set(1, 1, 1);
    scene.add(directionalLight);

    // Add click detection
    const raycaster = new THREE.Raycaster();
    const mouse = new THREE.Vector2();

    renderer.domElement.addEventListener('click', (event) => {
        const rect = renderer.domElement.getBoundingClientRect();
        mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
        mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

        raycaster.setFromCamera(mouse, camera);
        const nodeObjects = Object.values(graph3D.nodeObjects);
        const intersects = raycaster.intersectObjects(nodeObjects);

        if (intersects.length > 0) {
            const nodeId = intersects[0].object.userData.nodeId;
            onNodeClick(nodeId);
        } else {
            closeInfoPanel();
        }
    });

    // Animation loop
    function animate() {
        requestAnimationFrame(animate);
        controls.update();
        renderer.render(scene, camera);
    }
    animate();

    // Handle window resize
    window.addEventListener('resize', () => {
        if (!renderer || !camera) return;
        const width = container.clientWidth;
        const height = container.clientHeight;
        camera.aspect = width / height;
        camera.updateProjectionMatrix();
        renderer.setSize(width, height);
    });

    console.log('3D graph rendered with', graphData.nodes.length, 'nodes');
}

// Render the graph using Vis.js
function renderGraph() {
    const container = document.getElementById('graphNetwork');

    if (!graphData.nodes || graphData.nodes.length === 0) {
        container.innerHTML = '<div class="empty-state">No graph data available. Please process playlists and build the knowledge graph first.</div>';
        return;
    }

    // Check if we should render in 3D
    if (currentLayout === '3d') {
        render3DGraph();
        return;
    }

    // Cleanup any existing 3D renderer
    if (renderer) {
        container.innerHTML = '';
        renderer.dispose();
        renderer = null;
        scene = null;
        camera = null;
        controls = null;
        graph3D = null;
    }

    // Create video-to-color mapping
    const videoColors = {};
    const colorPalette = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c', '#e67e22', '#16a085', '#c0392b', '#2980b9'];
    let colorIndex = 0;

    graphData.nodes.forEach(node => {
        if (node.video_id && !videoColors[node.video_id]) {
            videoColors[node.video_id] = colorPalette[colorIndex % colorPalette.length];
            colorIndex++;
        }
    });

    // Prepare nodes for Vis.js
    const visNodes = graphData.nodes.map(node => ({
        id: node.id,
        label: truncateLabel(node.label, 25),
        title: node.title, // Just show the title on hover
        shape: 'dot',
        size: 15,
        font: {
            size: 12,
            color: '#333333',
            background: 'rgba(255, 255, 255, 0.9)'
        },
        color: {
            background: videoColors[node.video_id] || '#95a5a6',
            border: '#34495e',
            highlight: {
                background: '#ffa500',
                border: '#ff6600'
            }
        },
        data: node // Store full node data
    }));

    // Group edges by node pairs to handle multiple connections
    const edgeGroups = {};
    graphData.edges.forEach(edge => {
        const key = [edge.from, edge.to].sort().join('-');
        if (!edgeGroups[key]) {
            edgeGroups[key] = [];
        }
        edgeGroups[key].push(edge);
    });

    // Prepare edges for Vis.js with curved routing for multiple edges
    const visEdges = [];
    graphData.edges.forEach((edge) => {
        const key = [edge.from, edge.to].sort().join('-');
        const groupEdges = edgeGroups[key];
        const edgeIndex = groupEdges.indexOf(edge);

        // If multiple edges between same nodes, use dynamic smooth curves
        let smoothConfig;
        if (groupEdges.length > 1) {
            // Calculate roundness based on edge position
            const maxRoundness = 0.5;
            const step = maxRoundness / (groupEdges.length - 1);
            const roundness = edgeIndex === 0 ? 0 : step * edgeIndex;

            smoothConfig = {
                type: 'curvedCW',
                roundness: roundness
            };
        } else {
            // Single edge - use gentle curve
            smoothConfig = {
                type: 'dynamic',
                roundness: 0.2
            };
        }

        visEdges.push({
            from: edge.from,
            to: edge.to,
            arrows: {
                to: {
                    enabled: true,
                    scaleFactor: 0.8
                }
            },
            color: {
                color: getEdgeColor(edge.type),
                highlight: getEdgeColor(edge.type),
                opacity: 0.7
            },
            width: getEdgeWidth(edge.similarity),
            title: `${edge.type} (similarity: ${edge.similarity.toFixed(2)})`,
            smooth: smoothConfig
        });
    });

    // Create network
    const data = {
        nodes: new vis.DataSet(visNodes),
        edges: new vis.DataSet(visEdges)
    };

    const options = getLayoutOptions(currentLayout);

    network = new vis.Network(container, data, options);

    // Event handlers
    network.on('click', function(params) {
        if (params.nodes.length > 0) {
            const nodeId = params.nodes[0];
            onNodeClick(nodeId);
        } else {
            closeInfoPanel();
        }
    });

    network.on('doubleClick', function(params) {
        if (params.nodes.length > 0) {
            const nodeId = params.nodes[0];
            const node = visNodes.find(n => n.id === nodeId);
            if (node && node.data) {
                selectedNodeData = node.data;
                playChapterVideo();
            }
        }
    });

    console.log('Graph rendered with', visNodes.length, 'nodes and', visEdges.length, 'edges');
}

// Get layout options based on selected layout
function getLayoutOptions(layout) {
    const baseOptions = {
        nodes: {
            borderWidth: 2,
            borderWidthSelected: 4
        },
        edges: {
            smooth: {
                type: 'continuous'
            }
        },
        interaction: {
            hover: true,
            tooltipDelay: 100,
            zoomView: true,
            dragView: true
        },
        physics: {
            enabled: true,
            stabilization: {
                iterations: 200
            }
        }
    };

    switch(layout) {
        case 'hierarchical':
            // TOP-TO-BOTTOM Learning Path: Foundation → Advanced
            return {
                ...baseOptions,
                layout: {
                    hierarchical: {
                        direction: 'UD', // Up to Down (Top = Prerequisites, Bottom = Advanced)
                        sortMethod: 'directed',
                        levelSeparation: 200, // Vertical spacing between levels
                        nodeSpacing: 250, // Horizontal spacing
                        treeSpacing: 300, // Space between separate trees
                        blockShifting: true,
                        edgeMinimization: true,
                        parentCentralization: true
                    }
                },
                physics: {
                    enabled: false
                }
            };

        case 'circular':
            return {
                ...baseOptions,
                layout: {
                    randomSeed: 2
                },
                physics: {
                    enabled: true,
                    barnesHut: {
                        gravitationalConstant: -8000,
                        centralGravity: 0.3,
                        springLength: 350,
                        springConstant: 0.04,
                        avoidOverlap: 0.8
                    }
                }
            };

        case 'radial':
            return {
                ...baseOptions,
                layout: {
                    hierarchical: {
                        direction: 'UD',
                        sortMethod: 'hubsize',
                        levelSeparation: 200,
                        nodeSpacing: 150
                    }
                },
                physics: {
                    enabled: false
                }
            };

        case 'cluster':
            // Group nodes by video_id for clustering
            return {
                ...baseOptions,
                layout: {
                    randomSeed: 2
                },
                physics: {
                    enabled: true,
                    barnesHut: {
                        gravitationalConstant: -5000,
                        centralGravity: 0.05,
                        springLength: 400,
                        springConstant: 0.04,
                        avoidOverlap: 0.9
                    },
                    stabilization: {
                        iterations: 300
                    }
                }
            };

        case 'timeline':
            // LEFT-TO-RIGHT Learning Timeline: Start → End
            return {
                ...baseOptions,
                layout: {
                    hierarchical: {
                        direction: 'LR', // Left to Right (natural reading direction)
                        sortMethod: 'directed',
                        levelSeparation: 300, // Horizontal spacing between stages
                        nodeSpacing: 150, // Vertical spacing
                        treeSpacing: 200,
                        blockShifting: true,
                        edgeMinimization: true
                    }
                },
                physics: {
                    enabled: false
                }
            };

        case '3d':
            // Enable 3D mode
            is3DMode = true;
            return {
                ...baseOptions,
                layout: {
                    randomSeed: 3
                },
                physics: {
                    enabled: true,
                    barnesHut: {
                        gravitationalConstant: -8000,
                        centralGravity: 0.1,
                        springLength: 500,
                        springConstant: 0.02,
                        avoidOverlap: 1.0
                    },
                    stabilization: {
                        iterations: 400
                    }
                }
            };

        case 'forceDirected':
        default:
            return {
                ...baseOptions,
                layout: {
                    randomSeed: 2
                },
                physics: {
                    enabled: true,
                    barnesHut: {
                        gravitationalConstant: -4000,
                        centralGravity: 0.1,
                        springLength: 350,
                        springConstant: 0.04,
                        avoidOverlap: 0.8
                    },
                    stabilization: {
                        iterations: 250
                    }
                }
            };
    }
}

// Node click handler
function onNodeClick(nodeId) {
    selectedNodeId = nodeId;

    // Find node data
    const node = graphData.nodes.find(n => n.id === nodeId);
    if (!node) return;

    selectedNodeData = node;

    // Update info panel
    document.getElementById('nodeTitle').textContent = node.title;
    document.getElementById('nodeDescription').textContent = node.description || 'No description available';
    document.getElementById('nodeTimeline').textContent =
        `${formatTime(node.start_time)} - ${formatTime(node.end_time)}`;

    // Show connections
    const connections = graphData.edges.filter(e => e.from === nodeId || e.to === nodeId);
    const connectedNodes = connections.map(edge => {
        const connectedNodeId = edge.from === nodeId ? edge.to : edge.from;
        const connectedNode = graphData.nodes.find(n => n.id === connectedNodeId);
        return `<div class="connection-item">
            <span class="connection-type">${edge.type}</span>
            <span class="connection-name">${connectedNode ? connectedNode.title : 'Unknown'}</span>
        </div>`;
    }).join('');

    document.getElementById('nodeConnections').innerHTML =
        connectedNodes || '<p>No connections</p>';

    // Show panel
    document.getElementById('infoPanel').style.display = 'block';

    // Highlight node in network
    network.selectNodes([nodeId]);
}

// Close info panel
function closeInfoPanel() {
    document.getElementById('infoPanel').style.display = 'none';
    selectedNodeId = null;
    if (network) {
        network.unselectAll();
    }
}

// Change graph layout
function changeLayout() {
    currentLayout = document.getElementById('layoutSelect').value;
    updateLearningDirection();
    renderGraph();
}

// Update learning direction indicator based on layout
function updateLearningDirection() {
    const directionDiv = document.getElementById('learningDirection');
    const directionText = document.getElementById('directionText');

    const directions = {
        'hierarchical': { show: true, text: '⬇️ Start from TOP → Work your way DOWN' },
        'timeline': { show: true, text: '➡️ Start from LEFT → Progress to RIGHT' },
        'radial': { show: true, text: '🎯 Start from CENTER → Explore OUTWARD' },
        'cluster': { show: true, text: '📹 Explore by Video Clusters' },
        'forceDirected': { show: false, text: '' },
        'circular': { show: false, text: '' },
        '3d': { show: true, text: '🖱️ Drag to Rotate | Scroll to Zoom' }
    };

    const direction = directions[currentLayout] || { show: false, text: '' };

    if (direction.show) {
        directionText.textContent = direction.text;
        directionDiv.style.display = 'block';
    } else {
        directionDiv.style.display = 'none';
    }
}

// Update graph scope
function updateGraphScope() {
    const scope = document.getElementById('graphScope').value;
    const videoSelect = document.getElementById('videoSelect');

    if (scope === 'video') {
        videoSelect.style.display = 'inline-block';
        loadAvailableVideos();
    } else {
        videoSelect.style.display = 'none';
        loadKnowledgeGraph();
    }
}

// Load available videos for filtering
async function loadAvailableVideos() {
    const videoSelect = document.getElementById('videoSelect');
    videoSelect.innerHTML = '<option value="">Loading...</option>';

    try {
        const response = await fetch(`${API_BASE_URL}/api/knowledge-graph/videos`);
        if (!response.ok) {
            throw new Error('Failed to load videos');
        }

        const data = await response.json();
        videoSelect.innerHTML = '<option value="">All Videos</option>';

        data.videos.forEach(video => {
            const option = document.createElement('option');
            option.value = video.id;
            option.textContent = video.title;
            videoSelect.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading videos:', error);
        videoSelect.innerHTML = '<option value="">Error loading videos</option>';
    }
}

// Load graph for specific video
function loadGraphForVideo() {
    const videoId = document.getElementById('videoSelect').value;
    if (videoId) {
        loadKnowledgeGraph(videoId);
    }
}

// Load and display graph statistics
async function loadGraphStats() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/knowledge-graph/stats`);
        if (!response.ok) return;

        const stats = await response.json();
        console.log('Graph stats:', stats);

        document.getElementById('totalNodes').textContent = stats.total_chapters || 0;
        document.getElementById('totalVideos').textContent = stats.total_videos || 0;

        // Calculate total edges
        const totalEdges = Object.values(stats.relationships || {}).reduce((sum, count) => sum + count, 0);
        document.getElementById('totalEdges').textContent = totalEdges;

    } catch (error) {
        console.error('Error loading graph stats:', error);
    }
}

// Show learning path to selected node
async function showLearningPath() {
    if (!selectedNodeId || !selectedNodeData) {
        alert('Please select a chapter node first');
        return;
    }

    try {
        // URL encode the chapter ID
        const encodedId = encodeURIComponent(selectedNodeId);
        const response = await fetch(
            `${API_BASE_URL}/api/knowledge-graph/learning-path/${encodedId}`
        );

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to get learning path');
        }

        const data = await response.json();
        console.log('Learning path:', data);

        if (!data.path || data.path.length === 0) {
            alert(`No prerequisites found for "${selectedNodeData.title}".\n\nThis might be a foundational topic that you can start learning directly!`);
            return;
        }

        if (data.path.length === 1) {
            alert(`"${selectedNodeData.title}" has no prerequisites.\n\nThis is a foundational topic - you can start here!`);
            return;
        }

        // Highlight path in the graph
        highlightPath(data.path);

        // Show path details
        const pathSummary = data.path.slice(0, -1).map((node, i) =>
            `${i + 1}. ${node.title}`
        ).join('\n');

        alert(`Learning Path to "${selectedNodeData.title}":\n\nRecommended prerequisites:\n${pathSummary}\n\n${data.path.length}. ${selectedNodeData.title} (Your Goal)`);

    } catch (error) {
        console.error('Error getting learning path:', error);
        alert('Error getting learning path:\n' + error.message + '\n\nMake sure the knowledge graph has been built with prerequisite relationships.');
    }
}

// Highlight a path in the graph
function highlightPath(pathNodes) {
    if (!network) return;

    const nodeIds = pathNodes.map(node => node.id);

    // Highlight nodes
    network.selectNodes(nodeIds);

    // Fit view to show the path
    network.fit({
        nodes: nodeIds,
        animation: {
            duration: 1000,
            easingFunction: 'easeInOutQuad'
        }
    });
}

// Play video for selected chapter
function playChapterVideo() {
    if (!selectedNodeData) {
        alert('Please select a chapter first');
        return;
    }

    if (!selectedNodeData.video_url) {
        alert('No video URL available for this chapter');
        return;
    }

    // Extract YouTube video ID from URL
    const videoUrl = selectedNodeData.video_url;
    const videoIdMatch = videoUrl.match(/[?&]v=([^&]+)/);

    if (!videoIdMatch) {
        alert('Invalid YouTube URL');
        return;
    }

    const videoId = videoIdMatch[1];

    // Open video modal
    openVideoModal(videoId, selectedNodeData);
}

// Video modal functions
function openVideoModal(videoId, chapterData) {
    const modal = document.getElementById('videoModal');
    document.getElementById('videoTitle').textContent = chapterData.video_title || 'Video';
    document.getElementById('chapterTitle').textContent = chapterData.title;
    document.getElementById('chapterDescription').textContent = chapterData.description || '';
    document.getElementById('clipStartTime').textContent = formatTime(chapterData.start_time);
    document.getElementById('clipEndTime').textContent = formatTime(chapterData.end_time);

    modal.style.display = 'flex';

    // Load YouTube IFrame API if not loaded
    if (!window.YT) {
        const tag = document.createElement('script');
        tag.src = 'https://www.youtube.com/iframe_api';
        const firstScriptTag = document.getElementsByTagName('script')[0];
        firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);

        window.onYouTubeIframeAPIReady = function() {
            initializeYouTubePlayer(videoId, chapterData);
        };
    } else {
        initializeYouTubePlayer(videoId, chapterData);
    }
}

function closeVideoModal() {
    const modal = document.getElementById('videoModal');
    modal.style.display = 'none';

    if (ytPlayer) {
        ytPlayer.destroy();
        ytPlayer = null;
    }
}

function initializeYouTubePlayer(videoId, chapterData) {
    ytPlayer = new YT.Player('videoPlayerContainer', {
        height: '480',
        width: '100%',
        videoId: videoId,
        playerVars: {
            start: Math.floor(chapterData.start_time),
            autoplay: 1
        },
        events: {
            onStateChange: function(event) {
                if (event.data === YT.PlayerState.PLAYING) {
                    const checkTime = setInterval(function() {
                        if (ytPlayer && ytPlayer.getCurrentTime) {
                            const currentTime = ytPlayer.getCurrentTime();
                            if (currentTime >= chapterData.end_time) {
                                ytPlayer.pauseVideo();
                                clearInterval(checkTime);
                            }
                        }
                    }, 1000);
                }
            }
        }
    });
}

function jumpToClip() {
    if (ytPlayer && selectedNodeData) {
        ytPlayer.seekTo(selectedNodeData.start_time, true);
        ytPlayer.playVideo();
    } else {
        alert('Please open a video first by clicking "Play Chapter"');
    }
}

// Utility Functions
function truncateLabel(text, maxLength) {
    if (!text) return '';
    return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
}

function formatTime(seconds) {
    if (!seconds && seconds !== 0) return '0:00';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
}

function getNodeColor(node) {
    // Color by group/cluster - for now use random based on ID hash
    const colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c'];
    const hash = node.id.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
    return colors[hash % colors.length];
}

function getEdgeColor(type) {
    const colorMap = {
        'NEXT_TOPIC': '#4CAF50',
        'SIMILAR_TO': '#2196F3',
        'RELATES_TO': '#FF9800',
        'PREREQUISITE_OF': '#9C27B0'
    };
    return colorMap[type] || '#999999';
}

function getEdgeWidth(similarity) {
    // Width based on similarity score (0-1)
    return Math.max(1, Math.min(5, similarity * 5));
}

// Show layout info modal
function showLayoutInfo() {
    document.getElementById('layoutInfoModal').style.display = 'flex';
}

// Close layout info modal
function closeLayoutInfo() {
    document.getElementById('layoutInfoModal').style.display = 'none';
}
