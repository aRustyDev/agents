# Package Definition
#
# Demonstrates package structure in Roc.

package [
    # Core types
    Core.User,
    Core.Session,
    Core.Permission,

    # Authentication module
    Auth.login,
    Auth.logout,
    Auth.validateToken,

    # Data access
    Data.Query,
    Data.execute,
    Data.transaction,

    # Utilities
    Utils.hash,
    Utils.encrypt,
    Utils.decrypt,
] {
    # External package dependencies
    json: "https://github.com/lukewilliamboswell/roc-json/releases/download/0.6.0/bMPr8pR7hN6eMPz8GdAhGdZJXyf4lxhEI1G_EAe_bS4.tar.br",
    http: "https://github.com/roc-lang/basic-webserver/releases/download/0.4.0/example.tar.br",
}

## This package exposes multiple modules organized by concern:
##
## - Core: Domain types and entities
## - Auth: Authentication and authorization
## - Data: Database operations
## - Utils: Cryptographic utilities
