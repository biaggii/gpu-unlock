# RTX 3090 / Zenith II Extreme Windows implementation

This branch starts the actual UEFI hardware investigation. Current executable:
**read-only probe**, not yet the unlock/handoff application. It does not declare
this machine supported. The Linux unlock core is unchanged.

## Target reported by the owner

| Field | Value |
| --- | --- |
| OS | Windows 10 Pro x64, build 19045, UEFI |
| CPU | AMD Threadripper 3970X |
| Motherboard / BIOS | ASUS ROG ZENITH II EXTREME / 2502 |
| GPU | RTX 3090, PCI 10de:2204, subsystem 1458:4042, revision A1 |
| Windows PCI address | 0000:22:00.0; discover independently in UEFI |
| Driver / VBIOS | 617.42 / 94.02.59.00.5A |

Only one video controller was reported. Display wiring and UEFI GOP ownership
are still unconfirmed. Do not reuse another motherboard's BAR, root-port,
ROM hash, console-driver fingerprint or display-release profile.

## Build and collect evidence

The `RTX 3090 UEFI probe` Actions workflow builds pinned GPL-2.0-only sources
from craftingmod/rtx30-unlock at 5c076dc4ee7fa369639669fa591ac74d8f6dfcd8.
It runs the upstream probe host tests, builds the x64 EFI, verifies its PE
structure and packages it with licenses and a SHA-256 provenance record.
No proprietary firmware download or unlock payload generation is involved.

1. Download `rtx3090-readonly-probe` from a successful workflow run.
2. Extract onto an existing spare FAT32 USB so it contains
   `EFI/BOOT/BOOTX64.EFI` and `RTX30-PROBE/KEEP.txt`. Preserve the directory.
   Do not replace files on the internal Windows EFI System Partition.
3. This unsigned EFI requires Secure Boot off. First query
   `Confirm-SecureBootUEFI` and `manage-bde -status C:` in administrator
   PowerShell. If encryption is active or the firmware setting is unclear,
   resolve that boot prerequisite before changing anything; keep recovery
   information private. The probe itself changes neither setting.
4. Select the USB using the firmware's one-time UEFI boot menu. It inventories
   PCI/GOP state and, when its read checks pass, reads registers and ROM copies.
   It does not write GPU registers, enable bus mastering, reset the GPU,
   disconnect display drivers, or change boot variables. It writes only report
   files to its own USB marker directory.
5. It returns after a short delay. Choose the original Windows Boot Manager.
   If firmware cannot return normally, power off and remove the test USB.
6. Return `RTX30-PROBE/RUNxx/REPORT.TXT` and `INVENTORY.TXT`. Retain PROM.BIN
   and ROMIMAGE.BIN locally; do not publish them in a GitHub issue. A failed
   read is evidence to investigate, not permission to remove its check.

## Remaining implementation work

Use the actual captured PCI/BAR, firmware layout, selector state and GOP
ancestry to design the target's ownership/release and Windows handoff. Validate
the FWSEC/WPR/FLR cleanup sequence and failure paths before testing an unlock.
Then compare controlled FP16/BF16 and FP32 results on Windows. A host test or
successful EFI build alone does not prove hardware support.

## 繁體中文

這是 RTX 3090 Windows 移植的第一個可執行階段：UEFI 唯讀診斷，不是解鎖程式。
下載成功 Actions 執行產生的 artifact，解壓至獨立 FAT32 USB，保留 EFI 與
RTX30-PROBE 目錄。先確認 Secure Boot／磁碟加密狀態，再從一次性 UEFI 開機選單
選 USB。程式只讀 GPU 並寫 USB 報告，不會解鎖、重置 GPU 或變更開機項目。
返回 Windows 後提供 RUNxx 裡的 REPORT.TXT 與 INVENTORY.TXT；ROM 檔先留在本機。
下一階段依實際報告實作這台 Zenith II 的解鎖與 Windows 顯示恢復流程。
