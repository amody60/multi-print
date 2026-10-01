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

function showScreen(screenName) {
    document.querySelectorAll('.screen-container').forEach(s => s.classList.remove('active'));
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
    
    document.getElementById(`${screenName}Screen`).classList.add('active');
    document.getElementById(`nav-${screenName}`).classList.add('active');

    if (screenName === 'groups') { renderPrinterCheckboxes(); renderSavedGroups(); }
    if (screenName === 'settings') { renderSettingsPrinters(); }
    if (screenName === 'history') { loadHistory(); }
}