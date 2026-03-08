param(
    [string]$Root = "."
)

$targets = @(
    "frontend/static/js/app.js",
    "frontend/static/js/dashboard.js",
    "frontend/static/js/chat.js",
    "frontend/static/js/settings.js"
)

foreach ($rel in $targets) {
    $path = Join-Path $Root $rel
    if (-not (Test-Path $path)) {
        continue
    }

    $content = Get-Content -Raw -Path $path

    # Normalize broken optional chaining / nullish patterns that may be reintroduced.
    $fixed = $content
    $fixed = $fixed.Replace(" ? .", "?.")
    $fixed = $fixed.Replace(" ?.", "?.")
    $fixed = $fixed.Replace("? .", "?.")
    $fixed = $fixed.Replace("? ?", "??")

    if ($fixed -ne $content) {
        Set-Content -Path $path -Value $fixed -NoNewline
        Write-Output "fixed: $rel"
    } else {
        Write-Output "ok: $rel"
    }
}
