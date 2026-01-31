# /hunt - Comprehensive Threat Hunting Assistant

A sophisticated threat hunting command that guides security analysts through the entire threat hunting lifecycle, from initial context gathering to final reporting.

## Usage
```
/project:hunt [init|plan|research|indicators|queries|report|todos]
```

## Arguments (XOR - only one at a time)

- **init** - Initialize hunting context and gather threat actor information
- **plan** - Create research and hunt plans based on context
- **research** - Execute research plan and analyze threat actor TTPs
- **indicators** - Generate indicators from research findings
- **queries** - Create detection queries for configured search platforms
- **report** - Generate comprehensive threat hunting report
- **todos** - Update task list based on findings and queries

## Features

### 1. Multi-Platform Support
- Splunk SPL
- Microsoft KQL (Sentinel/Defender)
- Elastic Query DSL
- SQL-based platforms
- Dynamically loads platform-specific guides

### 2. MITRE ATT&CK Integration
- Maps findings to techniques
- Generates coverage matrices
- Tracks TTP patterns
- Prioritizes based on risk

### 3. Persistent Context
- Maintains state across sessions
- Progress tracking
- Workflow resumption
- Cross-task context sharing

### 4. OSINT Integration
- MITRE ATT&CK API
- Threat intelligence feeds
- Infrastructure analysis
- Actor attribution research

## Directory Structure
```
.hunt/
├── context.md              # Hunt configuration
├── persistent.context.md   # Cross-session state
├── plans/
│   ├── research.md        # Research strategy
│   └── threat-hunt.md     # Hunt methodology
├── research/
│   ├── findings.md        # Research results
│   └── analysis.md        # TTP analysis
├── indicators/
│   └── [indicator].md     # Individual IOCs
├── queries/
│   ├── splunk/           # Platform-specific
│   ├── kql/              # queries
│   ├── elastic/
│   └── sql/
├── findings/             # Manual findings
└── todos.md             # Task tracking
```

## Implementation

