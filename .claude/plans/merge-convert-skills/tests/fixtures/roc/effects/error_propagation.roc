# Error Propagation
#
# Demonstrates error handling patterns in Roc.

module [fetchUser, processData, handleAllErrors]

## Error type definitions

NetworkError : [
    ConnectionFailed Str,
    Timeout,
    InvalidResponse,
]

ParseError : [
    InvalidJson Str,
    MissingField Str,
    TypeMismatch { expected : Str, got : Str },
]

ValidationError : [
    InvalidEmail,
    PasswordTooShort U64,
    UserNotFound U64,
]

## Combined error type

AppError : [
    Network NetworkError,
    Parse ParseError,
    Validation ValidationError,
]

## Converting specific errors to general error

wrapNetworkError : Result a NetworkError -> Result a AppError
wrapNetworkError = \result ->
    when result is
        Ok value -> Ok value
        Err e -> Err (Network e)

wrapParseError : Result a ParseError -> Result a AppError
wrapParseError = \result ->
    when result is
        Ok value -> Ok value
        Err e -> Err (Parse e)

wrapValidationError : Result a ValidationError -> Result a AppError
wrapValidationError = \result ->
    when result is
        Ok value -> Ok value
        Err e -> Err (Validation e)

## Simulated network call

fetchData : Str -> Result Str NetworkError
fetchData = \url ->
    if Str.startsWith url "http" then
        Ok "{\"data\": \"value\"}"
    else
        Err (ConnectionFailed "Invalid URL")

## Simulated parsing

parseJson : Str -> Result { data : Str } ParseError
parseJson = \json ->
    if Str.contains json "data" then
        Ok { data: "parsed value" }
    else
        Err (MissingField "data")

## Simulated validation

User : { id : U64, email : Str, name : Str }

validateUser : { data : Str } -> Result User ValidationError
validateUser = \{ data } ->
    if Str.isEmpty data then
        Err (UserNotFound 0)
    else
        Ok { id: 1, email: "user@example.com", name: data }

## Chaining with error propagation

fetchUser : Str -> Result User AppError
fetchUser = \url ->
    jsonResult = fetchData url |> wrapNetworkError

    when jsonResult is
        Err e -> Err e
        Ok json ->
            parseResult = parseJson json |> wrapParseError
            when parseResult is
                Err e -> Err e
                Ok parsed ->
                    validateUser parsed |> wrapValidationError

## Better chaining with try pattern

fetchUserTry : Str -> Result User AppError
fetchUserTry = \url ->
    json <- Result.try (fetchData url |> wrapNetworkError)
    parsed <- Result.try (parseJson json |> wrapParseError)
    validateUser parsed |> wrapValidationError

## Error recovery

recoverFromNetwork : Result a NetworkError -> Result a [UnrecoverableError Str]
recoverFromNetwork = \result ->
    when result is
        Ok value -> Ok value
        Err Timeout -> Err (UnrecoverableError "Request timed out")
        Err (ConnectionFailed msg) -> Err (UnrecoverableError msg)
        Err InvalidResponse -> Err (UnrecoverableError "Invalid response")

## Handling all error cases

handleAllErrors : Result User AppError -> Str
handleAllErrors = \result ->
    when result is
        Ok user -> Str.concat "Success: " user.name
        Err (Network Timeout) -> "Network timeout - please retry"
        Err (Network (ConnectionFailed msg)) -> Str.concat "Connection failed: " msg
        Err (Network InvalidResponse) -> "Invalid server response"
        Err (Parse (InvalidJson msg)) -> Str.concat "Invalid JSON: " msg
        Err (Parse (MissingField field)) -> Str.concat "Missing field: " field
        Err (Parse (TypeMismatch { expected, got })) ->
            Str.concat "Type mismatch: expected " (Str.concat expected (Str.concat ", got " got))
        Err (Validation InvalidEmail) -> "Invalid email address"
        Err (Validation (PasswordTooShort min)) ->
            Str.concat "Password too short, minimum " (Str.concat (Num.toStr min) " characters")
        Err (Validation (UserNotFound id)) ->
            Str.concat "User not found: " (Num.toStr id)

## Default error handling

processData : Str -> User
processData = \url ->
    defaultUser = { id: 0, email: "unknown", name: "Unknown" }

    when fetchUser url is
        Ok user -> user
        Err _ -> defaultUser

## Logging errors

logAndRecover : Result a AppError, a -> a
logAndRecover = \result, default ->
    when result is
        Ok value -> value
        Err e ->
            # In real code, this would log the error
            _errorMsg = handleAllErrors (Err e)
            default
