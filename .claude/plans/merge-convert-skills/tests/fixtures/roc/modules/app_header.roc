# App Header Example
#
# Demonstrates the app header format for Roc applications.

app [main] { pf: platform "https://github.com/roc-lang/basic-cli/releases/download/0.10.0/vNe6s9hWzoTZtFmNkvSvMl63s9gxRRrKX7lRsnq6NDY.tar.br" }

import pf.Stdout
import pf.Stderr
import pf.Task exposing [Task]
import pf.Arg
import pf.Env
import pf.File
import pf.Path

## Main entry point

main : Task {} *
main =
    args <- Task.await Arg.list

    when args is
        [_, "greet", name, ..] -> greetUser name
        [_, "version", ..] -> printVersion
        [_, "help", ..] -> printHelp
        _ -> printUsage

## Command implementations

greetUser : Str -> Task {} *
greetUser = \name ->
    Stdout.line (Str.concat "Hello, " (Str.concat name "!"))

printVersion : Task {} *
printVersion =
    Stdout.line "Version 1.0.0"

printHelp : Task {} *
printHelp =
    {} <- Stdout.line "Available commands:"
    {} <- Stdout.line "  greet <name>  - Greet a user"
    {} <- Stdout.line "  version       - Show version"
    Stdout.line "  help          - Show this help"

printUsage : Task {} *
printUsage =
    Stderr.line "Usage: app <command> [args]"

## Environment variable access

getEnvOrDefault : Str, Str -> Task Str *
getEnvOrDefault = \key, default ->
    result <- Task.attempt (Env.var key)
    when result is
        Ok value -> Task.ok value
        Err _ -> Task.ok default

## File operations

readConfigFile : Task Str [FileReadError]
readConfigFile =
    path = Path.fromStr "config.txt"
    result <- Task.attempt (File.readUtf8 path)
    when result is
        Ok content -> Task.ok content
        Err _ -> Task.err FileReadError

writeLogFile : Str -> Task {} [FileWriteError]
writeLogFile = \content ->
    path = Path.fromStr "app.log"
    result <- Task.attempt (File.writeUtf8 path content)
    when result is
        Ok {} -> Task.ok {}
        Err _ -> Task.err FileWriteError
