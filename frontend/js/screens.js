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
        
        if (!res.ok) {
            const errData = await res.json();
            throw new Error(errData.detail || 'السيرفر رفض الحفظ');
        }
        
        document.getElementById('newGroupName').value = '';
        await loadData(); 
        renderSavedGroups(); 
        alert('تم حفظ المجموعة بنجاح!');
    } catch (e) {
        // ✅ إظهار رسالة الخطأ الحقيقية اللي بيرجعها الباك-إند
        alert('حدث خطأ أثناء الحفظ:\n' + e.message);
        console.error("Save group failed:", e);
    }
}