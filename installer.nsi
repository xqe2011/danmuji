Unicode True
Name "企鹅弹幕机 版本${VERSION}"
InstallDir $PROGRAMFILES64\qedanmuji
OutFile "Installer.exe"
!include MUI2.nsh
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_LANGUAGE SimpChinese

Section "install"
    ReadRegStr $R0 HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\企鹅弹幕机" "QuietUninstallString"
    ReadRegStr $R1 HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\企鹅弹幕机" "InstallLocation"
    ${IfNot} $R0 == ""
        MessageBox MB_OKCANCEL "已经安装了其他版本的企鹅弹幕机，是否覆盖?" IDOK go
		    Abort
        go:
        DetailPrint "正在卸载旧版本"
        ExecWait "$R0 _?=$R1"
    ${EndIf}

    SetOutPath $INSTDIR
    File /r "dist\launcher\*.*"
    SetOutPath $DESKTOP
    File /oname=企鹅弹幕机帮助文件.txt "help.txt"

    writeUninstaller "$INSTDIR\uninstall.exe"
    createShortCut "$DESKTOP\企鹅弹幕机.lnk" "$INSTDIR\launcher.exe"
    createDirectory "$SMPROGRAMS\企鹅弹幕机"
	createShortCut "$SMPROGRAMS\企鹅弹幕机\企鹅弹幕机.lnk" "$INSTDIR\launcher.exe"
    createShortCut "$SMPROGRAMS\企鹅弹幕机\卸载.lnk" "$INSTDIR\uninstall.exe"

    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\企鹅弹幕机" "DisplayName" "企鹅弹幕机"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\企鹅弹幕机" "DisplayIcon" "$INSTDIR\launcher.exe"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\企鹅弹幕机" "UninstallString" "$\"$INSTDIR\uninstall.exe$\""
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\企鹅弹幕机" "QuietUninstallString" "$\"$INSTDIR\uninstall.exe$\" /S"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\企鹅弹幕机" "InstallLocation" "$\"$INSTDIR$\""
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\企鹅弹幕机" "DisplayVersion" "${VERSION}"
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\企鹅弹幕机" "NoModify" 1
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\企鹅弹幕机" "NoRepair" 1

    Exec '"$WINDIR\NOTEPAD.EXE" "$DESKTOP\企鹅弹幕机帮助文件.txt"'
    Abort
SectionEnd

function un.onInit
    ${IfNot} ${Silent}
        MessageBox MB_OKCANCEL "是否确认删除企鹅弹幕机?" IDOK next
		    Abort
    ${EndIf}
	next:
functionEnd
 
section "uninstall"
	rmDir /r "$SMPROGRAMS\企鹅弹幕机"
    rmDir /r $INSTDIR

	DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\企鹅弹幕机"
sectionEnd