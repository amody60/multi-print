const i18n = {
    ar: { home: "الرئيسية (طابور الطباعة)", groups: "إدارة المجموعات", history: "سجل الطباعة", settings: "الإعدادات", queue_title: "طابور الطباعة", clear_all: "مسح الكل", drop_text: "<h3>اسحب وأفلت الملفات هنا</h3><p>أو اضغط للاختيار (PDF, DOCX, PPTX, JPG, PNG)</p>", destination: "وجهة الطباعة", orientation: "اتجاه الورق", portrait: "طولي (Portrait)", landscape: "عرضي (Landscape)", nup: "السلايدات (N-up)", sides: "الوجه", simplex: "وش بس", duplex: "وش وضهر", color: "الألوان", colored: "ألوان", bw: "أبيض وأسود", copies: "النسخ", group_mode: "وضع المجموعات", enable_groups: "تفعيل المجموعات", preview_print: "معاينة وطباعة الكل", groups_title: "إدارة المجموعات", back_home: "رجوع للرئيسية", new_group: "إنشاء مجموعة جديدة", group_name_ph: "اسم المجموعة (مثال: طابعات الدور الأول)", select_printers: "اختر الطابعات:", save_group: "حفظ المجموعة", existing_groups: "المجموعات الحالية", history_title: "سجل الطباعة", settings_title: "إعدادات الطابعات", printer_props: "تعديل خصائص الطابعات", printer_props_desc: "إذا كان البرنامج يقرأ أن الطابعة لا تدعم الوجهين بالخطأ، يمكنك تعديلها هنا.", save_settings: "حفظ الإعدادات", preview_all: "معاينة شاملة لجميع الملفات", print_now: "✅ طباعة الآن", close: "إغلاق", tb_date: "التاريخ", tb_file: "اسم الملف", tb_printer: "الطابعة", tb_pages: "الصفحات", tb_sheets: "الأوراق", active_groups: "مفعل: اختار مجموعة", all: "الكل", custom: "مخصص", ready: "جاهز", converting: "جاري التحويل..." },
    en: { home: "Home (Print Queue)", groups: "Groups Manager", history: "Print History", settings: "Settings", queue_title: "Print Queue", clear_all: "Clear All", drop_text: "<h3>Drag & Drop files here</h3><p>or click to select (PDF, DOCX, PPTX, JPG, PNG)</p>", destination: "Destination", orientation: "Orientation", portrait: "Portrait", landscape: "Landscape", nup: "N-up Slides", sides: "Sides", simplex: "Simplex", duplex: "Duplex", color: "Color", colored: "Color", bw: "Grayscale", copies: "Copies", group_mode: "Group Mode", enable_groups: "Enable Groups", preview_print: "Preview & Print All", groups_title: "Groups Manager", back_home: "Back to Home", new_group: "Create New Group", group_name_ph: "Group Name (e.g., 1st Floor Printers)", select_printers: "Select Printers:", save_group: "Save Group", existing_groups: "Existing Groups", history_title: "Print History", settings_title: "Printer Settings", printer_props: "Edit Printer Properties", printer_props_desc: "If the software wrongly detects duplex support, you can manually fix it here.", save_settings: "Save Settings", preview_all: "Full Preview of All Files", print_now: "✅ Print Now", close: "Close", tb_date: "Date", tb_file: "File Name", tb_printer: "Printer", tb_pages: "Pages", tb_sheets: "Sheets", active_groups: "Active: Select Group", all: "All", custom: "Custom", ready: "Ready", converting: "Converting..." }
};
let currentLang = 'ar';

function toggleLang() {
    currentLang = currentLang === 'ar' ? 'en' : 'ar';
    document.documentElement.lang = currentLang;
    document.documentElement.dir = currentLang === 'ar' ? 'rtl' : 'ltr';
    applyTranslations();
    saveUISettings();
}

function applyTranslations() {
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (i18n[currentLang][key]) el.innerHTML = i18n[currentLang][key];
    });
    document.querySelectorAll('[data-i18n-ph]').forEach(el => {
        const key = el.getAttribute('data-i18n-ph');
        if (i18n[currentLang][key]) el.placeholder = i18n[currentLang][key];
    });
}

function toggleDarkMode() {
    document.body.classList.toggle('dark-mode');
    saveUISettings();
}

async function saveUISettings() {
    try {
        await fetch('http://127.0.0.1:8000/api/settings/ui', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ lang: currentLang, dark_mode: document.body.classList.contains('dark-mode') })
        });
    } catch (e) { console.error(e); }
}

