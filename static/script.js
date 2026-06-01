// ── State ──────────────────────────────────────────
let isBuilding = false;
let liveImageCount = 0;
let currentJobId = null;

// ── Init ───────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    loadDatasets();
    setupSourceChips();
    setupSlider();
    setupKeyboardShortcuts();
});

// ── Slider ─────────────────────────────────────────
function setupSlider() {
    const slider = document.getElementById('limit-slider');
    const display = document.getElementById('limit-value');
    slider.addEventListener('input', () => {
        display.textContent = slider.value;
    });
}

// ── Source Chips ────────────────────────────────────
function setupSourceChips() {
    document.querySelectorAll('.source-chip').forEach(chip => {
        chip.addEventListener('click', (e) => {
            e.preventDefault();
            const checkbox = chip.querySelector('input[type="checkbox"]');
            checkbox.checked = !checkbox.checked;
            chip.classList.toggle('active', checkbox.checked);
        });
    });
}

// ── Keyboard Shortcuts ─────────────────────────────
function setupKeyboardShortcuts() {
    document.getElementById('topic-input').addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !isBuilding) {
            startBuild();
        }
    });
    
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') closeLightbox();
    });
}

// ── Build Pipeline ─────────────────────────────────
async function startBuild() {
    const topic = document.getElementById('topic-input').value.trim();
    if (!topic) {
        shakeElement(document.getElementById('topic-input'));
        return;
    }
    
    if (isBuilding) return;
    isBuilding = true;
    
    const limit = parseInt(document.getElementById('limit-slider').value);
    const sources = getSelectedSources();
    const outputDir = document.getElementById('output-dir').value.trim();
    
    if (sources.length === 0) {
        shakeElement(document.getElementById('source-row'));
        isBuilding = false;
        return;
    }
    
    // UI: Switch to loading state
    const btn = document.getElementById('build-btn');
    btn.classList.add('loading');
    btn.disabled = true;
    
    // Show log, gallery, and stop sections
    const logSection = document.getElementById('log-section');
    const gallerySection = document.getElementById('gallery-section');
    const stopSection = document.getElementById('stop-section');
    logSection.classList.add('visible');
    gallerySection.classList.add('visible');
    stopSection.classList.add('visible');
    
    // Populate stop controls
    populateStopControls(sources, topic);
    
    // Clear previous logs/gallery
    document.getElementById('log-terminal').innerHTML = '';
    document.getElementById('gallery-grid').innerHTML = '';
    liveImageCount = 0;
    document.getElementById('gallery-count').textContent = '0';
    
    // Scroll to log
    logSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    
    try {
        // Start the build job
        const resp = await fetch('/api/build', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ topic, limit, sources, outputDir })
        });
        const data = await resp.json();
        
        if (data.error) {
            addLogLine(data.error, 'error');
            resetBuildButton();
            return;
        }
        
        currentJobId = data.job_id;
        
        // Connect to SSE stream
        const eventSource = new EventSource(`/api/stream/${data.job_id}`);
        
        eventSource.onmessage = (event) => {
            const msg = JSON.parse(event.data);
            
            switch (msg.type) {
                case 'image':
                    addGalleryImage(msg.url, msg.source, msg.filename);
                    break;
                case 'complete':
                    eventSource.close();
                    addLogLine(msg.message, 'done');
                    resetBuildButton();
                    loadDatasets();
                    break;
                case 'keepalive':
                    break;
                default:
                    if (msg.message === '---') {
                        addLogLine('─────────────────────────', 'separator');
                    } else {
                        addLogLine(msg.message, msg.type);
                    }
            }
        };
        
        eventSource.onerror = () => {
            eventSource.close();
            addLogLine('Connection lost.', 'error');
            resetBuildButton();
            loadDatasets();
        };
        
    } catch (err) {
        addLogLine(`Error: ${err.message}`, 'error');
        resetBuildButton();
    }
}

function getSelectedSources() {
    const sources = [];
    document.querySelectorAll('.source-chip').forEach(chip => {
        if (chip.classList.contains('active')) {
            sources.push(chip.dataset.source);
        }
    });
    return sources;
}

function resetBuildButton() {
    isBuilding = false;
    currentJobId = null;
    const btn = document.getElementById('build-btn');
    btn.classList.remove('loading');
    btn.disabled = false;
    
    // Hide stop section
    document.getElementById('stop-section').classList.remove('visible');
}

// ── Stop Controls ──────────────────────────────────
function populateStopControls(sources, topic) {
    // Source stop buttons
    const sourceContainer = document.getElementById('stop-sources');
    sourceContainer.innerHTML = '<span class="stop-label">Stop by source:</span>';
    sources.forEach(src => {
        const btn = document.createElement('button');
        btn.className = 'btn-stop btn-stop--source';
        btn.textContent = `⏹ ${src.charAt(0).toUpperCase() + src.slice(1)}`;
        btn.onclick = () => stopSource(src, btn);
        sourceContainer.appendChild(btn);
    });
    
    // Topic stop buttons (from comma-separated input)
    const topicContainer = document.getElementById('stop-topics');
    const subTopics = topic.split(',').map(t => t.trim()).filter(t => t);
    
    if (subTopics.length > 1) {
        topicContainer.innerHTML = '<span class="stop-label">Stop by category:</span>';
        subTopics.forEach(sub => {
            const btn = document.createElement('button');
            btn.className = 'btn-stop btn-stop--topic';
            btn.textContent = `⏹ ${sub}`;
            btn.onclick = () => stopTopic(sub, btn);
            topicContainer.appendChild(btn);
        });
        topicContainer.style.display = 'flex';
    } else {
        topicContainer.innerHTML = '';
        topicContainer.style.display = 'none';
    }
}

