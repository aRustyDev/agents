/* WARNING: Script requires that SQLITE_DBCONFIG_DEFENSIVE be disabled */
PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE mcp_servers (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  slug TEXT UNIQUE NOT NULL,
  description TEXT,
  homepage TEXT,
  repository TEXT,

  -- Installation
  install_method TEXT,                -- brew|npx|pip|docker|manual
  install_command TEXT,
  dockerized INTEGER DEFAULT 0,       -- 0=no, 1=yes, 2=only (docker-only)

  -- Technical profile
  language TEXT,                       -- rust|python|typescript|go|java|csharp|etc
  transport TEXT,                      -- stdio|sse|http-stream|multi (comma-sep if multiple)
  config_schema TEXT,                  -- JSON: server's configuration/env schema
  locale TEXT DEFAULT 'en',            -- ISO 639-1 codes, comma-sep (en,es,zh,etc)

  -- Pricing
  pricing TEXT DEFAULT 'free',         -- free|paid|freemium
  pricing_notes TEXT,                  -- details on tiers/limits

  -- Discovery metadata
  features TEXT,                       -- comma-separated feature tags
  source_registry TEXT,
  source_url TEXT,
  stars INTEGER,
  last_updated TEXT,
  discovered_at TEXT DEFAULT (datetime('now')),
  refreshed_at TEXT DEFAULT (datetime('now'))
);
INSERT INTO mcp_servers VALUES(1,'code-graph-rag-mcp','code-graph-rag-mcp',NULL,NULL,NULL,NULL,NULL,0,NULL,NULL,NULL,'en','free',NULL,NULL,'mcpservers.org','https://mcpservers.org/servers/github-com-er77-code-graph-rag-mcp',NULL,NULL,'2026-02-03 00:53:03','2026-02-03 00:53:03');
INSERT INTO mcp_servers VALUES(2,'code-reasoning','code-reasoning',NULL,NULL,NULL,NULL,NULL,0,NULL,NULL,NULL,'en','free',NULL,NULL,'mcpservers.org','https://mcpservers.org/servers/mettamatt/code-reasoning',NULL,NULL,'2026-02-03 00:53:03','2026-02-03 00:53:03');
INSERT INTO mcp_servers VALUES(3,'code-knowledge-mcptool','code-knowledge-mcptool',NULL,NULL,NULL,NULL,NULL,0,NULL,NULL,NULL,'en','free',NULL,NULL,'mcpservers.org','https://mcpservers.org/servers/davidvc/code-knowledge-mcptool',NULL,NULL,'2026-02-03 00:53:03','2026-02-03 00:53:03');
INSERT INTO mcp_servers VALUES(4,'code-index-mcp (johnhuang316)','code-index-mcp-johnhuang',NULL,NULL,NULL,NULL,NULL,0,NULL,NULL,NULL,'en','free',NULL,NULL,'mcpservers.org','https://mcpservers.org/servers/johnhuang316/code-index-mcp',NULL,NULL,'2026-02-03 00:53:03','2026-02-03 00:53:03');
INSERT INTO mcp_servers VALUES(5,'Code-Index-MCP','code-index-mcp-viperjuice','Modular, extensible local-first code indexer designed to enhance Claude Code and other LLMs with deep code understanding capabilities. Built on the Model Context Protocol (MCP) for seamless integration with AI assistants.','https://github.com/ViperJuice/Code-Index-MCP','https://github.com/ViperJuice/Code-Index-MCP','pip,docker,manual','pip install code-index-mcp',2,'python','stdio','{"VOYAGE_AI_API_KEY":"optional - for semantic search","MCP_SERVER_HOST":"0.0.0.0","MCP_SERVER_PORT":"8000","MCP_LOG_LEVEL":"INFO","MCP_WORKSPACE_ROOT":".","MCP_MAX_FILE_SIZE":"10485760","MCP_ARTIFACT_SYNC":"false","SEMANTIC_SEARCH_ENABLED":"true"}','en','freemium','Core features free. Semantic search requires Voyage AI API (~$0.05/1M tokens). GitHub Artifacts free for public repos.','local-first,code-indexing,symbol-search,semantic-search,multi-language,real-time-updates,file-monitoring,git-sync,hybrid-search,tree-sitter-parsing,plugin-based,performance-optimized,48-languages','mcpservers.org','https://mcpservers.org/servers/ViperJuice/Code-Index-MCP',NULL,'2026-02-02','2026-02-03 00:53:03','2026-02-03 00:55:53');
INSERT INTO mcp_servers VALUES(6,'code-council','code-council',NULL,NULL,NULL,NULL,NULL,0,NULL,NULL,NULL,'en','free',NULL,NULL,'mcpservers.org','https://mcpservers.org/servers/klitchevo/code-council',NULL,NULL,'2026-02-03 00:53:03','2026-02-03 00:53:03');
INSERT INTO mcp_servers VALUES(7,'code-context-mcp','code-context-mcp',NULL,NULL,NULL,NULL,NULL,0,NULL,NULL,NULL,'en','free',NULL,NULL,'mcpservers.org','https://mcpservers.org/servers/fkesheh/code-context-mcp',NULL,NULL,'2026-02-03 00:53:03','2026-02-03 00:53:03');
INSERT INTO mcp_servers VALUES(8,'mcp_server_code_assist','code-assist',NULL,NULL,NULL,NULL,NULL,0,NULL,NULL,NULL,'en','free',NULL,NULL,'mcpservers.org','https://mcpservers.org/servers/abhishekbhakat/mcp_server_code_assist',NULL,NULL,'2026-02-03 00:53:03','2026-02-03 00:53:03');
INSERT INTO mcp_servers VALUES(9,'code-context-provider-mcp','code-context-provider',NULL,NULL,NULL,NULL,NULL,0,NULL,NULL,NULL,'en','free',NULL,NULL,'mcpservers.org','https://mcpservers.org/servers/AB498/code-context-provider-mcp',NULL,NULL,'2026-02-03 00:53:03','2026-02-03 00:53:03');
INSERT INTO mcp_servers VALUES(10,'code-assistant','code-assistant',NULL,NULL,NULL,NULL,NULL,0,NULL,NULL,NULL,'en','free',NULL,NULL,'mcpservers.org','https://mcpservers.org/servers/stippi/code-assistant',NULL,NULL,'2026-02-03 00:53:03','2026-02-03 00:53:03');
INSERT INTO mcp_servers VALUES(11,'code-mcp','code-mcp',NULL,NULL,NULL,NULL,NULL,0,NULL,NULL,NULL,'en','free',NULL,NULL,'mcpservers.org','https://mcpservers.org/servers/zeocax/code-mcp',NULL,NULL,'2026-02-03 00:53:03','2026-02-03 00:53:03');
INSERT INTO mcp_servers VALUES(12,'codacy-mcp-server','codacy-mcp-server','MCP Server for the Codacy API, enabling access to repositories, files, quality, coverage, security and more.','https://github.com/codacy/codacy-mcp-server','https://github.com/codacy/codacy-mcp-server','npx','npx -y @codacy/codacy-mcp@latest',1,'typescript','stdio','{"env":{"CODACY_ACCOUNT_TOKEN":{"type":"string","required":true,"description":"Personal API access token from Codacy account"}}}','en','free',NULL,'code-quality,security,coverage,pull-requests,repository-management,cli-analysis','mcpservers.org','https://mcpservers.org/servers/codacy/codacy-mcp-server',55,'2026-01-13T11:13:31Z','2026-02-03 00:53:03','2026-02-03 00:54:51');
INSERT INTO mcp_servers VALUES(13,'code-scalpel','code-scalpel',NULL,NULL,NULL,NULL,NULL,0,NULL,NULL,NULL,'en','free',NULL,NULL,'mcpservers.org','https://mcpservers.org/servers/3d-tech-solutions/code-scalpel',NULL,NULL,'2026-02-03 00:53:03','2026-02-03 00:53:03');
INSERT INTO mcp_servers VALUES(14,'code-scanner-server','code-scanner-server',NULL,NULL,NULL,NULL,NULL,0,NULL,NULL,NULL,'en','free',NULL,NULL,'mcpservers.org','https://mcpservers.org/servers/Ixe1/code-scanner-server',NULL,NULL,'2026-02-03 00:53:03','2026-02-03 00:53:03');
INSERT INTO mcp_servers VALUES(15,'mcp-code-understanding','code-understanding',NULL,NULL,NULL,NULL,NULL,0,NULL,NULL,NULL,'en','free',NULL,NULL,'mcpservers.org','https://mcpservers.org/servers/codingthefuturewithai/mcp-code-understanding',NULL,NULL,'2026-02-03 00:53:03','2026-02-03 00:53:03');
INSERT INTO mcp_servers VALUES(16,'code-summarizer','code-summarizer',NULL,NULL,NULL,NULL,NULL,0,NULL,NULL,NULL,'en','free',NULL,NULL,'mcpservers.org','https://mcpservers.org/servers/nicobailon/code-summarizer',NULL,NULL,'2026-02-03 00:53:03','2026-02-03 00:53:03');
INSERT INTO mcp_servers VALUES(17,'codealive-mcp','codealive-mcp',NULL,NULL,NULL,NULL,NULL,0,NULL,NULL,NULL,'en','free',NULL,NULL,'mcpservers.org','https://mcpservers.org/servers/CodeAlive-AI/codealive-mcp',NULL,NULL,'2026-02-03 00:53:03','2026-02-03 00:53:03');
INSERT INTO mcp_servers VALUES(18,'codebase-context-dumper','codebase-context-dumper',NULL,NULL,NULL,NULL,NULL,0,NULL,NULL,NULL,'en','free',NULL,NULL,'mcpservers.org','https://mcpservers.org/servers/lex-tools/codebase-context-dumper',NULL,NULL,'2026-02-03 00:53:03','2026-02-03 00:53:03');
INSERT INTO mcp_servers VALUES(19,'CodebaseIndexMCP','codebase-index-mcp',NULL,NULL,NULL,NULL,NULL,0,NULL,NULL,NULL,'en','free',NULL,NULL,'mcpservers.org','https://mcpservers.org/servers/mengtoumingren/CodebaseIndexMCP',NULL,NULL,'2026-02-03 00:53:03','2026-02-03 00:53:03');
INSERT INTO mcp_servers VALUES(20,'codebase-mcp-server','codebase-mcp-server',NULL,NULL,NULL,NULL,NULL,0,NULL,NULL,NULL,'en','free',NULL,NULL,'mcpservers.org','https://mcpservers.org/servers/MyunghoBae/codebase-mcp-server',NULL,NULL,'2026-02-03 00:53:03','2026-02-03 00:53:03');
INSERT INTO mcp_servers VALUES(21,'codebase-optimizer-mcp','codebase-optimizer-mcp',NULL,NULL,NULL,NULL,NULL,0,NULL,NULL,NULL,'en','free',NULL,NULL,'mcpservers.org','https://mcpservers.org/servers/liadgez/codebase-optimizer-mcp',NULL,NULL,'2026-02-03 00:53:27','2026-02-03 00:53:27');
INSERT INTO mcp_servers VALUES(22,'codebase-iq-pro','codebase-iq-pro',NULL,NULL,NULL,NULL,NULL,0,NULL,NULL,NULL,'en','free',NULL,NULL,'mcpservers.org','https://mcpservers.org/servers/chatcbdai/codebase-iq-pro',NULL,NULL,'2026-02-03 00:53:27','2026-02-03 00:53:27');
INSERT INTO mcp_servers VALUES(23,'mcp-server-codegraph','mcp-server-codegraph','MCP server that provides tools to generate and query a graph representation of your codebase','https://github.com/CartographAI/mcp-server-codegraph','https://github.com/CartographAI/mcp-server-codegraph','npx','npx -y @cartographai/mcp-server-codegraph /path/to/directory',0,'typescript','stdio',NULL,'en','free',NULL,'codebase-analysis,graph-representation,entity-extraction,relationship-tracking,multi-language-support','mcpservers.org','https://mcpservers.org/servers/CartographAI/mcp-server-codegraph',17,'2026-01-19','2026-02-03 00:53:27','2026-02-03 00:59:00');
INSERT INTO mcp_servers VALUES(24,'codegraph-rust','codegraph-rust',NULL,NULL,NULL,NULL,NULL,0,NULL,NULL,NULL,'en','free',NULL,NULL,'mcpservers.org','https://mcpservers.org/servers/github-com-jakedismo-codegraph-rust',NULL,NULL,'2026-02-03 00:53:27','2026-02-03 00:53:27');
INSERT INTO mcp_servers VALUES(25,'codegraphcontext','codegraphcontext',NULL,NULL,NULL,NULL,NULL,0,NULL,NULL,NULL,'en','free',NULL,NULL,'mcpservers.org','https://mcpservers.org/servers/shashankss1205/codegraphcontext',NULL,NULL,'2026-02-03 00:53:27','2026-02-03 00:53:27');
INSERT INTO mcp_servers VALUES(26,'CodeSeeker-MCP','codeseeker-mcp',NULL,NULL,NULL,NULL,NULL,0,NULL,NULL,NULL,'en','free',NULL,NULL,'mcpservers.org','https://mcpservers.org/servers/mixelpixx/CodeSeeker-MCP',NULL,NULL,'2026-02-03 00:53:27','2026-02-03 00:53:27');
INSERT INTO mcp_servers VALUES(27,'codetoprompt-mcp','codetoprompt-mcp',NULL,NULL,NULL,NULL,NULL,0,NULL,NULL,NULL,'en','free',NULL,NULL,'mcpservers.org','https://mcpservers.org/servers/yash9439/codetoprompt-mcp',NULL,NULL,'2026-02-03 00:53:27','2026-02-03 00:53:27');
INSERT INTO mcp_servers VALUES(28,'coding-standards-mcp','coding-standards-mcp',NULL,NULL,NULL,NULL,NULL,0,NULL,NULL,NULL,'en','free',NULL,NULL,'mcpservers.org','https://mcpservers.org/servers/ggerve/coding-standards-mcp',NULL,NULL,'2026-02-03 00:53:27','2026-02-03 00:53:27');
INSERT INTO mcp_servers VALUES(29,'deep-code-reasoning-mcp','deep-code-reasoning-mcp',NULL,NULL,NULL,NULL,NULL,0,NULL,NULL,NULL,'en','free',NULL,NULL,'mcpservers.org','https://mcpservers.org/servers/haasonsaas/deep-code-reasoning-mcp',NULL,NULL,'2026-02-03 00:53:27','2026-02-03 00:53:27');
INSERT INTO mcp_servers VALUES(30,'mcp-code-crosscheck','mcp-code-crosscheck',NULL,NULL,NULL,NULL,NULL,0,NULL,NULL,NULL,'en','free',NULL,NULL,'mcpservers.org','https://mcpservers.org/servers/olaservo/mcp-code-crosscheck',NULL,NULL,'2026-02-03 00:53:27','2026-02-03 00:53:27');
INSERT INTO mcp_servers VALUES(31,'mcp-code-graph','mcp-code-graph',NULL,NULL,NULL,NULL,NULL,0,NULL,NULL,NULL,'en','free',NULL,NULL,'mcpservers.org','https://mcpservers.org/servers/github-com-judinilabs-mcp-code-graph',NULL,NULL,'2026-02-03 00:53:27','2026-02-03 00:53:27');
INSERT INTO mcp_servers VALUES(32,'mcp_analyze_quality','mcp-analyze-quality',NULL,NULL,NULL,NULL,NULL,0,NULL,NULL,NULL,'en','free',NULL,NULL,'mcpservers.org','https://mcpservers.org/servers/DaSheng1994/mcp_analyze_quality',NULL,NULL,'2026-02-03 00:53:27','2026-02-03 00:53:27');
INSERT INTO mcp_servers VALUES(33,'semgrep-mcp','semgrep-mcp','A Model Context Protocol (MCP) server for using Semgrep to scan code for security vulnerabilities. NOTE: Archived repository - moved to main semgrep repo.','https://mcp.semgrep.ai','https://github.com/semgrep/mcp','uvx','uvx semgrep-mcp',0,'Python',NULL,NULL,'en','free',NULL,'security scanning,code analysis,AST generation,custom rules,vulnerability detection,cloud platform integration','mcpservers.org','https://mcpservers.org/servers/semgrep/mcp',637,'2025-10-28','2026-02-03 00:53:27','2026-02-03 00:54:35');
INSERT INTO mcp_servers VALUES(34,'mcp-server-semgrep','mcp-server-semgrep',NULL,NULL,NULL,NULL,NULL,0,NULL,NULL,NULL,'en','free',NULL,NULL,'mcpservers.org','https://mcpservers.org/servers/Szowesgad/mcp-server-semgrep',NULL,NULL,'2026-02-03 00:53:27','2026-02-03 00:53:27');
INSERT INTO mcp_servers VALUES(35,'mcp-sbom-server','mcp-sbom-server','MCP server for generating and analyzing Software Bill of Materials (SBOM) using CycloneDX format','https://github.com/sbomify/mcp-sbom','https://github.com/sbomify/mcp-sbom','pip','uv run mcp-sbom',0,'python','stdio',NULL,'en','free',NULL,'sbom-generation,cyclonedx,dependency-analysis,license-detection,vulnerability-scanning','mcpservers.org','https://mcpservers.org/servers/gkhays/mcp-sbom-server',2,'2025-12-15','2026-02-03 00:53:27','2026-02-03 00:59:00');
INSERT INTO mcp_servers VALUES(36,'mcp-sbom-server-mirror','mcp-sbom-server-mirror',NULL,NULL,NULL,NULL,NULL,0,NULL,NULL,NULL,'en','free',NULL,NULL,'mcpservers.org','https://mcpservers.org/servers/MCP-Mirror/gkhays_mcp-sbom-server',NULL,NULL,'2026-02-03 00:53:27','2026-02-03 00:53:27');
INSERT INTO mcp_servers VALUES(37,'MCP Tree-sitter Server','mcp-server-tree-sitter','MCP server that provides code analysis capabilities using tree-sitter, designed to give AI assistants intelligent access to codebases with context management capabilities.',NULL,'https://github.com/wrale/mcp-server-tree-sitter','pip','pip install mcp-server-tree-sitter',0,'Python',NULL,NULL,'en','free',NULL,'Project management, code exploration, syntax analysis, pattern search, symbol extraction, complexity analysis, dependency tracking, query building, similar code detection','mcpservers.org','https://mcpservers.org/servers/wrale/mcp-server-tree-sitter',253,'2025-03-18','2026-02-03 00:53:27','2026-02-03 00:56:35');
INSERT INTO mcp_servers VALUES(38,'code-research-mcp-server','code-research-mcp-server',NULL,NULL,NULL,NULL,NULL,0,NULL,NULL,NULL,'en','free',NULL,NULL,'mcpservers.org','https://mcpservers.org/servers/nahmanmate/code-research-mcp-server',NULL,NULL,'2026-02-03 00:53:27','2026-02-03 00:53:27');
INSERT INTO mcp_servers VALUES(39,'mcp-qdrant-codebase-embeddings','mcp-qdrant-codebase-embeddings',NULL,NULL,NULL,NULL,NULL,0,NULL,NULL,NULL,'en','free',NULL,NULL,'mcpservers.org','https://mcpservers.org/servers/steiner385/mcp-qdrant-codebase-embeddings',NULL,NULL,'2026-02-03 00:53:27','2026-02-03 00:53:27');
CREATE TABLE mcp_server_tools (
  id INTEGER PRIMARY KEY,
  server_id INTEGER NOT NULL REFERENCES mcp_servers(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  description TEXT,
  input_schema TEXT,                   -- JSON: tool's input parameters schema
  UNIQUE(server_id, name)
);
INSERT INTO mcp_server_tools VALUES(1,12,'codacy_setup_repository','Add or follow a repository in Codacy if not already present. This tool ensures the repository is registered with Codacy, allowing further analysis and management.',NULL);
INSERT INTO mcp_server_tools VALUES(2,12,'codacy_list_organizations','List organizations with pagination support.',NULL);
INSERT INTO mcp_server_tools VALUES(3,12,'codacy_list_organization_repositories','List repositories in an organization with pagination support.',NULL);
INSERT INTO mcp_server_tools VALUES(4,12,'codacy_get_repository_with_analysis','Get repository with analysis information, including metrics for Grade, Issues, Duplication, Complexity, and Coverage.',NULL);
INSERT INTO mcp_server_tools VALUES(5,12,'codacy_list_repository_issues','Lists and filters code quality issues in a repository. Primary tool for investigating general code quality concerns (e.g. best practices, performance, complexity, style) but NOT security issues. Features include pagination, filtering by severity/category/language, author-based filtering, branch-specific analysis, and pattern-based searching.',NULL);
INSERT INTO mcp_server_tools VALUES(6,12,'codacy_list_files','List files in a repository with pagination support.',NULL);
INSERT INTO mcp_server_tools VALUES(7,12,'codacy_get_file_issues','Get the issue list for a file in a repository.',NULL);
INSERT INTO mcp_server_tools VALUES(8,12,'codacy_get_file_coverage','Get coverage information for a file in the head commit of a repository branch.',NULL);
INSERT INTO mcp_server_tools VALUES(9,12,'codacy_get_file_clones','Get the list of duplication clones (identical or very similar code segments) for a file in a repository.',NULL);
INSERT INTO mcp_server_tools VALUES(10,12,'codacy_get_file_with_analysis','Get detailed analysis information for a file, including metrics for Grade, Issues, Duplication, Complexity, and Coverage.',NULL);
INSERT INTO mcp_server_tools VALUES(11,12,'codacy_search_organization_srm_items','Primary tool to list security items/issues/vulnerabilities/findings across an organization. Results are related to the organization''s security and risk management (SRM) dashboard on Codacy. Covers SAST, Secrets, SCA, IaC, CICD, DAST, and PenTesting.',NULL);
INSERT INTO mcp_server_tools VALUES(12,12,'codacy_search_repository_srm_items','List security items/issues/vulnerabilities/findings for a specific repository. Covers SAST, Secrets, SCA, IaC, CICD, DAST, and PenTesting.',NULL);
INSERT INTO mcp_server_tools VALUES(13,12,'codacy_list_repository_pull_requests','List pull requests from a repository that the user has access to.',NULL);
INSERT INTO mcp_server_tools VALUES(14,12,'codacy_get_repository_pull_request','Get detailed information about a specific pull request.',NULL);
INSERT INTO mcp_server_tools VALUES(15,12,'codacy_list_pull_request_issues','Returns a list of issues found in a pull request (new or fixed issues).',NULL);
INSERT INTO mcp_server_tools VALUES(16,12,'codacy_get_pull_request_files_coverage','Get diff coverage information for all files in a pull request.',NULL);
INSERT INTO mcp_server_tools VALUES(17,12,'codacy_get_pull_request_git_diff','Returns the human-readable Git diff of a pull request.',NULL);
INSERT INTO mcp_server_tools VALUES(18,12,'codacy_list_tools','List all code analysis tools available in Codacy.',NULL);
INSERT INTO mcp_server_tools VALUES(19,12,'codacy_list_repository_tools','Get analysis tools settings and available tools for a repository.',NULL);
INSERT INTO mcp_server_tools VALUES(20,12,'codacy_get_pattern','Get the definition of a specific pattern.',NULL);
INSERT INTO mcp_server_tools VALUES(21,12,'codacy_list_repository_tool_patterns','List the patterns of a tool available for a repository.',NULL);
INSERT INTO mcp_server_tools VALUES(22,12,'codacy_get_issue','Get detailed information about a specific issue.',NULL);
INSERT INTO mcp_server_tools VALUES(23,12,'codacy_cli_analyze','Run quality analysis locally using Codacy CLI. Features include: analyze specific files or entire directories, use specific tools or all available tools, get immediate results without waiting for scheduled analysis, and apply fixes based on Codacy configuration.',NULL);
INSERT INTO mcp_server_tools VALUES(24,5,'symbol','Get symbol definition - find definitions of functions, classes, variables, and other code symbols','{"type":"object","properties":{"symbol_name":{"type":"string","description":"Name of the symbol to find","required":true},"file_path":{"type":"string","description":"Specific file to search in (optional)"}},"required":["symbol_name"]}');
INSERT INTO mcp_server_tools VALUES(25,5,'search','Search for code patterns with support for regex patterns and multi-language search','{"type":"object","properties":{"query":{"type":"string","description":"Search pattern (regex supported)","required":true},"file_extensions":{"type":"string","description":"Comma-separated list of file extensions to filter (optional)"}},"required":["query"]}');
INSERT INTO mcp_server_tools VALUES(26,5,'index_rebuild','Rebuild the code index for the current workspace','{"type":"object","properties":{"workspace_path":{"type":"string","description":"Path to workspace to index (defaults to current)"}}}');
INSERT INTO mcp_server_tools VALUES(27,5,'index_status','Check the status of the code index including file count, last update time, and index size','{"type":"object","properties":{}}');
INSERT INTO mcp_server_tools VALUES(28,5,'artifact_sync','Synchronize code indexes with GitHub Artifacts for team sharing','{"type":"object","properties":{"operation":{"type":"string","enum":["pull","push","sync"],"description":"Sync operation to perform"}}}');
INSERT INTO mcp_server_tools VALUES(29,33,'security_check','Scan code for security vulnerabilities',NULL);
INSERT INTO mcp_server_tools VALUES(30,33,'semgrep_scan','Scan code files with a given config string',NULL);
INSERT INTO mcp_server_tools VALUES(31,33,'semgrep_scan_with_custom_rule','Scan code using a custom Semgrep rule',NULL);
INSERT INTO mcp_server_tools VALUES(32,33,'get_abstract_syntax_tree','Output the AST of code',NULL);
INSERT INTO mcp_server_tools VALUES(33,33,'semgrep_findings','Fetch findings from Semgrep AppSec Platform API',NULL);
INSERT INTO mcp_server_tools VALUES(34,33,'supported_languages','Return list of languages Semgrep supports',NULL);
INSERT INTO mcp_server_tools VALUES(35,33,'semgrep_rule_schema','Fetch the latest semgrep rule JSON Schema',NULL);
INSERT INTO mcp_server_tools VALUES(36,37,'register_project_tool','Register a project for analysis',NULL);
INSERT INTO mcp_server_tools VALUES(37,37,'list_projects_tool','List all registered projects',NULL);
INSERT INTO mcp_server_tools VALUES(38,37,'remove_project_tool','Remove a registered project',NULL);
INSERT INTO mcp_server_tools VALUES(39,37,'list_files','List files with pattern matching',NULL);
INSERT INTO mcp_server_tools VALUES(40,37,'get_file','Get file content',NULL);
INSERT INTO mcp_server_tools VALUES(41,37,'get_file_metadata','Get file metadata',NULL);
INSERT INTO mcp_server_tools VALUES(42,37,'get_ast','Get AST for a file with configurable depth',NULL);
INSERT INTO mcp_server_tools VALUES(43,37,'get_node_at_position','Find node at specific position',NULL);
INSERT INTO mcp_server_tools VALUES(44,37,'text_search','Text search within a project',NULL);
INSERT INTO mcp_server_tools VALUES(45,37,'query_execution','Execute tree-sitter query against code',NULL);
INSERT INTO mcp_server_tools VALUES(46,37,'symbol_extraction','Extract symbols for functions and classes',NULL);
INSERT INTO mcp_server_tools VALUES(47,37,'find_symbol_usages','Find symbol usages within codebase',NULL);
INSERT INTO mcp_server_tools VALUES(48,37,'project_analysis','High-level project analysis',NULL);
INSERT INTO mcp_server_tools VALUES(49,37,'dependency_analysis','Code dependency identification',NULL);
INSERT INTO mcp_server_tools VALUES(50,37,'complexity_analysis','Code complexity analysis',NULL);
INSERT INTO mcp_server_tools VALUES(51,37,'get_query_template_tool','Get query template',NULL);
INSERT INTO mcp_server_tools VALUES(52,37,'list_query_templates_tool','List available query templates',NULL);
INSERT INTO mcp_server_tools VALUES(53,37,'build_query','Build tree-sitter query',NULL);
INSERT INTO mcp_server_tools VALUES(54,37,'adapt_query','Adapt query for different languages',NULL);
INSERT INTO mcp_server_tools VALUES(55,37,'get_node_types','Get node types for a language',NULL);
INSERT INTO mcp_server_tools VALUES(56,23,'create_graph','Generate a code graph from a directory',NULL);
INSERT INTO mcp_server_tools VALUES(57,23,'search_graph','Search the code graph for entities and relationships',NULL);
INSERT INTO mcp_server_tools VALUES(58,23,'get_entity','Get details of a specific entity in the graph',NULL);
INSERT INTO mcp_server_tools VALUES(59,23,'get_relationships','Get relationships for an entity',NULL);
INSERT INTO mcp_server_tools VALUES(60,35,'generate_sbom','Generate a CycloneDX SBOM for a project',NULL);
INSERT INTO mcp_server_tools VALUES(61,35,'analyze_sbom','Analyze an existing SBOM for vulnerabilities and license issues',NULL);
INSERT INTO mcp_server_tools VALUES(62,35,'compare_sboms','Compare two SBOMs to find differences',NULL);
CREATE TABLE mcp_server_deps (
  id INTEGER PRIMARY KEY,
  server_id INTEGER NOT NULL REFERENCES mcp_servers(id) ON DELETE CASCADE,
  name TEXT NOT NULL,                    -- jq, ripgrep, brave-api, postgres, etc
  kind TEXT NOT NULL,                    -- binary|api|service|library|runtime
  required INTEGER DEFAULT 1,            -- 1=required, 0=optional
  version_constraint TEXT,               -- >=1.5, ^3.0, etc
  notes TEXT,                            -- "needs BRAVE_API_KEY env var", etc
  UNIQUE(server_id, name)
);
CREATE TABLE mcp_server_assessments (
  id INTEGER PRIMARY KEY,
  server_id INTEGER NOT NULL UNIQUE REFERENCES mcp_servers(id) ON DELETE CASCADE,

  -- Testing robustness
  has_unit_tests INTEGER DEFAULT 0,
  has_integration_tests INTEGER DEFAULT 0,
  has_e2e_tests INTEGER DEFAULT 0,
  test_coverage_pct REAL,              -- 0.0-100.0 if measurable
  test_robustness TEXT,                -- summary assessment of test quality

  -- Codebase analysis
  codebase_ast TEXT,                   -- JSON: simplified AST / structure map
  codebase_index TEXT,                 -- JSON: file index with line counts, exports
  codebase_summary TEXT,               -- prose summary of architecture

  assessed_at TEXT DEFAULT (datetime('now'))
);
PRAGMA writable_schema=ON;
INSERT INTO sqlite_schema(type,name,tbl_name,rootpage,sql)VALUES('table','mcp_servers_fts','mcp_servers_fts',0,'CREATE VIRTUAL TABLE mcp_servers_fts USING fts5(
  name, description, features, language, transport,
  content=''mcp_servers'',
  content_rowid=''id''
)');
CREATE TABLE IF NOT EXISTS 'mcp_servers_fts_data'(id INTEGER PRIMARY KEY, block BLOB);
INSERT INTO mcp_servers_fts_data VALUES(1,X'276f7b5a0604');
INSERT INTO mcp_servers_fts_data VALUES(10,X'000000000108080008010101020101030101040101050101060101070101080101');
INSERT INTO mcp_servers_fts_data VALUES(137438953473,X'0000017807306173736973740802050703616e740a02030106636f646163790c02020401650102020102020102020102020102020102020102020102040102020102020102020202020102020102030102020505616c6976651102020504626173651202020202020908696e6465786d637013020203056e746578740702030202030902030305756e63696c060203010664756d706572120204010567726170680102030105696e646578040203010203010c6a6f686e6875616e6733313604020501096b6e6f776c6564676503020301036d63700102050302040102040202040102020102050202030102030302020202030302030404746f6f6c030204010870726f7669646572090204010372616701020402086561736f6e696e6702020301077363616c70656c0d020304046e6e65720e0203020565727665720802030402040202040602040209756d6d6172697a6572100203010d756e6465727374616e64696e670f0204010a76697065726a75696365050205040b080b300a0c0d100a0b0a0d110e26090d080d0c09130e12');
INSERT INTO mcp_servers_fts_data VALUES(274877906945,X'0000017f0830616e616c797a652002030104636f64651d0203010203010203070202050462617365150202010202110204050567726170681702040102020a07636f6e7465787419020205067365656b65721a02020508746f70726f6d70741b02020403696e671c02020209726f7373636865636b1e02040104646565701d0202010a656d62656464696e6773270205010567726170681f02040102697116020301036d637015020402020203020301020301020401020501020201020201020201020301020201020201020201020201020401020202056972726f7224020501096f7074696d697a6572150203010370726f1602040106716472616e74270203020675616c6974792002040109726561736f6e696e671d020403067365617263682602030203757374180203010473626f6d2302030102030206656d677265702102020102040304727665721702030b020301020401020401020301020502056974746572250205020874616e64617264731c0203010474726565250204040c120f0d0c0b0d080e090f0a07350a0e080b0b0e0b080c0e180a0d');
INSERT INTO mcp_servers_fts_data VALUES(412316860417,X'00000195023061210601010202076e616c79736973210601020502077263686976656421060101120202737421060102060105636c6f7564210601020c02036f6465210c01010d01020403056e74657874210601010402057573746f6d21060102080109646574656374696f6e210601020b0103666f72210801010808010a67656e65726174696f6e2106010207010b696e746567726174696f6e210601020e01046d61696e21060101160202637021090301010602046f64656c21060101030303766564210601011401046e6f746521060101110108706c6174666f726d210601020d0207726f746f636f6c210601010502057974686f6e210601030201047265706f210601011805067369746f727921060101130204756c6573210601020901047363616e210601010c05046e696e672106010203020765637572697479210c01010f01020203056d67726570210b0201010a0f03047276657221060101070102746f210801010b0c01057573696e672106010109010f76756c6e65726162696c697469657321060101100d0179210601020a04080e0e090c0d0c0c100b11120b0a0b0a0b0f0e0c0b0d0b0b0b110e0b0a0c16');
INSERT INTO mcp_servers_fts_data VALUES(549755813889,X'0000013707306163636573730c0601010902076e616c797369730c0601020b0301640c06010110020270690c060101070103636c690c0601020a02056f646163790c09020101060401650c0601020203067665726167650c0c01010e0102050108656e61626c696e670c06010108010566696c65730c0601010c02026f720c06010104010a6d616e6167656d656e740c06010209020263700c090301010202036f72650c06010111010470756c6c0c0601020601077175616c6974790c0c01010d010203010c7265706f7369746f726965730c0601010b0a01790c0601020803067175657374730c06010207010873656375726974790c0c01010f0102040304727665720c090401010302047464696f0c0601040201037468650c0601010502016f0c0601010a02097970657363726970740c06010302040d0e08090a0d08100f0c09110a0a0b1113080d120c0b0a08');
INSERT INTO mcp_servers_fts_data VALUES(687194767361,X'000002ae03303438050601021c01026169050601012002026e64050601010d02097373697374616e74730506010121010562617365640506010219020475696c740506010115010c6361706162696c6974696573050601011402056c61756465050601010b02036f6465051302010106080801020403056e746578740506010119010464656570050601011103067369676e656405060101080107656e68616e6365050601010a02097874656e7369626c650506010103010466696c65050601020f0303727374050c01010501020302026f72050601011c01036769740506010211010668796272696405060102130105696e6465780503030602657205060101070603696e6705060102050309746567726174696f6e050601011e01086c616e6775616765050601020b090173050601021d02036c6d73050601010f02046f63616c050c01010401020201036d637005090401011b02046f64656c05060101180404756c6172050601010203086e69746f72696e6705060102100204756c7469050601020a01026f6e050601011602087074696d697a6564050601021b020474686572050601010e010770617273696e670506010217020a6572666f726d616e6365050601021a02056c7567696e05060102180207726f746f636f6c050601011a02057974686f6e050601030201047265616c050601020c01087365616d6c657373050601011d0403726368050a010207040d03066d616e746963050601020802056974746572050601021602047464696f05060104020205796d626f6c050601020603026e630506010212010374686505060101170203696d65050601020d02016f050601010902037265650506010215010d756e6465727374616e64696e6705060101130206706461746573050601020e010a76697065726a75696365050101047769746805080101101104090909100c0b130c100c0b0d0e100b0d090a0d0a090a100f080a0e0b0b0b0f0b090f0b0e110c0e0c0b0f0c0d0c0b0c090a0a080a140d0e');
INSERT INTO mcp_servers_fts_data VALUES(824633720833,X'000001e607306163636573732506010112020169250601010f02076e616c79736973250e0101070102070802097373697374616e7473250601011001086275696c64696e672506010211010c6361706162696c697469657325080101081202036f6465250e0101060102041105056261736573250601011403086d706c6578697479250601020c03056e746578742506010116010a646570656e64656e6379250601020e03067369676e6564250601010c030774656374696f6e2506010214010b6578706c6f726174696f6e250601020503087472616374696f6e250601020b010467697665250601010e010b696e74656c6c6967656e742506010111010a6d616e6167656d656e74250c0101170102030202637025090201010201077061747465726e25060102080206726f6a656374250601020204057669646573250601010502057974686f6e2506010302010571756572792506010210010673656172636825060102090304727665722509050101030206696d696c6172250601021203047474657225090401010b0205796d626f6c250601020a03046e7461782506010206010474686174250601010402016f250801010d0802077261636b696e67250601020f0302656525090301010a01057573696e6725060101090104776974682506010115040d0812100f140e0c0f0c110d0e120f0b12140a0e0d0c0c0c0d0c0d0c0c0b0b090e0a0c');
INSERT INTO mcp_servers_fts_data VALUES(962072674305,X'00000156023061170601010b02076e616c79736973170601020303016417060101090108636f646562617365170c010110010202050567726170681703040106656e7469747917060102060209787472616374696f6e1706010207010867656e65726174651706010108020472617068170c01010c01020401086c616e6775616765170601020b01036d63701709020101020204756c7469170601020a01026f66170601010e010870726f7669646573170601010501057175657279170601010a010c72656c6174696f6e736869701706010208030c70726573656e746174696f6e170c01010d010205010673657276657217090301010302047464696f170601040202067570706f7274170601020c010474686174170601010402016f170601010703036f6c73170601010602077261636b696e671706010209020979706573637269707417060103020104796f7572170601010f04080e08120a0d100f0e0f0b0b090f0c13160e0b0d0b080a0e10');
INSERT INTO mcp_servers_fts_data VALUES(1099511627777,X'000001320930616e616c79736973230601020606047a696e6723060101070301642306010106010462696c6c230601010901096379636c6f6e656478230c01010e010204010a646570656e64656e63792306010205030774656374696f6e23060102080103666f72230601010404036d6174230601010f010a67656e65726174696e67230601010509026f6e230601020301076c6963656e7365230601020701096d6174657269616c73230601010b0202637023090201010201026f66230601010a0106707974686f6e2306010302010473626f6d230f0301010c010202020763616e6e696e67230601020a0205657276657223090401010302076f667477617265230601010802047464696f230601040201057573696e67230601010d010d76756c6e65726162696c6974792306010209040f0b080b13110e0a0a11090e100a090d0f0e0d0e0b0c');
CREATE TABLE IF NOT EXISTS 'mcp_servers_fts_idx'(segid, term, pgno, PRIMARY KEY(segid, term)) WITHOUT ROWID;
INSERT INTO mcp_servers_fts_idx VALUES(1,X'',2);
INSERT INTO mcp_servers_fts_idx VALUES(2,X'',2);
INSERT INTO mcp_servers_fts_idx VALUES(3,X'',2);
INSERT INTO mcp_servers_fts_idx VALUES(4,X'',2);
INSERT INTO mcp_servers_fts_idx VALUES(5,X'',2);
INSERT INTO mcp_servers_fts_idx VALUES(6,X'',2);
INSERT INTO mcp_servers_fts_idx VALUES(7,X'',2);
INSERT INTO mcp_servers_fts_idx VALUES(8,X'',2);
CREATE TABLE IF NOT EXISTS 'mcp_servers_fts_docsize'(id INTEGER PRIMARY KEY, sz BLOB);
INSERT INTO mcp_servers_fts_docsize VALUES(1,X'0400000000');
INSERT INTO mcp_servers_fts_docsize VALUES(2,X'0200000000');
INSERT INTO mcp_servers_fts_docsize VALUES(3,X'0300000000');
INSERT INTO mcp_servers_fts_docsize VALUES(4,X'0400000000');
INSERT INTO mcp_servers_fts_docsize VALUES(5,X'03201c0101');
INSERT INTO mcp_servers_fts_docsize VALUES(6,X'0200000000');
INSERT INTO mcp_servers_fts_docsize VALUES(7,X'0300000000');
INSERT INTO mcp_servers_fts_docsize VALUES(8,X'0400000000');
INSERT INTO mcp_servers_fts_docsize VALUES(9,X'0400000000');
INSERT INTO mcp_servers_fts_docsize VALUES(10,X'0200000000');
INSERT INTO mcp_servers_fts_docsize VALUES(11,X'0200000000');
INSERT INTO mcp_servers_fts_docsize VALUES(12,X'03100a0101');
INSERT INTO mcp_servers_fts_docsize VALUES(13,X'0200000000');
INSERT INTO mcp_servers_fts_docsize VALUES(14,X'0300000000');
INSERT INTO mcp_servers_fts_docsize VALUES(15,X'0300000000');
INSERT INTO mcp_servers_fts_docsize VALUES(16,X'0200000000');
INSERT INTO mcp_servers_fts_docsize VALUES(17,X'0200000000');
INSERT INTO mcp_servers_fts_docsize VALUES(18,X'0300000000');
INSERT INTO mcp_servers_fts_docsize VALUES(19,X'0100000000');
INSERT INTO mcp_servers_fts_docsize VALUES(20,X'0300000000');
INSERT INTO mcp_servers_fts_docsize VALUES(21,X'0300000000');
INSERT INTO mcp_servers_fts_docsize VALUES(22,X'0300000000');
INSERT INTO mcp_servers_fts_docsize VALUES(23,X'030f0b0101');
INSERT INTO mcp_servers_fts_docsize VALUES(24,X'0200000000');
INSERT INTO mcp_servers_fts_docsize VALUES(25,X'0100000000');
INSERT INTO mcp_servers_fts_docsize VALUES(26,X'0200000000');
INSERT INTO mcp_servers_fts_docsize VALUES(27,X'0200000000');
INSERT INTO mcp_servers_fts_docsize VALUES(28,X'0300000000');
INSERT INTO mcp_servers_fts_docsize VALUES(29,X'0400000000');
INSERT INTO mcp_servers_fts_docsize VALUES(30,X'0300000000');
INSERT INTO mcp_servers_fts_docsize VALUES(31,X'0300000000');
INSERT INTO mcp_servers_fts_docsize VALUES(32,X'0300000000');
INSERT INTO mcp_servers_fts_docsize VALUES(33,X'02170d0100');
INSERT INTO mcp_servers_fts_docsize VALUES(34,X'0300000000');
INSERT INTO mcp_servers_fts_docsize VALUES(35,X'030e090101');
INSERT INTO mcp_servers_fts_docsize VALUES(36,X'0400000000');
INSERT INTO mcp_servers_fts_docsize VALUES(37,X'0417130100');
INSERT INTO mcp_servers_fts_docsize VALUES(38,X'0400000000');
INSERT INTO mcp_servers_fts_docsize VALUES(39,X'0400000000');
CREATE TABLE IF NOT EXISTS 'mcp_servers_fts_config'(k PRIMARY KEY, v) WITHOUT ROWID;
INSERT INTO mcp_servers_fts_config VALUES('version',4);
CREATE TRIGGER mcp_servers_ai AFTER INSERT ON mcp_servers BEGIN
  INSERT INTO mcp_servers_fts(rowid, name, description, features, language, transport)
  VALUES (new.id, new.name, new.description, new.features, new.language, new.transport);
END;
CREATE TRIGGER mcp_servers_ad AFTER DELETE ON mcp_servers BEGIN
  INSERT INTO mcp_servers_fts(mcp_servers_fts, rowid, name, description, features, language, transport)
  VALUES ('delete', old.id, old.name, old.description, old.features, old.language, old.transport);
END;
CREATE TRIGGER mcp_servers_au AFTER UPDATE ON mcp_servers BEGIN
  INSERT INTO mcp_servers_fts(mcp_servers_fts, rowid, name, description, features, language, transport)
  VALUES ('delete', old.id, old.name, old.description, old.features, old.language, old.transport);
  INSERT INTO mcp_servers_fts(rowid, name, description, features, language, transport)
  VALUES (new.id, new.name, new.description, new.features, new.language, new.transport);
END;
PRAGMA writable_schema=OFF;
COMMIT;
