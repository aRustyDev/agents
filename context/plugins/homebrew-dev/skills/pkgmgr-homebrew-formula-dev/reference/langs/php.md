## PHP Formula Patterns

> **Recommended:** Use `language: "autotools"` or `language: "custom"` — PHP extensions use autotools; standalone PHP tools use custom install.

### Overview

PHP projects are rarely Homebrew formulas. PHP extensions use the `phpize`/`configure`/`make` flow. Standalone CLI tools written in PHP typically use a Phar archive or Composer.

### Dependencies

```text
depends_on "php"
```

### Example Pattern (Phar-based)

```text
def install
  bin.install "mytool.phar" => "mytool"
end
```

### Common Issues

- **SAPI builds:** PHP SAPI (Server API) builds are complex — prefer official `php` formula
- **Composer:** Most PHP tools use Composer — consider distributing as a Phar instead
- **Extensions:** PHP extension formulas need `phpize`, `./configure`, `make`
