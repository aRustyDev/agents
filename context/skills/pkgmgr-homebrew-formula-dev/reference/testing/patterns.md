## Test Block Patterns

### Simple help check

```text
test do
  assert_match "tool-name", shell_output("#{bin}/tool --help")
end
```

### Non-zero exit on help

Some tools exit non-zero when showing help. Pass the expected exit code:

```text
test do
  assert_match "tool-name", shell_output("#{bin}/tool --help", 2)
end
```

### Version check

```text
test do
  assert_match version.to_s, shell_output("#{bin}/tool --version")
end
```

### Functional test with file I/O

```text
test do
  (testpath/"input.txt").write("test content")
  output = shell_output("#{bin}/tool #{testpath}/input.txt")
  assert_equal "expected", output.strip
end
```
