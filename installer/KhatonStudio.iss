#define MyAppName "Khaton Studio"
#define MyAppVersion "0.3.0"
#define MyAppPublisher "e3e4e5hoi-star"
#define MyAppExeName "KhatonStudio.exe"

[Setup]
AppId={{B5A7C98A-2F8A-4E9B-9F2A-6B41D9E8F0C4}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\Khaton Studio
DefaultGroupName={#MyAppName}
OutputDir=..\installer-output
OutputBaseFilename=KhatonStudio-Setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=admin
UninstallDisplayIcon={app}\{#MyAppExeName}

[Files]
Source: "..\dist\KhatonStudio.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Khaton Studio"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\Khaton Studio"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional icons:"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch Khaton Studio"; Flags: nowait postinstall skipifsilent