// --- App Logic ---
let filesQueue = [];
let availablePrinters = [];
let availableGroups = {};
let groupMode = false;
let draggedItemId = null;

async function loadData() {
    try {
        const resUI = await fetch('http://127.0.0.1:8000/api/settings/ui');
        const uiSettings = await resUI.json();
        currentLang = uiSettings.lang || 'ar';
        document.documentElement.lang = currentLang;
        document.documentElement.dir = currentLang === 'ar' ? 'rtl' : 'ltr';
        if (uiSettings.dark_mode) {
            document.body.classList.add('dark-mode');
        }
    } catch (e) { console.error("Failed to load UI settings", e); }

    const resP = await fetch('http://127.0.0.1:8000/api/printers');
    availablePrinters = await resP.json();
    const resG = await fetch('http://127.0.0.1:8000/api/groups');
    availableGroups = await resG.json();
    
    updatePrinterDropdown();
    applyTranslations();

    try {
        const resFR = await fetch('http://127.0.0.1:8000/api/settings/first_run');
        const frData = await resFR.json();
        if (frData.first_run) {
            openFirstRunWizard();
        }
    } catch (e) { console.error("First run check failed", e); }
}

function openFirstRunWizard() {
    const dSelect = document.getElementById('wizardDefaultPrinter');
    const fSelect = document.getElementById('wizardFallbackPrinter');
    dSelect.innerHTML = '';
    fSelect.innerHTML = '';
    availablePrinters.forEach(p => {
        dSelect.innerHTML += `<option value="${p.name}">${p.name}</option>`;
        fSelect.innerHTML += `<option value="${p.name}">${p.name}</option>`;
    });
    document.getElementById('firstRunWizard').style.display = 'flex';
}

async function saveFirstRun() {
    const defaultP = document.getElementById('wizardDefaultPrinter').value;
    const fallbackP = document.getElementById('wizardFallbackPrinter').value;
    const paper = document.getElementById('wizardPaperSize').value;
    
    await fetch('http://127.0.0.1:8000/api/settings/first_run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ default_printer: defaultP, fallback_printer: fallbackP, paper_size: paper })
    });
    
    document.getElementById('firstRunWizard').style.display = 'none';
    document.getElementById('printerSelect').value = defaultP;
    alert('تم حفظ الإعدادات بنجاح!');
}

function showScreen(screenName) {
    document.querySelectorAll('.screen-container').forEach(s => s.classList.remove('active'));
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
    
    document.getElementById(`${screenName}Screen`).classList.add('active');
    document.getElementById(`nav-${screenName}`).classList.add('active');

    if (screenName === 'groups') { renderPrinterCheckboxes(); renderSavedGroups(); }
    if (screenName === 'settings') { renderSettingsPrinters(); }
    if (screenName === 'history') { loadHistory(); }
}

function updatePrinterDropdown() {
    const select = document.getElementById('printerSelect');
    select.innerHTML = '';
    if (groupMode) {
        for (let g in availableGroups) select.innerHTML += `<option value="GROUP:${g}">${g}</option>`;
        if(select.innerHTML === '') select.innerHTML = `<option>${i18n[currentLang].no_groups || 'No groups'}</option>`;
    } else {
        availablePrinters.forEach(p => select.innerHTML += `<option value="${p.name}">${p.name}</option>`);
    }
}

function toggleGroupMode() {
    groupMode = !groupMode;
    const btn = document.getElementById('groupToggleBtn');
    if (groupMode) {
        btn.innerText = i18n[currentLang].active_groups;
        btn.style.background = "#10b981";
    } else {
        btn.innerText = i18n[currentLang].enable_groups;
        btn.style.background = "#e2e8f0"; btn.style.color = "#1e293b";
    }
    updatePrinterDropdown();
}

document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('dropZone');
    if(dropZone) {
        dropZone.addEventListener('click', () => document.getElementById('fileInput').click());
        dropZone.addEventListener('dragover', (e) => { e.preventDefault(); dropZone.classList.add('dragover'); });
        dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));
        dropZone.addEventListener('drop', (e) => {
            e.preventDefault(); dropZone.classList.remove('dragover');
            handleFiles(e.dataTransfer.files);
        });
    }
});

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

