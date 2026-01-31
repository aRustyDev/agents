; Tree-sitter query examples for kvconf parser

; Find all string values (both single and double quoted)
(variable
  value: (string_double) @string.double)

(variable
  value: (string_single) @string.single)

; Find all boolean configurations
(variable
  name: (identifier) @key
  value: (bool) @boolean)

; Find URL/URI values
(variable
  value: [(uri) (url)] @url)

; Find numeric values
(variable
  name: (identifier) @key
  value: (integer) @number)

; Find environment variable interpolations
(interpolation
  (identifier) @variable.builtin)

; Find comments
(comment) @comment

; Find specific configuration keys
((identifier) @important
  (#match? @important "^(DATABASE_URL|API_KEY|SECRET)"))

; Find empty values
(variable
  name: (identifier) @key.empty
  value: (empty) @value.empty)

; Find all variables with error nodes
(variable
  (ERROR) @error)