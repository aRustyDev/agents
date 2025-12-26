#!/usr/bin/env python3
"""
Initialize a new Cloudflare Worker project with best practices.

Usage:
    python3 scripts/init-worker.py <project-name> [--with-d1] [--with-kv] [--with-r2]

Examples:
    python3 scripts/init-worker.py my-api
    python3 scripts/init-worker.py my-api --with-d1 --with-kv
"""

import argparse
import subprocess
import sys
from pathlib import Path


WRANGLER_TEMPLATE = '''name = "{name}"
main = "src/index.ts"
compatibility_date = "2024-01-01"
compatibility_flags = ["nodejs_compat"]

[vars]
ENVIRONMENT = "development"

{bindings}
'''

D1_BINDING = '''[[d1_databases]]
binding = "DB"
database_name = "{name}-db"
database_id = "TODO: run 'wrangler d1 create {name}-db' and paste ID here"
'''

KV_BINDING = '''[[kv_namespaces]]
binding = "KV"
id = "TODO: run 'wrangler kv:namespace create KV' and paste ID here"
'''

R2_BINDING = '''[[r2_buckets]]
binding = "BUCKET"
bucket_name = "{name}-bucket"
'''

INDEX_TS = '''import {{ Hono }} from 'hono';
import {{ cors }} from 'hono/cors';

interface Env {{
  ENVIRONMENT: string;
{env_types}
}}

const app = new Hono<{{ Bindings: Env }}>();

app.use('*', cors());

app.get('/', (c) => {{
  return c.json({{
    message: 'Hello from {name}!',
    environment: c.env.ENVIRONMENT,
  }});
}});

app.get('/health', (c) => {{
  return c.json({{ status: 'ok' }});
}});

export default app;
'''

ENV_TYPES = {
    'd1': '  DB: D1Database;',
    'kv': '  KV: KVNamespace;',
    'r2': '  BUCKET: R2Bucket;',
}


def run_command(cmd: list[str], cwd: Path | None = None) -> bool:
    """Run a shell command and return success status."""
    try:
        subprocess.run(cmd, check=True, cwd=cwd)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running {' '.join(cmd)}: {e}", file=sys.stderr)
        return False


def create_project(name: str, with_d1: bool, with_kv: bool, with_r2: bool) -> bool:
    """Create a new Cloudflare Worker project."""
    project_path = Path(name)

    if project_path.exists():
        print(f"Error: Directory '{name}' already exists", file=sys.stderr)
        return False

    # Create directory structure
    project_path.mkdir()
    (project_path / 'src').mkdir()
    (project_path / 'test').mkdir()

    # Build bindings configuration
    bindings = []
    env_types = []

    if with_d1:
        bindings.append(D1_BINDING.format(name=name))
        env_types.append(ENV_TYPES['d1'])
        (project_path / 'migrations').mkdir()

    if with_kv:
        bindings.append(KV_BINDING)
        env_types.append(ENV_TYPES['kv'])

    if with_r2:
        bindings.append(R2_BINDING.format(name=name))
        env_types.append(ENV_TYPES['r2'])

    # Write wrangler.toml
    wrangler_content = WRANGLER_TEMPLATE.format(
        name=name,
        bindings='\n'.join(bindings)
    )
    (project_path / 'wrangler.toml').write_text(wrangler_content)

    # Write src/index.ts
    index_content = INDEX_TS.format(
        name=name,
        env_types='\n'.join(env_types) if env_types else '  // Add bindings here'
    )
    (project_path / 'src' / 'index.ts').write_text(index_content)

    # Write package.json
    package_json = f'''{{
  "name": "{name}",
  "version": "0.1.0",
  "private": true,
  "scripts": {{
    "dev": "wrangler dev",
    "deploy": "wrangler deploy",
    "test": "vitest"
  }},
  "dependencies": {{
    "hono": "^4.0.0"
  }},
  "devDependencies": {{
    "@cloudflare/workers-types": "^4.0.0",
    "typescript": "^5.0.0",
    "vitest": "^1.0.0",
    "wrangler": "^3.0.0"
  }}
}}
'''
    (project_path / 'package.json').write_text(package_json)

    # Write tsconfig.json
    tsconfig = '''{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "lib": ["ES2022"],
    "types": ["@cloudflare/workers-types"],
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "skipLibCheck": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules"]
}
'''
    (project_path / 'tsconfig.json').write_text(tsconfig)

    # Write .gitignore
    gitignore = '''node_modules/
dist/
.wrangler/
.dev.vars
'''
    (project_path / '.gitignore').write_text(gitignore)

    print(f"\n✅ Created Cloudflare Worker project: {name}")
    print(f"\nNext steps:")
    print(f"  cd {name}")
    print(f"  npm install")

    if with_d1:
        print(f"  wrangler d1 create {name}-db")
        print(f"  # Update wrangler.toml with database_id")

    if with_kv:
        print(f"  wrangler kv:namespace create KV")
        print(f"  # Update wrangler.toml with namespace id")

    if with_r2:
        print(f"  wrangler r2 bucket create {name}-bucket")

    print(f"  npm run dev")

    return True


def main():
    parser = argparse.ArgumentParser(
        description='Initialize a new Cloudflare Worker project'
    )
    parser.add_argument('name', help='Project name')
    parser.add_argument('--with-d1', action='store_true', help='Include D1 database')
    parser.add_argument('--with-kv', action='store_true', help='Include KV namespace')
    parser.add_argument('--with-r2', action='store_true', help='Include R2 bucket')

    args = parser.parse_args()

    success = create_project(
        args.name,
        with_d1=args.with_d1,
        with_kv=args.with_kv,
        with_r2=args.with_r2
    )

    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