async function preparePrintAll() {
    if (filesQueue.length === 0) return alert('No files');
    const readyFiles = filesQueue.filter(f => f.status === 'ready').map(f => f.pdf_path);
    if(readyFiles.length === 0) return alert('Files not ready');
    try {
        const res = await fetch('http://127.0.0.1:8000/api/files/preview_all', {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ files: readyFiles })
        });
        const data = await res.json();
        const container = document.getElementById('previewImageContainer');
        container.innerHTML = '';
        data.images.forEach(imgUrl => {
            container.innerHTML += `<img src="${imgUrl}" style="max-width: 800px; width: 100%; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-radius: 4px; background: white; margin-bottom: 15px;">`;
        });
        document.getElementById('previewFullscreen').style.display = 'flex';
    } catch (e) { alert('Preview failed'); }
}

function closePreview() {
    document.getElementById('previewFullscreen').style.display = 'none';
    document.getElementById('previewImageContainer').innerHTML = '';
}

async function executePrint() {
    const printBtn = document.getElementById('executePrintBtn');
    printBtn.disabled = true; printBtn.innerText = "...";
    
    const progContainer = document.getElementById('printProgressContainer');
    const progBar = document.getElementById('printProgressBar');
    const progText = document.getElementById('printProgressText');
    const progCount = document.getElementById('printProgressCount');
    progContainer.style.display = 'block';
    progBar.style.width = '0%';
    
    const target = document.getElementById('printerSelect').value;
    const n_up = parseInt(document.getElementById('nupSelect').value);
    const duplex = document.getElementById('duplexSelect').value === 'true';
    const color = document.getElementById('colorSelect').value === 'true';
    const copies = parseInt(document.getElementById('copiesInput').value);
    const orientation = document.getElementById('orientationSelect').value;
    let isGroup = target.startsWith('GROUP:');
    let printerName = isGroup ? null : target;
    let groupName = isGroup ? target.replace('GROUP:', '') : null;

    let totalOriginal = 0, totalPrinted = 0, totalSaved = 0;
    let usedPrinters = [];
    let failedFiles = [];

    const readyFiles = filesQueue.filter(f => f.status === 'ready');
    for (let i = 0; i < readyFiles.length; i++) {
        const f = readyFiles[i];
        
        let progress = Math.round(((i) / readyFiles.length) * 100);
        progBar.style.width = `${progress}%`;
        progText.innerText = `جاري طباعة: ${f.name}`;
        progCount.innerText = `${i} / ${readyFiles.length} (تم طباعة ${totalPrinted} ورقة)`;

        const page_range = f.page_range === 'custom' ? f.custom_range : null;
        try {
            const res = await fetch('http://127.0.0.1:8000/api/print/job', {
                method: 'POST', headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    pdf_path: f.pdf_path, original_name: f.name, printer_name: printerName, group_name: groupName,
                    n_up, duplex, color, copies, orientation, page_range
                })
            });
            
            if (res.ok) {
                const data = await res.json();
                if(data.report) {
                    totalOriginal += data.report.original_pages;
                    totalPrinted += data.report.printed_sheets;
                    totalSaved += data.report.saved_sheets;
                    usedPrinters.push(data.report.printer_used);
                }
            } else {
                const errData = await res.json();
                failedFiles.push(`${f.name} (السبب: ${errData.detail})`);
            }
        } catch (e) { 
            failedFiles.push(`${f.name} (خطأ في الاتصال بالخادم)`);
        }
    }
    
    progBar.style.width = '100%';
    progText.innerText = 'اكتملت الطباعة';
    progCount.innerText = `${readyFiles.length} / ${readyFiles.length}`;
    
    await new Promise(r => setTimeout(r, 1000)); 
    progContainer.style.display = 'none'; 
    
    closePreview();
    printBtn.disabled = false; printBtn.innerText = i18n[currentLang].print_now;
    
    const reportDiv = document.getElementById('reportContainer');
    reportDiv.innerHTML = `
        <div class="report-box">
            <h3>✅ Report</h3>
            <div class="report-line"><span>Original Pages:</span> <strong>${totalOriginal}</strong></div>
            <div class="report-line"><span>Printed Sheets:</span> <strong>${totalPrinted}</strong></div>
            <div class="report-line"><span>Saved Sheets:</span> <strong style="color:#10b981">${totalSaved}</strong></div>
            <div class="report-line"><span>Printers:</span> <strong>${[...new Set(usedPrinters)].join(', ')}</strong></div>
            ${failedFiles.length > 0 ? `<div class="report-line" style="color:#ef4444; margin-top: 10px; flex-direction: column; align-items: flex-start;"><span>⚠️ ملفات لم تطبع:</span> <strong style="font-size: 12px; font-weight: normal; margin-top: 5px;">${failedFiles.join('<br>')}</strong></div>` : ''}
        </div>
    `;
    
    if (failedFiles.length > 0) {
        alert(`انتبه! ${failedFiles.length} ملف لم يطبع. تفاصيل الأخطاء موجودة في التقرير بالأسفل.`);
    } else {
        alert('تم إرسال جميع الملفات للطابعة بنجاح!');
    }
}

