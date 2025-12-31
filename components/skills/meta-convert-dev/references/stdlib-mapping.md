# Standard Library Mapping Reference

Finding equivalent standard library functions is one of the most common challenges in code conversion. This reference provides mapping strategies and common equivalents.

## Mapping Strategy

### 1. Direct Equivalents

Some functions have near-identical counterparts:

```python
# Python
len([1, 2, 3])  # 3
```

```rust
// Rust
[1, 2, 3].len()  // 3
```

### 2. Method vs Function

Languages differ in whether stdlib is methods or functions:

```python
# Python: often functions
sorted([3, 1, 2])  # [1, 2, 3]
len("hello")       # 5
```

```rust
// Rust: often methods
let mut v = vec![3, 1, 2];
v.sort();  // in-place
"hello".len()  // 5
```

### 3. Different Module Location

Same concept, different location:

| Concept | Python | Rust | Go | Elixir |
|---------|--------|------|------|--------|
| Random | `random.randint()` | `rand::random()` | `rand.Intn()` | `:rand.uniform()` |
| JSON | `json.dumps()` | `serde_json::to_string()` | `json.Marshal()` | `Jason.encode!()` |
| Regex | `re.match()` | `regex::Regex::new()` | `regexp.MatchString()` | `Regex.match?()` |

### 4. Semantic Differences

Same name, different behavior:

```python
# Python: filter returns iterator
filter(lambda x: x > 0, [-1, 2, -3, 4])
```

```rust
// Rust: filter is lazy iterator adapter
[-1, 2, -3, 4].iter().filter(|&&x| x > 0)
// Must collect() to materialize
```

## Collections Operations

### List/Array/Vector

| Operation | Python | Rust | Go | Elixir | F# |
|-----------|--------|------|------|--------|-----|
| Create | `[1, 2, 3]` | `vec![1, 2, 3]` | `[]int{1, 2, 3}` | `[1, 2, 3]` | `[1; 2; 3]` |
| Length | `len(xs)` | `xs.len()` | `len(xs)` | `length(xs)` | `List.length xs` |
| Append | `xs.append(x)` | `xs.push(x)` | `xs = append(xs, x)` | `xs ++ [x]` | `xs @ [x]` |
| Get index | `xs[i]` | `xs[i]` or `xs.get(i)` | `xs[i]` | `Enum.at(xs, i)` | `xs.[i]` |
| Slice | `xs[1:3]` | `&xs[1..3]` | `xs[1:3]` | `Enum.slice(xs, 1, 2)` | `xs.[1..2]` |
| Map | `list(map(f, xs))` | `xs.iter().map(f).collect()` | (loop) | `Enum.map(xs, f)` | `List.map f xs` |
| Filter | `list(filter(p, xs))` | `xs.iter().filter(p).collect()` | (loop) | `Enum.filter(xs, p)` | `List.filter p xs` |
| Reduce | `reduce(f, xs, init)` | `xs.iter().fold(init, f)` | (loop) | `Enum.reduce(xs, init, f)` | `List.fold f init xs` |
| Find | `next((x for x in xs if p(x)), None)` | `xs.iter().find(\|x\| p(x))` | (loop) | `Enum.find(xs, p)` | `List.tryFind p xs` |
| Sort | `sorted(xs)` | `xs.sort(); xs` | `sort.Ints(xs)` | `Enum.sort(xs)` | `List.sort xs` |
| Reverse | `xs[::-1]` | `xs.reverse(); xs` | (loop or slices) | `Enum.reverse(xs)` | `List.rev xs` |
| Contains | `x in xs` | `xs.contains(&x)` | (loop) | `x in xs` | `List.contains x xs` |
| All/Any | `all(p(x) for x in xs)` | `xs.iter().all(p)` | (loop) | `Enum.all?(xs, p)` | `List.forall p xs` |

### Dictionary/HashMap/Map

