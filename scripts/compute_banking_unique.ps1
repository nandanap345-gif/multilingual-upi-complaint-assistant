$paths = @('data/raw_data/banking77_train.csv','data/raw_data/banking77_test.csv')
$labels = @()
foreach ($p in $paths) {
    if (Test-Path $p) {
        $lines = Get-Content $p
        foreach ($line in $lines) {
            if ([string]::IsNullOrWhiteSpace($line)) { continue }
            $idx = $line.LastIndexOf(',')
            if ($idx -lt 0) { continue } else { $labels += $line.Substring($idx+1).Trim() }
        }
    }
}
$uniq = $labels | Sort-Object -Unique
Write-Output "COMBINED_UNIQUE_COUNT:$($uniq.Count)"
foreach ($u in $uniq) { Write-Output "LABEL: $u" }