```typescript
interface HuntCommand {
  name: string;
  description: string;
  author: string;
  version: string;
  trigger: string;
  arguments: {
    init: () => Promise<void>;
    plan: () => Promise<void>;
    research: () => Promise<void>;
    indicators: () => Promise<void>;
    queries: () => Promise<void>;
    report: () => Promise<void>;
    todos: () => Promise<void>;
  };
}

const hunt: HuntCommand = {
  name: "hunt",
  description: "Comprehensive threat hunting assistant",
  author: "Security Team",
  version: "1.0.0",
  trigger: "/project:hunt",
  
  arguments: {
    init: async () => {
      // Check/create directory structure
      const dirs = [
        '.hunt',
        '.hunt/plans',
        '.hunt/research',
        '.hunt/indicators',
        '.hunt/queries',
        '.hunt/queries/splunk',
        '.hunt/queries/kql',
        '.hunt/queries/elastic',
        '.hunt/queries/sql',
        '.hunt/findings'
      ];
      
      for (const dir of dirs) {
        if (!fs.existsSync(dir)) {
          fs.mkdirSync(dir, { recursive: true });
        }
      }
      
      // Interactive context gathering
      const context = {
        threatActor: {
          name: await prompt("Threat Actor Name:"),
          aliases: await promptList("Known Aliases (comma-separated):"),
          attribution: await prompt("Attribution Confidence (low/medium/high):"),
          objectives: await promptList("Known Objectives:"),
          targets: await promptList("Known Target Industries/Regions:")
        },
        datasets: await gatherDatasets(),
        client: await gatherClientProfile(),
        scope: await gatherScope(),
        searchPlatform: await prompt("Primary Search Platform (splunk/kql/elastic/sql):"),
        created: new Date().toISOString(),
        lastModified: new Date().toISOString()
      };
      
      // Repeatedly clarify until satisfied
      while (await needsClarification(context)) {
        context = await clarifyContext(context);
      }
      
      // Save context
      await saveContext(context);
      
      // Initialize persistent context
      await initPersistentContext();
    },
    
    plan: async () => {
      // Load context
      const context = await loadContext();
      if (!context) {
        console.log("No context found. Running init first...");
        await this.arguments.init();
        return await this.arguments.plan();
      }
      
      // Load search tool guide
      const toolGuide = await loadToolGuide(context.searchPlatform);
      
      // Research threat actor
      const actorResearch = await researchThreatActor(context.threatActor);
      
      // Generate research plan
      const researchPlan = {
        objectives: [
          "Identify all known aliases and attribution",
          "Map complete TTP framework",
          "Discover infrastructure patterns",
          "Analyze targeting methodology",
          "Find detection opportunities"
        ],
        sources: [
          "MITRE ATT&CK",
          "Open source intelligence",
          "Threat intelligence reports",
          "Security vendor research",
          "Infrastructure analysis"
        ],
        methodology: "Structured analytical techniques",
        timeline: "Systematic phase-based approach",
        deliverables: [
          "Comprehensive actor profile",
          "TTP mapping",
          "Infrastructure indicators",
          "Detection strategies"
        ]
      };
      
      // Generate hunt plan
      const huntPlan = {
        priorities: [
          "Active exploitation indicators",
          "Compromise of high-value assets",
          "Lateral movement patterns",
          "Data exfiltration attempts",
          "Persistence mechanisms"
        ],
        methodology: generateHuntMethodology(context, actorResearch),
        phases: [
          "Initial triage",
          "Deep-dive analysis",
          "Pattern correlation",
          "Validation",
          "Remediation planning"
        ],
        success_criteria: [
          "Complete dataset coverage",
          "All TTPs investigated",
          "Risk assessment completed",
          "Actionable findings documented"
        ]
      };
      
      // Save plans
      await savePlan('research', researchPlan);
      await savePlan('threat-hunt', huntPlan);
      
      // Update progress
      await updateProgress('plan', 'completed');
    },
    
    research: async () => {
      // Load research plan
      const plan = await loadPlan('research');
      if (!plan) {
        console.log("No research plan found. Running plan first...");
        await this.arguments.plan();
        return await this.arguments.research();
      }
      
      const context = await loadContext();
      const findings = [];
      const analysis = {
        patterns: [],
        infrastructure: [],
        ttps: [],
        targeting: [],
        detection_opportunities: []
      };
      
      // Execute research systematically
      for (const objective of plan.objectives) {
        console.log(`Researching: ${objective}`);
        const result = await executeResearch(objective, context);
        findings.push(...result.findings);
        
        // Deep analysis of each finding
        for (const finding of result.findings) {
          const analyzed = await analyzeFinding(finding, context);
          updateAnalysis(analysis, analyzed);
        }
      }
      
      // Find missed connections
      const connections = await findConnections(findings, analysis);
      analysis.connections = connections;
      
      // Map to MITRE ATT&CK
      analysis.attack_mapping = await mapToAttack(analysis.ttps);
      
      // Save results
      await saveResearch('findings', findings);
      await saveResearch('analysis', analysis);
      
      // Update progress
      await updateProgress('research', 'completed');
    },
    
    indicators: async () => {
      // Load research
      const findings = await loadResearch('findings');
      const analysis = await loadResearch('analysis');
      
      if (!findings || !analysis) {
        console.log("No research found. Running research first...");
        await this.arguments.research();
        return await this.arguments.indicators();
      }
      
      // Load indicator template
      const template = await loadTemplate('indicator');
      
      // Extract indicators
      const indicators = await extractIndicators(findings, analysis);
      
      // Process each indicator
      for (const indicator of indicators) {
        const enriched = await enrichIndicator(indicator);
        const formatted = await formatIndicator(enriched, template);
        await saveIndicator(formatted);
      }
      
      // Update progress
      await updateProgress('indicators', 'completed');
    },
    
    queries: async () => {
      // Load context and indicators
      const context = await loadContext();
      const indicators = await loadIndicators();
      
      if (!indicators || indicators.length === 0) {
        console.log("No indicators found. Running indicators first...");
        await this.arguments.indicators();
        return await this.arguments.queries();
      }
      
      // Load query template for platform
      const template = await loadTemplate(`query-${context.searchPlatform}`);
      
      // Generate queries
      const queries = [];
      for (const indicator of indicators) {
        const query = await generateQuery(indicator, context, template);
        queries.push(query);
      }
      
      // Optimize and deduplicate
      const optimized = await optimizeQueries(queries);
      
      // Save queries
      for (const query of optimized) {
        await saveQuery(query, context.searchPlatform);
      }
      
      // Update progress
      await updateProgress('queries', 'completed');
    },
    
    report: async () => {
      // Load all findings
      const findings = await loadFindings();
      const context = await loadContext();
      
      if (!findings || findings.length === 0) {
        console.log("No findings to report. Please add findings to .hunt/findings/ directory.");
        return;
      }
      
      // Analyze findings
      const reportPlan = await createReportPlan(findings, context);
      
      // Interactive refinement
      let approved = false;
      while (!approved) {
        console.log("Report Plan:", reportPlan);
        const feedback = await prompt("Any clarifications or changes needed? (enter 'approve' when ready)");
        if (feedback.toLowerCase() === 'approve') {
          approved = true;
        } else {
          reportPlan = await refineReportPlan(reportPlan, feedback);
        }
      }
      
      // Generate report
      const template = await loadTemplate('report');
      const report = await generateReport(reportPlan, template);
      await saveReport(report);
      
      // Update progress
      await updateProgress('report', 'completed');
    },
    
    todos: async () => {
      // Load findings and queries
      const findings = await loadFindings();
      const queries = await loadAllQueries();
      
      // Generate todos
      const todos = [];
      
      // From findings
      for (const finding of findings) {
        const tasks = await generateTasksFromFinding(finding);
        todos.push(...tasks);
      }
      
      // From queries
      for (const query of queries) {
        const tasks = await generateTasksFromQuery(query);
        todos.push(...tasks);
      }
      
      // Prioritize and deduplicate
      const prioritized = await prioritizeTodos(todos);
      
      // Update todos file
      await updateTodos(prioritized);
      
      // Update progress
      await updateProgress('todos', 'completed');
    }
  }
};

// Helper functions
async function loadContext() {
  const contextPath = '.hunt/context.md';
  if (!fs.existsSync(contextPath)) {
    return null;
  }
  return parseContext(await fs.readFile(contextPath));
}

async function loadToolGuide(platform) {
  const localPath = `.claude/guides/tools/${platform}.md`;
  const globalPath = `~/.claude/guides/tools/${platform}.md`;
  
  if (fs.existsSync(localPath)) {
    return await fs.readFile(localPath);
  } else if (fs.existsSync(globalPath)) {
    return await fs.readFile(globalPath);
  }
  return null;
}

async function loadTemplate(type) {
  const localPath = `.claude/templates/hunt/${type}.md`;
  const globalPath = `~/.claude/templates/hunt/${type}.md`;
  
  if (fs.existsSync(localPath)) {
    return await fs.readFile(localPath);
  } else if (fs.existsSync(globalPath)) {
    return await fs.readFile(globalPath);
  } else {
    // Create default template
    const template = await createDefaultTemplate(type);
    console.log(`Creating default ${type} template. Please review:`);
    console.log(template);
    const approved = await prompt("Approve template? (yes/no/edit)");
    if (approved === 'edit') {
      return await editTemplate(template);
    }
    await fs.writeFile(globalPath, template);
    return template;
  }
}

async function updateProgress(phase, status) {
  const progressPath = '.hunt/persistent.context.md';
  const progress = await loadProgress() || {};
  progress[phase] = {
    status,
    timestamp: new Date().toISOString()
  };
  await saveProgress(progress);
}

// Export command
export default hunt;
```

