<#
.SYNOPSIS
최종 발표자료 두 개를 PowerPoint의 PDF 저장 기능으로 변환한다.
.DESCRIPTION
OutputDirectory의 PPTX 두 개를 읽기 전용·창 없는 모드로 연다.
같은 폴더에 슬라이드 PDF 두 개를 만들며 원본 PPTX와 기존 PDF는 변경하지 않는다.
입력 경로는 파일 인자로 받고 생성된 PDF 경로를 출력한다.
#>
param([string]$OutputDirectory = (Join-Path $PSScriptRoot '..\docs\presentation'))

$ErrorActionPreference = 'Stop'	# 변환 오류가 나면 성공으로 보고하지 않고 즉시 중단한다.
$outputRoot = (Resolve-Path -LiteralPath $OutputDirectory).Path	# 실제 존재하는 출력 폴더의 절대 경로만 사용한다.
$names = @('a1_1_mission_explanation', 'a1_1_evaluation_qa')	# 사용자가 요청한 두 최종 발표자료만 변환한다.
foreach ($name in $names) {
    if (-not (Test-Path -LiteralPath (Join-Path $outputRoot "$name.pptx"))) {
        throw "Missing final presentation: $name.pptx"
    }
    if (Test-Path -LiteralPath (Join-Path $outputRoot "$name.pdf")) {
        throw "PDF already exists: $name.pdf"
    }
}
$powerPointWasRunning = [bool](Get-Process -Name POWERPNT -ErrorAction SilentlyContinue)	# 사용자가 열어 둔 PowerPoint를 종료하지 않기 위해 시작 상태를 기록한다.
$application = $null
try {
    $application = New-Object -ComObject PowerPoint.Application	# 설치된 PowerPoint의 실제 PDF 저장 엔진을 호출한다.
    foreach ($name in $names) {
        $deck = $null
        try {
            $pptxPath = Join-Path $outputRoot "$name.pptx"
            $pdfPath = Join-Path $outputRoot "$name.pdf"
            $deck = $application.Presentations.Open($pptxPath, -1, 0, 0)	# 읽기 전용·창 없는 모드로 열어 원본 PPTX 편집을 방지한다.
            $pageCount = $deck.Slides.Count	# 변환한 발표자료의 실제 장 수를 완료 기록에 남긴다.
            $deck.SaveAs($pdfPath, 32)	# PowerPoint의 PDF 형식 번호를 사용해 같은 슬라이드 화면을 저장한다.
            Write-Output "PDF: $pdfPath ($pageCount pages)"
        }
        finally {
            if ($null -ne $deck) {
                $deck.Close()	# 이 작업이 연 발표자료만 닫는다.
                [void][System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($deck)	# 파일 핸들과 자동화 객체 참조가 남지 않도록 해제한다.
            }
        }
    }
}
finally {
    if ($null -ne $application) {
        if (-not $powerPointWasRunning -and $application.Presentations.Count -eq 0) {	# 작업이 새로 시작했고 열린 자료가 없는 경우에만 앱을 종료한다.
            $application.Quit()	# 사용자의 기존 PowerPoint 세션은 유지한다.
        }
        [void][System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($application)	# 앱 자동화 참조를 정리해 백그라운드 자원 누수를 방지한다.
    }
}
