/**
 * Test fixtures for TypeScript imports and exports.
 */

// Default import simulation (for testing)
// import React from "react";
// import express from "express";

// Named imports simulation
// import { useState, useEffect, useCallback } from "react";
// import { Request, Response, NextFunction } from "express";

// Type-only imports simulation
// import type { FC, ReactNode, ComponentProps } from "react";
// import type { RequestHandler, ErrorRequestHandler } from "express";

// Namespace import simulation
// import * as lodash from "lodash";
// import * as path from "path";

// Mixed imports simulation
// import React, { useState, useEffect } from "react";
// import express, { Router, Request, Response } from "express";

export * as utils from './types/generics'
export type { Config } from './types/interfaces'
// Re-exports
export { User } from './types/interfaces'
export * from './types/type_aliases'

// Named exports
export const VERSION = '1.0.0'
export const API_URL = 'https://api.example.com'

export function helper(): void {
  console.log('Helper function')
}

export class Service {
  call(): void {}
}

export interface PublicInterface {
  id: number
  name: string
}

export type PublicType = string | number

export enum Status {
  Active = 'active',
  Inactive = 'inactive',
}

// Default export with named exports
export default class MainService {
  private config: Record<string, unknown>

  constructor(config: Record<string, unknown> = {}) {
    this.config = config
  }

  getConfig(): Record<string, unknown> {
    return this.config
  }
}

// Export list
const privateHelper = () => {}
const privateValue = 42

export { privateHelper as publicHelper, privateValue as value }

// Type exports
type InternalType = { internal: boolean }
interface InternalInterface {
  internal: boolean
}

export type { InternalType, InternalInterface }

// Export assignment (CommonJS style) - commented as it's not ES module compatible
// export = MainService;

// Dynamic imports (for reference)
async function loadModule() {
  const module = await import('./types/interfaces')
  return module
}

// Conditional exports
const isDevelopment = process.env.NODE_ENV === 'development'

export const debug = isDevelopment
  ? (message: string) => console.log(`[DEBUG] ${message}`)
  : () => {}

// Barrel file pattern (index.ts would typically contain these)
// export * from "./user";
// export * from "./product";
// export * from "./order";
// export { default as UserService } from "./user.service";
// export { default as ProductService } from "./product.service";