## Examples

### Initialize a new hunt
```
/project:hunt init
> Creating threat hunting context...
> Threat Actor Name: APT29
> Known Aliases: Cozy Bear, The Dukes
> Primary Search Platform: splunk
> Dataset: Security Logs (90 days, 2.3TB)
> Client Industry: Government
> Context saved to .hunt/context.md
```

### Generate hunt plans
```
/project:hunt plan
> Loading context and Splunk guide...
> Researching APT29 variants and TTPs...
> Creating research plan aligned with MITRE ATT&CK...
> Generating hunt plan for Government sector...
> Plans saved to .hunt/plans/
```

### Execute research
```
/project:hunt research
> Executing research plan...
> Analyzing APT29 TTPs...
> Discovering infrastructure patterns...
> Mapping to client profile...
> Research complete. Findings saved to .hunt/research/
```

### Generate queries
```
/project:hunt queries
> Loading indicators and Splunk configuration...
> Generating optimized SPL queries...
> Adding dependency tracking and documentation...
> 47 queries saved to .hunt/queries/splunk/
```

## Configuration

The command automatically creates and manages:
- Context files for threat actor and environment details
- Research and hunt plans aligned with MITRE ATT&CK
- Indicator extraction and management
- Platform-specific query generation
- Comprehensive reporting templates
- Task tracking and prioritization

## Best Practices

1. **Always start with init** to establish proper context
2. **Follow the workflow order** for best results
3. **Review auto-generated content** before proceeding
4. **Maintain findings manually** in .hunt/findings/
5. **Use persistent context** for long-running hunts
6. **Leverage templates** for consistency

## Integration

The hunt command integrates with:
- MITRE ATT&CK framework
- Multiple search platforms
- OSINT sources
- Template system
- Progress tracking

For more information, see the threat hunting guides in ~/.claude/guides/security/