<#
.SYNOPSIS
    ARGUS CCM - Check des capacites materielles et recommandation de modele IA.
.DESCRIPTION
    Detecte RAM / CPU / GPU / disque + presence Docker, Ollama, Terraform, Ansible.
    En deduit un PROFIL d'execution (FULL / LIGHT) et recommande le modele Ollama
    le plus coherent avec la machine (inference CPU vs GPU dedie).
    Aucune modification systeme : lecture seule.
.NOTES
    Projet : grc-argus-ccm (codename ARGUS) - Continuous Controls Monitoring
#>

[CmdletBinding()]
param(
    # Ecrit le resultat en JSON pour consommation par l'agent / le deploiement
    [string]$JsonOut = ""
)

$ErrorActionPreference = "Stop"

function Write-Section([string]$t) { Write-Host "`n===== $t =====" -ForegroundColor Cyan }
function Get-Cmd([string]$name) { (Get-Command $name -ErrorAction SilentlyContinue) }

# ----------------------------------------------------------------------------
# 1. Collecte materielle
# ----------------------------------------------------------------------------
$cpu = Get-CimInstance Win32_Processor | Select-Object -First 1
$cs  = Get-CimInstance Win32_ComputerSystem
$os  = Get-CimInstance Win32_OperatingSystem
$gpu = Get-CimInstance Win32_VideoController | Select-Object -First 1
$disk = Get-PSDrive C

$ramGB      = [math]::Round($cs.TotalPhysicalMemory / 1GB, 1)
$ramFreeGB  = [math]::Round($os.FreePhysicalMemory / 1MB, 1)
$cores      = $cpu.NumberOfCores
$threads    = $cpu.NumberOfLogicalProcessors
$vramGB     = [math]::Round($gpu.AdapterRAM / 1GB, 1)
$diskFreeGB = [math]::Round($disk.Free / 1GB, 1)

# GPU dedie ? (heuristique : VRAM dediee >= 4 Go et pas un controleur integre connu)
$gpuName = $gpu.Name
$isIntegrated = $gpuName -match "Intel|UHD|Iris|AMD Radeon\(TM\) Graphics|Vega \d+ Graphics"
$hasDedicatedGpu = (-not $isIntegrated) -and ($vramGB -ge 4)

# ----------------------------------------------------------------------------
# 2. Collecte outillage
# ----------------------------------------------------------------------------
$dockerOk = $false; $swarmState = "inconnu"; $dockerMemGB = 0
if (Get-Cmd docker) {
    try {
        $dockerOk = $true
        $swarmState = (& docker info --format '{{.Swarm.LocalNodeState}}' 2>$null)
        $memBytes   = (& docker info --format '{{.MemTotal}}' 2>$null)
        if ($memBytes) { $dockerMemGB = [math]::Round([double]$memBytes / 1GB, 1) }
    } catch { $dockerOk = $false }
}

$ollamaOk = [bool](Get-Cmd ollama)
$ollamaModels = @()
if ($ollamaOk) {
    try { $ollamaModels = (& ollama list 2>$null | Select-Object -Skip 1 | ForEach-Object { ($_ -split '\s+')[0] }) | Where-Object { $_ } } catch {}
}

$terraformOk = [bool](Get-Cmd terraform)
$ansibleOk   = [bool](Get-Cmd ansible)   # natif Windows quasi jamais present -> WSL

# ----------------------------------------------------------------------------
# 3. Logique de recommandation
# ----------------------------------------------------------------------------
# Profil d'execution : FULL = Splunk + cible + agent en simultane.
$profile = if ($ramGB -ge 16 -and $dockerOk) { "FULL" }
           elseif ($ramGB -ge 8) { "LIGHT" }
           else { "MINIMAL" }

# Modele IA : sans GPU dedie -> inference CPU -> petit modele obligatoire.
if ($hasDedicatedGpu -and $vramGB -ge 8) {
    $modelReco = "gemma2:9b"
    $modelNote = "GPU dedie suffisant : 9B possible (bonne qualite de redaction)."
} elseif ($hasDedicatedGpu) {
    $modelReco = "gemma2:9b (surveiller la VRAM) ou gemma2:2b"
    $modelNote = "GPU dedie limite : tester 9B, repli 2B si lenteur."
} else {
    $modelReco = "gemma2:2b"
    $modelNote = "Pas de GPU dedie : inference CPU. 2B = bon compromis. Eviter 9B (lent). Appels agent a lancer en asynchrone/batch."
}

