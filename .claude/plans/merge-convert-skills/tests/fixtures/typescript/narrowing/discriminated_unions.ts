// Discriminated unions (tagged unions)

// Basic discriminated union
interface Circle {
  kind: 'circle'
  radius: number
}

interface Rectangle {
  kind: 'rectangle'
  width: number
  height: number
}

interface Triangle {
  kind: 'triangle'
  base: number
  height: number
}

type Shape = Circle | Rectangle | Triangle

function getArea(shape: Shape): number {
  switch (shape.kind) {
    case 'circle':
      return Math.PI * shape.radius ** 2
    case 'rectangle':
      return shape.width * shape.height
    case 'triangle':
      return (shape.base * shape.height) / 2
  }
}

// Exhaustiveness checking
function assertNever(x: never): never {
  throw new Error(`Unexpected value: ${x}`)
}

function getAreaExhaustive(shape: Shape): number {
  switch (shape.kind) {
    case 'circle':
      return Math.PI * shape.radius ** 2
    case 'rectangle':
      return shape.width * shape.height
    case 'triangle':
      return (shape.base * shape.height) / 2
    default:
      return assertNever(shape)
  }
}

// Multiple discriminants
interface NetworkLoading {
  state: 'loading'
}

interface NetworkSuccess<T> {
  state: 'success'
  data: T
}

interface NetworkError {
  state: 'error'
  code: number
  message: string
}

type NetworkState<T> = NetworkLoading | NetworkSuccess<T> | NetworkError

function handleNetworkState<T>(state: NetworkState<T>): T | null {
  switch (state.state) {
    case 'loading':
      console.log('Loading...')
      return null
    case 'success':
      return state.data
    case 'error':
      console.error(`Error ${state.code}: ${state.message}`)
      return null
  }
}

// Action pattern (Redux-style)
interface AddTodoAction {
  type: 'ADD_TODO'
  payload: { id: number; text: string }
}

interface RemoveTodoAction {
  type: 'REMOVE_TODO'
  payload: { id: number }
}

interface ToggleTodoAction {
  type: 'TOGGLE_TODO'
  payload: { id: number }
}

type TodoAction = AddTodoAction | RemoveTodoAction | ToggleTodoAction

interface TodoState {
  todos: { id: number; text: string; done: boolean }[]
}

function todoReducer(state: TodoState, action: TodoAction): TodoState {
  switch (action.type) {
    case 'ADD_TODO':
      return {
        todos: [...state.todos, { id: action.payload.id, text: action.payload.text, done: false }],
      }
    case 'REMOVE_TODO':
      return {
        todos: state.todos.filter((t) => t.id !== action.payload.id),
      }
    case 'TOGGLE_TODO':
      return {
        todos: state.todos.map((t) => (t.id === action.payload.id ? { ...t, done: !t.done } : t)),
      }
  }
}

// Literal type discriminant
type EventType = 'click' | 'hover' | 'focus'

interface BaseEvent {
  timestamp: number
}

interface ClickEvent extends BaseEvent {
  type: 'click'
  x: number
  y: number
}

interface HoverEvent extends BaseEvent {
  type: 'hover'
  element: string
}

interface FocusEvent extends BaseEvent {
  type: 'focus'
  element: string
}

type UIEvent = ClickEvent | HoverEvent | FocusEvent

function logEvent(event: UIEvent): void {
  console.log(`Event at ${event.timestamp}:`)
  switch (event.type) {
    case 'click':
      console.log(`Click at (${event.x}, ${event.y})`)
      break
    case 'hover':
      console.log(`Hover on ${event.element}`)
      break
    case 'focus':
      console.log(`Focus on ${event.element}`)
      break
  }
}

export {
  type Circle,
  type Rectangle,
  type Triangle,
  type Shape,
  getArea,
  getAreaExhaustive,
  type NetworkLoading,
  type NetworkSuccess,
  type NetworkError,
  type NetworkState,
  handleNetworkState,
  type TodoAction,
  type TodoState,
  todoReducer,
  type UIEvent,
  logEvent,
}
