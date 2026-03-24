# Virtualization Provider Patterns

## vSphere Provider (vmware/vsphere)

### Provider Configuration
```hcl
terraform {
  required_providers {
    vsphere = {
      source  = "hashicorp/vsphere"
      version = "~> 2.0"
    }
  }
}

provider "vsphere" {
  user                 = var.vsphere_user
  password             = var.vsphere_password
  vsphere_server       = var.vsphere_server
  allow_unverified_ssl = var.allow_unverified_ssl

  # Optional REST API configuration
  rest_session_path = "/rest"
}
```

### Data Sources
```hcl
data "vsphere_datacenter" "dc" {
  name = var.datacenter
}

data "vsphere_compute_cluster" "cluster" {
  name          = var.cluster
  datacenter_id = data.vsphere_datacenter.dc.id
}

data "vsphere_datastore" "datastore" {
  name          = var.datastore
  datacenter_id = data.vsphere_datacenter.dc.id
}

data "vsphere_network" "network" {
  name          = var.network
  datacenter_id = data.vsphere_datacenter.dc.id
}

data "vsphere_virtual_machine" "template" {
  name          = var.template
  datacenter_id = data.vsphere_datacenter.dc.id
}

data "vsphere_resource_pool" "pool" {
  name          = var.resource_pool
  datacenter_id = data.vsphere_datacenter.dc.id
}

data "vsphere_host" "host" {
  name          = var.esxi_host
  datacenter_id = data.vsphere_datacenter.dc.id
}

data "vsphere_content_library" "library" {
  name = var.content_library
}

data "vsphere_content_library_item" "template" {
  library_id = data.vsphere_content_library.library.id
  name       = var.library_template
  type       = "ovf"
}
```

### Virtual Machine Module
```hcl
variable "virtual_machines" {
  description = "Virtual machine configurations"
  type = map(object({
    num_cpus             = number
    memory               = number
    guest_id             = optional(string, "ubuntu64Guest")
    firmware             = optional(string, "efi")
    efi_secure_boot_enabled = optional(bool, true)
    disk_size            = number
    thin_provisioned     = optional(bool, true)
    eagerly_scrub        = optional(bool, false)
    folder               = optional(string)
    annotation           = optional(string)
    cpu_hot_add_enabled  = optional(bool, false)
    memory_hot_add_enabled = optional(bool, false)
    resource_pool_id     = optional(string)
    host_system_id       = optional(string)
    wait_for_guest_net_timeout = optional(number, 5)
    wait_for_guest_ip_timeout  = optional(number, 5)
    customize = optional(object({
      linux_options = optional(object({
        host_name = string
        domain    = string
      }))
      network_interface = optional(object({
        ipv4_address = string
        ipv4_netmask = number
      }))
      ipv4_gateway = optional(string)
      dns_server_list = optional(list(string))
      dns_suffix_list = optional(list(string))
    }))
    extra_config = optional(map(string), {})
    tags         = optional(list(string), [])
  }))
}

resource "vsphere_virtual_machine" "this" {
  for_each = var.virtual_machines

  name             = each.key
  resource_pool_id = each.value.resource_pool_id != null ? each.value.resource_pool_id : data.vsphere_compute_cluster.cluster.resource_pool_id
  datastore_id     = data.vsphere_datastore.datastore.id
  host_system_id   = each.value.host_system_id
  folder           = each.value.folder
  annotation       = each.value.annotation

  num_cpus             = each.value.num_cpus
  memory               = each.value.memory
  guest_id             = each.value.guest_id
  firmware             = each.value.firmware
  efi_secure_boot_enabled = each.value.efi_secure_boot_enabled

  cpu_hot_add_enabled    = each.value.cpu_hot_add_enabled
  memory_hot_add_enabled = each.value.memory_hot_add_enabled

  wait_for_guest_net_timeout = each.value.wait_for_guest_net_timeout
  wait_for_guest_ip_timeout  = each.value.wait_for_guest_ip_timeout

  network_interface {
    network_id   = data.vsphere_network.network.id
    adapter_type = "vmxnet3"
  }

  disk {
    label            = "disk0"
    size             = each.value.disk_size
    thin_provisioned = each.value.thin_provisioned
    eagerly_scrub    = each.value.eagerly_scrub
  }

  clone {
    template_uuid = data.vsphere_virtual_machine.template.id

    dynamic "customize" {
      for_each = each.value.customize != null ? [each.value.customize] : []
      content {
        dynamic "linux_options" {
          for_each = customize.value.linux_options != null ? [customize.value.linux_options] : []
          content {
            host_name = linux_options.value.host_name
            domain    = linux_options.value.domain
          }
        }

        dynamic "network_interface" {
          for_each = customize.value.network_interface != null ? [customize.value.network_interface] : []
          content {
            ipv4_address = network_interface.value.ipv4_address
            ipv4_netmask = network_interface.value.ipv4_netmask
          }
        }

        ipv4_gateway    = customize.value.ipv4_gateway
        dns_server_list = customize.value.dns_server_list
        dns_suffix_list = customize.value.dns_suffix_list
      }
    }
  }

  extra_config = each.value.extra_config
  tags         = each.value.tags

  lifecycle {
    ignore_changes = [
      clone[0].template_uuid,
      disk[0].io_share_count,
    ]
  }
}
```

