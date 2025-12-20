# Process: CostTracking

## Purpose
Track and optimize CI/CD costs across platforms to reduce expenses while maintaining performance

## Trigger
- Monthly cost review
- Budget threshold alerts
- Pipeline performance degradation
- New project onboarding

## Prerequisites
- Access to billing data
- Pipeline metrics collection
- Resource usage monitoring

## Metrics to Track

### 1. Build Minutes/Hours
```yaml
metrics:
  build_time:
    - total_minutes_per_month
    - minutes_per_pipeline
    - minutes_per_job
    - peak_usage_times
    - idle_time_percentage
```

### 2. Storage Usage
```yaml
metrics:
  storage:
    - artifact_storage_gb
    - cache_storage_gb
    - docker_registry_gb
    - log_retention_gb
    - backup_storage_gb
```

### 3. Data Transfer
```yaml
metrics:
  transfer:
    - artifact_downloads_gb
    - docker_pulls_gb
    - external_api_calls
    - cross_region_transfer_gb
```

### 4. Third-party Service Costs
```yaml
metrics:
  services:
    - security_scanning_cost
    - monitoring_tools_cost
    - deployment_tools_cost
    - notification_services_cost
```

## Optimization Strategies

### 1. Caching Optimization
```yaml
caching:
  strategies:
    - dependency_caching:
        description: Cache package dependencies
        savings: 40-60% build time
        implementation: |
          # GitHub Actions
          - uses: actions/cache@v3
            with:
              path: ~/.npm
              key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}
          
          # GitLab CI
          cache:
            key:
              files:
                - package-lock.json
            paths:
              - node_modules/
    
    - docker_layer_caching:
        description: Cache Docker layers
        savings: 50-70% build time
        implementation: |
          # Use buildkit
          DOCKER_BUILDKIT=1 docker build --cache-from type=local,src=/tmp/.buildx-cache
    
    - build_output_caching:
        description: Cache build artifacts
        savings: 30-50% pipeline time
```

### 2. Parallel Job Efficiency
```yaml
parallelization:
  strategies:
    - smart_job_splitting:
        description: Split tests intelligently
        implementation: |
          # Split by timing data
          split-tests --by-timing --count $CI_NODE_TOTAL
    
    - matrix_optimization:
        description: Optimize matrix builds
        implementation: |
          strategy:
            matrix:
              include:
                - os: ubuntu-latest
                  node: 18  # Only test latest on Linux
                - os: windows-latest
                  node: 16  # Test older on Windows
    
    - fail_fast:
        description: Stop on first failure
        implementation: |
          strategy:
            fail-fast: true
            max-parallel: 2
```

### 3. Self-hosted Runners
```yaml
self_hosted:
  cost_comparison:
    github_hosted:
      cost_per_minute: $0.008
      monthly_estimate: $500-2000
    
    self_hosted:
      ec2_instance: t3.large
      monthly_cost: $60-80
      break_even: 200 hours/month
  
  implementation:
    aws_spot_instances: |
      # Use spot instances for 70% savings
      resource "aws_spot_instance_request" "runner" {
        ami           = "ami-runner"
        instance_type = "t3.large"
        spot_price    = "0.03"
      }
    
    autoscaling: |
      # Scale based on queue depth
      resource "aws_autoscaling_group" "runners" {
        min_size         = 0
        max_size         = 10
        desired_capacity = var.queue_depth > 0 ? 2 : 0
      }
```

### 4. Artifact Retention Policies
```yaml
retention:
  policies:
    - development_artifacts:
        retention_days: 1
        pattern: "dev-*"
    
    - staging_artifacts:
        retention_days: 7
        pattern: "staging-*"
    
    - production_artifacts:
        retention_days: 90
        pattern: "prod-*"
    
    - log_files:
        retention_days: 14
        compression: true
        
  implementation: |
    # GitHub Actions
    - uses: actions/upload-artifact@v3
      with:
        retention-days: 1
    
    # GitLab CI
    artifacts:
      expire_in: 1 day
```

