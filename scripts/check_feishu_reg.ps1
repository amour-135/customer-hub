Get-ChildItem 'HKCU:\SOFTWARE\Classes\feishu' -Recurse -ErrorAction SilentlyContinue | ForEach-Object {
     = .Name
     = (.GetValue('') + ' | ' + .GetValue('(default)'))
    Write-Output ( + ' => ' + )
}