// JSDoc documentation patterns

/**
 * @fileoverview Utility functions for data processing.
 * @module utils/data
 * @author Development Team
 * @version 1.0.0
 * @license MIT
 */

/**
 * Represents a point in 2D space.
 *
 * @class Point
 * @example
 * const p = new Point(10, 20);
 * console.log(p.distanceFromOrigin()); // ~22.36
 */
class Point {
  /**
   * The X coordinate.
   * @type {number}
   * @readonly
   */
  readonly x: number

  /**
   * The Y coordinate.
   * @type {number}
   * @readonly
   */
  readonly y: number

  /**
   * Creates a new Point.
   * @param {number} x - X coordinate
   * @param {number} y - Y coordinate
   */
  constructor(x: number, y: number) {
    this.x = x
    this.y = y
  }

  /**
   * Calculates distance from the origin (0, 0).
   * @returns {number} Distance from origin
   * @see {@link https://en.wikipedia.org/wiki/Euclidean_distance}
   */
  distanceFromOrigin(): number {
    return Math.sqrt(this.x ** 2 + this.y ** 2)
  }

  /**
   * Calculates distance to another point.
   * @param {Point} other - The other point
   * @returns {number} Distance between points
   */
  distanceTo(other: Point): number {
    return Math.sqrt((this.x - other.x) ** 2 + (this.y - other.y) ** 2)
  }

  /**
   * Creates a new point by adding coordinates.
   * @param {Point} other - Point to add
   * @returns {Point} New point with summed coordinates
   */
  add(other: Point): Point {
    return new Point(this.x + other.x, this.y + other.y)
  }
}

/**
 * Result of an operation that may fail.
 *
 * @template T - Success value type
 * @template E - Error type
 * @typedef {Object} Result
 * @property {boolean} success - Whether operation succeeded
 * @property {T} [value] - Success value (if success is true)
 * @property {E} [error] - Error value (if success is false)
 */
type Result<T, E> = { success: true; value: T } | { success: false; error: E }

/**
 * Wraps a function that may throw in a Result type.
 *
 * @template T - Return type of the function
 * @param {() => T} fn - Function to wrap
 * @returns {Result<T, Error>} Success with value or failure with error
 * @example
 * const result = tryCatch(() => JSON.parse('{"valid": true}'));
 * if (result.success) {
 *   console.log(result.value);
 * }
 */
function tryCatch<T>(fn: () => T): Result<T, Error> {
  try {
    return { success: true, value: fn() }
  } catch (e) {
    return { success: false, error: e instanceof Error ? e : new Error(String(e)) }
  }
}

/**
 * Options for the data processor.
 *
 * @interface ProcessorOptions
 * @property {boolean} [validate=true] - Validate input data
 * @property {boolean} [transform=false] - Apply transformations
 * @property {number} [maxItems=1000] - Maximum items to process
 * @property {(item: unknown) => boolean} [filter] - Custom filter function
 */
interface ProcessorOptions {
  validate?: boolean
  transform?: boolean
  maxItems?: number
  filter?: (item: unknown) => boolean
}

/**
 * Processes an array of data items.
 *
 * @param {unknown[]} data - Data to process
 * @param {ProcessorOptions} [options={}] - Processing options
 * @returns {unknown[]} Processed data
 * @throws {TypeError} If data is not an array
 * @throws {RangeError} If data exceeds maxItems
 *
 * @example
 * // Basic usage
 * const result = processData([1, 2, 3]);
 *
 * @example
 * // With options
 * const result = processData(items, {
 *   validate: true,
 *   maxItems: 100,
 *   filter: (x) => x != null
 * });
 */
function processData(data: unknown[], options: ProcessorOptions = {}): unknown[] {
  const { validate = true, maxItems = 1000, filter } = options

  if (!Array.isArray(data)) {
    throw new TypeError('Data must be an array')
  }

  if (data.length > maxItems) {
    throw new RangeError(`Data exceeds maximum of ${maxItems} items`)
  }

  let result = data

  if (validate) {
    result = result.filter((item) => item != null)
  }

  if (filter) {
    result = result.filter(filter)
  }

  return result
}

/**
 * @deprecated Use {@link processData} instead
 * @param {unknown[]} items - Items to process
 * @returns {unknown[]} Processed items
 */
function legacyProcess(items: unknown[]): unknown[] {
  console.warn('legacyProcess is deprecated, use processData instead')
  return processData(items)
}

/**
 * Event types supported by the system.
 * @typedef {"click" | "hover" | "submit"} EventType
 */
type EventType = 'click' | 'hover' | 'submit'

/**
 * Event handler callback.
 * @callback EventHandler
 * @param {EventType} type - Event type
 * @param {unknown} data - Event data
 * @returns {void}
 */
type EventHandler = (type: EventType, data: unknown) => void

/**
 * Registers an event handler.
 * @param {EventType} type - Event type to handle
 * @param {EventHandler} handler - Handler function
 * @fires module:events~eventRegistered
 * @listens module:events~eventTriggered
 */
function registerHandler(type: EventType, handler: EventHandler): void {
  console.log(`Registered handler for ${type}`)
  // Implementation would go here
}

export {
  Point,
  type Result,
  tryCatch,
  type ProcessorOptions,
  processData,
  legacyProcess,
  type EventType,
  type EventHandler,
  registerHandler,
}
