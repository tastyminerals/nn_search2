; Script generated by the Inno Setup Script Wizard.
; SEE THE DOCUMENTATION FOR DETAILS ON CREATING INNO SETUP SCRIPT FILES!

#define NNSEARCH2_name "nn_search2"
#define NNSEARCH2_version "2.1"
#define NNSEARCH2_publisher "tastyminerals@gmail.com"
#define NNSEARCH2_url "https://github.com/tastyminerals/nn_search2"
#define NNSEARCH2_runfile "nn_search2_win.exe"

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
; Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{42DF91BD-1E72-4A59-8388-AAC2D794577F}
AppName={#NNSEARCH2_name}
AppVersion={#NNSEARCH2_version}
;AppVerName={#NNSEARCH2_name} {#NNSEARCH2_version}
AppPublisher={#NNSEARCH2_publisher}
AppPublisherURL={#NNSEARCH2_url}
AppSupportURL={#NNSEARCH2_url}
AppUpdatesURL={#NNSEARCH2_url}
DefaultGroupName={#NNSEARCH2_name}
AllowNoIcons=yes
DefaultDirName=C:\nn_search2
DisableDirPage=no
LicenseFile=C:\Users\hp-dm\Desktop\nn_search2\LICENSE
InfoBeforeFile=C:\Users\hp-dm\Desktop\nn_search2\README.md
OutputBaseFilename=nn_search2
SetupIconFile=C:\Users\hp-dm\Desktop\nn_search2\data\icons\nn-search.ico
Compression=lzma
SolidCompression=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 0,6.1

[Files]
Source: "C:\Users\hp-dm\Desktop\nn_search2\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "C:\Users\hp-dm\Desktop\nn_search2\data\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "C:\Users\hp-dm\Desktop\nn_search2\nltk_data\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "C:\Users\hp-dm\Desktop\nn_search2\samples\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "C:\Users\hp-dm\Desktop\nn_search2\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "C:\Users\hp-dm\Desktop\nn_search2\data\icons\nn-search.ico"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
 
[Icons]
Name: "{group}\{#NNSEARCH2_name}"; Filename: "{app}\{#NNSEARCH2_runfile}"; WorkingDir: {app}; IconFilename: {app}\data\icons\nn-search.ico; Comment: "nn-search2"
Name: "{group}\{cm:ProgramOnTheWeb,{#NNSEARCH2_name}}"; Filename: "{#NNSEARCH2_url}"
Name: "{group}\{cm:UninstallProgram,{#NNSEARCH2_name}}"; Filename: "{uninstallexe}"
Name: "{commondesktop}\{#NNSEARCH2_name}"; Filename: "{app}\{#NNSEARCH2_runfile}"; WorkingDir: {app}; Tasks: desktopicon; IconFilename: {app}\data\icons\nn-search.ico; Comment: "nn_search2"

[Run]
Filename: "{app}\{#NNSEARCH2_runfile}"; Description: "{cm:LaunchProgram,{#StringChange(NNSEARCH2_name, '&', '&&')}}"; Flags: shellexec postinstall skipifsilent