### VM from Content Library
```hcl
resource "vsphere_virtual_machine" "from_content_library" {
  for_each = var.content_library_vms

  name             = each.key
  resource_pool_id = data.vsphere_compute_cluster.cluster.resource_pool_id
  datastore_id     = data.vsphere_datastore.datastore.id

  num_cpus = each.value.num_cpus
  memory   = each.value.memory
  guest_id = each.value.guest_id

  network_interface {
    network_id = data.vsphere_network.network.id
  }

  disk {
    label = "disk0"
    size  = each.value.disk_size
  }

  clone {
    template_uuid = data.vsphere_content_library_item.template.id
  }

  cdrom {
    client_device = true
  }
}
```

### vApp Module
```hcl
resource "vsphere_vapp_container" "this" {
  for_each = var.vapps

  name                    = each.key
  parent_resource_pool_id = data.vsphere_compute_cluster.cluster.resource_pool_id
  parent_folder_id        = each.value.folder_id

  cpu_share_level    = each.value.cpu_share_level
  cpu_reservation    = each.value.cpu_reservation
  cpu_expandable     = each.value.cpu_expandable
  cpu_limit          = each.value.cpu_limit
  memory_share_level = each.value.memory_share_level
  memory_reservation = each.value.memory_reservation
  memory_expandable  = each.value.memory_expandable
  memory_limit       = each.value.memory_limit

  tags = each.value.tags
}
```

### Distributed Switch Module
```hcl
resource "vsphere_distributed_virtual_switch" "this" {
  for_each = var.distributed_switches

  name          = each.key
  datacenter_id = data.vsphere_datacenter.dc.id

  max_mtu                = each.value.max_mtu
  link_discovery_protocol = each.value.link_discovery_protocol
  link_discovery_operation = each.value.link_discovery_operation

  uplinks         = each.value.uplinks
  active_uplinks  = each.value.active_uplinks
  standby_uplinks = each.value.standby_uplinks

  dynamic "host" {
    for_each = each.value.hosts
    content {
      host_system_id = host.value.host_system_id
      devices        = host.value.devices
    }
  }

  tags = each.value.tags
}

resource "vsphere_distributed_port_group" "this" {
  for_each = var.port_groups

  name                            = each.key
  distributed_virtual_switch_uuid = vsphere_distributed_virtual_switch.this[each.value.switch_name].id
  vlan_id                         = each.value.vlan_id
  type                            = each.value.type  # earlyBinding, lateBinding, ephemeral

  allow_forged_transmits = each.value.allow_forged_transmits
  allow_mac_changes      = each.value.allow_mac_changes
  allow_promiscuous      = each.value.allow_promiscuous
}
```

---

## VMware Cloud (VMC) Provider (vmware/vmc)

