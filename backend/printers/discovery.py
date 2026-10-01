"""Discover physical printers installed on the local Windows machine."""
import win32print
import win32api
from typing import Any
from backend.config.logger import logger

VIRTUAL_PRINTER_KEYWORDS = ("pdf", "fax", "onenote", "xps")
DC_DUPLEX = 6

def _is_virtual_printer(printer_name: str) -> bool:
    normalized_name = printer_name.casefold()
    return any(keyword in normalized_name for keyword in VIRTUAL_PRINTER_KEYWORDS)

def _get_duplex_support(printer_name: str) -> bool:
    try:
        result = win32print.DeviceCapabilities(printer_name, None, DC_DUPLEX)
        if result: return True
    except Exception: pass
        
    try:
        printer_handle = win32print.OpenPrinter(printer_name)
        try:
            printer_info: dict[str, Any] = win32print.GetPrinter(printer_handle, 2)
            attributes = printer_info.get("Attributes", 0)
            if attributes & 0x00004000: return True
            devmode = printer_info.get("pDevMode")
            duplex_mode = getattr(devmode, "Duplex", 0) if devmode else 0
            return duplex_mode in (2, 3)
        finally:
            win32print.ClosePrinter(printer_handle)
    except Exception as e:
        logger.warning(f"Could not check duplex for {printer_name}: {e}")
        return False

def discover_printers() -> list[dict[str, bool | str]]:
    discovered_printers = []
    printers = []

    try:
        flags = win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS
        printers = win32print.EnumPrinters(flags, None, 2)
    except Exception as e:
        logger.error(f"EnumPrinters failed: {e}. Trying win32api fallback...")
        try:
            printers = win32api.EnumPrinters(win32print.PRINTER_ENUM_LOCAL, None, 2)
        except Exception as e2:
            logger.error(f"win32api fallback failed: {e2}")
            return []

    for printer in printers:
        try:
            printer_name = printer["pPrinterName"]
            if _is_virtual_printer(printer_name):
                continue
            discovered_printers.append({
                "name": printer_name,
                "is_duplex": _get_duplex_support(printer_name),
            })
        except Exception as p_err:
            logger.warning(f"Error processing a printer: {p_err}")

    logger.info(f"Discovered {len(discovered_printers)} physical printers.")
    return discovered_printers