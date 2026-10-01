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
    progText.style.color = "var(--primary)"; // Reset color
    
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
        progText.innerText = `جاري إرسال: ${f.name}`;
        progCount.innerText = `${i} / ${readyFiles.length} (تمت طباعة ${totalPrinted} ورقة)`;

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
                    
                    // ✅ تحديث الـ Progress Bar باسم الطابعة اللي استلمت الملف
                    progText.innerText = `تم الإرسال إلى: ${data.report.printer_used}`;
                    progText.style.color = "#10b981"; // نخليه أخضر شوية
                    await new Promise(r => setTimeout(r, 500)); // نستنى نص ثانية عشان المستخدم يقرا الاسم
                    progText.style.color = "var(--primary)"; // نرجع لونه أصلي
                }
            } else {
                const errData = await res.json();
                failedFiles.push(`${f.name} (السبب: ${errData.detail})`);
                progText.innerText = `فشل: ${f.name}`;
                progText.style.color = "#ef4444";
                await new Promise(r => setTimeout(r, 1000));
                progText.style.color = "var(--primary)";
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