### Provider Configuration
```hcl
terraform {
  required_providers {
    vmc = {
      source  = "vmware/vmc"
      version = "~> 1.0"
    }
  }
}

provider "vmc" {
  refresh_token = var.vmc_refresh_token
  org_id        = var.vmc_org_id
}
```

### SDDC Module
```hcl
data "vmc_connected_accounts" "this" {
  account_number = var.aws_account_number
}

data "vmc_customer_subnets" "this" {
  connected_account_id = data.vmc_connected_accounts.this.id
  region               = var.region
}

resource "vmc_sddc" "this" {
  for_each = var.sddcs

  sddc_name           = each.key
  vpc_cidr            = each.value.vpc_cidr
  num_host            = each.value.num_hosts
  provider_type       = each.value.provider_type  # AWS, ZEROCLOUD
  region              = each.value.region
  vxlan_subnet        = each.value.vxlan_subnet
  delay_account_link  = each.value.delay_account_link
  skip_creating_vxlan = each.value.skip_creating_vxlan
  sso_domain          = each.value.sso_domain
  sddc_type           = each.value.sddc_type  # DEFAULT, 1NODE
  deployment_type     = each.value.deployment_type  # SingleAZ, MultiAZ
  size                = each.value.size  # medium, large, i3.metal, etc.

  account_link_sddc_config {
    customer_subnet_ids  = data.vmc_customer_subnets.this.ids
    connected_account_id = data.vmc_connected_accounts.this.id
  }

  microsoft_licensing_config {
    mssql_licensing = each.value.mssql_licensing
    windows_licensing = each.value.windows_licensing
  }

  timeouts {
    create = each.value.create_timeout
    update = each.value.update_timeout
    delete = each.value.delete_timeout
  }
}
```

### Cluster Module
```hcl
resource "vmc_cluster" "this" {
  for_each = var.clusters

  sddc_id      = each.value.sddc_id
  num_hosts    = each.value.num_hosts
  host_cpu_cores_count = each.value.cpu_cores
  host_instance_type   = each.value.instance_type
  storage_capacity     = each.value.storage_capacity

  microsoft_licensing_config {
    mssql_licensing = each.value.mssql_licensing
    windows_licensing = each.value.windows_licensing
  }
}
```

### Site Recovery Module
```hcl
resource "vmc_site_recovery" "this" {
  for_each = var.site_recovery_configs

  sddc_id                       = each.value.sddc_id
  srm_extension_key_suffix      = each.value.srm_suffix
}

resource "vmc_srm_node" "this" {
  for_each = var.srm_nodes

  sddc_id                  = each.value.sddc_id
  srm_node_extension_key_suffix = each.value.node_suffix
}
```

### Public IP Module
```hcl
resource "vmc_public_ip" "this" {
  for_each = var.public_ips

  nsxt_reverse_proxy_url = each.value.nsxt_url
  display_name           = each.key
}
```

---

## Proxmox Provider (bpg/proxmox)

### Provider Configuration
```hcl
terraform {
  required_providers {
    proxmox = {
      source  = "bpg/proxmox"
      version = "~> 0.46"
    }
  }
}

provider "proxmox" {
  endpoint = var.proxmox_url
  username = var.proxmox_username
  password = var.proxmox_password

  # Or use API token
  # api_token = var.proxmox_api_token

  insecure = var.proxmox_insecure

  ssh {
    agent    = true
    username = var.ssh_username
  }
}
```

