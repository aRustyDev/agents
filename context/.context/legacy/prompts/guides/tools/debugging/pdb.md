---
name: Python Debugger (pdb) Guide
module_type: guide
scope: temporary
priority: low
triggers: ["pdb", "python debugger", "python debugging", "breakpoint", "debug python", "ipdb"]
dependencies: []
conflicts: []
version: 1.0.0
---

# Python Debugger (pdb) Guide

## Purpose
Master the Python debugger (pdb) for interactive debugging, including breakpoints, stack navigation, variable inspection, and advanced debugging techniques.

## Basic Usage

### Setting Breakpoints

#### Modern Python (3.7+)
```python
def calculate_price(items, tax_rate):
    subtotal = sum(item['price'] for item in items)
    
    breakpoint()  # Drops into debugger here
    
    tax = subtotal * tax_rate
    total = subtotal + tax
    return total
```

#### Classic Method
```python
import pdb

def calculate_price(items, tax_rate):
    subtotal = sum(item['price'] for item in items)
    
    pdb.set_trace()  # Drops into debugger here
    
    tax = subtotal * tax_rate
    total = subtotal + tax
    return total
```

#### Conditional Breakpoints
```python
def process_users(users):
    for i, user in enumerate(users):
        # Only break for specific condition
        if user['age'] < 0:
            breakpoint()
        
        # Or with pdb
        import pdb; pdb.set_trace() if user['role'] == 'admin' else None
        
        process_user(user)
```

### Running Scripts with pdb
```bash
# Run entire script under debugger
python -m pdb script.py

# Start in post-mortem mode on error
python -m pdb -c continue script.py

# Run specific function
python -m pdb -c "import mymodule; mymodule.function()"
```

## Essential Commands

### Navigation Commands
```python
# (Pdb) command reference
l(ist) [first [,last]]    # List source code
w(here)                   # Show current stack trace
u(p) [count]              # Move up in stack frame
d(own) [count]            # Move down in stack frame
b(reak) [[filename:]lineno | function]  # Set breakpoint
cl(ear) [filename:lineno | bpnumber]    # Clear breakpoint
```

### Execution Control
```python
c(ont(inue))              # Continue execution
n(ext)                    # Execute current line
s(tep)                    # Step into functions
r(eturn)                  # Continue until return
j(ump) lineno            # Jump to line number
q(uit)                    # Quit debugger
restart                   # Restart program
```

### Inspection Commands
```python
p expression              # Print expression
pp expression             # Pretty-print expression
a(rgs)                    # Print function arguments
l(ist) [first [,last]]    # List source code
source expression         # Try to get source code for object
whatis expression         # Print type of expression
display [expression]      # Display expression if changed
undisplay [expression]    # Stop displaying expression
```

## Advanced Debugging

### Interactive Exploration
```python
# In pdb prompt
(Pdb) # Explore objects
(Pdb) dir(obj)                    # List attributes
(Pdb) vars(obj)                   # Show object's __dict__
(Pdb) help(obj.method)            # Get help on method
(Pdb) obj.__class__.__mro__       # Show inheritance

# Execute arbitrary Python
(Pdb) [x*2 for x in range(5)]
[0, 2, 4, 6, 8]

# Import modules
(Pdb) import json
(Pdb) json.dumps({"test": "data"})
'{"test": "data"}'

# Modify variables
(Pdb) x = 42
(Pdb) my_list.append('new item')
```

### Breakpoint Management
```python
# Set multiple breakpoints
(Pdb) b 45                      # Break at line 45
(Pdb) b myfunction              # Break at function
(Pdb) b module.py:23            # Break in different file
(Pdb) b 89, condition           # Conditional breakpoint
(Pdb) b 89, x > 10             # Break when x > 10

# List breakpoints
(Pdb) b
Num Type         Disp Enb   Where
1   breakpoint   keep yes   at script.py:45
2   breakpoint   keep yes   at script.py:89
        stop only if x > 10

# Enable/disable breakpoints
(Pdb) disable 1                 # Disable breakpoint 1
(Pdb) enable 1                  # Re-enable breakpoint 1
(Pdb) clear                     # Clear all breakpoints
(Pdb) clear 1                   # Clear specific breakpoint
```

### Commands and Aliases
```python
# Define custom commands
(Pdb) alias pi for k in %1.__dict__: print(f"{k}: {%1.__dict__[k]}")
(Pdb) pi obj  # Print object attributes

# Common aliases
(Pdb) alias ll list 1, 20       # List more lines
(Pdb) alias ni next;;list       # Next and list
(Pdb) alias si step;;list       # Step and list

# Save aliases permanently
# Add to ~/.pdbrc:
alias ll list 1, 30
alias pi for k in %1.__dict__: print(f"{k}: {%1.__dict__[k]}")
```

## Enhanced Debuggers

### Using ipdb (IPython Debugger)
```python
# Install: pip install ipdb

import ipdb

def complex_function(data):
    result = process_data(data)
    ipdb.set_trace()  # Better interface than pdb
    return transform_result(result)

# Features:
# - Syntax highlighting
# - Tab completion
# - Better introspection
# - IPython magic commands
```

### Using pdb++ (pdb Enhanced)
```python
# Install: pip install pdbpp

# Automatically enhances regular pdb
import pdb; pdb.set_trace()

# Features:
# - Syntax highlighting
# - Sticky mode (shows code context)
# - Smart command parsing
# - Better tab completion
```

## Debugging Patterns

