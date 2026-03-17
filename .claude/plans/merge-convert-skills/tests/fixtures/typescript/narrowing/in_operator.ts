// Narrowing with the 'in' operator

// Basic in operator narrowing
interface Car {
  drive(): void
  wheels: number
}

interface Boat {
  sail(): void
  propellers: number
}

type Vehicle = Car | Boat

function useVehicle(vehicle: Vehicle): void {
  if ('drive' in vehicle) {
    vehicle.drive()
    console.log(`Car with ${vehicle.wheels} wheels`)
  } else {
    vehicle.sail()
    console.log(`Boat with ${vehicle.propellers} propellers`)
  }
}

// Narrowing with optional properties
interface WithOptional {
  required: string
  optional?: number
}

function processOptional(obj: WithOptional): number {
  if ('optional' in obj && obj.optional !== undefined) {
    return obj.optional * 2
  }
  return 0
}

// Multiple property checks
interface DatabaseConfig {
  type: 'database'
  host: string
  port: number
}

interface FileConfig {
  type: 'file'
  path: string
}

interface MemoryConfig {
  type: 'memory'
  maxSize: number
}

type StorageConfig = DatabaseConfig | FileConfig | MemoryConfig

function getStorageDescription(config: StorageConfig): string {
  if ('host' in config) {
    return `Database at ${config.host}:${config.port}`
  }
  if ('path' in config) {
    return `File at ${config.path}`
  }
  return `Memory storage (max ${config.maxSize} bytes)`
}

// Narrowing with index signatures
interface StringDict {
  [key: string]: string
}

interface NumberDict {
  [key: string]: number
}

type Dict = StringDict | NumberDict

function processDict(dict: Dict, key: string): string | number | undefined {
  if (key in dict) {
    return dict[key]
  }
  return undefined
}

// Narrowing inherited properties
interface Base {
  id: number
}

interface Extended extends Base {
  extra: string
}

function processBase(obj: Base | Extended): void {
  console.log(`ID: ${obj.id}`)
  if ('extra' in obj) {
    console.log(`Extra: ${obj.extra}`)
  }
}

// Narrowing with Symbol properties
const specialKey = Symbol('special')

interface WithSymbol {
  [specialKey]: string
  regular: number
}

interface WithoutSymbol {
  regular: number
}

type MaybeSymbol = WithSymbol | WithoutSymbol

function checkSymbol(obj: MaybeSymbol): string | null {
  if (specialKey in obj) {
    return obj[specialKey]
  }
  return null
}

// Narrowing in array contexts
interface ItemA {
  kind: 'a'
  valueA: string
}

interface ItemB {
  kind: 'b'
  valueB: number
}

type Item = ItemA | ItemB

function filterByKind(items: Item[], kind: 'a' | 'b'): Item[] {
  return items.filter((item) => {
    if (kind === 'a' && 'valueA' in item) {
      return true
    }
    if (kind === 'b' && 'valueB' in item) {
      return true
    }
    return false
  })
}

export {
  type Car,
  type Boat,
  type Vehicle,
  useVehicle,
  processOptional,
  type DatabaseConfig,
  type FileConfig,
  type MemoryConfig,
  type StorageConfig,
  getStorageDescription,
  processDict,
  processBase,
  specialKey,
  checkSymbol,
  type Item,
  filterByKind,
}
