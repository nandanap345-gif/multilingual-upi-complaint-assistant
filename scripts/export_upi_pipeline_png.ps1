$ErrorActionPreference = "Stop"

$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$pngPath = Join-Path $root "analysis\figures\upi_pipeline.png"

Add-Type -AssemblyName PresentationCore,PresentationFramework,WindowsBase,System.Xaml

$width = 1600
$height = 900
$dpi = 96

function New-Brush([string]$hex) {
    $c = [System.Windows.Media.ColorConverter]::ConvertFromString($hex)
    return New-Object System.Windows.Media.SolidColorBrush $c
}

function Add-RoundedRect {
    param(
        [System.Windows.Media.DrawingContext]$Context,
        [double]$X,
        [double]$Y,
        [double]$W,
        [double]$H,
        [double]$R,
        [System.Windows.Media.Brush]$Fill,
        [System.Windows.Media.Brush]$Stroke = $null,
        [double]$StrokeThickness = 0
    )
    $rect = New-Object System.Windows.Rect $X, $Y, $W, $H
    $pen = $null
    if ($Stroke) { $pen = New-Object System.Windows.Media.Pen $Stroke, $StrokeThickness }
    $Context.DrawRoundedRectangle($Fill, $pen, $rect, $R, $R)
}

function Add-Text {
    param(
        [System.Windows.Media.DrawingContext]$Context,
        [string]$Text,
        [double]$X,
        [double]$Y,
        [double]$Size,
        [string]$Hex = "#ffffff",
        [switch]$Bold,
        [switch]$Caps
    )
    if ($Caps) { $Text = $Text.ToUpperInvariant() }
    $typeface = if ($Bold) {
        New-Object System.Windows.Media.Typeface(
            (New-Object System.Windows.FontFamily "Segoe UI"),
            [System.Windows.FontStyles]::Normal,
            [System.Windows.FontWeights]::Bold,
            [System.Windows.FontStretches]::Normal
        )
    } else {
        New-Object System.Windows.Media.Typeface "Segoe UI"
    }
    $brush = New-Brush $Hex
    $ft = New-Object System.Windows.Media.FormattedText(
        $Text,
        [System.Globalization.CultureInfo]::InvariantCulture,
        [System.Windows.FlowDirection]::LeftToRight,
        $typeface,
        $Size,
        $brush,
        1.0
    )
    $Context.DrawText($ft, (New-Object System.Windows.Point $X, $Y))
    return $ft
}

$visual = New-Object System.Windows.Media.DrawingVisual
$dc = $visual.RenderOpen()

# Background
$bg = New-Object System.Windows.Media.LinearGradientBrush
$bg.StartPoint = New-Object System.Windows.Point 0,0
$bg.EndPoint = New-Object System.Windows.Point 1,1
$bg.GradientStops.Add((New-Object System.Windows.Media.GradientStop ([System.Windows.Media.ColorConverter]::ConvertFromString("#081225")), 0.0))
$bg.GradientStops.Add((New-Object System.Windows.Media.GradientStop ([System.Windows.Media.ColorConverter]::ConvertFromString("#0f2042")), 0.45))
$bg.GradientStops.Add((New-Object System.Windows.Media.GradientStop ([System.Windows.Media.ColorConverter]::ConvertFromString("#133a7c")), 1.0))
$dc.DrawRectangle($bg, $null, (New-Object System.Windows.Rect 0,0,$width,$height))

$gridBrush = New-Brush "#0f172a"
$gridBrush.Opacity = 0.06
for ($x = 0; $x -le $width; $x += 42) {
    $dc.DrawLine((New-Object System.Windows.Media.Pen $gridBrush, 1), (New-Object System.Windows.Point $x,0), (New-Object System.Windows.Point $x,$height))
}
for ($y = 0; $y -le $height; $y += 42) {
    $dc.DrawLine((New-Object System.Windows.Media.Pen $gridBrush, 1), (New-Object System.Windows.Point 0,$y), (New-Object System.Windows.Point $width,$y))
}

foreach ($circle in @(
    @{X=1385;Y=110;R=170;Color="#60a5fa";Opacity=0.12},
    @{X=210;Y=790;R=220;Color="#38bdf8";Opacity=0.08},
    @{X=1220;Y=770;R=240;Color="#2563eb";Opacity=0.08}
)) {
    $b = New-Brush $circle.Color
    $b.Opacity = $circle.Opacity
    $dc.DrawEllipse($b, $null, (New-Object System.Windows.Point $circle.X, $circle.Y), $circle.R, $circle.R)
}

$panelBrush = New-Brush "#ffffff"
$panelBrush.Opacity = 0.10
$panelStroke = New-Brush "#93c5fd"
$panelStroke.Opacity = 0.22
Add-RoundedRect $dc 90 245 1420 520 28 $panelBrush $panelStroke 1

Add-Text $dc "Project Pipeline" 90 105 15 "#7dd3fc" -Bold -Caps | Out-Null
Add-Text $dc "UPI Complaint Intelligence" 90 160 44 "#ffffff" -Bold | Out-Null
Add-Text $dc "Multilingual complaint routing with explainable NLP, privacy masking, and support-ready summaries." 90 198 20 "#dbeafe" | Out-Null
Add-Text $dc "Customer-facing flow" 118 292 16 "#ffffff" | Out-Null
Add-Text $dc "complaint text, voice transcription, or sample text" 118 328 16 "#ffffff" | Out-Null

