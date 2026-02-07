# Record Types in Roc
#
# Demonstrates record type definitions and operations.

module [User, Config, Point, Rectangle, createUser, updateEmail, getFullName]

## Simple record type alias

User : {
    id : U64,
    name : Str,
    email : Str,
    age : U8,
}

## Nested record

Config : {
    database : {
        host : Str,
        port : U16,
        name : Str,
    },
    server : {
        host : Str,
        port : U16,
        workers : U8,
    },
}

## Generic point

Point a : { x : a, y : a }

## Rectangle using Point

Rectangle : {
    topLeft : Point F64,
    bottomRight : Point F64,
}

## Record with optional field

UserProfile : {
    user : User,
    bio? : Str,
    website? : Str,
}

## Create record

createUser : U64, Str, Str, U8 -> User
createUser = \id, name, email, age ->
    { id, name, email, age }

## Update record field

updateEmail : User, Str -> User
updateEmail = \user, newEmail ->
    { user & email: newEmail }

## Update multiple fields

updateProfile : User, Str, U8 -> User
updateProfile = \user, newName, newAge ->
    { user & name: newName, age: newAge }

## Access nested fields

getDbHost : Config -> Str
getDbHost = \config ->
    config.database.host

## Destructure in function parameter

getFullName : { firstName : Str, lastName : Str }* -> Str
getFullName = \{ firstName, lastName } ->
    Str.concat firstName (Str.concat " " lastName)

## Record extension (open records)

greet : { name : Str }* -> Str
greet = \record ->
    Str.concat "Hello, " record.name

## Point operations

addPoints : Point (Num a), Point (Num a) -> Point (Num a)
addPoints = \p1, p2 ->
    { x: p1.x + p2.x, y: p1.y + p2.y }

scalePoint : Point (Num a), Num a -> Point (Num a)
scalePoint = \point, factor ->
    { x: point.x * factor, y: point.y * factor }

## Rectangle operations

area : Rectangle -> F64
area = \rect ->
    width = rect.bottomRight.x - rect.topLeft.x
    height = rect.bottomRight.y - rect.topLeft.y
    width * height

contains : Rectangle, Point F64 -> Bool
contains = \rect, point ->
    point.x >= rect.topLeft.x
    && point.x <= rect.bottomRight.x
    && point.y >= rect.topLeft.y
    && point.y <= rect.bottomRight.y