# Avertissements concrets
$warnings = New-Object System.Collections.Generic.List[string]
if (-not $dockerOk)              { $warnings.Add("Docker introuvable ou non demarre -> requis pour la stack CCM.") }
elseif ($swarmState -ne "active"){ $warnings.Add("Docker Swarm inactif -> lancer 'docker swarm init' (Phase 1, requis pour secrets + overlay).") }
if (-not $terraformOk)           { $warnings.Add("Terraform absent -> installer le binaire Windows (Phase 1).") }
if (-not $ansibleOk)             { $warnings.Add("Ansible absent en natif (normal sous Windows) -> l'utiliser depuis WSL Ubuntu.") }
if (-not $ollamaOk)              { $warnings.Add("Ollama absent -> requis pour l'agent IA local.") }
elseif ($modelReco -match "2b" -and ($ollamaModels -notcontains "gemma2:2b")) { $warnings.Add("Modele recommande non telecharge -> 'ollama pull gemma2:2b'.") }
if ($diskFreeGB -lt 30)          { $warnings.Add("Moins de 30 Go libres -> images Docker + Splunk peuvent saturer.") }

# ----------------------------------------------------------------------------
# 4. Affichage
# ----------------------------------------------------------------------------
Write-Section "MATERIEL"
Write-Host ("CPU        : {0} ({1}c/{2}t)" -f $cpu.Name.Trim(), $cores, $threads)
Write-Host ("RAM        : {0} Go total / {1} Go libre" -f $ramGB, $ramFreeGB)
Write-Host ("GPU        : {0} (~{1} Go) - {2}" -f $gpuName, $vramGB, $(if($hasDedicatedGpu){"dedie"}else{"integre / CPU pour l'IA"}))
Write-Host ("Disque C:  : {0} Go libres" -f $diskFreeGB)

Write-Section "OUTILLAGE"
Write-Host ("Docker     : {0}{1}" -f $(if($dockerOk){"OK"}else{"ABSENT"}), $(if($dockerOk){" (Swarm: $swarmState, ~$dockerMemGB Go)"}else{""}))
Write-Host ("Ollama     : {0}{1}" -f $(if($ollamaOk){"OK"}else{"ABSENT"}), $(if($ollamaModels){" [$($ollamaModels -join ', ')]"}else{""}))
Write-Host ("Terraform  : {0}" -f $(if($terraformOk){"OK"}else{"ABSENT"}))
Write-Host ("Ansible    : {0}" -f $(if($ansibleOk){"OK"}else{"ABSENT (utiliser WSL)"}))

Write-Section "RECOMMANDATION ARGUS"
Write-Host ("Profil d'execution : {0}" -f $profile) -ForegroundColor Green
Write-Host ("Modele IA recommande : {0}" -f $modelReco) -ForegroundColor Green
Write-Host ("  -> {0}" -f $modelNote)

if ($warnings.Count -gt 0) {
    Write-Section "A TRAITER AVANT DEPLOIEMENT"
    foreach ($w in $warnings) { Write-Host ("  [!] {0}" -f $w) -ForegroundColor Yellow }
} else {
    Write-Host "`nAucune friction bloquante detectee." -ForegroundColor Green
}

# ----------------------------------------------------------------------------
# 5. Sortie JSON optionnelle (consommee par l'agent / deploy)
# ----------------------------------------------------------------------------
$result = [ordered]@{
    timestamp   = (Get-Date).ToString("s")
    ram_gb      = $ramGB
    cpu_cores   = $cores
    cpu_threads = $threads
    gpu_name    = $gpuName
    gpu_vram_gb = $vramGB
    gpu_dedicated = $hasDedicatedGpu
    disk_free_gb  = $diskFreeGB
    docker_ok     = $dockerOk
    swarm_state   = $swarmState
    ollama_ok     = $ollamaOk
    ollama_models = $ollamaModels
    terraform_ok  = $terraformOk
    ansible_ok    = $ansibleOk
    profile       = $profile
    model_reco    = $modelReco
    warnings      = $warnings
}

if ($JsonOut) {
    $result | ConvertTo-Json -Depth 4 | Out-File -FilePath $JsonOut -Encoding utf8
    Write-Host "`nResultat ecrit dans $JsonOut" -ForegroundColor Cyan
}
