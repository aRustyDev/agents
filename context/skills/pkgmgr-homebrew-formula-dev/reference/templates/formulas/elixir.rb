class MyElixirTool < Formula
  desc "An Elixir CLI tool"
  homepage "https://github.com/example/my-elixir-tool"
  url "https://github.com/example/my-elixir-tool/archive/refs/tags/v1.0.0.tar.gz"
  sha256 "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
  license "Apache-2.0"

  livecheck do
    url :stable
    strategy :github_latest
  end

  depends_on "elixir" => :build

  depends_on "erlang"

  def install
    ENV["MIX_ENV"] = "prod"
    system "mix", "deps.get"
    system "mix", "escript.build"
    bin.install "my-elixir-tool"
  end

  test do
    system bin/"my-elixir-tool", "--version"
    assert_match "my-elixir-tool", shell_output("#{bin}/my-elixir-tool --help")
  end
end