async function stopAll() {
    if (!currentJobId) return;
    try {
        await fetch(`/api/stop/${currentJobId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ stop_type: 'all' })
        });
        addLogLine('⏹ Stopping all sources...', 'warning');
        document.getElementById('stop-all-btn').disabled = true;
        document.getElementById('stop-all-btn').classList.add('stopped');
    } catch (err) {
        console.error('Failed to stop:', err);
    }
}

async function stopSource(source, btnEl) {
    if (!currentJobId) return;
    try {
        await fetch(`/api/stop/${currentJobId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ stop_type: 'source', target: source })
        });
        addLogLine(`⏹ Stopping ${source}...`, 'warning');
        btnEl.disabled = true;
        btnEl.classList.add('stopped');
    } catch (err) {
        console.error('Failed to stop source:', err);
    }
}

async function stopTopic(topic, btnEl) {
    if (!currentJobId) return;
    try {
        await fetch(`/api/stop/${currentJobId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ stop_type: 'topic', target: topic })
        });
        addLogLine(`⏹ Stopping category "${topic}"...`, 'warning');
        btnEl.disabled = true;
        btnEl.classList.add('stopped');
    } catch (err) {
        console.error('Failed to stop topic:', err);
    }
}

// ── Log Terminal ───────────────────────────────────
function addLogLine(text, type = 'info') {
    const terminal = document.getElementById('log-terminal');
    const line = document.createElement('div');
    line.className = `log-line ${type}`;
    line.textContent = text;
    terminal.appendChild(line);
    terminal.scrollTop = terminal.scrollHeight;
}

// ── Live Gallery ───────────────────────────────────
function addGalleryImage(url, source, filename) {
    liveImageCount++;
    document.getElementById('gallery-count').textContent = liveImageCount;
    
    const grid = document.getElementById('gallery-grid');
    const item = document.createElement('div');
    item.className = 'gallery-item';
    item.innerHTML = `
        <img src="${url}" alt="${filename}" loading="lazy" onclick="openLightbox('${url}')">
        <div class="source-badge">${source}</div>
    `;
    grid.appendChild(item);
}

// ── Load Existing Datasets ─────────────────────────
async function loadDatasets() {
    try {
        const resp = await fetch('/api/datasets');
        const datasets = await resp.json();
        const list = document.getElementById('dataset-list');
        const emptyState = document.getElementById('empty-state');
        
        if (datasets.length === 0) {
            list.innerHTML = '';
            list.appendChild(emptyState);
            emptyState.style.display = 'block';
            return;
        }
        
        list.innerHTML = '';
        
        datasets.forEach(ds => {
            const card = document.createElement('div');
            card.className = 'dataset-card';
            
            const previewImgs = ds.images.slice(0, 5).map(
                url => `<img src="${url}" alt="preview" loading="lazy">`
            ).join('');
            
            card.innerHTML = `
                <div class="dataset-card__header">
                    <div class="dataset-card__name">${ds.display_name}</div>
                    <div class="dataset-card__count"><span>${ds.count}</span> images</div>
                </div>
                <div class="dataset-card__preview">${previewImgs}</div>
                <button class="dataset-card__delete" onclick="deleteDataset(event, '${ds.label}')" title="Delete dataset">🗑</button>
            `;
            
            card.addEventListener('click', (e) => {
                if (e.target.closest('.dataset-card__delete')) return;
                viewDataset(ds);
            });
            
            list.appendChild(card);
        });
        
    } catch (err) {
        console.error('Failed to load datasets:', err);
    }
}

// ── View Dataset ───────────────────────────────────
function viewDataset(ds) {
    const gallerySection = document.getElementById('gallery-section');
    gallerySection.classList.add('visible');
    
    const grid = document.getElementById('gallery-grid');
    grid.innerHTML = '';
    
    liveImageCount = ds.count;
    document.getElementById('gallery-count').textContent = ds.count;
    
    ds.images.forEach(url => {
        let source = 'dataset';
        if (url.includes('unsplash')) source = 'unsplash';
        else if (url.includes('pexels')) source = 'pexels';
        else if (url.includes('pixabay')) source = 'pixabay';
        else if (url.includes('pinterest')) source = 'pinterest';
        
        const item = document.createElement('div');
        item.className = 'gallery-item';
        item.innerHTML = `
            <img src="${url}" alt="Dataset image" loading="lazy" onclick="openLightbox('${url}')">
        `;
        grid.appendChild(item);
    });
    
    gallerySection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// ── Delete Dataset ─────────────────────────────────
async function deleteDataset(event, label) {
    event.stopPropagation();
    if (!confirm(`Delete the "${label.replace(/_/g, ' ')}" dataset? This cannot be undone.`)) return;
    
    try {
        await fetch(`/api/datasets/${label}`, { method: 'DELETE' });
        loadDatasets();
    } catch (err) {
        console.error('Failed to delete:', err);
    }
}

// ── Lightbox ───────────────────────────────────────
function openLightbox(url) {
    const lightbox = document.getElementById('lightbox');
    document.getElementById('lightbox-img').src = url;
    lightbox.classList.add('active');
}

function closeLightbox() {
    document.getElementById('lightbox').classList.remove('active');
}

// ── Helpers ────────────────────────────────────────
function shakeElement(el) {
    el.style.animation = 'none';
    el.offsetHeight; // trigger reflow
    el.style.animation = 'shake 0.4s ease';
    setTimeout(() => el.style.animation = '', 400);
}

// Add shake animation dynamically
const style = document.createElement('style');
style.textContent = `
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        20% { transform: translateX(-6px); }
        40% { transform: translateX(6px); }
        60% { transform: translateX(-4px); }
        80% { transform: translateX(4px); }
    }
`;
document.head.appendChild(style);
