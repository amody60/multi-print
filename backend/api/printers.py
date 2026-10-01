"""Printer discovery and groups API endpoints."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

from backend.printers.discovery import discover_printers
from backend.printers.groups import get_groups, save_group, delete_group
from backend.config.settings_store import load_settings, save_settings

router = APIRouter(prefix="/api", tags=["printers"])

@router.get("/printers")
def get_printers() -> list[dict[str, bool | str]]:
    """Return connected physical printers as JSON."""
    return discover_printers()

# --- Printer Groups APIs ---

class GroupPayload(BaseModel):
    name: str
    printers: List[str]

@router.get("/groups")
def list_groups() -> dict:
    return get_groups()

@router.post("/groups")
def create_or_update_group(payload: GroupPayload) -> dict:
    save_group(payload.name, payload.printers)
    return {"status": "success", "groups": get_groups()}

@router.delete("/groups/{group_name}")
def remove_group(group_name: str) -> dict:
    success = delete_group(group_name)
    if not success:
        raise HTTPException(status_code=404, detail="Group not found")
    return {"status": "success", "groups": get_groups()}

# --- Printer Settings APIs ---

class PrinterSettingsPayload(BaseModel):
    printers: dict

@router.get("/settings/printers")
def get_printer_settings() -> dict:
    settings = load_settings()
    return settings.get("printer_settings", {})

@router.post("/settings/printers")
def save_printer_settings(payload: PrinterSettingsPayload) -> dict:
    settings = load_settings()
    settings["printer_settings"] = payload.printers
    save_settings(settings)
    return {"status": "success"}

# --- UI Settings APIs (Dark Mode & Language) ---

class UISettingsPayload(BaseModel):
    lang: str = "ar"
    dark_mode: bool = False

@router.get("/settings/ui")
def get_ui_settings() -> dict:
    settings = load_settings()
    return settings.get("ui_settings", {"lang": "ar", "dark_mode": False})

@router.post("/settings/ui")
def save_ui_settings(payload: UISettingsPayload) -> dict:
    settings = load_settings()
    settings["ui_settings"] = {"lang": payload.lang, "dark_mode": payload.dark_mode}
    save_settings(settings)
    return {"status": "success"}
# --- First Run Wizard APIs ---

@router.get("/settings/first_run")
def check_first_run() -> dict:
    settings = load_settings()
    # لو الإعدادات فاضية أو first_run_completed مش true، يبقى أول مرة
    return {"first_run": not settings.get("first_run_completed", False)}

class FirstRunPayload(BaseModel):
    default_printer: str
    fallback_printer: str
    paper_size: str = "A4"

@router.post("/settings/first_run")
def save_first_run(payload: FirstRunPayload) -> dict:
    settings = load_settings()
    settings["first_run_completed"] = True
    settings["default_printer"] = payload.default_printer
    settings["fallback_printer"] = payload.fallback_printer
    settings["paper_size"] = payload.paper_size
    save_settings(settings)
    return {"status": "success"}