[Setup]
AppId={{61E701EC-C5D6-4CF9-9534-34AFCEEA3294}
AppName=Betelgeuse A.I.
AppVersion=0.4.0
AppPublisher=Betelgeuse
DefaultDirName={localappdata}\Programs\Betelgeuse
DefaultGroupName=Betelgeuse
PrivilegesRequired=lowest
OutputDir=..\build\installer
OutputBaseFilename=Betelgeuse-Setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
UninstallDisplayIcon={app}\BetelgeuseAI.exe
DisableProgramGroupPage=yes
[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"
[Tasks]
Name: "desktopicon"; Description: "Criar atalho na área de trabalho"; Flags: unchecked
[Files]
Source: "..\build\desktop\BetelgeuseAI.exe"; DestDir: "{app}"; Flags: ignoreversion
[Icons]
Name: "{userprograms}\Betelgeuse A.I."; Filename: "{app}\BetelgeuseAI.exe"
Name: "{userdesktop}\Betelgeuse A.I."; Filename: "{app}\BetelgeuseAI.exe"; Tasks: desktopicon
[Run]
Filename: "{app}\BetelgeuseAI.exe"; Description: "Abrir Betelgeuse A.I."; Flags: nowait postinstall skipifsilent
