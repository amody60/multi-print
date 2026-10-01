async function handleFiles(fileList) {
    for (let file of fileList) {
        const formData = new FormData();
        formData.append('file', file);
        const tempId = 'file_' + Date.now() + Math.random();
        filesQueue.push({ id: tempId, name: file.name, status: 'converting', pdf_path: '', page_count: 0, page_range: 'all', custom_range: '' });
        renderQueue();
        try {
            const res = await fetch('http://127.0.0.1:8000/api/files/upload', { method: 'POST', body: formData });
            const data = await res.json();
            const idx = filesQueue.findIndex(f => f.id === tempId);
            if (idx > -1) {
                filesQueue[idx].pdf_path = data.pdf_path;
                filesQueue[idx].status = 'ready';
                filesQueue[idx].page_count = data.page_count || 0;
            }
            renderQueue();
        } catch (e) { alert('Failed: ' + file.name); }
    }
}

function renderQueue() {
    const list = document.getElementById('queueList');
    list.innerHTML = '';
    if (filesQueue.length === 0) {
        list.innerHTML = `<p style="text-align:center; color:var(--text-muted); margin-top:20px;">No files</p>`;
        return;
    }
    filesQueue.forEach(f => {
        const div = document.createElement('div');
        div.className = 'file-card';
        div.draggable = true;
        div.ondragstart = (e) => { draggedItemId = f.id; div.classList.add('dragging'); };
        div.ondragend = () => div.classList.remove('dragging');
        div.ondragover = (e) => e.preventDefault();
        div.ondrop = (e) => {
            e.preventDefault();
            const targetIndex = filesQueue.findIndex(item => item.id === f.id);
            const draggedIndex = filesQueue.findIndex(item => item.id === draggedItemId);
            if (draggedIndex !== -1 && targetIndex !== -1) {
                const item = filesQueue.splice(draggedIndex, 1)[0];
                filesQueue.splice(targetIndex, 0, item);
                renderQueue();
            }
        };
        
        const showRangeInput = f.page_range === 'custom' ? 'block' : 'none';
        
        div.innerHTML = `
            <div class="file-info">
                <div class="file-icon">${f.name.split('.').pop().toUpperCase().substring(0,3)}</div>
                <div>
                    <div class="file-name">${f.name}</div>
                    <div class="file-status" style="color: ${f.status === 'ready' ? '#10b981' : 'var(--text-muted)'}; font-size: 12px;">
                        ${f.status === 'ready' ? `${i18n[currentLang].ready} (${f.page_count}p)` : i18n[currentLang].converting}
                    </div>
                </div>
            </div>
            <div style="display:flex; gap:10px; align-items:center;">
                <select onchange="updateFileRange('${f.id}', this.value)" style="width: 90px;">
                    <option value="all" ${f.page_range === 'all' ? 'selected' : ''}>${i18n[currentLang].all}</option>
                    <option value="custom" ${f.page_range === 'custom' ? 'selected' : ''}>${i18n[currentLang].custom}</option>
                </select>
                <input type="text" class="page-range-input" placeholder="1-3, 5" style="display:${showRangeInput};" value="${f.custom_range}" onchange="updateCustomRange('${f.id}', this.value)">
                <button class="btn btn-danger btn-sm" onclick="removeFile('${f.id}')">X</button>
            </div>
        `;
        list.appendChild(div);
    });
}

function updateFileRange(id, val) {
    const idx = filesQueue.findIndex(f => f.id === id);
    if (idx > -1) { filesQueue[idx].page_range = val; renderQueue(); }
}
function updateCustomRange(id, val) {
    const idx = filesQueue.findIndex(f => f.id === id);
    if (idx > -1) filesQueue[idx].custom_range = val;
}
function removeFile(id) {
    filesQueue = filesQueue.filter(f => f.id !== id);
    renderQueue();
}