function updatePrinterDropdown() {
    const select = document.getElementById('printerSelect');
    if (!select) return;
    
    select.innerHTML = '';
    
    // ✅ لو وضع المجموعات مش مفعل، نعرض الطابعات العادية
    if (!groupMode) {
        if (availablePrinters.length === 0) {
            select.innerHTML = '<option>لا توجد طابعات متصلة</option>';
            return;
        }
        availablePrinters.forEach(p => {
            select.innerHTML += `<option value="${p.name}">${p.name} ${p.is_duplex ? '(يدعم وضهر)' : ''}</option>`;
        });
    } else {
        // لو وضع المجموعات مفعل
        if (Object.keys(availableGroups).length === 0) {
            select.innerHTML = '<option>لا توجد مجموعات</option>';
        } else {
            for (let g in availableGroups) {
                select.innerHTML += `<option value="GROUP:${g}">مجموعة: ${g}</option>`;
            }
        }
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

function renderPrinterCheckboxes() {
    const c = document.getElementById('printersCheckboxes'); 
    if(!c) return;
    c.innerHTML = '';
    availablePrinters.forEach(p => c.innerHTML += `<label class="printer-checkbox"><input type="checkbox" value="${p.name}"> ${p.name} ${p.is_duplex ? '(Duplex)' : ''}</label>`);
}

async function saveGroup() {
    const name = document.getElementById('newGroupName').value.trim();
    const selected = Array.from(document.querySelectorAll('#printersCheckboxes input:checked')).map(cb => cb.value);
    
    if (!name || selected.length === 0) {
        alert('اكتب اسم للمجموعة واختر طابعة واحدة على الأقل');
        return;
    }

    try {
        const res = await fetch('http://127.0.0.1:8000/api/groups', { 
            method: 'POST', 
            headers: {'Content-Type':'application/json'}, 
            body: JSON.stringify({name, printers: selected}) 
        });
        
        if (!res.ok) throw new Error('السيرفر رفض الحفظ');
        
        document.getElementById('newGroupName').value = '';
        await loadData(); 
        renderSavedGroups(); 
        alert('تم حفظ المجموعة بنجاح!');
    } catch (e) {
        alert('حدث خطأ أثناء الحفظ! برجاء انقل البرنامج لمجلد عادي زي C:\\MultiPrint لأن الويندوز مانع الكتابة.');
        console.error("Save group failed:", e);
    }
}

function renderSavedGroups() {
    const c = document.getElementById('savedGroupsList'); 
    if(!c) return;
    c.innerHTML = '';
    if (Object.keys(availableGroups).length === 0) {
        c.innerHTML = '<p style="color:var(--text-muted);">None</p>';
        return;
    }
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
    const c = document.getElementById('settingsPrintersList'); 
    if(!c) return;
    c.innerHTML = '';
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
    const tb = document.getElementById('historyTableBody'); 
    if(!tb) return;
    tb.innerHTML = '';
    if(data.length === 0) tb.innerHTML = `<tr><td colspan="5" style="text-align:center;">No history</td></tr>`;
    data.reverse().forEach(h => {
        tb.innerHTML += `<tr><td>${h.timestamp}</td><td>${h.file_name}</td><td>${h.printer}</td><td>${h.pages}</td><td>${h.sheets}</td></tr>`;
    });
}