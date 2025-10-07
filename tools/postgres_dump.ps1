$scriptDir = Split-Path -Path $MyInvocation.MyCommand.Definition -Parent

$secretsDir = Resolve-Path (Join-Path -Path $scriptDir -ChildPath "..\secrets")
$userFile = Join-Path -Path $secretsDir -ChildPath "postgres_user"
$passwordFile = Join-Path -Path $secretsDir -ChildPath "postgres_password"
$dbNameFile = Join-Path -Path $secretsDir -ChildPath "postgres_db"
$dumpDir = Resolve-Path (Join-Path -Path $scriptDir -ChildPath "..\dump")

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$dumpFileName = "dump_${timestamp}.dump"
$dumpFile = Join-Path -Path $dumpDir -ChildPath $dumpFileName
$serviceName = "kokkai-summary-db"

Write-Host "Starting database dump..."
Write-Host "Output file: ${dumpFile}"

$user = Get-Content -Path $userFile -Raw
$password = Get-Content -Path $passwordFile -Raw
$dbName = Get-Content -Path $dbNameFile -Raw

docker exec -e PGPASSWORD=$password $serviceName pg_dump -U $user -d $dbName -F c -f /tmp/$dumpFileName
docker cp ${serviceName}:/tmp/$dumpFileName $dumpFile
docker exec $serviceName rm /tmp/$dumpFileName

if ($LASTEXITCODE -eq 0) {
    Write-Host "Database dump completed successfully."
} else {
    Write-Host "Error: Database dump failed."
}