$cardFill = New-Object System.Windows.Media.LinearGradientBrush
$cardFill.StartPoint = New-Object System.Windows.Point 0,0
$cardFill.EndPoint = New-Object System.Windows.Point 0,1
$cardFill.GradientStops.Add((New-Object System.Windows.Media.GradientStop ([System.Windows.Media.ColorConverter]::ConvertFromString("#f8fbff")), 0.0))
$cardFill.GradientStops.Add((New-Object System.Windows.Media.GradientStop ([System.Windows.Media.ColorConverter]::ConvertFromString("#edf4ff")), 1.0))
$cardStroke = New-Brush "#ffffff"

$boxXs = @(110,345,580,815,1050,1285)
foreach ($x in $boxXs) {
    Add-RoundedRect $dc $x 360 205 210 24 $cardFill $cardStroke 1
}

$arrowPen = New-Object System.Windows.Media.Pen (New-Brush "#8ab4ff"), 5
foreach ($coords in @(
    @(315,465,340,465),
    @(550,465,575,465),
    @(785,465,810,465),
    @(1020,465,1045,465),
    @(1255,465,1280,465)
)) {
    $dc.DrawLine($arrowPen, (New-Object System.Windows.Point $coords[0],$coords[1]), (New-Object System.Windows.Point $coords[2],$coords[3]))
    # arrow head
    $x2=$coords[2]; $y2=$coords[3]
    $points = New-Object System.Windows.Media.StreamGeometry
    $g = $points.Open()
    $g.BeginFigure((New-Object System.Windows.Point ($x2+2),($y2-7)), $true, $true)
    $g.LineTo((New-Object System.Windows.Point ($x2+14),$y2), $true, $false)
    $g.LineTo((New-Object System.Windows.Point ($x2+2),($y2+7)), $true, $false)
    $g.Close()
    $points.Freeze()
    $dc.DrawGeometry((New-Brush "#8ab4ff"), $null, $points)
}

function Draw-BoxText($x, $n, $title, $l1, $l2, $l3) {
    Add-Text $dc $n ($x + 30) 408 15 "#2563eb" -Bold -Caps | Out-Null
    Add-Text $dc $title ($x + 30) 440 24 "#10203b" -Bold | Out-Null
    Add-Text $dc $l1 ($x + 30) 472 18 "#334155" | Out-Null
    Add-Text $dc $l2 ($x + 30) 500 18 "#334155" | Out-Null
    Add-Text $dc $l3 ($x + 30) 528 18 "#334155" | Out-Null
}

Draw-BoxText 110 "1" "Input" "Complaint typed or spoken" "English, Hindi, Malayalam," "Hinglish, Romanized text"
Draw-BoxText 345 "2" "Preprocess" "Normalize text and detect" "language or script" "Mask OTP, PIN, UPI ID"
Draw-BoxText 580 "3" "Rule Router" "Keyword and signal scoring" "Intent: pending, failed," "debited, fraud, refund"
Draw-BoxText 815 "4" "ML Fallback" "TF-IDF character n-grams" "+ logistic regression" "Works on messy real text"
Draw-BoxText 1050 "5" "Explain Output" "Confidence, urgency, next" "steps, clarification" "Structured safe summary"
Draw-BoxText 1285 "6" "Support View" "Masked ticket history" "Priority and language" "analytics for support"

$darkPanel = New-Brush "#0b1220"
$darkPanel.Opacity = 0.70
Add-RoundedRect $dc 110 615 1380 105 18 $darkPanel (New-Brush "#60a5fa") 1
Add-Text $dc "Key NLP concepts used" 140 655 16 "#cbd5e1" | Out-Null

function Chip($x, $y, $w, $label) {
    Add-RoundedRect $dc $x $y $w 30 14 (New-Brush "#dbeafe") $null 0
    Add-Text $dc $label ($x + 24) ($y + 8) 14 "#0f172a" -Bold | Out-Null
}

Chip 140 675 150 "Normalization"
Chip 304 675 140 "Language ID"
Chip 458 675 170 "Privacy masking"
Chip 642 675 180 "Rule-based intent"
Chip 836 675 220 "TF-IDF char n-grams"
Chip 1070 675 180 "Confidence scoring"
Chip 1264 675 182 "Ticket analytics"

Add-Text $dc "Use this diagram in your expo deck to explain how a complaint moves from customer input to masked support review." 90 846 16 "#cbd5e1" | Out-Null

$dc.Close()

$bitmap = New-Object System.Windows.Media.Imaging.RenderTargetBitmap($width, $height, $dpi, $dpi, [System.Windows.Media.PixelFormats]::Pbgra32)
$bitmap.Render($visual)
$encoder = New-Object System.Windows.Media.Imaging.PngBitmapEncoder
$encoder.Frames.Add([System.Windows.Media.Imaging.BitmapFrame]::Create($bitmap))
$stream = New-Object System.IO.FileStream($pngPath, [System.IO.FileMode]::Create)
try {
    $encoder.Save($stream)
} finally {
    $stream.Close()
}

Write-Output $pngPath
