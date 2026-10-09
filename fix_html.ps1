$bytes = [System.IO.File]::ReadAllBytes('C:\workspace\customer-hub\index.html')
$old = [System.Text.Encoding]::UTF8.GetBytes('  <button class=""refresh-btn"" onclick=""loadData()"">刷新</button>' + ""
"")
$new = [System.Text.Encoding]::UTF8.GetBytes('  <button class=""sync-btn"" onclick=""syncAndReload()"">同步BOSS</button>' + ""
"")
$idx = [System.Array]::IndexOf($bytes, $old[0])
if ($idx -ge 0) {
    $found = $true
    for ($i = 1; $i -lt $old.Length; $i++) {
        if ($bytes[$idx + $i] -ne $old[$i]) { $found = $false; break }
    }
    if ($found) {
        Write-Output 'Found at' $idx 'replacing...'
        $result = New-Object byte[] ($bytes.Length - $old.Length + $new.Length)
        [Array]::Copy($bytes, 0, $result, 0, $idx)
        [Array]::Copy($new, 0, $result, $idx, $new.Length)
        [Array]::Copy($bytes, $idx + $old.Length, $result, $idx + $new.Length, $bytes.Length - $idx - $old.Length)
        [System.IO.File]::WriteAllBytes('C:\workspace\customer-hub\index.html', $result)
        Write-Output 'Done'
    } else { Write-Output 'First byte matches but not full pattern' }
} else { Write-Output 'Pattern not found' }