async function clearQueue() {
    const filesToDelete = filesQueue.map(f => f.pdf_path).filter(p => p);
    if (filesToDelete.length > 0) {
        try {
            await fetch('http://127.0.0.1:8000/api/files/cleanup', {
                method: 'DELETE',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(filesToDelete)
            });
        } catch (e) { console.error("Cleanup failed", e); }
    }
    filesQueue = [];
    renderQueue();
    document.getElementById('reportContainer').innerHTML='';
}

// Groups & Settings Functions
function renderPrinterCheckboxes() {
    const c = document.getElementById('printersCheckboxes'); c.innerHTML = '';
    availablePrinters.forEach(p => c.innerHTML += `<label class="printer-checkbox"><input type="checkbox" value="${p.name}"> ${p.name} ${p.is_duplex ? '(Duplex)' : ''}</label>`);
}
async function saveGroup() {
    const name = document.getElementById('newGroupName').value.trim();
    const selected = Array.from(document.querySelectorAll('#printersCheckboxes input:checked')).map(cb => cb.value);
    if (!name || selected.length === 0) return alert('Invalid');
    await fetch('http://127.0.0.1:8000/api/groups', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({name, printers: selected}) });
    await loadData(); renderSavedGroups(); alert('Saved!');
}
function renderSavedGroups() {
    const c = document.getElementById('savedGroupsList'); c.innerHTML = '';
    if (Object.keys(availableGroups).length === 0) return c.innerHTML = '<p style="color:var(--text-muted);">None</p>';
    for (let g in availableGroups) {
        c.innerHTML += `<div style="display:flex; justify-content:space-between; padding:15px; background:var(--input-bg); border-radius:8px; margin-bottom:10px; border:1px solid var(--border);"><div><strong>${g}</strong><p style="color:var(--text-muted);">${availableGroups[g].printers.join(', ')}</p></div><button class="btn btn-danger btn-sm" onclick="deleteGroup('${g}')">X</button></div>`;
    }
}
async function deleteGroup(name) {
    await fetch(`http://127.0.0.1:8000/api/groups/${encodeURIComponent(name)}`, { method: 'DELETE' });
    await loadData(); renderSavedGroups(); updatePrinterDropdown();
}
async function renderSettingsPrinters() {
    if (availablePrinters.length === 0) await loadData();
    const res = await fetch('http://127.0.0.1:8000/api/settings/printers');
    const ps = await res.json();
    const c = document.getElementById('settingsPrintersList'); c.innerHTML = '';
    availablePrinters.forEach(p => {
        const s = ps[p.name] || { is_duplex: p.is_duplex, color: true };
        c.innerHTML += `<div style="background:var(--input-bg); border:1px solid var(--border); border-radius:12px; padding:20px; display:flex; justify-content:space-between; align-items:center;"><div><strong>${p.name}</strong></div><div style="display:flex; gap:20px;"><select id="dup-${p.name}"><option value="true" ${s.is_duplex?'selected':''}>Duplex</option><option value="false" ${!s.is_duplex?'selected':''}>Simplex</option></select><select id="col-${p.name}"><option value="true" ${s.color?'selected':''}>Color</option><option value="false" ${!s.color?'selected':''}>B/W</option></select></div></div>`;
    });
}
async function savePrinterSettings() {
    let st = {};
    availablePrinters.forEach(p => { st[p.name] = { is_duplex: document.getElementById(`dup-${p.name}`).value === 'true', color: document.getElementById(`col-${p.name}`).value === 'true' }; });
    await fetch('http://127.0.0.1:8000/api/settings/printers', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({printers: st}) });
    alert('Saved!');
}
async function loadHistory() {
    const res = await fetch('http://127.0.0.1:8000/api/history/');
    const data = await res.json();
    const tb = document.getElementById('historyTableBody'); tb.innerHTML = '';
    if(data.length === 0) tb.innerHTML = `<tr><td colspan="5" style="text-align:center;">No history</td></tr>`;
    data.reverse().forEach(h => {
        tb.innerHTML += `<tr><td>${h.timestamp}</td><td>${h.file_name}</td><td>${h.printer}</td><td>${h.pages}</td><td>${h.sheets}</td></tr>`;
    });
}

window.onload = loadData;