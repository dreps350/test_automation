param([string]$configPath="sql.config",[string]$queryPath="sql.query")

$sqlConfig = Get-Content $configPath | Out-String | ConvertFrom-StringData

$serverName = Join-Path -Path $sqlConfig.serverName.Replace('"', '') -ChildPath $sqlConfig.instanceName.Replace('"', '')
$uid = $sqlConfig.userName
$pwd = $sqlConfig.userPwd
$query = Get-Content $queryPath

Write-Output "Connecting to $serverName"
$connectionString = "Server=$serverName;Uid=$uid;Pwd=$pwd"
$connection = New-Object System.Data.SqlClient.SqlConnection($connectionString)
$command = New-Object System.Data.SqlClient.SqlCommand($query, $connection)

$connection.Open()

$adapter = new-object System.Data.SqlClient.SqlDataAdapter $command
$dataSet = new-object System.Data.DataSet
$adapter.Fill($dataSet) | Out-Null

$connection.Close() 
$dataSet.Tables