import os
import sys
import json
import uuid
import threading
import queue
import time
from io import StringIO
from flask import Flask, send_from_directory, jsonify, request, Response

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from dataset_builder.collectors.unsplash import UnsplashCollector
from dataset_builder.collectors.pexels import PexelsCollector
from dataset_builder.collectors.pixabay import PixabayCollector
from dataset_builder.collectors.pinterest import PinterestCollector
from dataset_builder.cleaner import AutomaticCleaner
from dataset_builder.metadata import MetadataGenerator

app = Flask(__name__, static_folder='static')

BASE_DATASET_DIR = os.path.join(os.path.dirname(__file__), 'dataset', 'important')

# Store active jobs: job_id -> { status, log_queue, topic, limit, stop_flags }
active_jobs = {}


def run_pipeline(job_id, topic, limit, sources, output_dir=None):
    """Run the dataset pipeline in a background thread, pushing logs to a queue."""
    import concurrent.futures
    
    job = active_jobs[job_id]
    log_q = job['log_queue']
    stop_flags = job['stop_flags']
    
    label = topic.lower().replace(' ', '_')
    if output_dir:
        if os.path.basename(output_dir) == label:
            target_folder = output_dir
        else:
            target_folder = os.path.join(output_dir, label)
    else:
        target_folder = os.path.join(BASE_DATASET_DIR, label)
        
    os.makedirs(target_folder, exist_ok=True)
    
    def log(msg, msg_type="info"):
        log_q.put(json.dumps({"type": msg_type, "message": msg}))
    
    log(f"Starting dataset build for topic: {topic}")
    log(f"Target folder: {target_folder}")
    log(f"Max images per source: {limit}")
    log(f"Sources: {', '.join(sources)}")
    log("---")
    
    cleaner = AutomaticCleaner(target_folder)
    metadata = MetadataGenerator(target_folder)
    
    collector_map = {
        "unsplash": ("unsplash", UnsplashCollector),
        "pexels": ("pexels", PexelsCollector),
        "pixabay": ("pixabay", PixabayCollector),
        "pinterest": ("pinterest", PinterestCollector),
    }
    
    # Trackers that might be updated by multiple threads
    stats_lock = threading.Lock()
    total_downloaded = 0
    total_kept = 0
    
    def run_collector(source_key):
        nonlocal total_downloaded, total_kept
        if source_key not in collector_map:
            return
            
        source_type, CollectorClass = collector_map[source_key]
        
        # Split topic into sub-topics by comma
        sub_topics = [t.strip() for t in topic.split(',') if t.strip()]
        
        kept = 0
        for sub_idx, sub_topic in enumerate(sub_topics):
            # Check if we should stop this source entirely
            if stop_flags.get(f"source:{source_key}"):
                log(f"⏹ {source_type.capitalize()} stopped by user.", "warning")
                break
            
            # Check if we should stop this specific sub-topic
            if stop_flags.get(f"topic:{sub_topic.lower().strip()}"):
                log(f"⏹ Skipping '{sub_topic}' on {source_type.capitalize()} (stopped by user).", "warning")
                continue
                
            # Check if the entire job is stopped
            if stop_flags.get("__all__"):
                log(f"⏹ {source_type.capitalize()} stopped (full stop).", "warning")
                break
            
            if kept >= limit:
                break
                
            log(f"🔍 Searching {source_type.capitalize()} for '{sub_topic}'...", "source")
            collector = CollectorClass(target_folder, limit - kept)
            
            try:
                for filepath, source_url in collector.search_and_download(sub_topic):
                    # Check stop flags on every image
                    if stop_flags.get(f"source:{source_key}") or \
                       stop_flags.get(f"topic:{sub_topic.lower().strip()}") or \
                       stop_flags.get("__all__"):
                        break
                    
                    if cleaner.is_valid_and_clean(filepath):
                        with stats_lock:
                            metadata.log_image(filepath, label, source_type, source_url)
                            kept += 1
                            total_kept += 1
                            total_downloaded += 1
                            
                        filename = os.path.basename(filepath)
                        log_q.put(json.dumps({
                            "type": "image",
                            "filename": filename,
                            "source": source_type,
                            "url": f"/api/images/{label}/{filename}" if not output_dir else f"/api/images_custom/{label}/{filename}?folder={target_folder}"
                        }))
                        log(f"  ✓ {source_type.capitalize()} Kept: {filename}", "success")
                    else:
                        with stats_lock:
                            total_downloaded += 1
                            
                    if kept >= limit:
                        break
            except Exception as e:
                log(f"❌ Error collecting from {source_type.capitalize()} for '{sub_topic}': {str(e)}", "error")
                print(f"Failed to load {source_type.capitalize()} for {sub_topic}: {e}")
                
        log(f"✅ {source_type.capitalize()}: {kept} images kept", "success")
            
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(run_collector, src) for src in sources]
        concurrent.futures.wait(futures)
    
    log("---")
    log(f"🏁 Build complete! {total_kept}/{total_downloaded} images in final dataset.", "done")
    job['status'] = 'complete'
    log_q.put(json.dumps({"type": "complete", "message": f"{total_kept} images collected", "total": total_kept}))


