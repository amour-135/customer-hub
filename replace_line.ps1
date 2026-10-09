$content = [System.IO.File]::ReadAllText('C:\workspace\customer-hub\index.html', [System.Text.Encoding]::UTF8)
$lines = $content -split "?
"
$lineIdx = -1
for ($i = 0; $i -lt $lines.Length; $i++) {
    if ($lines[$i] -match 'refresh-btn.*刷新') {
        $lineIdx = $i
        Write-Output ('Line:' + $i + ' => ' + $lines[$i])
        break
    }
}