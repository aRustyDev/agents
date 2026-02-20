## Perl Formula Patterns

> **Recommended:** Use `language: "custom"` — Perl tools use custom install with `cpanm` or `Makefile.PL`.

### Overview

Perl tools are rarely Homebrew formulas. Most Perl software is distributed via CPAN. When needed, use `language: "custom"` with `Makefile.PL` or direct install.

### Dependencies

```text
depends_on "perl"
```

### Example Pattern

```text
def install
  system "perl", "Makefile.PL", "INSTALL_BASE=#{libexec}"
  system "make", "install"
  bin.install Dir[libexec/"bin/*"]
end
```

### Common Issues

- **CPAN modules:** Perl dependencies need to be resolved — check for `cpanfile`
- **XS modules:** Perl XS (C extension) modules need compiler deps
- **System Perl vs Homebrew Perl:** Use `depends_on "perl"` for consistent behavior