### 5. Build Frequency Optimization
```yaml
frequency:
  strategies:
    - batch_builds:
        description: Group commits
        implementation: |
          # Only build on batched commits
          on:
            schedule:
              - cron: '0 */4 * * *'  # Every 4 hours
    
    - skip_redundant:
        description: Skip unchanged paths
        implementation: |
          - name: Check changes
            uses: dorny/paths-filter@v2
            id: changes
            with:
              filters: |
                backend:
                  - 'backend/**'
                frontend:
                  - 'frontend/**'
    
    - cancel_outdated:
        description: Cancel superseded builds
        implementation: |
          concurrency:
            group: ${{ github.workflow }}-${{ github.ref }}
            cancel-in-progress: true
```

## Platform-Specific Tracking

### GitHub Actions
```yaml
github_actions:
  api_endpoints:
    - usage: GET /repos/{owner}/{repo}/actions/billing
    - workflow_usage: GET /repos/{owner}/{repo}/actions/workflows/{id}/timing
  
  cost_calculation: |
    const minutesByOS = {
      'ubuntu': usage.ubuntu_minutes,
      'windows': usage.windows_minutes * 2,  // 2x multiplier
      'macos': usage.macos_minutes * 10      // 10x multiplier
    };
    
    const totalMinutes = Object.values(minutesByOS).reduce((a, b) => a + b, 0);
    const monthlyCost = totalMinutes * 0.008;
  
  optimization_tips:
    - Use Ubuntu runners when possible (cheapest)
    - Implement job caching aggressively
    - Use workflow_dispatch for manual runs
    - Enable automatic cancellation
```

### GitLab CI
```yaml
gitlab_ci:
  api_endpoints:
    - usage: GET /projects/:id/statistics
    - pipeline_stats: GET /projects/:id/pipelines/statistics
  
  cost_tracking: |
    # Pipeline minutes by runner type
    SELECT 
      runner_type,
      SUM(duration_seconds) / 60 as minutes,
      COUNT(*) as job_count
    FROM ci_builds
    WHERE created_at > DATE_SUB(NOW(), INTERVAL 1 MONTH)
    GROUP BY runner_type;
  
  shared_runner_costs:
    free_tier: 400 minutes/month
    additional_packs: $10 per 1000 minutes
    
  optimization_tips:
    - Use project runners for high-volume
    - Implement DAG pipelines
    - Use interruptible jobs
    - Cache aggressively
```

## Cost Monitoring Dashboard

```yaml
dashboard:
  metrics:
    - current_month_spend:
        query: SELECT SUM(cost) FROM ci_costs WHERE month = CURRENT_MONTH
        alert_threshold: 80% of budget
    
    - cost_per_developer:
        query: SELECT cost / developer_count FROM team_costs
        benchmark: $50-100/month
    
    - waste_percentage:
        query: SELECT (failed_builds_cost / total_cost) * 100
        target: < 10%
    
    - cache_hit_rate:
        query: SELECT (cache_hits / total_builds) * 100
        target: > 80%
```

## Cost Reduction Playbook

### Quick Wins (1 day)
1. Enable caching for dependencies
2. Set artifact retention policies
3. Cancel redundant builds
4. Use fail-fast strategy

### Medium Effort (1 week)
1. Implement parallel job optimization
2. Set up self-hosted runners
3. Create build frequency rules
4. Optimize Docker builds

### Long Term (1 month)
1. Implement full monitoring
2. Automate cost optimization
3. Create team dashboards
4. Establish cost budgets

## ROI Calculation

```yaml
roi_metrics:
  cost_reduction:
    before: $2000/month
    after: $800/month
    savings: $1200/month ($14,400/year)
  
  time_savings:
    build_time_reduction: 40%
    developer_hours_saved: 20/month
    value: $2000/month @ $100/hour
  
  total_benefit: $3200/month
  implementation_cost: $5000 (one-time)
  break_even: 1.6 months
```

## Alerts and Automation

```yaml
alerts:
  - cost_spike:
      condition: daily_cost > 1.5 * average_daily_cost
      action: notify_team_lead
  
  - budget_threshold:
      condition: monthly_spend > 0.8 * budget
      action: 
        - notify_finance
        - throttle_builds
  
  - inefficiency_detection:
      condition: cache_hit_rate < 50%
      action: 
        - generate_optimization_report
        - create_jira_ticket

automation:
  - auto_scaling:
      trigger: queue_depth > 10
      action: scale_up_runners
  
  - artifact_cleanup:
      schedule: daily
      action: delete_old_artifacts
  
  - cost_report:
      schedule: weekly
      action: send_cost_summary
```