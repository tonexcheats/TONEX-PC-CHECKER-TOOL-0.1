# TONEX PC CHECKER TOOL

A lightweight Windows system-monitoring utility with a dark red gaming interface.

## Features
- Live CPU, RAM, disk and process counts
- Process list with PID, CPU, memory and status
- Process search and user-confirmed End Task
- Read-only Windows services viewer
- System information page
- Automatic refresh

## Build the Windows EXE without Visual Studio
1. Create a free GitHub account if you do not already have one.
2. Create a new repository named `TONEX-PC-CHECKER-TOOL`.
3. Upload the contents of this ZIP (including the `.github` folder).
4. Open the repository's **Actions** tab.
5. Select **Build TONEX PC CHECKER TOOL** and click **Run workflow** (or wait for the first push build).
6. When the run finishes, open it and download the artifact named `TONEX-PC-CHECKER-TOOL-Windows`.
7. Extract the ZIP. Run `TONEX_PC_CHECKER_TOOL.exe`.

## Notes
- Built for Windows 10/11, 64-bit.
- The Services page is read-only.
- End Task is an ordinary process termination feature; unsaved work in the selected app may be lost.
- Some protected processes may not expose full details without administrator privileges.
- This is a monitoring utility, not an antivirus or cheat detector.
