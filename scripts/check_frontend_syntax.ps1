param(
    [string]$Root = "."
)

$targets = @(
    "frontend/static/js/app.js",
    "frontend/static/js/dashboard.js",
    "frontend/static/js/chat.js",
    "frontend/static/js/settings.js"
)

$patterns = @(
    "\?\s+\.",
    "\s\?\.",
    "\?\s+\?"
)

$hasError = $false

foreach ($rel in $targets) {
    $path = Join-Path $Root $rel
    if (-not (Test-Path $path)) {
        continue
    }

    $content = Get-Content -Raw -Path $path

    foreach ($pattern in $patterns) {
        $matches = [regex]::Matches($content, $pattern)
        if ($matches.Count -gt 0) {
            Write-Output "ERROR: invalid syntax pattern '$pattern' in $rel ($($matches.Count) occurrence(s))"
            $hasError = $true
        }
    }
}

if ($hasError) {
    Write-Output "\nFix suggestion: run scripts/fix_frontend_syntax.ps1 before commit."
    exit 1
}

Write-Output "Frontend syntax check passed."
exit 0
