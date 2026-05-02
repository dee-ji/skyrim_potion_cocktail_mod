Scriptname SPC_BridgeInventoryExporter extends Quest

; Phase 2 bridge source scaffold.
;
; This script intentionally does not implement discovery scoring, rarity, or recipe
; ranking. Its job is to collect Skyrim-side data and write the JSON exchange
; format documented in docs/skyrim-bridge.md.
;
; A working implementation should use SKSE plus a JSON-capable Papyrus utility
; such as PapyrusUtil or JContainers. Keep that dependency explicit in release
; notes before shipping a compiled plugin.

String Property ExportFileName = "Data\\SKSE\\Plugins\\SkyrimPotionCocktails\\bridge-export.json" Auto

Function ExportInventory()
    Debug.Notification("Skyrim Potion Cocktails bridge export is not wired yet.")
EndFunction

