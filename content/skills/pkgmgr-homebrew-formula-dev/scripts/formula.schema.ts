module.exports.SCHEMA = {
  $id: 'https://schemas.arusty.dev/homebrew/formula.schema.json',
  $schema: 'https://json-schema.org/draft/2020-12/schema',
  title: 'Homebrew Formulas',
  description: 'Array of Homebrew formula definitions for code generation',
  type: 'object',
  properties: {
    formulas: {
      type: 'array',
      uniqueItems: true,
      items: { $ref: '#/$defs/formula' },
    },
  },
  required: ['formulas'],

  $defs: {
    // ─── Primitive types ───────────────────────────────────────────────

    'url-pattern': {
      title: 'URL Pattern',
      description: 'HTTP(S) URL',
      type: 'string',
      pattern: '^https?://',
      examples: [
        'https://github.com/owner/repo/archive/refs/tags/v1.0.0.tar.gz',
        'https://downloads.example.com/tool-1.2.3.tar.xz',
      ],
    },

    'git-url-pattern': {
      title: 'Git URL Pattern',
      description: 'URL ending in .git for HEAD-only or VCS sources',
      type: 'string',
      pattern: '\\.git$',
      examples: ['https://github.com/owner/repo.git', 'git@github.com:owner/repo.git'],
    },

    'sha256-hash': {
      title: 'SHA-256 Hash',
      description: 'Lowercase hex-encoded SHA-256 digest',
      type: 'string',
      pattern: '^[a-f0-9]{64}$',
      examples: ['e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'],
    },

    'version-string': {
      title: 'Version String',
      description: 'Semantic version (major.minor.patch with optional pre-release)',
      type: 'string',
      pattern: '^\\d+\\.\\d+\\.\\d+([\\-+].+)?$',
      examples: ['1.0.0', '2.3.1-rc1', '0.9.0+build.123'],
    },

    'spdx-identifier': {
      title: 'SPDX License Identifier',
      description: 'Common SPDX license identifier',
      type: 'string',
      enum: [
        'MIT',
        'Apache-2.0',
        'GPL-2.0-only',
        'GPL-2.0-or-later',
        'GPL-3.0-only',
        'GPL-3.0-or-later',
        'LGPL-2.1-only',
        'LGPL-2.1-or-later',
        'LGPL-3.0-only',
        'LGPL-3.0-or-later',
        'BSD-2-Clause',
        'BSD-3-Clause',
        'ISC',
        'MPL-2.0',
        'AGPL-3.0-only',
        'AGPL-3.0-or-later',
        'Unlicense',
        'Zlib',
        'BSL-1.0',
        '0BSD',
        'CC0-1.0',
        'WTFPL',
        'Artistic-2.0',
        'PostgreSQL',
        'OpenSSL',
      ],
    },

    // ─── Complex types ─────────────────────────────────────────────────

    license: {
      title: 'License',
      description: 'SPDX license — simple identifier or complex expression with all_of/any_of/with',
      oneOf: [
        { $ref: '#/$defs/spdx-identifier' },
        {
          type: 'object',
          title: 'Complex License',
          description: 'License expression with combinators',
          properties: {
            all_of: {
              type: 'array',
              description: 'All licenses apply (AND)',
              items: { $ref: '#/$defs/spdx-identifier' },
              examples: [['Apache-2.0', 'MIT']],
            },
            any_of: {
              type: 'array',
              description: 'Any one of these licenses applies (OR)',
              items: { $ref: '#/$defs/spdx-identifier' },
              examples: [['MIT', 'Apache-2.0']],
            },
            with: {
              type: 'array',
              description: 'License exceptions (WITH clause)',
              items: { type: 'string' },
              examples: [['LLVM-exception']],
            },
          },
          additionalProperties: false,
        },
      ],
    },

    'head-config': {
      title: 'HEAD Configuration',
      description: 'Configuration for building from the latest VCS revision',
      type: 'object',
      properties: {
        url: {
          $ref: '#/$defs/git-url-pattern',
          description: 'Git repository URL',
        },
        branch: {
          type: 'string',
          description: 'Branch to track',
          enum: ['main', 'master', 'develop', 'trunk'],
          default: 'main',
          examples: ['main', 'master'],
        },
        revision: {
          type: 'string',
          description: 'Pin to a specific commit SHA',
          examples: ['abc123def456'],
        },
      },
      required: ['url'],
      dependentRequired: { revision: ['url'] },
      additionalProperties: false,
    },

    'bottle-config': {
      title: 'Bottle Configuration',
      description: 'Pre-built binary bottle specification',
      type: 'object',
      properties: {
        cellar: {
          title: 'Cellar',
          description: 'Cellar path or relocatability marker',
          oneOf: [
            {
              type: 'string',
              enum: [':any', ':any_skip_relocation'],
              default: ':any_skip_relocation',
            },
            { type: 'string', pattern: '^/' },
          ],
          examples: [':any_skip_relocation', '/usr/local/Cellar'],
        },
        sha256: {
          type: 'object',
          title: 'Platform SHA256 Map',
          description: 'Map of platform tag to SHA-256 digest',
          additionalProperties: { $ref: '#/$defs/sha256-hash' },
          examples: [
            {
              arm64_sonoma: 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
              ventura: 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
            },
          ],
        },
        rebuild: {
          type: 'integer',
          description: 'Bottle rebuild number',
          minimum: 0,
          default: 0,
          examples: [0, 1],
        },
      },
      additionalProperties: false,
    },

    'livecheck-config': {
      title: 'Livecheck Configuration',
      description: 'Automated version-checking configuration',
      type: 'object',
      properties: {
        url: {
          title: 'Livecheck URL',
          description: 'URL to check or a symbol referencing the formula URL',
          oneOf: [
            { type: 'string', enum: [':stable', ':homepage', ':head', ':url'] },
            { $ref: '#/$defs/url-pattern' },
          ],
          default: ':stable',
          examples: [':stable', ':homepage', 'https://github.com/owner/repo/releases'],
        },
        strategy: {
          type: 'string',
          description: 'Livecheck strategy',
          enum: [
            ':github_latest',
            ':github_releases',
            ':page_match',
            ':header_match',
            ':sparkle',
            ':git',
            ':npm',
            ':pypi',
            ':crate',
          ],
          default: ':github_latest',
          examples: [':github_latest', ':page_match'],
        },
        regex: {
          type: 'string',
          description: 'Ruby regex pattern for version extraction',
          examples: ['/v?(\\d+(?:\\.\\d+)+)/i'],
        },
      },
      allOf: [
        {
          if: { properties: { strategy: { const: ':page_match' } }, required: ['strategy'] },
          then: { required: ['regex'] },
        },
      ],
      additionalProperties: false,
    },

    dependency: {
      title: 'Dependency',
      description: 'A formula or cask dependency',
      type: 'object',
      properties: {
        name: {
          type: 'string',
          description: 'Dependency formula name',
          examples: ['openssl@3', 'pkg-config', 'cmake'],
        },
        type: {
          type: 'string',
          description: 'Dependency type tag',
          enum: [':build', ':test', ':runtime', ':optional', ':recommended'],
          default: ':build',
          examples: [':build', ':test'],
        },
      },
      required: ['name'],
      additionalProperties: false,
    },

    'uses-from-macos': {
      title: 'Uses From macOS',
      description: 'System library provided by macOS; only added as dep on Linux',
      type: 'object',
      properties: {
        name: {
          type: 'string',
          description: 'macOS system library name',
          examples: ['curl', 'zlib', 'libxml2', 'ncurses'],
        },
        since: {
          type: 'string',
          description: 'Minimum macOS version providing this library',
          enum: [
            ':el_capitan',
            ':sierra',
            ':high_sierra',
            ':mojave',
            ':catalina',
            ':big_sur',
            ':monterey',
            ':ventura',
            ':sonoma',
            ':sequoia',
          ],
          examples: [':ventura', ':sonoma'],
        },
      },
      required: ['name'],
      additionalProperties: false,
    },

    resource: {
      title: 'Resource',
      description: 'Additional source archive fetched during install (e.g. Python deps)',
      type: 'object',
      properties: {
        name: {
          type: 'string',
          description: 'Resource name',
          examples: ['certifi', 'urllib3'],
        },
        url: {
          $ref: '#/$defs/url-pattern',
          description: 'Download URL for the resource',
        },
        sha256: {
          $ref: '#/$defs/sha256-hash',
          description: 'SHA-256 of the resource archive',
        },
      },
      required: ['name', 'url', 'sha256'],
      additionalProperties: false,
    },

    'patch-config': {
      title: 'Patch',
      description: 'A patch to apply — external URL or inline diff',
      oneOf: [
        {
          type: 'object',
          title: 'External Patch',
          description: 'Patch fetched from a URL',
          properties: {
            url: { $ref: '#/$defs/url-pattern', description: 'Patch file URL' },
            sha256: { $ref: '#/$defs/sha256-hash', description: 'Patch file SHA-256' },
          },
          required: ['url', 'sha256'],
          additionalProperties: false,
        },
        {
          type: 'string',
          title: 'Inline Patch',
          description: 'Inline diff content (DATA or __END__)',
          examples: ['diff --git a/file.c b/file.c\n...'],
        },
      ],
    },

    'conflicts-with': {
      title: 'Conflicts With',
      description: 'Formula that conflicts with this one',
      type: 'object',
      properties: {
        name: {
          type: 'string',
          description: 'Conflicting formula name',
          examples: ['ripgrep'],
        },
        because: {
          type: 'string',
          description: 'Reason for the conflict',
          examples: ['both install an `rg` binary'],
        },
      },
      required: ['name'],
      additionalProperties: false,
    },

    'keg-only': {
      title: 'Keg Only',
      description: 'Reason this formula is keg-only (not symlinked into prefix)',
      oneOf: [
        {
          type: 'string',
          enum: [':versioned_formula', ':provided_by_macos', ':shadowed_by_macos'],
        },
        {
          type: 'string',
          description: 'Custom keg-only reason',
          examples: ['this formula conflicts with the system version'],
        },
      ],
    },

    deprecation: {
      title: 'Deprecation',
      description: 'Deprecation notice with date and reason',
      type: 'object',
      properties: {
        date: {
          type: 'string',
          description: 'Deprecation date (ISO 8601)',
          pattern: '^\\d{4}-\\d{2}-\\d{2}$',
          examples: ['2024-01-15'],
        },
        because: {
          type: 'string',
          description: 'Reason for deprecation',
          examples: [':unsupported', ':repo_archived', 'no longer maintained'],
        },
      },
      required: ['date', 'because'],
      additionalProperties: false,
    },

    'fails-with': {
      title: 'Fails With',
      description: 'Compiler version known to mis-compile this formula',
      type: 'object',
      properties: {
        compiler: {
          type: 'string',
          description: 'Compiler name',
          enum: [':gcc', ':clang', ':llvm_gcc'],
          examples: [':gcc'],
        },
        version: {
          type: 'string',
          description: 'Compiler version range',
          examples: ['5', '< 11'],
        },
        cause: {
          type: 'string',
          description: 'Why it fails',
          examples: ['internal compiler error'],
        },
      },
      required: ['compiler'],
      additionalProperties: false,
    },

    'on-platform': {
      title: 'Platform-specific Configuration',
      description: 'Dependencies and env overrides for a specific OS',
      type: 'object',
      properties: {
        dependencies: {
          type: 'array',
          uniqueItems: true,
          items: { $ref: '#/$defs/dependency' },
          description: 'Platform-specific dependencies',
        },
        env: {
          type: 'object',
          description: 'Environment variable overrides',
          additionalProperties: { type: 'string' },
          examples: [{ LDFLAGS: '-lrt' }],
        },
      },
      additionalProperties: false,
    },

    'service-config': {
      title: 'Service Configuration',
      description: 'launchd/systemd service definition',
      type: 'object',
      properties: {
        run: {
          description: 'Command to run (string or array)',
          oneOf: [
            { type: 'string', examples: ['#{opt_bin}/myservice'] },
            {
              type: 'array',
              items: { type: 'string' },
              examples: [['#{opt_bin}/myservice', '--config', '#{etc}/my.conf']],
            },
          ],
        },
        run_type: {
          type: 'string',
          description: 'How the service is managed',
          enum: [':immediate', ':interval', ':cron'],
          default: ':immediate',
          examples: [':immediate', ':interval'],
        },
        interval: {
          type: 'integer',
          description: 'Run interval in seconds (when run_type is :interval)',
          minimum: 1,
          examples: [300, 3600],
        },
        cron: {
          type: 'string',
          description: 'Cron schedule (when run_type is :cron)',
          examples: ['0 * * * *'],
        },
        keep_alive: {
          title: 'Keep Alive',
          description: 'Whether to restart the service if it exits',
          oneOf: [
            { type: 'boolean', default: false },
            {
              type: 'object',
              properties: {
                always: { type: 'boolean' },
                successful_exit: { type: 'boolean' },
                crashed: { type: 'boolean' },
              },
              additionalProperties: false,
            },
          ],
          examples: [true, { crashed: true }],
        },
        log_path: {
          type: 'string',
          description: 'Path for stdout log',
          examples: ['#{var}/log/myservice.log'],
        },
        error_log_path: {
          type: 'string',
          description: 'Path for stderr log',
          examples: ['#{var}/log/myservice-error.log'],
        },
        environment_variables: {
          type: 'object',
          description: 'Environment variables for the service',
          additionalProperties: { type: 'string' },
          examples: [{ LANG: 'en_US.UTF-8' }],
        },
        working_dir: {
          type: 'string',
          description: 'Working directory for the service',
          examples: ['#{var}/lib/myservice'],
        },
      },
      required: ['run'],
      allOf: [
        {
          if: { properties: { run_type: { const: ':interval' } }, required: ['run_type'] },
          then: { required: ['interval'] },
        },
        {
          if: { properties: { run_type: { const: ':cron' } }, required: ['run_type'] },
          then: { required: ['cron'] },
        },
      ],
      additionalProperties: false,
    },

    // ─── Language-specific install configs ──────────────────────────────

    'install-go': {
      title: 'Go Install Configuration',
      description: 'Install config for Go formulas',
      $comment: 'Ruby DSL: std_go_args(ldflags:, output:)',
      type: 'object',
      properties: {
        cmd_path: {
          type: 'string',
          description: 'Go package path to build (relative to module root)',
          default: './cmd/...',
          examples: ['./cmd/mytool', './'],
        },
        ldflags: {
          type: 'string',
          description: 'Linker flags passed via -ldflags',
          default: '-s -w -X main.version=#{version}',
          examples: ['-s -w -X main.version=#{version}'],
        },
        output: {
          type: 'string',
          description: 'Output binary name (defaults to formula name)',
          examples: ['mytool'],
        },
        tags: {
          type: 'array',
          items: { type: 'string' },
          description: 'Go build tags',
          examples: [['netgo', 'osusergo']],
        },
        env: {
          type: 'object',
          description: 'Environment variables for go build',
          additionalProperties: { type: 'string' },
          examples: [{ CGO_ENABLED: '0' }],
        },
      },
      additionalProperties: false,
    },

    'install-rust': {
      title: 'Rust Install Configuration',
      description: 'Install config for Rust/Cargo formulas',
      $comment: 'Ruby DSL: std_cargo_args(path:, features:)',
      type: 'object',
      properties: {
        path: {
          type: 'string',
          description: 'Path to Cargo.toml directory',
          default: '.',
          examples: ['.', 'crates/cli'],
        },
        features: {
          type: 'array',
          items: { type: 'string' },
          description: 'Cargo features to enable',
          examples: [['tls', 'jemalloc']],
        },
        all_features: {
          type: 'boolean',
          description: 'Enable all Cargo features',
          default: false,
        },
        no_default_features: {
          type: 'boolean',
          description: 'Disable default Cargo features',
          default: false,
        },
        bins: {
          type: 'array',
          items: { type: 'string' },
          description: 'Specific binaries to install',
          examples: [['mytool', 'mytool-helper']],
        },
      },
      additionalProperties: false,
    },

    'install-python': {
      title: 'Python Install Configuration',
      description: 'Install config for Python formulas',
      $comment: 'Ruby DSL: virtualenv_install_with_resources',
      type: 'object',
      properties: {
        python_version: {
          type: 'string',
          description: 'Python version to use',
          default: 'python3',
          examples: ['python3', 'python@3.12'],
        },
        resources: {
          type: 'array',
          uniqueItems: true,
          items: { $ref: '#/$defs/resource' },
          description: 'Python package resources to install',
        },
        using: {
          type: 'string',
          description: 'Install method',
          enum: ['virtualenv', 'pip', 'setuptools'],
          default: 'virtualenv',
          examples: ['virtualenv'],
        },
        site_packages: {
          type: 'boolean',
          description: 'Allow access to system site-packages',
          default: false,
        },
      },
      additionalProperties: false,
    },

    'install-nodejs': {
      title: 'Node.js Install Configuration',
      description: 'Install config for Node.js/npm formulas',
      $comment: 'Ruby DSL: std_npm_args',
      type: 'object',
      properties: {
        node_version: {
          type: 'string',
          description: 'Node.js version dependency',
          default: 'node',
          examples: ['node', 'node@20'],
        },
        npm_install: {
          type: 'boolean',
          description: 'Use npm install for building',
          default: true,
        },
        build_from_source: {
          type: 'boolean',
          description: 'Build native addons from source',
          default: false,
        },
      },
      additionalProperties: false,
    },

    'install-cmake': {
      title: 'CMake Install Configuration',
      description: 'Install config for CMake-based formulas',
      $comment: 'Ruby DSL: std_cmake_args',
      type: 'object',
      properties: {
        source_dir: {
          type: 'string',
          description: 'Path to CMakeLists.txt directory',
          default: '.',
          examples: ['.', 'src'],
        },
        build_dir: {
          type: 'string',
          description: 'Out-of-source build directory',
          default: 'build',
          examples: ['build'],
        },
        cmake_args: {
          type: 'array',
          items: { type: 'string' },
          description: 'Additional CMake arguments',
          examples: [['-DBUILD_SHARED_LIBS=ON', '-DCMAKE_BUILD_TYPE=Release']],
        },
      },
      additionalProperties: false,
    },

    'install-autotools': {
      title: 'Autotools Install Configuration',
      description: 'Install config for autotools (./configure && make) formulas',
      $comment: 'Ruby DSL: std_configure_args',
      type: 'object',
      properties: {
        configure_args: {
          type: 'array',
          items: { type: 'string' },
          description: 'Extra arguments to ./configure',
          examples: [['--enable-shared', '--disable-static']],
        },
        autoreconf: {
          type: 'boolean',
          description: 'Run autoreconf -fiv before configure',
          default: false,
        },
      },
      additionalProperties: false,
    },

    'install-meson': {
      title: 'Meson Install Configuration',
      description: 'Install config for Meson-based formulas',
      $comment: 'Ruby DSL: std_meson_args',
      type: 'object',
      properties: {
        build_dir: {
          type: 'string',
          description: 'Build directory',
          default: 'build',
          examples: ['build'],
        },
        meson_args: {
          type: 'array',
          items: { type: 'string' },
          description: 'Additional Meson arguments',
          examples: [['-Dfeature=enabled']],
        },
      },
      additionalProperties: false,
    },

    'install-java': {
      title: 'Java Install Configuration',
      description: 'Install config for Java formulas',
      $comment: 'Ruby DSL: write_jar_script',
      type: 'object',
      properties: {
        java_version: {
          type: 'string',
          description: 'Java version dependency',
          default: 'openjdk',
          examples: ['openjdk', 'openjdk@17', 'openjdk@21'],
        },
        build_system: {
          type: 'string',
          description: 'Java build system',
          enum: ['maven', 'gradle', 'ant', 'manual'],
          default: 'maven',
          examples: ['maven', 'gradle'],
        },
        jar_path: {
          type: 'string',
          description: 'Path to the output JAR file',
          examples: ['target/mytool.jar'],
        },
        wrapper_name: {
          type: 'string',
          description: 'Name for the shell wrapper script',
          examples: ['mytool'],
        },
      },
      dependentRequired: { jar_path: ['wrapper_name'] },
      additionalProperties: false,
    },

    'install-zig': {
      title: 'Zig Install Configuration',
      description: 'Install config for Zig formulas',
      $comment: 'Ruby DSL: zig build',
      type: 'object',
      properties: {
        build_mode: {
          type: 'string',
          description: 'Zig build optimization mode',
          enum: ['ReleaseSafe', 'ReleaseFast', 'ReleaseSmall', 'Debug'],
          default: 'ReleaseSafe',
          examples: ['ReleaseSafe', 'ReleaseFast'],
        },
        targets: {
          type: 'array',
          items: { type: 'string' },
          description: 'Zig build targets',
          examples: [['install']],
        },
      },
      additionalProperties: false,
    },

    'install-make': {
      title: 'Make Install Configuration',
      description: 'Install config for Makefile-based formulas',
      $comment: 'Ruby DSL: system "make", "install"',
      type: 'object',
      properties: {
        make_args: {
          type: 'array',
          items: { type: 'string' },
          description: 'Extra arguments to make',
          examples: [['CC=#{ENV.cc}', 'PREFIX=#{prefix}']],
        },
        make_targets: {
          type: 'array',
          items: { type: 'string' },
          description: 'Make targets to build before install',
          default: ['all'],
          examples: [['all']],
        },
        install_target: {
          type: 'string',
          description: 'Make install target',
          default: 'install',
          examples: ['install'],
        },
      },
      additionalProperties: false,
    },

    'install-custom': {
      title: 'Custom Install Configuration',
      description: 'Install config for formulas with non-standard build systems',
      $comment: 'Ruby DSL: custom install block',
      type: 'object',
      properties: {
        commands: {
          type: 'array',
          items: { type: 'string' },
          description: 'Sequence of Ruby DSL commands for the install block',
          examples: [['system "make"', 'bin.install "mybinary"']],
        },
      },
      required: ['commands'],
      additionalProperties: false,
    },

    'install-swift': {
      title: 'Swift Install Configuration',
      description: 'Install config for Swift formulas',
      $comment: 'Ruby DSL: swift build',
      type: 'object',
      properties: {
        configuration: {
          type: 'string',
          description: 'Build configuration',
          enum: ['release', 'debug'],
          default: 'release',
          examples: ['release'],
        },
        static_linking: {
          type: 'boolean',
          description: 'Use static linking',
          default: true,
        },
        build_args: {
          type: 'array',
          items: { type: 'string' },
          description: 'Additional swift build arguments',
          examples: [['--disable-sandbox']],
        },
      },
      additionalProperties: false,
    },

    'install-elixir': {
      title: 'Elixir Install Configuration',
      description: 'Install config for Elixir/Mix formulas',
      $comment: 'Ruby DSL: mix escript.build',
      type: 'object',
      properties: {
        mix_env: {
          type: 'string',
          description: 'MIX_ENV value',
          default: 'prod',
          examples: ['prod'],
        },
        build_type: {
          type: 'string',
          description: 'Build output type',
          enum: ['escript', 'release'],
          default: 'escript',
          examples: ['escript'],
        },
      },
      additionalProperties: false,
    },

    'install-haskell': {
      title: 'Haskell Install Configuration',
      description: 'Install config for Haskell formulas',
      $comment: 'Ruby DSL: cabal v2-install or stack',
      type: 'object',
      properties: {
        build_system: {
          type: 'string',
          description: 'Haskell build system',
          enum: ['cabal', 'stack'],
          default: 'cabal',
          examples: ['cabal', 'stack'],
        },
        flags: {
          type: 'array',
          items: { type: 'string' },
          description: 'Cabal flags or Stack arguments',
          examples: [['-f', 'threaded']],
        },
      },
      additionalProperties: false,
    },

    'install-kotlin': {
      title: 'Kotlin Install Configuration',
      description: 'Install config for Kotlin/Gradle formulas',
      $comment: 'Ruby DSL: gradle installDist',
      type: 'object',
      properties: {
        gradle_task: {
          type: 'string',
          description: 'Gradle task to run',
          default: 'installDist',
          examples: ['installDist', 'shadowJar'],
        },
        java_version: {
          type: 'string',
          description: 'Java version dependency',
          default: 'openjdk',
          examples: ['openjdk', 'openjdk@17'],
        },
        wrapper_name: {
          type: 'string',
          description: 'Name for the shell wrapper script',
          examples: ['mytool'],
        },
      },
      additionalProperties: false,
    },

    'install-scala': {
      title: 'Scala Install Configuration',
      description: 'Install config for Scala/sbt formulas',
      $comment: 'Ruby DSL: sbt assembly',
      type: 'object',
      properties: {
        sbt_task: {
          type: 'string',
          description: 'sbt task to run',
          default: 'assembly',
          examples: ['assembly', 'universal:packageBin'],
        },
        java_version: {
          type: 'string',
          description: 'Java version dependency',
          default: 'openjdk',
          examples: ['openjdk', 'openjdk@17'],
        },
        wrapper_name: {
          type: 'string',
          description: 'Name for the shell wrapper script',
          examples: ['mytool'],
        },
      },
      additionalProperties: false,
    },

    'install-erlang-app': {
      title: 'Erlang Application Install Configuration',
      description: 'Install config for Erlang/rebar3 formulas',
      $comment: 'Ruby DSL: rebar3 escriptize',
      type: 'object',
      properties: {
        build_type: {
          type: 'string',
          description: 'Build output type',
          enum: ['escript', 'release'],
          default: 'escript',
          examples: ['escript'],
        },
        rebar3_args: {
          type: 'array',
          items: { type: 'string' },
          description: 'Additional rebar3 arguments',
        },
      },
      additionalProperties: false,
    },

    'install-ocaml': {
      title: 'OCaml Install Configuration',
      description: 'Install config for OCaml formulas',
      $comment: 'Ruby DSL: dune build',
      type: 'object',
      properties: {
        build_system: {
          type: 'string',
          description: 'OCaml build system',
          enum: ['dune', 'opam'],
          default: 'dune',
          examples: ['dune', 'opam'],
        },
        dune_args: {
          type: 'array',
          items: { type: 'string' },
          description: 'Additional dune arguments',
        },
      },
      additionalProperties: false,
    },

    'install-nim': {
      title: 'Nim Install Configuration',
      description: 'Install config for Nim formulas',
      $comment: 'Ruby DSL: nimble build',
      type: 'object',
      properties: {
        nimble_args: {
          type: 'array',
          items: { type: 'string' },
          description: 'Additional nimble build arguments',
          examples: [['-y', '--verbose']],
        },
      },
      additionalProperties: false,
    },

    'install-dart': {
      title: 'Dart Install Configuration',
      description: 'Install config for Dart formulas',
      $comment: 'Ruby DSL: dart compile exe',
      type: 'object',
      properties: {
        compile_target: {
          type: 'string',
          description: 'Dart compile target type',
          enum: ['exe', 'aot-snapshot', 'kernel'],
          default: 'exe',
          examples: ['exe'],
        },
        source_file: {
          type: 'string',
          description: 'Main Dart file to compile',
          default: 'bin/main.dart',
          examples: ['bin/main.dart'],
        },
      },
      additionalProperties: false,
    },

    'install-gleam': {
      title: 'Gleam Install Configuration',
      description: 'Install config for Gleam formulas',
      $comment: 'Ruby DSL: gleam export erlang-shipment',
      type: 'object',
      properties: {
        export_type: {
          type: 'string',
          description: 'Gleam export type',
          enum: ['erlang-shipment', 'hex-tarball'],
          default: 'erlang-shipment',
          examples: ['erlang-shipment'],
        },
      },
      additionalProperties: false,
    },

    'install-roc': {
      title: 'Roc Install Configuration',
      description: 'Install config for Roc formulas',
      $comment: 'Ruby DSL: roc build --optimize',
      type: 'object',
      properties: {
        optimize: {
          type: 'boolean',
          description: 'Enable optimized build',
          default: true,
        },
        source_file: {
          type: 'string',
          description: 'Main Roc source file',
          default: 'main.roc',
          examples: ['main.roc', 'src/main.roc'],
        },
      },
      additionalProperties: false,
    },

    'install-julia': {
      title: 'Julia Install Configuration',
      description: 'Install config for Julia formulas',
      $comment: 'Ruby DSL: write script wrapper',
      type: 'object',
      properties: {
        script_path: {
          type: 'string',
          description: 'Path to main Julia script',
          default: 'src/main.jl',
          examples: ['src/main.jl', 'bin/main.jl'],
        },
        depot_path: {
          type: 'string',
          description: 'Julia depot path for packages',
          default: '#{libexec}/julia',
          examples: ['#{libexec}/julia'],
        },
      },
      additionalProperties: false,
    },

    'install-dotnet': {
      title: '.NET Install Configuration',
      description: 'Install config for .NET (C#/F#) formulas',
      $comment: 'Ruby DSL: dotnet publish',
      type: 'object',
      properties: {
        project: {
          type: 'string',
          description: 'Project or solution file to build',
          examples: ['src/MyApp/MyApp.csproj', 'MyApp.sln'],
        },
        configuration: {
          type: 'string',
          description: 'Build configuration',
          default: 'Release',
          examples: ['Release'],
        },
        self_contained: {
          type: 'boolean',
          description: 'Publish as self-contained',
          default: false,
        },
        framework: {
          type: 'string',
          description: 'Target framework',
          examples: ['net8.0', 'net9.0'],
        },
      },
      additionalProperties: false,
    },

    // ─── Main formula definition ───────────────────────────────────────

    formula: {
      title: 'Homebrew Formula',
      description: 'A single Homebrew formula definition',
      type: 'object',
      properties: {
        // Core fields
        name: {
          type: 'string',
          description: 'Formula name (kebab-case, lowercase)',
          pattern: '^[a-z][a-z0-9]*(-[a-z0-9]+)*$',
          examples: ['my-tool', 'openssl@3'],
        },
        desc: {
          type: 'string',
          description: 'Short description displayed in brew info',
          maxLength: 80,
          examples: ['A command-line tool for doing something useful'],
        },
        homepage: {
          $ref: '#/$defs/url-pattern',
          description: 'Project homepage URL',
          examples: ['https://github.com/owner/repo'],
        },
        url: {
          $ref: '#/$defs/url-pattern',
          description: 'Source tarball URL',
        },
        sha256: {
          $ref: '#/$defs/sha256-hash',
          description: 'SHA-256 of the source tarball',
        },
        version: {
          $ref: '#/$defs/version-string',
          description: 'Explicit version override (usually inferred from URL)',
        },
        revision: {
          type: 'integer',
          description: 'Formula revision number (bump when formula changes but version does not)',
          minimum: 0,
          default: 0,
          examples: [0, 1],
        },
        license: {
          $ref: '#/$defs/license',
          description: 'SPDX license expression',
        },
        head: {
          $ref: '#/$defs/head-config',
          description: 'HEAD-only build configuration',
        },
        bottle: {
          $ref: '#/$defs/bottle-config',
          description: 'Pre-built bottle specification',
        },
        livecheck: {
          $ref: '#/$defs/livecheck-config',
          description: 'Automated version checking',
        },
        language: {
          type: 'string',
          description: 'Primary build language/system (drives install config shape)',
          enum: [
            'go',
            'rust',
            'python',
            'nodejs',
            'cmake',
            'autotools',
            'meson',
            'java',
            'zig',
            'make',
            'custom',
            'swift',
            'elixir',
            'haskell',
            'kotlin',
            'scala',
            'erlang',
            'ocaml',
            'nim',
            'dart',
            'gleam',
            'roc',
            'julia',
            'dotnet',
          ],
          examples: ['go', 'rust', 'python'],
        },

        // Arrays
        dependencies: {
          type: 'array',
          uniqueItems: true,
          items: { $ref: '#/$defs/dependency' },
          description: 'Formula dependencies',
        },
        uses_from_macos: {
          type: 'array',
          uniqueItems: true,
          items: { $ref: '#/$defs/uses-from-macos' },
          description: 'System libraries provided by macOS',
        },
        resources: {
          type: 'array',
          uniqueItems: true,
          items: { $ref: '#/$defs/resource' },
          description: 'Additional source archives',
        },
        patches: {
          type: 'array',
          uniqueItems: true,
          items: { $ref: '#/$defs/patch-config' },
          description: 'Patches to apply to the source',
        },
        conflicts_with: {
          type: 'array',
          uniqueItems: true,
          items: { $ref: '#/$defs/conflicts-with' },
          description: 'Formulas that conflict with this one',
        },
        skip_clean: {
          type: 'array',
          uniqueItems: true,
          items: { type: 'string' },
          description: 'Paths to skip during post-install cleanup',
          examples: [['libexec']],
        },
        link_overwrite: {
          type: 'array',
          uniqueItems: true,
          items: { type: 'string' },
          description: 'Files allowed to overwrite during linking',
          examples: [['bin/tool']],
        },
        fails_with: {
          type: 'array',
          uniqueItems: true,
          items: { $ref: '#/$defs/fails-with' },
          description: 'Known compiler incompatibilities',
        },

        // Scalars
        caveats: {
          type: 'string',
          description: 'Post-install message shown to user',
          examples: ['Run `brew services start myservice` to start the service.'],
        },
        keg_only: {
          $ref: '#/$defs/keg-only',
          description: 'Reason the formula is keg-only',
        },
        pour_bottle: {
          type: 'boolean',
          description: 'Whether to pour the bottle on install',
          default: true,
        },
        deprecate: {
          $ref: '#/$defs/deprecation',
          description: 'Deprecation notice',
        },
        disable: {
          $ref: '#/$defs/deprecation',
          description: 'Disable notice (stronger than deprecation)',
        },

        // Nested objects
        install: {
          type: 'object',
          description:
            'Language-specific install configuration (shape determined by language field)',
        },
        test: {
          type: 'object',
          description: 'Post-install test configuration',
          properties: {
            command: {
              type: 'string',
              description: 'Shell command to verify the install',
              examples: ['system bin/"mytool", "--version"'],
            },
            input: {
              type: 'string',
              description: 'Stdin input for the test command',
              examples: ['test input'],
            },
            expected_output: {
              type: 'string',
              description: 'Expected output pattern (Ruby regex or string)',
              examples: ['mytool version #{version}'],
            },
          },
          additionalProperties: false,
        },
        service: {
          $ref: '#/$defs/service-config',
          description: 'launchd/systemd service definition',
        },
        on_macos: {
          $ref: '#/$defs/on-platform',
          description: 'macOS-specific overrides',
        },
        on_linux: {
          $ref: '#/$defs/on-platform',
          description: 'Linux-specific overrides',
        },
        completions: {
          type: 'object',
          description: 'Shell completion file generation',
          properties: {
            bash: {
              type: 'string',
              description: 'Command to generate bash completions',
              examples: ['generate_completions bash > bash_completion.d/mytool'],
            },
            zsh: {
              type: 'string',
              description: 'Command to generate zsh completions',
              examples: ['generate_completions zsh > zsh/site-functions/_mytool'],
            },
            fish: {
              type: 'string',
              description: 'Command to generate fish completions',
              examples: ['generate_completions fish > fish/vendor_completions.d/mytool.fish'],
            },
          },
          additionalProperties: false,
        },
      },

      required: ['name', 'desc', 'homepage', 'license'],

      // Standard vs HEAD-only
      if: {
        required: ['url'],
      },
      then: {
        required: ['sha256', 'livecheck'],
      },
      else: {
        required: ['head'],
      },

      // Language dispatch + dependentSchemas
      allOf: [
        {
          if: { properties: { language: { const: 'go' } }, required: ['language'] },
          then: {
            properties: { install: { $ref: '#/$defs/install-go' } },
            required: ['install'],
          },
        },
        {
          if: { properties: { language: { const: 'rust' } }, required: ['language'] },
          then: {
            properties: { install: { $ref: '#/$defs/install-rust' } },
            required: ['install'],
          },
        },
        {
          if: { properties: { language: { const: 'python' } }, required: ['language'] },
          then: {
            properties: { install: { $ref: '#/$defs/install-python' } },
            required: ['install'],
          },
        },
        {
          if: { properties: { language: { const: 'nodejs' } }, required: ['language'] },
          then: {
            properties: { install: { $ref: '#/$defs/install-nodejs' } },
            required: ['install'],
          },
        },
        {
          if: { properties: { language: { const: 'cmake' } }, required: ['language'] },
          then: {
            properties: { install: { $ref: '#/$defs/install-cmake' } },
            required: ['install'],
          },
        },
        {
          if: { properties: { language: { const: 'autotools' } }, required: ['language'] },
          then: {
            properties: { install: { $ref: '#/$defs/install-autotools' } },
            required: ['install'],
          },
        },
        {
          if: { properties: { language: { const: 'meson' } }, required: ['language'] },
          then: {
            properties: { install: { $ref: '#/$defs/install-meson' } },
            required: ['install'],
          },
        },
        {
          if: { properties: { language: { const: 'java' } }, required: ['language'] },
          then: {
            properties: { install: { $ref: '#/$defs/install-java' } },
            required: ['install'],
          },
        },
        {
          if: { properties: { language: { const: 'zig' } }, required: ['language'] },
          then: {
            properties: { install: { $ref: '#/$defs/install-zig' } },
            required: ['install'],
          },
        },
        {
          if: { properties: { language: { const: 'make' } }, required: ['language'] },
          then: {
            properties: { install: { $ref: '#/$defs/install-make' } },
            required: ['install'],
          },
        },
        {
          if: { properties: { language: { const: 'custom' } }, required: ['language'] },
          then: {
            properties: { install: { $ref: '#/$defs/install-custom' } },
            required: ['install'],
          },
        },
        {
          if: { properties: { language: { const: 'swift' } }, required: ['language'] },
          then: {
            properties: { install: { $ref: '#/$defs/install-swift' } },
            required: ['install'],
          },
        },
        {
          if: { properties: { language: { const: 'elixir' } }, required: ['language'] },
          then: {
            properties: { install: { $ref: '#/$defs/install-elixir' } },
            required: ['install'],
          },
        },
        {
          if: { properties: { language: { const: 'haskell' } }, required: ['language'] },
          then: {
            properties: { install: { $ref: '#/$defs/install-haskell' } },
            required: ['install'],
          },
        },
        {
          if: { properties: { language: { const: 'kotlin' } }, required: ['language'] },
          then: {
            properties: { install: { $ref: '#/$defs/install-kotlin' } },
            required: ['install'],
          },
        },
        {
          if: { properties: { language: { const: 'scala' } }, required: ['language'] },
          then: {
            properties: { install: { $ref: '#/$defs/install-scala' } },
            required: ['install'],
          },
        },
        {
          if: { properties: { language: { const: 'erlang' } }, required: ['language'] },
          then: {
            properties: { install: { $ref: '#/$defs/install-erlang-app' } },
            required: ['install'],
          },
        },
        {
          if: { properties: { language: { const: 'ocaml' } }, required: ['language'] },
          then: {
            properties: { install: { $ref: '#/$defs/install-ocaml' } },
            required: ['install'],
          },
        },
        {
          if: { properties: { language: { const: 'nim' } }, required: ['language'] },
          then: {
            properties: { install: { $ref: '#/$defs/install-nim' } },
            required: ['install'],
          },
        },
        {
          if: { properties: { language: { const: 'dart' } }, required: ['language'] },
          then: {
            properties: { install: { $ref: '#/$defs/install-dart' } },
            required: ['install'],
          },
        },
        {
          if: { properties: { language: { const: 'gleam' } }, required: ['language'] },
          then: {
            properties: { install: { $ref: '#/$defs/install-gleam' } },
            required: ['install'],
          },
        },
        {
          if: { properties: { language: { const: 'roc' } }, required: ['language'] },
          then: {
            properties: { install: { $ref: '#/$defs/install-roc' } },
            required: ['install'],
          },
        },
        {
          if: { properties: { language: { const: 'julia' } }, required: ['language'] },
          then: {
            properties: { install: { $ref: '#/$defs/install-julia' } },
            required: ['install'],
          },
        },
        {
          if: { properties: { language: { const: 'dotnet' } }, required: ['language'] },
          then: {
            properties: { install: { $ref: '#/$defs/install-dotnet' } },
            required: ['install'],
          },
        },
      ],

      dependentSchemas: {
        service: {
          required: ['caveats'],
        },
      },

      additionalProperties: false,
    },
  },
}