| Operation | Python | Rust | Go | Elixir | F# |
|-----------|--------|------|------|--------|-----|
| Create | `{"a": 1}` | `HashMap::from([("a", 1)])` | `map[string]int{"a": 1}` | `%{"a" => 1}` | `Map.ofList [("a", 1)]` |
| Get | `d["key"]` | `d.get(&key)` | `d[key]` | `Map.get(m, key)` | `Map.find key m` |
| Get w/default | `d.get("key", default)` | `d.get(&key).unwrap_or(&default)` | `d[key]` (zero val) | `Map.get(m, key, default)` | `Map.tryFind key m` |
| Set | `d["key"] = val` | `d.insert(key, val)` | `d[key] = val` | `Map.put(m, key, val)` | `Map.add key val m` |
| Delete | `del d["key"]` | `d.remove(&key)` | `delete(d, key)` | `Map.delete(m, key)` | `Map.remove key m` |
| Keys | `d.keys()` | `d.keys()` | (loop) | `Map.keys(m)` | `Map.keys m` |
| Values | `d.values()` | `d.values()` | (loop) | `Map.values(m)` | `Map.values m` |
| Iterate | `for k, v in d.items()` | `for (k, v) in &d` | `for k, v := range d` | `for {k, v} <- m` | `Map.iter (fun k v -> ...) m` |
| Merge | `{**d1, **d2}` | `d1.extend(d2)` | (loop) | `Map.merge(m1, m2)` | custom |

### Set

| Operation | Python | Rust | Go | Elixir | F# |
|-----------|--------|------|------|--------|-----|
| Create | `{1, 2, 3}` | `HashSet::from([1, 2, 3])` | custom | `MapSet.new([1, 2, 3])` | `Set.ofList [1; 2; 3]` |
| Add | `s.add(x)` | `s.insert(x)` | `s[x] = struct{}{}` | `MapSet.put(s, x)` | `Set.add x s` |
| Remove | `s.remove(x)` | `s.remove(&x)` | `delete(s, x)` | `MapSet.delete(s, x)` | `Set.remove x s` |
| Contains | `x in s` | `s.contains(&x)` | `_, ok := s[x]` | `MapSet.member?(s, x)` | `Set.contains x s` |
| Union | `s1 \| s2` | `s1.union(&s2)` | custom | `MapSet.union(s1, s2)` | `Set.union s1 s2` |
| Intersection | `s1 & s2` | `s1.intersection(&s2)` | custom | `MapSet.intersection(s1, s2)` | `Set.intersect s1 s2` |
| Difference | `s1 - s2` | `s1.difference(&s2)` | custom | `MapSet.difference(s1, s2)` | `Set.difference s1 s2` |

## String Operations

| Operation | Python | Rust | Go | Elixir |
|-----------|--------|------|------|--------|
| Length | `len(s)` | `s.len()` (bytes) or `s.chars().count()` | `len(s)` (bytes) or `utf8.RuneCountInString(s)` | `String.length(s)` |
| Concat | `s1 + s2` | `format!("{}{}", s1, s2)` | `s1 + s2` | `s1 <> s2` |
| Split | `s.split(",")` | `s.split(",")` | `strings.Split(s, ",")` | `String.split(s, ",")` |
| Join | `",".join(xs)` | `xs.join(",")` | `strings.Join(xs, ",")` | `Enum.join(xs, ",")` |
| Replace | `s.replace("a", "b")` | `s.replace("a", "b")` | `strings.Replace(s, "a", "b", -1)` | `String.replace(s, "a", "b")` |
| Trim | `s.strip()` | `s.trim()` | `strings.TrimSpace(s)` | `String.trim(s)` |
| Upper | `s.upper()` | `s.to_uppercase()` | `strings.ToUpper(s)` | `String.upcase(s)` |
| Lower | `s.lower()` | `s.to_lowercase()` | `strings.ToLower(s)` | `String.downcase(s)` |
| Starts with | `s.startswith("x")` | `s.starts_with("x")` | `strings.HasPrefix(s, "x")` | `String.starts_with?(s, "x")` |
| Ends with | `s.endswith("x")` | `s.ends_with("x")` | `strings.HasSuffix(s, "x")` | `String.ends_with?(s, "x")` |
| Contains | `"x" in s` | `s.contains("x")` | `strings.Contains(s, "x")` | `String.contains?(s, "x")` |
| Format | `f"value: {x}"` | `format!("value: {}", x)` | `fmt.Sprintf("value: %v", x)` | `"value: #{x}"` |