### Virtual Machine Module
```hcl
variable "virtual_machines" {
  description = "Proxmox VM configurations"
  type = map(object({
    node_name    = string
    vm_id        = optional(number)
    name         = string
    description  = optional(string)
    tags         = optional(list(string), [])
    clone = optional(object({
      vm_id    = number
      full     = optional(bool, true)
      retries  = optional(number, 1)
    }))
    cpu = optional(object({
      cores   = optional(number, 2)
      sockets = optional(number, 1)
      type    = optional(string, "x86-64-v2-AES")
    }))
    memory = optional(object({
      dedicated = optional(number, 2048)
      floating  = optional(number)
    }))
    disk = optional(list(object({
      datastore_id = string
      interface    = string
      size         = number
      file_format  = optional(string, "raw")
      iothread     = optional(bool, true)
      ssd          = optional(bool, true)
      discard      = optional(string, "on")
    })), [])
    network_device = optional(list(object({
      bridge     = string
      model      = optional(string, "virtio")
      vlan_id    = optional(number)
      mac_address = optional(string)
      firewall   = optional(bool, false)
    })), [])
    operating_system = optional(object({
      type = string  # l26 (Linux 2.6+), win10, other
    }))
    agent = optional(object({
      enabled = optional(bool, true)
      type    = optional(string, "virtio")
    }))
    initialization = optional(object({
      ip_config = optional(object({
        ipv4 = optional(object({
          address = string
          gateway = optional(string)
        }))
        ipv6 = optional(object({
          address = string
          gateway = optional(string)
        }))
      }))
      user_account = optional(object({
        username = string
        password = optional(string)
        keys     = optional(list(string))
      }))
      dns = optional(object({
        domain  = optional(string)
        servers = optional(list(string))
      }))
    }))
    started         = optional(bool, true)
    on_boot         = optional(bool, true)
    reboot          = optional(bool, false)
    stop_on_destroy = optional(bool, true)
    timeout_create  = optional(number, 600)
    timeout_clone   = optional(number, 600)
    timeout_migrate = optional(number, 600)
  }))
}

resource "proxmox_virtual_environment_vm" "this" {
  for_each = var.virtual_machines

  node_name   = each.value.node_name
  vm_id       = each.value.vm_id
  name        = each.value.name
  description = each.value.description
  tags        = each.value.tags

  dynamic "clone" {
    for_each = each.value.clone != null ? [each.value.clone] : []
    content {
      vm_id   = clone.value.vm_id
      full    = clone.value.full
      retries = clone.value.retries
    }
  }

  dynamic "cpu" {
    for_each = each.value.cpu != null ? [each.value.cpu] : []
    content {
      cores   = cpu.value.cores
      sockets = cpu.value.sockets
      type    = cpu.value.type
    }
  }

  dynamic "memory" {
    for_each = each.value.memory != null ? [each.value.memory] : []
    content {
      dedicated = memory.value.dedicated
      floating  = memory.value.floating
    }
  }

  dynamic "disk" {
    for_each = each.value.disk
    content {
      datastore_id = disk.value.datastore_id
      interface    = disk.value.interface
      size         = disk.value.size
      file_format  = disk.value.file_format
      iothread     = disk.value.iothread
      ssd          = disk.value.ssd
      discard      = disk.value.discard
    }
  }

  dynamic "network_device" {
    for_each = each.value.network_device
    content {
      bridge      = network_device.value.bridge
      model       = network_device.value.model
      vlan_id     = network_device.value.vlan_id
      mac_address = network_device.value.mac_address
      firewall    = network_device.value.firewall
    }
  }

  dynamic "operating_system" {
    for_each = each.value.operating_system != null ? [each.value.operating_system] : []
    content {
      type = operating_system.value.type
    }
  }

  dynamic "agent" {
    for_each = each.value.agent != null ? [each.value.agent] : []
    content {
      enabled = agent.value.enabled
      type    = agent.value.type
    }
  }

  dynamic "initialization" {
    for_each = each.value.initialization != null ? [each.value.initialization] : []
    content {
      dynamic "ip_config" {
        for_each = initialization.value.ip_config != null ? [initialization.value.ip_config] : []
        content {
          dynamic "ipv4" {
            for_each = ip_config.value.ipv4 != null ? [ip_config.value.ipv4] : []
            content {
              address = ipv4.value.address
              gateway = ipv4.value.gateway
            }
          }
          dynamic "ipv6" {
            for_each = ip_config.value.ipv6 != null ? [ip_config.value.ipv6] : []
            content {
              address = ipv6.value.address
              gateway = ipv6.value.gateway
            }
          }
        }
      }
      dynamic "user_account" {
        for_each = initialization.value.user_account != null ? [initialization.value.user_account] : []
        content {
          username = user_account.value.username
          password = user_account.value.password
          keys     = user_account.value.keys
        }
      }
      dynamic "dns" {
        for_each = initialization.value.dns != null ? [initialization.value.dns] : []
        content {
          domain  = dns.value.domain
          servers = dns.value.servers
        }
      }
    }
  }

  started         = each.value.started
  on_boot         = each.value.on_boot
  reboot          = each.value.reboot
  stop_on_destroy = each.value.stop_on_destroy

  timeout_create  = each.value.timeout_create
  timeout_clone   = each.value.timeout_clone
  timeout_migrate = each.value.timeout_migrate
}
```

