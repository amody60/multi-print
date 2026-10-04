; Multi Print Setup Script

[Setup]
AppName=Multi Print
AppVersion=1.0.3
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
SetupIconFile=app_icon.ico  # ✅ إضافة الأيقونة هنا

[Languages]
Name: "arabic"; MessagesFile: "compiler:Languages\Arabic.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a desktop icon"; GroupDescription: "Additional shortcuts:"

[Files]
; بنضع كل ملفات البرنامج من فولدر النسخة الجديد
Source: "dist\1.0.3\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; ✅ بنضع مجلد LibreOffice من المسار الرئيسي للمشروع
Source: "libreoffice\*"; DestDir: "{app}\libreoffice"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; عمل شورتكت في قائمة ابدأ
Name: "{group}\Multi Print"; Filename: "{app}\MultiPrint.exe"
; عمل شورتكت على الديسكتوب لو العميل اختار ده
Name: "{commondesktop}\Multi Print"; Filename: "{app}\MultiPrint.exe"; Tasks: desktopicon

[Run]
; تشغيل البرنامج تلقائياً بعد الانتهاء من التسطيب
Filename: "{app}\MultiPrint.exe"; Description: "Launch Multi Print"; Flags: nowait postinstall skipifsilent