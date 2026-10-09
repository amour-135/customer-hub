$bytes = [System.IO.File]::ReadAllBytes('C:\workspace\customer-hub\index.html')
$text = [System.Text.Encoding]::UTF8.GetString($bytes)
$idx = $text.IndexOf('refresh-btn')
if ($idx -ge 0) {
    Write-Output ($text.Substring($idx, 70))
    Write-Output ('byte pos:' + $idx)
}