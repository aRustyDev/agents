MATCH (charlie:Person {name: 'Charlie Sheen'}), (wallStreet:Movie {title: 'Wall
Street'})
MERGE (charlie)-[r:ACTED_IN]->(wallStreet)
RETURN charlie.name, type(r), wallStreet.title

CREATE (n), (m)

C
Cpp
Csharp
Clojure
Elixir
Elm
Erlang
Fsharp
Go
Haskell
Java
JavaScript
julia
ObjC
Python
R
Roc
Rust
Scala
Swift
TypeScript