## File I/O

| Operation | Python | Rust | Go | Elixir |
|-----------|--------|------|------|--------|
| Read all | `open(path).read()` | `fs::read_to_string(path)?` | `os.ReadFile(path)` | `File.read!(path)` |
| Read lines | `open(path).readlines()` | `BufReader::new(f).lines()` | `bufio.Scanner` | `File.stream!(path)` |
| Write all | `open(path, 'w').write(data)` | `fs::write(path, data)?` | `os.WriteFile(path, data, 0644)` | `File.write!(path, data)` |
| Append | `open(path, 'a').write(data)` | `OpenOptions::new().append(true)...` | `os.OpenFile(..., os.O_APPEND, ...)` | `File.write!(path, data, [:append])` |
| Check exists | `os.path.exists(path)` | `Path::new(path).exists()` | `os.Stat(path) == nil` | `File.exists?(path)` |
| Delete | `os.remove(path)` | `fs::remove_file(path)?` | `os.Remove(path)` | `File.rm!(path)` |
| List dir | `os.listdir(path)` | `fs::read_dir(path)?` | `os.ReadDir(path)` | `File.ls!(path)` |
| Create dir | `os.makedirs(path)` | `fs::create_dir_all(path)?` | `os.MkdirAll(path, 0755)` | `File.mkdir_p!(path)` |

## Date/Time

| Operation | Python | Rust | Go | Elixir |
|-----------|--------|------|------|--------|
| Now (local) | `datetime.now()` | `chrono::Local::now()` | `time.Now()` | `DateTime.utc_now()` |
| Now (UTC) | `datetime.utcnow()` | `chrono::Utc::now()` | `time.Now().UTC()` | `DateTime.utc_now()` |
| Parse | `datetime.strptime(s, fmt)` | `NaiveDateTime::parse_from_str(s, fmt)` | `time.Parse(layout, s)` | `DateTime.from_iso8601(s)` |
| Format | `dt.strftime(fmt)` | `dt.format(fmt).to_string()` | `t.Format(layout)` | `Calendar.strftime(dt, fmt)` |
| Add duration | `dt + timedelta(days=1)` | `dt + Duration::days(1)` | `t.Add(24 * time.Hour)` | `DateTime.add(dt, 1, :day)` |
| Difference | `dt2 - dt1` | `dt2 - dt1` | `t2.Sub(t1)` | `DateTime.diff(dt2, dt1)` |

## Error Handling

| Pattern | Python | Rust | Go | Elixir |
|---------|--------|------|------|--------|
| Try/Catch | `try: ... except:` | N/A (use Result) | N/A (use error return) | `try do ... rescue` |
| Return error | `raise Exception("msg")` | `Err(Error::new("msg"))` | `return nil, errors.New("msg")` | `{:error, "msg"}` |
| Unwrap or default | (catch exception) | `result.unwrap_or(default)` | (if err != nil) | `{:ok, val} = ...` |
| Propagate | `raise` | `?` operator | `if err != nil { return err }` | `with {:ok, val} <- ...` |
| Context | `raise NewError("msg") from e` | `.context("msg")?` (anyhow) | `fmt.Errorf("msg: %w", err)` | (wrap in tuple) |

## JSON

| Operation | Python | Rust | Go | Elixir |
|-----------|--------|------|------|--------|
| Encode | `json.dumps(obj)` | `serde_json::to_string(&obj)?` | `json.Marshal(obj)` | `Jason.encode!(obj)` |
| Decode | `json.loads(s)` | `serde_json::from_str(&s)?` | `json.Unmarshal([]byte(s), &obj)` | `Jason.decode!(s)` |
| Pretty print | `json.dumps(obj, indent=2)` | `serde_json::to_string_pretty(&obj)?` | `json.MarshalIndent(obj, "", "  ")` | `Jason.encode!(obj, pretty: true)` |

## HTTP Client