### LXC Container Module
```hcl
resource "proxmox_virtual_environment_container" "this" {
  for_each = var.containers

  node_name   = each.value.node_name
  vm_id       = each.value.vm_id
  description = each.value.description
  tags        = each.value.tags

  initialization {
    hostname = each.key

    ip_config {
      ipv4 {
        address = each.value.ipv4_address
        gateway = each.value.ipv4_gateway
      }
    }

    user_account {
      keys     = each.value.ssh_keys
      password = each.value.root_password
    }

    dns {
      domain  = each.value.dns_domain
      servers = each.value.dns_servers
    }
  }

  operating_system {
    template_file_id = each.value.template_file_id
    type             = each.value.os_type  # alpine, archlinux, centos, debian, fedora, gentoo, nixos, opensuse, ubuntu, unmanaged
  }

  cpu {
    cores = each.value.cores
  }

  memory {
    dedicated = each.value.memory
    swap      = each.value.swap
  }

  disk {
    datastore_id = each.value.datastore_id
    size         = each.value.disk_size
  }

  network_interface {
    name     = "eth0"
    bridge   = each.value.bridge
    vlan_id  = each.value.vlan_id
    firewall = each.value.firewall
  }

  features {
    nesting = each.value.nesting
    fuse    = each.value.fuse
    mount   = each.value.mount
  }

  unprivileged = each.value.unprivileged
  started      = each.value.started
  start_on_boot = each.value.start_on_boot
}
```

### Storage Module
```hcl
resource "proxmox_virtual_environment_file" "this" {
  for_each = var.files

  node_name    = each.value.node_name
  datastore_id = each.value.datastore_id
  content_type = each.value.content_type  # iso, vztmpl, snippets

  source_file {
    path      = each.value.source_path
    file_name = each.value.file_name
    checksum  = each.value.checksum
  }

  # Or from URL
  # source_raw {
  #   data      = each.value.data
  #   file_name = each.value.file_name
  # }
}

resource "proxmox_virtual_environment_download_file" "this" {
  for_each = var.download_files

  node_name    = each.value.node_name
  datastore_id = each.value.datastore_id
  content_type = each.value.content_type
  url          = each.value.url
  file_name    = each.value.file_name
  checksum     = each.value.checksum
  checksum_algorithm = each.value.checksum_algorithm

  overwrite         = each.value.overwrite
  upload_timeout    = each.value.upload_timeout
  verify            = each.value.verify
}
```

### Cluster Module
```hcl
resource "proxmox_virtual_environment_cluster_options" "this" {
  language       = var.cluster_language
  keyboard       = var.cluster_keyboard
  email_from     = var.cluster_email_from
  max_workers    = var.cluster_max_workers
  migration_type = var.cluster_migration_type  # secure, insecure

  ha {
    shutdown_policy = var.ha_shutdown_policy
  }

  bandwidth_limit {
    default = var.bandwidth_limit_default
    restore = var.bandwidth_limit_restore
    migration = var.bandwidth_limit_migration
  }
}

resource "proxmox_virtual_environment_haresource" "this" {
  for_each = var.ha_resources

  resource_id = each.value.resource_id  # vm:100, ct:101
  state       = each.value.state  # started, stopped, enabled, disabled
  group       = each.value.group
  comment     = each.value.comment

  max_relocate = each.value.max_relocate
  max_restart  = each.value.max_restart
}

resource "proxmox_virtual_environment_hagroup" "this" {
  for_each = var.ha_groups

  group      = each.key
  comment    = each.value.comment
  nodes      = each.value.nodes
  restricted = each.value.restricted
  nofailback = each.value.nofailback
}
```

