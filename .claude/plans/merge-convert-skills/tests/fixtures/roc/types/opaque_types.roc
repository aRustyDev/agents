# Opaque Types
#
# Demonstrates opaque type patterns in Roc for encapsulation.

module [
    Email,
    Password,
    UserId,
    NonEmptyList,
    fromStr,
    toStr,
    createPassword,
    verifyPassword,
    createUserId,
    getUserIdValue,
    fromList,
    head,
    tail,
]

## Opaque type for validated email

Email := Str

fromStr : Str -> Result Email [InvalidEmail]
fromStr = \str ->
    if Str.contains str "@" && Str.contains str "." then
        Ok (@Email str)
    else
        Err InvalidEmail

toStr : Email -> Str
toStr = \@Email str ->
    str

## Opaque type for hashed password

Password := { hash : Str, salt : Str }

createPassword : Str -> Password
createPassword = \plaintext ->
    # Simplified - real implementation would use proper hashing
    salt = "random_salt"
    hash = Str.concat plaintext salt
    @Password { hash, salt }

verifyPassword : Password, Str -> Bool
verifyPassword = \@Password { hash, salt }, attempt ->
    attemptHash = Str.concat attempt salt
    hash == attemptHash

## Opaque type for IDs

UserId := U64

createUserId : U64 -> UserId
createUserId = \id ->
    @UserId id

getUserIdValue : UserId -> U64
getUserIdValue = \@UserId id ->
    id

compareUserIds : UserId, UserId -> [LT, EQ, GT]
compareUserIds = \@UserId a, @UserId b ->
    if a < b then LT
    else if a > b then GT
    else EQ

## Opaque type with invariant: non-empty list

NonEmptyList a := { first : a, rest : List a }

fromList : List a -> Result (NonEmptyList a) [EmptyList]
fromList = \list ->
    when list is
        [first, .. as rest] -> Ok (@NonEmptyList { first, rest })
        [] -> Err EmptyList

head : NonEmptyList a -> a
head = \@NonEmptyList { first } ->
    first

tail : NonEmptyList a -> List a
tail = \@NonEmptyList { rest } ->
    rest

toList : NonEmptyList a -> List a
toList = \@NonEmptyList { first, rest } ->
    List.prepend rest first

length : NonEmptyList a -> U64
length = \@NonEmptyList { rest } ->
    1 + List.len rest

map : NonEmptyList a, (a -> b) -> NonEmptyList b
map = \@NonEmptyList { first, rest }, f ->
    @NonEmptyList {
        first: f first,
        rest: List.map rest f,
    }

## Opaque type for positive integers

PositiveInt := U64

positiveFromI64 : I64 -> Result PositiveInt [NotPositive]
positiveFromI64 = \n ->
    if n > 0 then
        Ok (@PositiveInt (Num.toU64 n))
    else
        Err NotPositive

positiveToU64 : PositiveInt -> U64
positiveToU64 = \@PositiveInt n ->
    n

addPositive : PositiveInt, PositiveInt -> PositiveInt
addPositive = \@PositiveInt a, @PositiveInt b ->
    @PositiveInt (a + b)

## Opaque type for validated ranges

Range := { min : I64, max : I64 }

createRange : I64, I64 -> Result Range [InvalidRange]
createRange = \minVal, maxVal ->
    if minVal <= maxVal then
        Ok (@Range { min: minVal, max: maxVal })
    else
        Err InvalidRange

inRange : Range, I64 -> Bool
inRange = \@Range { min, max }, value ->
    value >= min && value <= max

rangeSize : Range -> U64
rangeSize = \@Range { min, max } ->
    Num.toU64 (max - min + 1)
