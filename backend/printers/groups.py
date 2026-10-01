"""Manage printer groups and round-robin distribution logic."""

from backend.config.settings_store import load_settings, save_settings

def get_groups() -> dict:
    """Retrieve all saved printer groups."""
    settings = load_settings()
    return settings.get("printer_groups", {})

def save_group(group_name: str, printers: list[str]) -> None:
    """Create or update a specific printer group."""
    settings = load_settings()
    if "printer_groups" not in settings:
        settings["printer_groups"] = {}
    
    # لو المجموعة موجودة، نحتفظ بالـ Index بتاعها، لو جديدة نبدأ من 0
    current_index = 0
    if group_name in settings["printer_groups"]:
        current_index = settings["printer_groups"][group_name].get("last_used_index", 0)
        
    settings["printer_groups"][group_name] = {
        "printers": printers,
        "last_used_index": current_index
    }
    save_settings(settings)

def delete_group(group_name: str) -> bool:
    """Delete a specific printer group."""
    settings = load_settings()
    groups = settings.get("printer_groups", {})
    
    if group_name in groups:
        del groups[group_name]
        settings["printer_groups"] = groups
        save_settings(settings)
        return True
    return False

def get_next_printer_in_group(group_name: str) -> str | None:
    """Get the next printer in a group using Round-Robin algorithm."""
    settings = load_settings()
    groups = settings.get("printer_groups", {})
    
    if group_name not in groups:
        return None
        
    group_data = groups[group_name]
    printers = group_data.get("printers", [])
    if not printers:
        return None
        
    current_index = group_data.get("last_used_index", 0)
    
    # نتأكد إن الـ Index مش أكبر من عدد الطابعات
    if current_index >= len(printers):
        current_index = 0
        
    next_printer = printers[current_index]
    
    # تحديث الـ Index للطابعة اللي بعدها
    new_index = (current_index + 1) % len(printers)
    group_data["last_used_index"] = new_index
    
    # حفظ الإعدادات بالـ Index الجديد
    settings["printer_groups"][group_name] = group_data
    save_settings(settings)
    
    return next_printer