---

## Telmate Proxmox Provider (Alternative)

### Provider Configuration
```hcl
terraform {
  required_providers {
    proxmox = {
      source  = "Telmate/proxmox"
      version = "~> 3.0"
    }
  }
}

provider "proxmox" {
  pm_api_url      = var.proxmox_url
  pm_user         = var.proxmox_username
  pm_password     = var.proxmox_password
  pm_tls_insecure = var.proxmox_insecure

  pm_parallel     = 2
  pm_timeout      = 600
  pm_debug        = var.debug
}
```

### VM with Telmate Provider
```hcl
resource "proxmox_vm_qemu" "this" {
  for_each = var.virtual_machines

  name        = each.key
  target_node = each.value.node
  vmid        = each.value.vmid
  desc        = each.value.description

  clone      = each.value.template
  full_clone = each.value.full_clone

  os_type   = each.value.os_type
  qemu_os   = each.value.qemu_os
  bios      = each.value.bios
  boot      = each.value.boot
  bootdisk  = each.value.bootdisk

  cores   = each.value.cores
  sockets = each.value.sockets
  cpu     = each.value.cpu_type
  memory  = each.value.memory
  balloon = each.value.balloon

  scsihw = each.value.scsihw

  dynamic "disk" {
    for_each = each.value.disks
    content {
      type     = disk.value.type
      storage  = disk.value.storage
      size     = disk.value.size
      format   = disk.value.format
      iothread = disk.value.iothread
      ssd      = disk.value.ssd
      discard  = disk.value.discard
    }
  }

  dynamic "network" {
    for_each = each.value.networks
    content {
      model    = network.value.model
      bridge   = network.value.bridge
      tag      = network.value.vlan
      firewall = network.value.firewall
    }
  }

  # Cloud-init configuration
  ipconfig0   = each.value.ipconfig0
  nameserver  = each.value.nameserver
  searchdomain = each.value.searchdomain
  ciuser      = each.value.ciuser
  cipassword  = each.value.cipassword
  sshkeys     = each.value.sshkeys

  agent    = each.value.agent
  onboot   = each.value.onboot
  oncreate = each.value.oncreate

  lifecycle {
    ignore_changes = [
      network,
      disk,
    ]
  }
}
```

---

## Best Practices

### vSphere
1. **Use content libraries** - Centralized template management
2. **Configure DRS** - Automated resource balancing
3. **Use distributed switches** - Advanced networking
4. **Enable HA** - High availability clusters
5. **Use storage policies** - SPBM for storage placement
6. **Configure tagging** - Resource categorization
7. **Use vSphere with Tanzu** - Kubernetes integration
8. **Enable vMotion** - Live migration
9. **Configure resource pools** - Resource allocation
10. **Monitor with vRealize** - Operations management

### VMC
1. **Plan SDDC sizing** - Right-size from start
2. **Configure hybrid connectivity** - VPN, Direct Connect
3. **Use linked mode** - Unified management
4. **Enable Site Recovery** - Disaster recovery
5. **Configure NSX** - Software-defined networking
6. **Use HCX** - Workload migration
7. **Enable add-ons** - Extended services
8. **Monitor costs** - Capacity planning
9. **Configure backup** - Data protection
10. **Plan maintenance windows** - Scheduled updates

### Proxmox
1. **Use cloud-init** - Automated provisioning
2. **Enable QEMU guest agent** - Better management
3. **Configure HA** - High availability
4. **Use Ceph storage** - Distributed storage
5. **Enable ZFS** - Data integrity
6. **Use LXC where appropriate** - Container efficiency
7. **Configure backup** - Proxmox Backup Server
8. **Use VLANs** - Network isolation
9. **Monitor with Prometheus** - Metrics collection
10. **Use templates** - Standardized deployments
