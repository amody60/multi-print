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

    try {
        const resP = await fetch('http://127.0.0.1:8000/api/printers');
        if (!resP.ok) throw new Error('Server Error');
        availablePrinters = await resP.json();
        
        if (availablePrinters.length === 0) {
            alert('لم يتم العثور على طابعات. تأكد من تشغيل البرنامج كمسؤول.');
        }
    } catch (e) {
        alert('حدث خطأ في الاتصال بالباك-إند! تأكد من تشغيل البرنامج كمسؤول (Run as Administrator).');
        console.error("Backend connection failed:", e);
    }

    try {
        const resG = await fetch('http://127.0.0.1:8000/api/groups');
        availableGroups = await resG.json();
    } catch (e) { console.error("Failed to load groups", e); }
    
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

window.onload = loadData;