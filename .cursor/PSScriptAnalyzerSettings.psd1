@{
    # PowerShell Script Analyzer Rules
    Rules = @{
        PSAvoidUsingCmdletAliases = @{
            Enable = $true
        }
        PSAvoidUsingPositionalParameters = @{
            Enable = $true
        }
        PSUseCompatibleCommands = @{
            Enable = $true
            TargetVersions = @(
                "7.0",
                "6.2",
                "5.1"
            )
        }
        PSUseCompatibleSyntax = @{
            Enable = $true
            TargetVersions = @(
                "7.0",
                "6.2",
                "5.1"
            )
        }
        PSAvoidUsingDoubleQuotesForPaths = @{
            Enable = $true
        }
        PSAvoidUsingInvalidCommandVerbs = @{
            Enable = $true
        }
        PSReservedCmdletChar = @{
            Enable = $true
        }
        PSReservedParams = @{
            Enable = $true
        }
        PSAvoidDefaultValueSwitchParameter = @{
            Enable = $true
        }
        PSAvoidTrailingWhitespace = @{
            Enable = $true
        }
        PSPlaceCloseBrace = @{
            Enable = $true
            NoEmptyLineBefore = $false
            IgnoreOneLineBlock = $true
            NewLineAfter = $true
        }
        PSPlaceOpenBrace = @{
            Enable = $true
            OnSameLine = $true
            NewLineAfter = $true
            IgnoreOneLineBlock = $true
        }
        PSUseConsistentIndentation = @{
            Enable = $true
            IndentationSize = 4
            PipelineIndentation = "IncreaseIndentationForFirstPipeline"
            Kind = "space"
        }
        PSUseConsistentWhitespace = @{
            Enable = $true
            CheckInnerBrace = $true
            CheckOpenBrace = $true
            CheckOpenParen = $true
            CheckOperator = $true
            CheckPipe = $true
            CheckSeparator = $true
        }
        PSAlignAssignmentStatement = @{
            Enable = $true
            CheckHashtable = $true
        }
        PSAvoidUsingShellExecution = @{
            Enable = $true
        }
        # 特にPowerShellで&&を使用しないようにするルール
        PSAvoidUsingBashOperators = @{
            Enable = $true
            OperatorsToAvoid = @(
                "&&",
                "||",
                "|"
            )
        }
    }
} 