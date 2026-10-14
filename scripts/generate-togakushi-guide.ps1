$root = Join-Path (Get-Location) 'research/togakushi-attractions'
$imgDir = Join-Path $root 'images'
New-Item -ItemType Directory -Force -Path $imgDir | Out-Null

$items = @(
  @{slug='shrine-complex'; title='Togakushi Shrine complex'; summary="A sacred mountain-shrine complex consisting of five shrines: Hōkōsha, Hino-miko-sha, Chūsha, Kuzuryūsha, and Okusha. The shrines combine mythology, cedar forests, and mountain pilgrimage routes."; json='.firecrawl/img-shrine-complex.json'},
  @{slug='cedar-avenue'; title='Ancient cedar avenue'; summary="The celebrated approach to Okusha is lined with towering, centuries-old cedars. It is one of Togakushi's most atmospheric walks and forms the central approach to the upper shrine."; json='.firecrawl/img-cedar-avenue.json'},
  @{slug='kagamiike'; title='Kagami-ike Pond'; summary="A mirror-like mountain pond known for reflections of the surrounding peaks. It is an easy scenic stop and especially attractive during autumn foliage."; json='.firecrawl/img-kagamiike.json'},
  @{slug='forest-botanical-garden'; title='Togakushi Forest Botanical Garden'; summary="A peaceful woodland garden with walking paths, wetland habitats, ponds, and native alpine plants near the shrine area."; json='.firecrawl/img-botanical-garden.json'},
  @{slug='ninja-museum'; title='Togakushi Ninja Museum and Ninja House'; summary="A small museum dedicated to local ninja traditions, with historical displays, weapons, and a maze-like trick house that is particularly popular with families."; json='.firecrawl/img-ninja-museum.json'},
  @{slug='folk-museum'; title='Togakushi Folk Museum'; summary="A cultural museum preserving local buildings, tools, household objects, and displays about life in the Togakushi mountain settlement."; json='.firecrawl/img-folk-museum.json'},
  @{slug='soba'; title='Togakushi soba'; summary="Togakushi is famous for distinctive hand-made soba served at long-established restaurants around Chūsha and the other shrine areas."; json='.firecrawl/img-soba.json'},
  @{slug='mount-togakushi'; title='Mount Togakushi hiking'; summary="Mountain trails offer dramatic views and a more strenuous experience beyond the shrine walk. Conditions can change quickly, so check weather and trail status before setting out."; json='.firecrawl/img-mount-togakushi.json'},
  @{slug='nature-trails'; title='Togakushi woodland trails'; summary="Shorter forest and nature walks connect the shrine, botanical garden, ponds, and highland scenery, making them a gentler alternative to the more demanding mountain routes."; json='.firecrawl/img-nature-trails.json'},
  @{slug='ski-resort'; title='Togakushi Ski Resort'; summary="A winter ski area with alpine scenery and downhill terrain. In October it is primarily a scenic mountain destination; ski operations are seasonal."; json='.firecrawl/togakushi-ski-official.md'; ski=$true}
)

$rows = New-Object System.Collections.Generic.List[string]
$rows.Add('# Togakushi attractions')
$rows.Add('')
$rows.Add('Short reference guide with three locally downloaded images for each attraction. Image credits and original source pages are listed beneath each image.')
$rows.Add('')
$rows.Add('Images were collected on October 14, 2026. Check the original source pages for current usage rights before republishing.')
$rows.Add('')

foreach ($item in $items) {
  $rows.Add("## $($item.title)")
  $rows.Add('')
  $rows.Add($item.summary)
  $rows.Add('')

  $results = @()
  if ($item.ski) {
    $obj = Get-Content $item.json -Raw | ConvertFrom-Json
    $pattern = 'https://www\.togakushi-ss\.com/[^)\s]+\.(?:jpg|jpeg|png|webp)'
    $urls = [regex]::Matches($obj.markdown, $pattern) | ForEach-Object { $_.Value } | Select-Object -Unique -First 3
    foreach ($u in $urls) {
      $results += [pscustomobject]@{title='Togakushi Ski School / resort image'; imageUrl=$u; url='https://www.togakushi-ss.com/'}
    }
  } else {
    $obj = Get-Content $item.json -Raw | ConvertFrom-Json
    $results = @($obj.data.images | Select-Object -First 3)
  }

  $n = 0
  foreach ($r in $results) {
    $n++
    $u = [string]$r.imageUrl
    $uri = [uri]$u
    $ext = [IO.Path]::GetExtension($uri.AbsolutePath).ToLowerInvariant()
    if ($ext -notin @('.jpg','.jpeg','.png','.webp','.gif')) { $ext = '.jpg' }
    $file = "$($item.slug)-$n$ext"
    $out = Join-Path $imgDir $file
    try {
      Invoke-WebRequest -Uri $u -OutFile $out -Headers @{ 'User-Agent' = 'Mozilla/5.0' } -MaximumRedirection 5 -ErrorAction Stop
      $rows.Add("![ $($item.title) image $n](images/$file)")
      $rows.Add('')
      $sourceTitle = ([string]$r.title).Replace('|', '-').Trim()
      if ([string]::IsNullOrWhiteSpace($sourceTitle)) { $sourceTitle = 'Original image source' }
      $rows.Add("Source: [$sourceTitle]($([string]$r.url))")
      $rows.Add('')
    } catch {
      Write-Warning "Could not download $u : $($_.Exception.Message)"
    }
  }
  $rows.Add('---')
  $rows.Add('')
}

$rows | Set-Content (Join-Path $root 'README.md') -Encoding UTF8
Write-Output "Created $root"
Get-ChildItem $imgDir | Measure-Object | Select-Object -ExpandProperty Count
