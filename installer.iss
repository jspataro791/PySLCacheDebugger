; -- 64Bit.iss --
; Demonstrates installation of a program built for the x64 (a.k.a. AMD64)
; architecture.
; To successfully run this installation and the program it installs,
; you must have a "x64" edition of Windows.

; SEE THE DOCUMENTATION FOR DETAILS ON CREATING .ISS SCRIPT FILES!

#define DateTime GetDateTimeString('mmddyyyy', '', '');

[Setup]
AppName=PySLCacheDebugger
AppVersion=0.1
DefaultDirName={pf}\PySLCacheDebugger
DefaultGroupName=PySLCacheDebugger
UninstallDisplayIcon={app}\MyProg.exe
Compression=lzma2
OutputDir=installer
OutputBaseFilename=PySLCacheDebugger_01_{#DateTime}
LicenseFile=LICENSE.txt
SolidCompression=yes
; "ArchitecturesAllowed=x64" specifies that Setup cannot run on
; anything but x64.
ArchitecturesAllowed=x64
; "ArchitecturesInstallIn64BitMode=x64" requests that the install be
; done in "64-bit mode" on x64, meaning it should use the native
; 64-bit Program Files directory and the 64-bit view of the registry.
ArchitecturesInstallIn64BitMode=x64

[Files]
Source: "openjpeg-v2.3.0-windows-x64\*"; DestDir: "{pf}\openjpeg-v2.3.0-windows-x64"; Flags: recursesubdirs
Source: "dist\PySLCacheDebugger\*"; DestDir: "{app}";  Flags: recursesubdirs
Source: "LICENSE.txt"; DestDir: "{app}"; DestName: "LICENSE"
Source: "config\glymur\glymurrc"; DestDir: "{%USERPROFILE}\glymur\"; DestName: "glymurrc"

[Icons]
Name: "{group}\PySLCacheDebugger"; Filename: "{app}\PySLCacheDebugger.exe"
