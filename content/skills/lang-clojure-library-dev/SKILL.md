---
name: lang-clojure-library-dev
description: Clojure library development patterns covering functional design idioms, namespace organization, deps.edn and Leiningen configuration, protocols and multimethods, spec for validation, testing with clojure.test, and publishing to Clojars. Use when creating Clojure libraries, designing functional APIs, or configuring Clojure projects for distribution.
created: 2025-12-28T22:00
updated: 2025-12-28T22:00
tags: [lang, clojure, library, dev]
source: https://github.com/arustydev/agents
---

# Clojure Library Development

Clojure-specific patterns for library development. This skill covers functional API design, namespace organization, dependency management, validation with spec, testing strategies, and publishing to Clojars.

## Overview

**This skill covers:**
- Clojure library design idioms and functional patterns
- deps.edn and Leiningen project configuration
- Namespace organization and public API design
- Protocol and multimethod design for extensibility
- Spec for validation, testing, and documentation
- Testing with clojure.test and test.check
- Documentation with Codox
- Publishing to Clojars

**This skill does NOT cover:**
- ClojureScript library development (see `lang-clojurescript-library-dev`)
- Web application development (see `lang-clojure-web-dev`)
- Advanced macro development (see `lang-clojure-macros-dev`)
- Production deployment (see `cicd-clojure-ops`)

---

## Quick Reference

| Task | Command/Pattern |
|------|-----------------|
| New library (deps.edn) | `clj -Tnew lib :name myusername/mylib` |
| New library (Leiningen) | `lein new lib mylib` |
| Run REPL | `clj` or `lein repl` |
| Run tests | `clj -X:test` or `lein test` |
| Generate docs | `lein codox` |
| Install locally | `lein install` |
| Deploy to Clojars | `lein deploy clojars` |
| Check dependencies | `clj -X:deps tree` or `lein deps :tree` |

---

## Project Configuration

### deps.edn Structure

```clojure
;; deps.edn
{:paths ["src" "resources"]

 :deps {org.clojure/clojure {:mvn/version "1.11.1"}}

 :aliases
 {:test {:extra-paths ["test"]
         :extra-deps {org.clojure/test.check {:mvn/version "1.1.1"}
                      lambdaisland/kaocha {:mvn/version "1.87.1366"}}
         :main-opts ["-m" "kaocha.runner"]}

  :build {:deps {io.github.clojure/tools.build {:mvn/version "0.9.6"}}
          :ns-default build}

  :codox {:extra-deps {codox/codox {:mvn/version "0.10.8"}}
          :exec-fn codox.main/generate-docs
          :exec-args {:source-paths ["src"]
                      :output-path "docs"
                      :metadata {:doc/format :markdown}}}

  :jar {:replace-deps {com.github.seancorfield/depstar {:mvn/version "2.1.303"}}
        :exec-fn hf.depstar/jar
        :exec-args {:jar "mylib.jar"}}

  :deploy {:extra-deps {slipset/deps-deploy {:mvn/version "0.2.0"}}
           :exec-fn deps-deploy.deps-deploy/deploy
           :exec-args {:installer :remote
                       :artifact "mylib.jar"
                       :pom-file "pom.xml"}}}}
```

### Leiningen project.clj

```clojure
(defproject com.example/mylib "0.1.0-SNAPSHOT"
  :description "A useful Clojure library"
  :url "https://github.com/username/mylib"
  :license {:name "EPL-2.0"
            :url "https://www.eclipse.org/legal/epl-2.0/"}

  :dependencies [[org.clojure/clojure "1.11.1"]]

  :profiles {:dev {:dependencies [[org.clojure/test.check "1.1.1"]]
                   :plugins [[lein-codox "0.10.8"]
                             [lein-cljfmt "0.9.2"]
                             [lein-kibit "0.1.8"]]}}

  :codox {:output-path "docs"
          :metadata {:doc/format :markdown}
          :source-uri "https://github.com/username/mylib/blob/{version}/{filepath}#L{line}"}

  :deploy-repositories [["clojars" {:url "https://repo.clojars.org"
                                    :username :env/clojars_username
                                    :password :env/clojars_password
                                    :sign-releases false}]]

  :release-tasks [["vcs" "assert-committed"]
                  ["change" "version" "leiningen.release/bump-version" "release"]
                  ["vcs" "commit"]
                  ["vcs" "tag"]
                  ["deploy"]
                  ["change" "version" "leiningen.release/bump-version"]
                  ["vcs" "commit"]
                  ["vcs" "push"]])
```

