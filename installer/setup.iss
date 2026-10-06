; Inno Setup Script for Avocado Ripeness & Variety Inspector
#define MyAppName "Avocado Ripeness & Variety Inspector"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Avocado Inspection Team"
#define MyAppURL "https://github.com/Kuma2438/Ripeness-Level-Detection-of-Avocado-Fruit-Using-Image-Processing-Technology"
#define MyAppExeName "avocado-inspector.exe"

[Setup]
AppId={{E14A89C2-16B4-4D2A-9372-8C8B3E12D04F}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\AvocadoInspector
DisableProgramGroupPage=yes
OutputBaseFilename=AvocadoInspector-InnoSetup
OutputDir=..\package
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "..\package\avocado-inspector\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
