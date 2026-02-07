# Module Header Example
#
# Demonstrates the module header format for Roc libraries.

module [
    # Types
    User,
    UserRole,
    ValidationError,
    # Functions
    createUser,
    validateUser,
    updateEmail,
    getUserName,
    isAdmin,
]

## Type definitions

UserRole : [Admin, Moderator, User, Guest]

User : {
    id : U64,
    name : Str,
    email : Str,
    role : UserRole,
    active : Bool,
}

ValidationError : [
    EmptyName,
    InvalidEmail,
    EmailTooLong,
]

## Constructor function

createUser : U64, Str, Str, UserRole -> User
createUser = \id, name, email, role ->
    { id, name, email, role, active: Bool.true }

## Validation

validateUser : { name : Str, email : Str } -> Result {} ValidationError
validateUser = \{ name, email } ->
    if Str.isEmpty name then
        Err EmptyName
    else if !Str.contains email "@" then
        Err InvalidEmail
    else if Str.countUtf8Bytes email > 255 then
        Err EmailTooLong
    else
        Ok {}

## Update functions

updateEmail : User, Str -> User
updateEmail = \user, newEmail ->
    { user & email: newEmail }

updateRole : User, UserRole -> User
updateRole = \user, newRole ->
    { user & role: newRole }

deactivate : User -> User
deactivate = \user ->
    { user & active: Bool.false }

## Accessor functions

getUserName : User -> Str
getUserName = \user ->
    user.name

getUserEmail : User -> Str
getUserEmail = \user ->
    user.email

## Predicate functions

isAdmin : User -> Bool
isAdmin = \user ->
    when user.role is
        Admin -> Bool.true
        _ -> Bool.false

isModerator : User -> Bool
isModerator = \user ->
    when user.role is
        Moderator -> Bool.true
        _ -> Bool.false

isActive : User -> Bool
isActive = \user ->
    user.active

## Internal helper (not exported)

normalizeEmail : Str -> Str
normalizeEmail = \email ->
    Str.toLowercase email
