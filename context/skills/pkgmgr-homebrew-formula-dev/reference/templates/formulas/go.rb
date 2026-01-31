class MyTool < Formula
  desc "A fast CLI tool written in Go"
  homepage "https://github.com/example/my-tool"
  url "https://github.com/example/my-tool/archive/refs/tags/v1.2.3.tar.gz"
  sha256 "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
  license "MIT"
  head "https://github.com/example/my-tool.git", branch: "main"

  livecheck do
    url :stable
    strategy :github_latest
  end

  depends_on "go" => :build

  depends_on "pkg-config" => :build

  def install
    system "go", "build", *std_go_args(ldflags: "-s -w -X main.version=#{version}"), "./cmd/my-tool"

    generate_completions_from_executable(bin/"my-tool", "completions", "bash",
                                         shell_output_dir: bash_completion)
    generate_completions_from_executable(bin/"my-tool", "completions", "zsh",
                                         shell_output_dir: zsh_completion)
    generate_completions_from_executable(bin/"my-tool", "completions", "fish",
                                         shell_output_dir: fish_completion)
  end

  test do
    system bin/"my-tool", "--version"
    assert_match "my-tool version #{version}", shell_output("#{bin}/my-tool --help")
  end
end