### Post-Mortem Debugging
```python
import pdb
import traceback

def main():
    try:
        risky_operation()
    except Exception:
        # Enter debugger at exception point
        traceback.print_exc()
        pdb.post_mortem()

# Or globally
import sys

def excepthook(type, value, tb):
    traceback.print_exception(type, value, tb)
    pdb.post_mortem(tb)

sys.excepthook = excepthook
```

### Remote Debugging
```python
# For debugging running processes
import pdb
import socket
import sys

class RemotePdb(pdb.Pdb):
    def __init__(self, host='127.0.0.1', port=4444):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
        self.sock.bind((host, port))
        self.sock.listen(1)
        (clientsocket, address) = self.sock.accept()
        handle = clientsocket.makefile('rw')
        pdb.Pdb.__init__(self, stdin=handle, stdout=handle)
        sys.stdout = sys.stdin = handle

def set_trace():
    RemotePdb().set_trace()

# In your code
set_trace()  # Connect with: telnet localhost 4444
```

### Debugging Decorators
```python
import functools
import pdb

def debug_on_error(func):
    """Decorator that drops into debugger on exception"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            pdb.post_mortem()
    return wrapper

@debug_on_error
def problematic_function(x):
    return 1 / x  # Drops into debugger when x=0

def debug_calls(func):
    """Decorator that breaks before function calls"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        pdb.set_trace()
        return func(*args, **kwargs)
    return wrapper
```

## Debugging Specific Scenarios

### Debugging Loops
```python
def process_items(items):
    for i, item in enumerate(items):
        # Break on specific iteration
        if i == 42:
            breakpoint()
        
        # Or break on condition
        if item.value > 1000:
            breakpoint()
        
        result = process(item)
```

### Debugging Recursion
```python
import sys

def recursive_function(n, depth=0):
    # Track recursion depth
    if depth > sys.getrecursionlimit() - 100:
        breakpoint()  # Getting close to limit
    
    if n <= 0:
        return 1
    
    # Break at specific depth
    if depth == 5:
        breakpoint()
    
    return n * recursive_function(n - 1, depth + 1)
```

### Debugging Async Code
```python
import asyncio
import pdb

async def async_function():
    await asyncio.sleep(1)
    
    # Set trace in async function
    pdb.set_trace()
    
    result = await fetch_data()
    return result

# For better async debugging, use aiopdb
# pip install aiopdb
import aiopdb

async def better_async_function():
    await asyncio.sleep(1)
    
    # Better async debugging
    await aiopdb.set_trace()
    
    result = await fetch_data()
    return result
```

## Configuration

### .pdbrc File
```python
# ~/.pdbrc - Runs on pdb start

# Aliases
alias ll list 1, 30
alias pi for k in %1.__dict__: print(f"{k}: {%1.__dict__[k]}")
alias ps import pprint; pprint.pprint(%1)

# Pretty printing
import pprint
alias pp pprint.pprint(%1)

# Show instance variables
alias iv pp %1.__dict__

# Next and list
alias nl n;;l

# Step and list  
alias sl s;;l

# Print member functions
alias mf pp [m for m in dir(%1) if callable(getattr(%1, m)) and not m.startswith('_')]

# Enable tab completion
import rlcompleter
import readline
readline.parse_and_bind("tab: complete")
```

## Tips and Tricks

### Efficient Debugging
```python
# Skip over functions you don't want to debug
(Pdb) n  # Use next instead of step for library functions

# Return early from function
(Pdb) r  # Return immediately

# Jump over problematic code
(Pdb) j 50  # Jump to line 50, skipping current

# Re-run with different arguments
(Pdb) run arg1 arg2

# Reload module after changes
(Pdb) import importlib
(Pdb) importlib.reload(mymodule)
```

### Debugging Production Issues
```python
# Conditional debugging based on environment
import os

if os.getenv('DEBUG'):
    breakpoint()

# Time-based debugging
import time
start = time.time()
# ... code ...
if time.time() - start > 5:  # Taking too long
    breakpoint()

# Memory debugging
import psutil
process = psutil.Process()
if process.memory_info().rss > 1e9:  # > 1GB
    breakpoint()
```

### Integration with IDEs
```python
# VS Code
# Add to launch.json:
{
    "name": "Python: Debug Console",
    "type": "python",
    "request": "launch",
    "program": "${file}",
    "console": "integratedTerminal",
    "justMyCode": false
}

# PyCharm
# Use built-in debugger or configure for pdb:
# Run > Edit Configurations > Python Debug Server

# Vim
# Use :Termdebug or vim-pdb plugin
```

## Common Debugging Patterns

### Finding Where Variable Changes
```python
# Watch variable changes
class WatchedVar:
    def __init__(self, initial):
        self._value = initial
    
    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, new_value):
        if new_value != self._value:
            breakpoint()  # Break when value changes
        self._value = new_value

# Use it
watched = WatchedVar(10)
watched.value = 20  # Breaks here
```

### Debugging Import Issues
```python
# Debug import problems
import sys

# Before problematic import
original_modules = set(sys.modules.keys())
breakpoint()

import problematic_module

# See what was imported
new_modules = set(sys.modules.keys()) - original_modules
print(f"Imported: {new_modules}")
```

## Best Practices

### DO
- ✅ Remove breakpoints before committing
- ✅ Use conditional breakpoints for efficiency
- ✅ Learn keyboard shortcuts
- ✅ Use post-mortem for production issues
- ✅ Configure .pdbrc for productivity

### DON'T
- ❌ Leave pdb imports in production code
- ❌ Use print debugging when pdb is better
- ❌ Skip over important initialization
- ❌ Ignore pdb++ or ipdb enhancements
- ❌ Debug in production without safety

---
*The Python debugger is a powerful tool for understanding code behavior and fixing issues. Master it to become a more efficient Python developer.*