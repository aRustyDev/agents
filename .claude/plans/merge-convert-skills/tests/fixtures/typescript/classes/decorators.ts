/**
 * Test fixtures for TypeScript decorators.
 * Note: Requires experimentalDecorators in tsconfig.json
 */

// Simple class decorator
function Component(target: Function) {
  target.prototype.isComponent = true;
}

@Component
class MyComponent {
  render() {
    return "<div>Hello</div>";
  }
}

// Decorator factory
function Injectable(options?: { providedIn?: "root" | "platform" }) {
  return (target: Function) => {
    Reflect.defineMetadata("injectable", true, target);
    if (options?.providedIn) {
      Reflect.defineMetadata("providedIn", options.providedIn, target);
    }
  };
}

@Injectable({ providedIn: "root" })
class UserService {
  getUsers() {
    return [];
  }
}

// Multiple decorators
function Log(target: Function) {
  console.log(`Class ${target.name} was defined`);
}

function Sealed(target: Function) {
  Object.seal(target);
  Object.seal(target.prototype);
}

@Log
@Sealed
class SealedClass {
  name = "sealed";
}

// Method decorator
function Memoize(
  _target: object,
  _propertyKey: string,
  descriptor: PropertyDescriptor
) {
  const originalMethod = descriptor.value;
  const cache = new Map<string, unknown>();

  descriptor.value = function (...args: unknown[]) {
    const key = JSON.stringify(args);
    if (cache.has(key)) {
      return cache.get(key);
    }
    const result = originalMethod.apply(this, args);
    cache.set(key, result);
    return result;
  };

  return descriptor;
}

class Calculator {
  @Memoize
  fibonacci(n: number): number {
    if (n <= 1) return n;
    return this.fibonacci(n - 1) + this.fibonacci(n - 2);
  }
}

// Property decorator
function Required(target: object, propertyKey: string) {
  const requiredProperties: string[] =
    Reflect.getMetadata("required", target) || [];
  requiredProperties.push(propertyKey);
  Reflect.defineMetadata("required", requiredProperties, target);
}

function MinLength(length: number) {
  return (target: object, propertyKey: string) => {
    Reflect.defineMetadata("minLength", length, target, propertyKey);
  };
}

class User {
  @Required
  @MinLength(3)
  name: string = "";

  @Required
  email: string = "";
}

// Parameter decorator
function Inject(token: string) {
  return (
    target: object,
    propertyKey: string | symbol | undefined,
    parameterIndex: number
  ) => {
    const existingInjections: Array<{ index: number; token: string }> =
      Reflect.getMetadata("injections", target, propertyKey ?? "") || [];
    existingInjections.push({ index: parameterIndex, token });
    Reflect.defineMetadata("injections", existingInjections, target, propertyKey ?? "");
  };
}

class Container {
  constructor(
    @Inject("Logger") private logger: object,
    @Inject("Config") private config: object
  ) {}
}

// Accessor decorator
function Configurable(configurable: boolean) {
  return (
    _target: object,
    _propertyKey: string,
    descriptor: PropertyDescriptor
  ) => {
    descriptor.configurable = configurable;
  };
}

class Point3D {
  private _x: number = 0;
  private _y: number = 0;
  private _z: number = 0;

  @Configurable(false)
  get coordinates(): [number, number, number] {
    return [this._x, this._y, this._z];
  }
}

// Decorator composition
function First() {
  return (target: Function) => {
    console.log("First decorator");
  };
}

function Second() {
  return (target: Function) => {
    console.log("Second decorator");
  };
}

@First()
@Second()
class ComposedClass {}

// Class decorator that modifies constructor
function Timestamped<T extends { new (...args: unknown[]): object }>(
  constructor: T
) {
  return class extends constructor {
    createdAt = new Date();
    updatedAt = new Date();
  };
}

@Timestamped
class Article {
  title: string;

  constructor(title: string) {
    this.title = title;
  }
}

// Method decorator with metadata
function Route(path: string, method: "GET" | "POST" | "PUT" | "DELETE") {
  return (
    target: object,
    propertyKey: string,
    _descriptor: PropertyDescriptor
  ) => {
    Reflect.defineMetadata("route:path", path, target, propertyKey);
    Reflect.defineMetadata("route:method", method, target, propertyKey);
  };
}

class ApiController {
  @Route("/users", "GET")
  getUsers() {
    return [];
  }

  @Route("/users/:id", "GET")
  getUser(_id: string) {
    return {};
  }

  @Route("/users", "POST")
  createUser(_data: object) {
    return {};
  }
}

// Exported decorated class
@Injectable()
export class ProductService {
  @Memoize
  getProducts(): object[] {
    return [];
  }
}