---

## Namespace Organization

### Standard Library Structure

```
mylib/
├── deps.edn or project.clj
├── README.md
├── LICENSE
├── CHANGELOG.md
├── src/
│   └── mylib/
│       ├── core.clj          # Main public API
│       ├── protocols.clj     # Protocol definitions
│       ├── impl.clj          # Implementation details
│       └── util.clj          # Internal utilities
├── test/
│   └── mylib/
│       ├── core_test.clj
│       └── protocols_test.clj
├── dev/
│   └── user.clj              # Dev-time utilities
└── resources/
    └── config.edn            # Configuration files
```

### Core Namespace Pattern

```clojure
(ns mylib.core
  "Public API for mylib.

  This library provides functionality for X, Y, and Z.

  ## Quick Start

  ```clojure
  (require '[mylib.core :as mylib])

  (mylib/process-data {:foo \"bar\"})
  ```"
  (:require [mylib.protocols :as proto]
            [mylib.impl :as impl])
  (:import [java.time Instant]))

;; Re-export key protocols for convenience
(def ^:redef ProcessorProtocol proto/ProcessorProtocol)

;; Public API functions
(defn process-data
  "Process data according to the given options.

  Options:
  - `:strict?` - Enable strict validation (default: false)
  - `:timeout` - Timeout in milliseconds (default: 5000)

  Returns a map with `:result` and `:metadata` keys.

  Examples:
  ```clojure
  (process-data {:input \"hello\"})
  ;=> {:result \"HELLO\" :metadata {...}}

  (process-data {:input \"world\"} {:strict? true})
  ;=> {:result \"WORLD\" :metadata {...}}
  ```"
  ([data]
   (process-data data {}))
  ([data opts]
   (impl/process-data-impl data opts)))

;; Private helper (not part of public API)
(defn- internal-helper
  [x]
  (str x))
```

### Visibility and Public API

```clojure
;; Public function - part of API
(defn public-fn
  "Documented public function."
  [x]
  (inc x))

;; Private function - internal only
(defn- private-fn
  "Internal implementation detail."
  [x]
  (* x 2))

;; Dynamic var - rebindable
(def ^:dynamic *config*
  "Dynamic configuration var."
  {:default true})

;; Private def - internal constant
(def ^:private internal-constant
  "Not part of public API."
  42)

;; Marked for redef - can be redefined in REPL
(def ^:redef processor
  "Default processor implementation."
  default-processor)
```

---

## Functional API Design

### Data-Oriented Design

```clojure
;; Prefer plain data structures over custom types
(defn create-user
  "Returns a user map."
  [name email]
  {:user/name name
   :user/email email
   :user/created-at (java.time.Instant/now)})

;; Accept and return plain data
(defn update-user
  "Returns updated user map."
  [user updates]
  (merge user updates))

;; Use namespaced keywords for clarity
(defn user-full-name
  [{:user/keys [first-name last-name]}]
  (str first-name " " last-name))
```

### Polymorphism with Protocols

```clojure
;; protocols.clj
(defprotocol Processor
  "Protocol for data processing."
  (process [this data opts]
    "Process data with given options."))

;; Extend protocol for different types
(extend-protocol Processor
  java.lang.String
  (process [s data opts]
    (str s " " data))

  clojure.lang.Keyword
  (process [k data opts]
    (get data k))

  clojure.lang.Fn
  (process [f data opts]
    (f data)))

;; Define record implementing protocol
(defrecord DefaultProcessor [config]
  Processor
  (process [this data opts]
    (let [strict? (:strict? opts false)]
      (if strict?
        (validate-and-process data config)
        (simple-process data config)))))

;; Factory function
(defn make-processor
  "Create a processor with the given config."
  [config]
  (->DefaultProcessor config))
```

### Multimethods for Open Extension

```clojure
;; Define multimethod dispatching on type
(defmulti serialize
  "Serialize data based on format."
  (fn [data format] format))

(defmethod serialize :json
  [data _]
  (json/write-str data))

(defmethod serialize :edn
  [data _]
  (pr-str data))

(defmethod serialize :default
  [data format]
  (throw (ex-info "Unknown format" {:format format})))

;; Usage
(serialize {:foo "bar"} :json)
;=> "{\"foo\":\"bar\"}"

(serialize {:foo "bar"} :edn)
;=> "{:foo \"bar\"}"
```

### Higher-Order Functions

```clojure
(defn transform-collection
  "Transform collection using provided transformation fns.

  Takes a map of transformation functions and applies them
  in sequence: filter -> map -> reduce."
  [{:keys [filter-fn map-fn reduce-fn]
    :or {filter-fn identity
         map-fn identity
         reduce-fn conj}}]
  (fn [coll]
    (cond->> coll
      filter-fn (filter filter-fn)
      map-fn (map map-fn)
      reduce-fn (reduce reduce-fn []))))

;; Usage
(def process-numbers
  (transform-collection
    {:filter-fn even?
     :map-fn #(* % 2)
     :reduce-fn +}))

(process-numbers [1 2 3 4 5 6])
;=> 24
```

---

## Spec for Validation and Documentation

### Basic Specs

```clojure
(ns mylib.specs
  (:require [clojure.spec.alpha :as s]))

;; Spec for user map
(s/def ::name string?)
(s/def ::email (s/and string? #(re-matches #".+@.+\..+" %)))
(s/def ::age (s/and int? pos?))

(s/def ::user
  (s/keys :req [::name ::email]
          :opt [::age]))

;; Spec for function arguments
(s/fdef create-user
  :args (s/cat :name ::name :email ::email)
  :ret ::user)

(defn create-user
  [name email]
  {:mylib.specs/name name
   :mylib.specs/email email})

;; Validate data at runtime
(defn create-user-safe
  [name email]
  (let [user (create-user name email)]
    (if (s/valid? ::user user)
      user
      (throw (ex-info "Invalid user"
                      {:problems (s/explain-data ::user user)})))))
```

### Spec for Complex Data

```clojure
;; Nested specs
(s/def ::street string?)
(s/def ::city string?)
(s/def ::zip string?)
(s/def ::address (s/keys :req [::street ::city ::zip]))

(s/def ::user-with-address
  (s/keys :req [::name ::email]
          :opt [::address]))

;; Spec for collections
(s/def ::user-list (s/coll-of ::user :kind vector?))

;; Spec with custom predicate
(s/def ::positive-balance
  (s/and number? pos?))

;; Spec for polymorphic data
(s/def ::event-type #{:created :updated :deleted})
(s/def ::timestamp inst?)

(defmulti event-spec ::event-type)
(defmethod event-spec :created [_]
  (s/keys :req [::event-type ::timestamp ::user]))
(defmethod event-spec :updated [_]
  (s/keys :req [::event-type ::timestamp ::user ::changes]))
(defmethod event-spec :deleted [_]
  (s/keys :req [::event-type ::timestamp ::user-id]))

(s/def ::event (s/multi-spec event-spec ::event-type))
```

### Generative Testing with Spec

```clojure
(ns mylib.core-test
  (:require [clojure.test :refer :all]
            [clojure.spec.alpha :as s]
            [clojure.spec.gen.alpha :as gen]
            [clojure.spec.test.alpha :as stest]
            [mylib.core :as mylib]
            [mylib.specs :as specs]))

;; Generate sample data
(gen/sample (s/gen ::specs/user) 5)
;=> ({::specs/name "a" ::specs/email "b@c.d"} ...)

;; Property-based testing
(deftest user-creation-properties
  (testing "create-user always returns valid user"
    (let [results (gen/sample
                    (s/gen (s/cat :name ::specs/name
                                  :email ::specs/email))
                    100)]
      (doseq [{:keys [name email]} results]
        (is (s/valid? ::specs/user
                      (mylib/create-user name email)))))))

;; Instrument functions for testing
(stest/instrument `mylib/create-user)

;; Check function spec
(stest/check `mylib/create-user)
```

---

## Testing Patterns

### Unit Tests with clojure.test

```clojure
(ns mylib.core-test
  (:require [clojure.test :refer :all]
            [mylib.core :as mylib]))

(deftest process-data-test
  (testing "basic data processing"
    (is (= {:result "HELLO" :metadata {}}
           (mylib/process-data {:input "hello"}))))

  (testing "strict mode validation"
    (is (thrown? Exception
                 (mylib/process-data {:invalid "data"}
                                     {:strict? true}))))

  (testing "with custom options"
    (let [result (mylib/process-data {:input "world"}
                                     {:uppercase? false})]
      (is (= "world" (:result result))))))

;; Test fixtures
(defn setup-test-data []
  (def test-user {:name "Test" :email "test@example.com"}))

(defn teardown-test-data []
  (def test-user nil))

(use-fixtures :each
  (fn [f]
    (setup-test-data)
    (f)
    (teardown-test-data)))
```

### Property-Based Testing with test.check

```clojure
(ns mylib.properties-test
  (:require [clojure.test :refer :all]
            [clojure.test.check :as tc]
            [clojure.test.check.generators :as gen]
            [clojure.test.check.properties :as prop]
            [clojure.test.check.clojure-test :refer [defspec]]
            [mylib.core :as mylib]))

;; Define property
(def prop-reversible-serialization
  (prop/for-all [data gen/any-printable]
    (= data
       (-> data
           (mylib/serialize :edn)
           (mylib/deserialize :edn)))))

;; Run property test
(defspec serialization-roundtrip-test 100
  prop-reversible-serialization)

;; Custom generator
(def user-gen
  (gen/let [name gen/string-alphanumeric
            email (gen/fmap #(str % "@example.com")
                           gen/string-alphanumeric)]
    {:name name :email email}))

(defspec user-processing-test 50
  (prop/for-all [user user-gen]
    (mylib/valid-user? (mylib/process-user user))))
```

---

## Documentation with Codox

### Docstring Best Practices

```clojure
(defn complex-function
  "One-line summary of what the function does.

  More detailed explanation of the function's purpose,
  behavior, and any important considerations.

  ## Parameters

  - `data` - Input data map with `:id` and `:value` keys
  - `opts` - Optional configuration map
    - `:strict?` - Enable strict validation (default: false)
    - `:timeout` - Timeout in milliseconds (default: 5000)

  ## Returns

  A map with the following keys:
  - `:result` - Processed result
  - `:metadata` - Processing metadata

  ## Examples

  ```clojure
  (complex-function {:id 1 :value \"foo\"})
  ;=> {:result \"FOO\" :metadata {...}}

  (complex-function {:id 2 :value \"bar\"} {:strict? true})
  ;=> {:result \"BAR\" :metadata {...}}
  ```

  ## Throws

  - `ExceptionInfo` - When validation fails in strict mode

  ## See Also

  - [[simple-function]] - Simpler version without options
  - [[validate-data]] - Validation function used internally"
  [data opts]
  ;; implementation
  )
```

### Codox Metadata

```clojure
;; Mark functions as added in specific version
(defn ^{:added "0.2.0"} new-feature
  "Feature added in version 0.2.0."
  []
  ;; implementation
  )

;; Mark deprecated functions
(defn ^{:deprecated "0.3.0"} old-function
  "This function is deprecated. Use [[new-function]] instead."
  []
  ;; implementation
  )

;; Group related functions
(defn ^{:category :processing} process-data
  "Data processing function."
  [data]
  ;; implementation
  )

(defn ^{:category :processing} transform-data
  "Data transformation function."
  [data]
  ;; implementation
  )
```

---

## Publishing to Clojars

### Pre-publish Checklist

- [ ] All tests pass: `lein test` or `clj -X:test`
- [ ] Code is formatted: `lein cljfmt check`
- [ ] No reflection warnings: `lein check`
- [ ] Documentation is up to date
- [ ] CHANGELOG.md updated with version changes
- [ ] Version bumped in project.clj or deps.edn
- [ ] README.md includes installation instructions
- [ ] License file is present
- [ ] pom.xml is generated and correct

### Generate pom.xml (deps.edn)

```clojure
;; build.clj
(ns build
  (:require [clojure.tools.build.api :as b]))

(def lib 'com.example/mylib)
(def version "0.1.0")
(def class-dir "target/classes")
(def jar-file (format "target/%s-%s.jar" (name lib) version))

(defn clean [_]
  (b/delete {:path "target"}))

(defn pom [_]
  (b/write-pom {:class-dir class-dir
                :lib lib
                :version version
                :basis (b/create-basis {:project "deps.edn"})
                :src-dirs ["src"]
                :scm {:url "https://github.com/username/mylib"
                      :connection "scm:git:git://github.com/username/mylib.git"
                      :developerConnection "scm:git:ssh://git@github.com/username/mylib.git"
                      :tag (str "v" version)}}))

(defn jar [_]
  (clean nil)
  (pom nil)
  (b/copy-dir {:src-dirs ["src" "resources"]
               :target-dir class-dir})
  (b/jar {:class-dir class-dir
          :jar-file jar-file}))
```

### Deploy to Clojars (Leiningen)

```bash
# Set credentials (one-time setup)
export CLOJARS_USERNAME=your-username
export CLOJARS_PASSWORD=your-deploy-token

# Deploy
lein deploy clojars
```

### Deploy to Clojars (deps.edn)

```bash
# Build jar
clj -T:build jar

# Deploy
clj -X:deploy
```

### Semantic Versioning

| Change Type | Version Change | Example |
|------------|----------------|---------|
| Breaking API change | Major (X.0.0) | 1.5.3 → 2.0.0 |
| New feature (backward compatible) | Minor (0.X.0) | 1.5.3 → 1.6.0 |
| Bug fix | Patch (0.0.X) | 1.5.3 → 1.5.4 |
| Pre-release | Suffix | 1.0.0-alpha1 |
| Snapshot | SNAPSHOT | 1.0.0-SNAPSHOT |

---

## Common Patterns

### Error Handling

```clojure
;; Using ex-info for rich errors
(defn validate-input
  [input]
  (when-not (map? input)
    (throw (ex-info "Input must be a map"
                    {:type :validation-error
                     :input input})))
  input)

;; Catching and handling errors
(defn safe-process
  [data]
  (try
    {:success true
     :result (process data)}
    (catch Exception e
      {:success false
       :error {:message (.getMessage e)
               :data (ex-data e)}})))

;; Either-style error handling
(defn either-process
  [data]
  (if (valid? data)
    [:ok (process data)]
    [:error {:message "Invalid data" :data data}]))
```

### Resource Management

```clojure
(defn with-resource
  "Ensure resource cleanup."
  [resource-fn f]
  (let [resource (resource-fn)]
    (try
      (f resource)
      (finally
        (.close resource)))))

;; Using with-open for auto-closeable resources
(defn read-file
  [path]
  (with-open [rdr (clojure.java.io/reader path)]
    (doall (line-seq rdr))))
```

---

## Troubleshooting

### Circular Dependencies

**Problem:** Namespace circular dependency

```clojure
;; a.clj requires b.clj, b.clj requires a.clj
;; Error: Cyclic load dependency
```

**Solution:** Extract shared code to separate namespace

```clojure
;; shared.clj - common dependencies
(ns mylib.shared)

(defn shared-fn [])

;; a.clj
(ns mylib.a
  (:require [mylib.shared :as shared]))

;; b.clj
(ns mylib.b
  (:require [mylib.shared :as shared]))
```

### Reflection Warnings

**Problem:** Performance issues from reflection

```clojure
;; Warning: reflection on .method call
(defn slow-fn [^Object obj]
  (.someMethod obj))
```

**Solution:** Add type hints

```clojure
(defn fast-fn [^SomeClass obj]
  (.someMethod obj))

;; For return types
(defn ^String to-string [x]
  (str x))
```

### REPL State Issues

**Problem:** Stale definitions in REPL

**Solution:** Use `(require ... :reload)` or restart REPL

```clojure
;; Reload namespace
(require 'mylib.core :reload)

;; Reload namespace and dependencies
(require 'mylib.core :reload-all)

;; In dev, use tools.namespace
(require '[clojure.tools.namespace.repl :refer [refresh]])
(refresh)
```

---

## References

- [Clojure Style Guide](https://guide.clojure.style/)
- [clojure.spec Guide](https://clojure.org/guides/spec)
- [Codox Documentation](https://github.com/weavejester/codox)
- [Clojars](https://clojars.org/)
- [Clojure API Guidelines](https://clojure.org/guides/deps_and_cli)
- [Community Guidelines for Library Authors](https://dev.clojure.org/display/community/Library+Coding+Standards)
