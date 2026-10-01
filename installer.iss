; Multi Print Setup Script

[Setup]
AppName=Multi Print
AppVersion=1.0.0
AppPublisher=Multi Print Co.
DefaultDirName={pf}\MultiPrint
DefaultGroupName=Multi Print
OutputDir=installer_output
OutputBaseFilename=MultiPrint_Setup
Compression=lzma2
SolidCompression=yes
PrivilegesRequired=admin
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
DisableProgramGroupPage=yes
WizardStyle=modern

[Languages]
Name: "arabic"; MessagesFile: "compiler:Languages\Arabic.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a desktop icon"; GroupDescription: "Additional shortcuts:"

[Files]
; بنضع ملف البرنامج الأساسي (اللي جوه فولدر dist)
Source: "dist\MultiPrint.exe"; DestDir: "{app}"; Flags: ignoreversion
; بنضع مجلد LibreOffice كامل عشان يتحط جنب البرنامج
Source: "dist\libreoffice\*"; DestDir: "{app}\libreoffice"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; عمل شورتكت في قائمة ابدأ
Name: "{group}\Multi Print"; Filename: "{app}\MultiPrint.exe"
; عمل شورتكت على الديسكتوب لو العميل اختار ده
Name: "{commondesktop}\Multi Print"; Filename: "{app}\MultiPrint.exe"; Tasks: desktopicon

[Run]
; تشغيل البرنامج تلقائياً بعد الانتهاء من التسطيب
Filename: "{app}\MultiPrint.exe"; Description: "Launch Multi Print"; Flags: nowait postinstall skipifsilent