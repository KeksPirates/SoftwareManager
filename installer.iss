#define MyAppName "SoftwareManager"
#define MyAppPublisher "KeksPirates"
#define MyAppURL "https://github.com/KeksPirates/SoftwareManager"
#define MyAppExeName "SoftwareManager.exe"

; Version is passed via /D on the command line: iscc /DMyAppVersion=...
#ifndef MyAppVersion
  #define MyAppVersion "dev"
#endif

; SourceDir is passed via /D on the command line
#ifndef MySourceDir
  #define MySourceDir "dist-final\SoftwareManager"
#endif

; OutputDir is passed via /D on the command line
#ifndef MyOutputDir
  #define MyOutputDir "dist-final"
#endif

; OutputFilename is passed via /D on the command line
#ifndef MyOutputFilename
  #define MyOutputFilename "SoftwareManager-setup"
#endif

[Setup]
AppId={{8F2E4B6A-1C3D-4E5F-9A7B-0D8E6F2C4A1B}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}/issues
AppUpdatesURL={#MyAppURL}/releases
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
LicenseFile=LICENSE
OutputDir={#MyOutputDir}
OutputBaseFilename={#MyOutputFilename}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
DisableWelcomePage=no
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
UninstallDisplayIcon={app}\{#MyAppExeName}
UninstallDisplayName={#MyAppName}
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
CloseApplications=yes
RestartApplications=yes
ShowLanguageDialog=auto

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "{#MySourceDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
