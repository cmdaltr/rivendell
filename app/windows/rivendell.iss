; Rivendell's Windows installer (Inno Setup 6). Installs the source tree for the current
; user (no admin), with Start menu and desktop shortcuts to Rivendell.ps1, an optional
; evidence folder mounted through docker-compose.local.yml, and a pointer to Docker
; Desktop when it isn't installed. The release workflow compiles it:
;   ISCC /DAppVersion=1.4.0 /DSourceDir=<unpacked source> /DOutputDir=<dir> rivendell.iss

#ifndef AppVersion
  #define AppVersion "0.0.0"
#endif
#ifndef SourceDir
  #define SourceDir "..\.."
#endif
#ifndef OutputDir
  #define OutputDir "dist"
#endif
#define PowerShell "{sys}\WindowsPowerShell\v1.0\powershell.exe"
; Quotes doubled: it goes inside the quoted Parameters values below
#define Launcher '-NoProfile -ExecutionPolicy Bypass -File ""{app}\app\windows\Rivendell.ps1""'

[Setup]
AppId={{9AA724CE-3AC2-45C6-9E9E-4C2A5DC33BD1}
AppName=Rivendell
AppVersion={#AppVersion}
AppVerName=Rivendell {#AppVersion}
AppPublisher=cmdaltr
AppPublisherURL=https://github.com/cmdaltr/rivendell
AppSupportURL=https://github.com/cmdaltr/rivendell/issues
DefaultDirName={%USERPROFILE}\Rivendell
DisableDirPage=no
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
ArchitecturesAllowed=x64 arm64
ArchitecturesInstallIn64BitMode=x64 arm64
LicenseFile={#SourceDir}\LICENSE
SetupIconFile={#SourceDir}\app\icons\rivendell.ico
UninstallDisplayIcon={app}\app\icons\rivendell.ico
UninstallDisplayName=Rivendell
OutputDir={#OutputDir}
OutputBaseFilename=Rivendell-Setup-{#AppVersion}
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Shortcuts:"

[Files]
Source: "{#SourceDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\Rivendell"; Filename: "{#PowerShell}"; Parameters: "{#Launcher}"; WorkingDir: "{app}"; IconFilename: "{app}\app\icons\rivendell.ico"; Comment: "Rivendell DFIR platform"; Flags: runminimized
Name: "{autoprograms}\Stop Rivendell"; Filename: "{#PowerShell}"; Parameters: "{#Launcher} -Stop"; WorkingDir: "{app}"; IconFilename: "{app}\app\icons\rivendell.ico"; Comment: "Stop Rivendell's containers"; Flags: runminimized
Name: "{autodesktop}\Rivendell"; Filename: "{#PowerShell}"; Parameters: "{#Launcher}"; WorkingDir: "{app}"; IconFilename: "{app}\app\icons\rivendell.ico"; Comment: "Rivendell DFIR platform"; Tasks: desktopicon; Flags: runminimized

[Run]
Filename: "https://www.docker.com/products/docker-desktop/"; Description: "Open the Docker Desktop download page (Rivendell needs it)"; Flags: postinstall shellexec skipifsilent; Check: not DockerInstalled
Filename: "{#PowerShell}"; Parameters: "{#Launcher}"; WorkingDir: "{app}"; Description: "Start Rivendell"; Flags: postinstall nowait skipifsilent runminimized; Check: DockerInstalled

[UninstallDelete]
Type: files; Name: "{app}\.rivendell-version"
Type: files; Name: "{app}\.rivendell-built"

[Code]
const
  LocalHeader = '# Written by Rivendell''s Windows installer';

var
  DockerPage: TOutputMsgWizardPage;
  EvidencePage: TInputDirWizardPage;

function DockerInstalled: Boolean;
begin
  Result := FileExists(ExpandConstant('{commonpf64}\Docker\Docker\Docker Desktop.exe'))
    or (FileSearch('docker.exe', GetEnv('PATH')) <> '');
end;

procedure InitializeWizard;
begin
  DockerPage := CreateOutputMsgPage(wpWelcome, 'Docker Desktop',
    'Rivendell runs as a set of Docker containers.',
    'Docker Desktop isn''t installed. Setup carries on without it, and offers its download page at the end.' + #13#10#13#10 +
    'Install Docker Desktop (it needs WSL 2), start it once, then open Rivendell from the Start menu.' + #13#10#13#10 +
    'Docker Desktop is free for personal use and small businesses; larger organisations need a paid subscription.');

  EvidencePage := CreateInputDirPage(wpSelectDir, 'Evidence folder',
    'Optional: a folder of disk images, memory dumps or Gandalf archives.',
    'Rivendell sees it inside its containers under /mnt/<drive>/..., so D:\Cases becomes /mnt/d/Cases. ' +
    'External drives aren''t visible otherwise. Leave it blank to skip; run setup again to change it.',
    False, '');
  EvidencePage.Add('');
  EvidencePage.Values[0] := GetPreviousData('EvidenceDir', '');
end;

procedure RegisterPreviousData(PreviousDataKey: Integer);
begin
  SetPreviousData(PreviousDataKey, 'EvidenceDir', EvidencePage.Values[0]);
end;

function ShouldSkipPage(PageID: Integer): Boolean;
begin
  Result := (PageID = DockerPage.ID) and DockerInstalled;
end;

function NextButtonClick(CurPageID: Integer): Boolean;
var
  Dir: String;
begin
  Result := True;
  if CurPageID = EvidencePage.ID then
  begin
    Dir := Trim(EvidencePage.Values[0]);
    if (Dir <> '') and ((Length(Dir) < 3) or (Dir[2] <> ':') or not DirExists(Dir)) then
    begin
      MsgBox('Choose an existing folder on a lettered drive (C:\..., D:\...), or leave it blank.', mbError, MB_OK);
      Result := False;
    end;
  end;
end;

function ToContainerPath(Dir: String): String;
var
  Rest: String;
begin
  Rest := Copy(Dir, 3, Length(Dir));
  StringChangeEx(Rest, '\', '/', True);
  if (Length(Rest) > 1) and (Rest[Length(Rest)] = '/') then
    Rest := Copy(Rest, 1, Length(Rest) - 1);
  Result := '/mnt/' + Lowercase(Copy(Dir, 1, 1)) + Rest;
end;

procedure WriteEvidenceCompose;
var
  Dir, Source, Target, LocalFile, Yaml: String;
  Existing: AnsiString;
begin
  LocalFile := ExpandConstant('{app}\docker-compose.local.yml');
  // A hand-written file is left alone
  if FileExists(LocalFile) and LoadStringFromFile(LocalFile, Existing) and (Pos(LocalHeader, String(Existing)) <> 1) then
    Exit;
  Dir := Trim(EvidencePage.Values[0]);
  if Dir = '' then
  begin
    DeleteFile(LocalFile);
    Exit;
  end;
  Source := Dir;
  StringChangeEx(Source, '\', '/', True);
  Target := ToContainerPath(Dir);
  Yaml := LocalHeader + ': the evidence folder, read-only in the backend.' + #10 +
    'services:' + #10 +
    '  backend:' + #10 +
    '    volumes:' + #10 +
    '      - type: bind' + #10 +
    '        source: "' + Source + '"' + #10 +
    '        target: "' + Target + '"' + #10 +
    '        read_only: true' + #10 +
    '  celery-worker:' + #10 +
    '    volumes:' + #10 +
    '      - type: bind' + #10 +
    '        source: "' + Source + '"' + #10 +
    '        target: "' + Target + '"' + #10;
  SaveStringToFile(LocalFile, Yaml, False);
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    SaveStringToFile(ExpandConstant('{app}\.rivendell-version'), '{#AppVersion}', False);
    WriteEvidenceCompose;
  end;
end;
