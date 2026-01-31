root := `git rev-parse --show-toplevel`
tmpls := root + "/.claude/templates"
internal := root + "/internal"
datasource := internal + "/datasource"
provider := internal + "/provider"
resource := internal + "/resource"
about := internal + "/about"
util := internal + "/util"

mktree:
    mkdir -p {{root}}/internal/{about,data,resource,provider,utils}
    mkdir -p {{root}}/examples/{datasources,resources,tests}
    mkdir -p {{root}}/test
    mkdir -p {{root}}/docs
    mkdir -p {{root}}/build
    mkdir -p {{root}}/configs

mkdocs:
    mdbook init --title "" --ignore git {{root}}/docs

template target:
    @mustache {{root}}/.claude/templates/datasource.go.mustache
    @mustache {{root}}/.claude/templates/resource.go.mustache
    @mustache {{root}}/.claude/templates/provider.go.mustache
    touch {{root}}/internal/about/about.go
    touch {{root}}/internal/data/data.go
    touch {{root}}/internal/resource/resource.go
    touch {{root}}/internal/provider/provider.go
    touch {{root}}/internal/utils/utils.go
    touch {{root}}/examples/datasources/datasource.tf
    touch {{root}}/examples/resources/resource.tf
    touch {{root}}/examples/tests/test.tf
    touch {{root}}/test/test.go
    touch {{root}}/configs/config.yaml

# init:
#     go mod init github.com/addy/terraform-provider-addy
#     pre-commit install --install-hooks