# ── Routes ──────────────────────────────────────────────────────

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')


@app.route('/api/build', methods=['POST'])
def start_build():
    data = request.json
    topic = data.get('topic', '').strip()
    limit = int(data.get('limit', 100))
    sources = data.get('sources', ['unsplash', 'pexels', 'pixabay', 'pinterest'])
    output_dir = data.get('output_dir', '').strip() or None
    
    if not topic:
        return jsonify({"error": "Topic is required"}), 400
    
    job_id = str(uuid.uuid4())[:8]
    active_jobs[job_id] = {
        'status': 'running',
        'topic': topic,
        'limit': limit,
        'log_queue': queue.Queue(),
        'stop_flags': {}
    }
    
    thread = threading.Thread(target=run_pipeline, args=(job_id, topic, limit, sources, output_dir), daemon=True)
    thread.start()
    
    return jsonify({"job_id": job_id})


@app.route('/api/stop/<job_id>', methods=['POST'])
def stop_job(job_id):
    """Stop a running job. Supports granular stopping by source or sub-topic."""
    if job_id not in active_jobs:
        return jsonify({"error": "Job not found"}), 404
    
    data = request.json or {}
    stop_type = data.get('stop_type', 'all')  # 'all', 'source', 'topic'
    target = data.get('target', '')            # source name or sub-topic string
    
    job = active_jobs[job_id]
    
    if stop_type == 'all':
        job['stop_flags']['__all__'] = True
        return jsonify({"success": True, "message": "Stopping all sources..."})
    elif stop_type == 'source' and target:
        job['stop_flags'][f"source:{target}"] = True
        return jsonify({"success": True, "message": f"Stopping {target}..."})
    elif stop_type == 'topic' and target:
        job['stop_flags'][f"topic:{target.lower().strip()}"] = True
        return jsonify({"success": True, "message": f"Stopping topic '{target}'..."})
    
    return jsonify({"error": "Invalid stop request"}), 400


@app.route('/api/stream/<job_id>')
def stream_logs(job_id):
    """Server-Sent Events endpoint for real-time log streaming."""
    if job_id not in active_jobs:
        return jsonify({"error": "Job not found"}), 404
    
    def generate():
        log_q = active_jobs[job_id]['log_queue']
        while True:
            try:
                msg = log_q.get(timeout=60)
                yield f"data: {msg}\n\n"
                parsed = json.loads(msg)
                if parsed.get('type') == 'complete':
                    break
            except queue.Empty:
                # Send keepalive
                yield f"data: {json.dumps({'type': 'keepalive'})}\n\n"
    
    return Response(generate(), mimetype='text/event-stream',
                    headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no'})


@app.route('/api/datasets')
def list_datasets():
    """List all existing dataset topics."""
    datasets = []
    if os.path.exists(BASE_DATASET_DIR):
        for name in sorted(os.listdir(BASE_DATASET_DIR)):
            topic_path = os.path.join(BASE_DATASET_DIR, name)
            if os.path.isdir(topic_path):
                images = [f for f in os.listdir(topic_path)
                          if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]
                datasets.append({
                    "label": name,
                    "display_name": name.replace('_', ' ').title(),
                    "count": len(images),
                    "images": [f"/api/images/{name}/{img}" for img in images[:20]]  # preview
                })
    return jsonify(datasets)


@app.route('/api/images/<topic>/<filename>')
def serve_image(topic, filename):
    """Serve an image from the default dataset folder."""
    topic_path = os.path.join(BASE_DATASET_DIR, topic)
    return send_from_directory(topic_path, filename)

@app.route('/api/images_custom/<topic>/<filename>')
def serve_image_custom(topic, filename):
    """Serve an image from a custom output directory."""
    folder = request.args.get('folder')
    if not folder:
        return "Missing folder", 400
    return send_from_directory(folder, filename)


@app.route('/api/datasets/<topic>', methods=['DELETE'])
def delete_dataset(topic):
    """Delete an entire topic dataset."""
    import shutil
    topic_path = os.path.join(BASE_DATASET_DIR, topic)
    if os.path.exists(topic_path):
        shutil.rmtree(topic_path)
        return jsonify({"success": True})
    return jsonify({"error": "Not found"}), 404


if __name__ == '__main__':
    os.makedirs(BASE_DATASET_DIR, exist_ok=True)
    app.run(debug=True, port=5001, threaded=True)
