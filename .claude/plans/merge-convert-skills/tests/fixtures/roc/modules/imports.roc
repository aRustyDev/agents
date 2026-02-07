# Import Examples
#
# Demonstrates various import patterns in Roc.

app [main] { pf: platform "https://github.com/roc-lang/basic-cli/releases/download/0.10.0/vNe6s9hWzoTZtFmNkvSvMl63s9gxRRrKX7lRsnq6NDY.tar.br" }

# Platform imports with aliases
import pf.Stdout
import pf.Task exposing [Task, await]

# Local module imports
import User exposing [User, createUser, validateUser]
import Config exposing [Config, loadConfig]
import Utils

# Selective imports
import Math exposing [sin, cos, sqrt]

# Import all from module
import List
import Str
import Dict

## Using imported functions

main : Task {} *
main =
    # Using qualified names
    {} <- Stdout.line "Starting application..."

    # Using exposed names
    config <- await loadConfig

    # Using fully qualified
    items = List.map [1, 2, 3] (\n -> n * 2)
    joined = Str.joinWith (List.map items Num.toStr) ", "

    {} <- Stdout.line joined

    # Pattern using imports
    user = createUser 1 "Alice" "alice@example.com" User

    when validateUser { name: user.name, email: user.email } is
        Ok {} -> Stdout.line "User is valid"
        Err _ -> Stdout.line "User is invalid"

## Local module usage

applyMath : F64 -> F64
applyMath = \x ->
    # Using exposed functions
    s = sin x
    c = cos x
    sqrt (s * s + c * c)

## Utils module with qualified access

processData : List I64 -> I64
processData = \data ->
    Utils.sum data
    |> Utils.double
    |> Utils.clamp 0 100
