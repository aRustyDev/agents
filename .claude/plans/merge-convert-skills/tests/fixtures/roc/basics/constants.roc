# Constants in Roc
#
# Demonstrates constant definitions and immutable values.

module [pi, e, goldenRatio, maxSize, defaultTimeout, emptyList, defaultConfig]

## Numeric constants

pi : F64
pi = 3.14159265358979

e : F64
e = 2.71828182845905

goldenRatio : F64
goldenRatio = 1.61803398874989

## Integer constants

maxSize : U64
maxSize = 1_000_000

defaultTimeout : U64
defaultTimeout = 30_000

minValue : I64
minValue = -9_223_372_036_854_775_808

maxValue : I64
maxValue = 9_223_372_036_854_775_807

## String constants

greeting : Str
greeting = "Hello, Roc!"

emptyString : Str
emptyString = ""

multilineString : Str
multilineString =
    """
    This is a
    multiline
    string
    """

## List constants

emptyList : List a
emptyList = []

singletonList : List I64
singletonList = [42]

numberList : List I64
numberList = [1, 2, 3, 4, 5]

## Record constants

defaultConfig : { host : Str, port : U16, timeout : U64 }
defaultConfig = {
    host: "localhost",
    port: 8080,
    timeout: 30000,
}

## Boolean constants

enabled : Bool
enabled = Bool.true

disabled : Bool
disabled = Bool.false
