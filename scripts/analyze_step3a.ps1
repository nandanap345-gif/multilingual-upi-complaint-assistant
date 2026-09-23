$dataset_dir = "data/raw_data"

function Analyze-CsvFile {
    param(
        [string]$Path,
        [bool]$AssumeHeader = $false
    )
    $result = @{ path = $Path; exists = (Test-Path $Path) }
    if (-not $result.exists) { return $result }

    $item = Get-Item $Path
    $result.size_bytes = $item.Length
    $first = Get-Content $Path -TotalCount 1 -ErrorAction Stop
    $result.first_line = $first

    # Heuristic for header
    $hasHeader = $false
    if ($AssumeHeader) { $hasHeader = $true }
    else {
        if ($first -match '^(query|text|label|intent|sentence)\b' -or $first -match ',(intent|label|language|query|text|category)') { $hasHeader = $true }
    }
    $result.has_header = $hasHeader

    $all = Get-Content $Path -ErrorAction Stop
    $result.num_lines = $all.Length
    if ($hasHeader) { $data = $all | Select-Object -Skip 1 } else { $data = $all }
    $result.data_rows = $data.Count

    # Extract label by taking text after last comma (robust to commas in text)
    $labels = @()
    foreach ($line in $data) {
        if ([string]::IsNullOrWhiteSpace($line)) { continue }
        $idx = $line.LastIndexOf(',')
        if ($idx -lt 0) { $val = $line.Trim() } else { $val = $line.Substring($idx+1).Trim() }
        if ($val -ne '') { $labels += $val }
    }
    $result.unique_labels = $labels | Sort-Object -Unique
    $result.unique_label_count = $result.unique_labels.Count

    if ($hasHeader) { $result.columns = $first -split ',' } else { $result.columns = @('text','label') }
    return $result
}

# Analyze BANKING77 files
$train_path = Join-Path $dataset_dir 'banking77_train.csv'
$test_path  = Join-Path $dataset_dir 'banking77_test.csv'
$readme_path = Join-Path $dataset_dir 'banking77_README.md'
$train_info = Analyze-CsvFile -Path $train_path -AssumeHeader:$false
$test_info  = Analyze-CsvFile -Path $test_path -AssumeHeader:$false
$readme_text = ''
if (Test-Path $readme_path) { $readme_text = Get-Content $readme_path -Raw -ErrorAction SilentlyContinue }

$bank_languages = @()
if ($readme_text -match 'Languages' -and $readme_text -match 'English') { $bank_languages = @('English') }
elseif ($readme_text -match 'language:\s*-\s*en') { $bank_languages = @('English') }

$bank_license = ''
if ($readme_text -match 'Creative Commons' -or $readme_text -match 'CC-BY') { $bank_license = 'CC-BY-4.0' }

$bank_prov = [ordered]@{
    dataset = 'BANKING77'
    source_urls = @('https://raw.githubusercontent.com/PolyAI-LDN/task-specific-datasets/master/banking_data/train.csv','https://raw.githubusercontent.com/PolyAI-LDN/task-specific-datasets/master/banking_data/test.csv','https://huggingface.co/datasets/PolyAI/banking77')
    license = $bank_license
    download_date = (Get-Date).ToUniversalTime().ToString('o')
    files = @()
}
$bank_prov.files += [ordered]@{ filename = 'banking77_train.csv'; path = (Resolve-Path $train_path).Path; size_bytes = $train_info.size_bytes; num_lines = $train_info.num_lines; data_rows = $train_info.data_rows; columns = $train_info.columns; unique_label_count = $train_info.unique_label_count }
$bank_prov.files += [ordered]@{ filename = 'banking77_test.csv'; path = (Resolve-Path $test_path).Path; size_bytes = $test_info.size_bytes; num_lines = $test_info.num_lines; data_rows = $test_info.data_rows; columns = $test_info.columns; unique_label_count = $test_info.unique_label_count }
if ($bank_languages.Count -gt 0) { $bank_prov.languages = $bank_languages }

# Write BANKING77 provenance
$bank_prov_path = Join-Path $dataset_dir 'BANKING77_PROVENANCE.json'
$bank_prov | ConvertTo-Json -Depth 10 | Out-File -FilePath $bank_prov_path -Encoding UTF8
Write-Output "WROTE: $bank_prov_path"

# Download karanverma19 CSV
$k_url = 'https://huggingface.co/datasets/karanverma19/Multilingual_Customer_Support_Intent_Dataset_for_Indian_Contexts/resolve/main/multilingual_customer_support_intent_dataset.csv?download=true'
$k_out = Join-Path $dataset_dir 'karanverma19_multilingual_customer_support_intent_dataset.csv'
if (-not (Test-Path $k_out)) {
    try {
        Write-Output 'Downloading karanverma19...'
        Invoke-WebRequest -Uri $k_url -OutFile $k_out -ErrorAction Stop
        Write-Output 'Downloaded karanverma19'
    } catch {
        Write-Output "ERROR: failed to download karanverma19: $($_.Exception.Message)"
        exit 2
    }
} else { Write-Output 'SKIP: karanverma19 already exists' }

# Analyze karanverma19 (has header: query,intent,language,category)
if (Test-Path $k_out) {
    try {
        $k_csv = Import-Csv -Path $k_out -ErrorAction Stop
        $k_num_rows = $k_csv.Count
        $k_columns = ($k_csv | Get-Member -MemberType NoteProperty | Select-Object -ExpandProperty Name)
        $k_unique_intents = ($k_csv | Select-Object -ExpandProperty intent | Sort-Object -Unique)
        $k_unique_intent_count = $k_unique_intents.Count
        $k_languages = ($k_csv | Select-Object -ExpandProperty language | Sort-Object -Unique)
        $k_size = (Get-Item $k_out).Length
        $k_prov = [ordered]@{
            dataset = 'karanverma19'
            source_url = $k_url
            license = 'Apache-2.0 (as reported on Hugging Face)'
            download_date = (Get-Date).ToUniversalTime().ToString('o')
            file = [ordered]@{
                filename = (Split-Path $k_out -Leaf)
                path = (Resolve-Path $k_out).Path
                size_bytes = $k_size
                num_rows = $k_num_rows
                columns = $k_columns
                unique_intent_count = $k_unique_intent_count
                sample_unique_intents = $k_unique_intents[0..([Math]::Min(49,$k_unique_intents.Count-1))]
            }
        }
        if ($k_languages) { $k_prov.languages = $k_languages }
        $k_prov | ConvertTo-Json -Depth 10 | Out-File -FilePath (Join-Path $dataset_dir 'karanverma19_PROVENANCE.json') -Encoding UTF8
        Write-Output 'WROTE: karanverma19_PROVENANCE.json'
    } catch {
        Write-Output "ERROR: analysis failed for karanverma19: $($_.Exception.Message)"
        exit 3
    }
} else { Write-Output 'karanverma19 not downloaded; skipping analysis' }

# Summary
$summary = [ordered]@{
    banking_train = [ordered]@{ path = $train_info.path; data_rows = $train_info.data_rows; unique_label_count = $train_info.unique_label_count }
    banking_test  = [ordered]@{ path = $test_info.path; data_rows = $test_info.data_rows; unique_label_count = $test_info.unique_label_count }
    karanverma19_status = (if (Test-Path $k_out) { 'downloaded' } else { 'missing' })
}
$summary | ConvertTo-Json -Depth 6 | Write-Output
