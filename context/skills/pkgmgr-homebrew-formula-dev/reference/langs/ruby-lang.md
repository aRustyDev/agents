## Ruby (Language) Formula Patterns

> **Recommended:** Use `language: "custom"` — Ruby gem-based tools use custom install with bundler or direct gem install.

### Overview

Ruby tools are rarely packaged as Homebrew formulas because RubyGems provides its own distribution. When needed, use `language: "custom"` with gem install or bundler.

### Dependencies

```text
depends_on "ruby"
```

### Example Pattern

```text
def install
  ENV["GEM_HOME"] = libexec
  system "gem", "build", "*.gemspec"
  system "gem", "install", "--no-document", Dir["*.gem"].first
  bin.install Dir[libexec/"bin/*"]
  bin.env_script_all_files libexec/"bin", GEM_HOME: libexec
end
```

### Common Issues

- **System Ruby vs Homebrew Ruby:** Prefer `depends_on "ruby"` for Homebrew's Ruby
- **Native extensions:** Ruby gems with C extensions need compiler deps
- **Bundler:** Some tools need `bundle install` before building