| Operation | Python | Rust | Go | Elixir |
|-----------|--------|------|------|--------|
| GET | `requests.get(url)` | `reqwest::get(url).await?` | `http.Get(url)` | `HTTPoison.get!(url)` |
| POST | `requests.post(url, json=data)` | `client.post(url).json(&data).send()?` | `http.Post(url, "application/json", body)` | `HTTPoison.post!(url, body)` |
| Headers | `requests.get(url, headers={...})` | `.header("X-Header", "value")` | `req.Header.Set(...)` | `HTTPoison.get!(url, headers)` |
| Response body | `r.text` or `r.json()` | `r.text().await?` | `ioutil.ReadAll(r.Body)` | `r.body` |

## Regular Expressions

| Operation | Python | Rust | Go | Elixir |
|-----------|--------|------|------|--------|
| Compile | `re.compile(r"pattern")` | `Regex::new(r"pattern")?` | `regexp.MustCompile("pattern")` | `~r/pattern/` |
| Match | `re.match(pattern, s)` | `regex.is_match(&s)` | `re.MatchString(s)` | `Regex.match?(regex, s)` |
| Find all | `re.findall(pattern, s)` | `regex.find_iter(&s)` | `re.FindAllString(s, -1)` | `Regex.scan(regex, s)` |
| Replace | `re.sub(pattern, repl, s)` | `regex.replace_all(&s, repl)` | `re.ReplaceAllString(s, repl)` | `Regex.replace(regex, s, repl)` |
| Capture groups | `m.group(1)` | `caps.get(1)` | `matches[1]` | `Regex.named_captures(regex, s)` |

## Concurrency

| Operation | Python | Rust | Go | Elixir |
|-----------|--------|------|------|--------|
| Spawn task | `asyncio.create_task(coro)` | `tokio::spawn(future)` | `go func(){}()` | `Task.async(fn)` |
| Await | `await task` | `task.await` | (channels or WaitGroup) | `Task.await(task)` |
| Parallel map | `asyncio.gather(*tasks)` | `futures::future::join_all(futures)` | WaitGroup + goroutines | `Task.async_stream(enum, fn)` |
| Channel send | `queue.put(item)` | `tx.send(item)?` | `ch <- item` | `send(pid, item)` |
| Channel receive | `queue.get()` | `rx.recv()?` | `<-ch` | `receive do ... end` |
| Mutex | `threading.Lock()` | `Mutex::new(data)` | `sync.Mutex{}` | N/A (processes isolated) |

## Finding Equivalents: Strategy

1. **Check stdlib docs** - Most languages have comprehensive stdlib documentation
2. **Search "X in language Y"** - e.g., "map filter in Go"
3. **Check common crates/packages** - Many common operations are in popular third-party libraries
4. **Consider idiom differences** - What's a stdlib function in one language may be a language feature in another

### Common Third-Party Libraries

| Domain | Python | Rust | Go | Elixir |
|--------|--------|------|------|--------|
| HTTP | `requests` | `reqwest` | `net/http` (stdlib) | `HTTPoison` |
| JSON | `json` (stdlib) | `serde_json` | `encoding/json` (stdlib) | `Jason` |
| Async | `asyncio` (stdlib) | `tokio` | (goroutines, stdlib) | (built-in) |
| Testing | `pytest` | (built-in) | `testing` (stdlib) | `ExUnit` (stdlib) |
| Logging | `logging` (stdlib) | `log`, `tracing` | `log` (stdlib) | `Logger` (stdlib) |
| CLI | `argparse` (stdlib) | `clap` | `flag` (stdlib) | `OptionParser` (stdlib) |
| Dates | `datetime` (stdlib) | `chrono` | `time` (stdlib) | `DateTime` (stdlib) |
| Regex | `re` (stdlib) | `regex` | `regexp` (stdlib) | `Regex` (stdlib) |

---

## Cross-References

- [Platform Ecosystem](platform-ecosystem.md) - Platform-specific stdlib differences
- [Numeric Edge Cases](numeric-edge-cases.md) - Math function mapping
- [Build System Mapping](build-system-mapping.md) - Package management for third-party deps
