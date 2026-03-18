class MyErlangTool < Formula
  desc "An Erlang CLI tool"
  homepage "https://github.com/example/my-erlang-tool"
  url "https://github.com/example/my-erlang-tool/archive/refs/tags/v1.0.0.tar.gz"
  sha256 "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
  license "Apache-2.0"

  livecheck do
    url :stable
    strategy :github_latest
  end

  depends_on "rebar3" => :build

  depends_on "erlang"

  def install
    system "rebar3", "escriptize"
    bin.install "_build/default/bin/my-erlang-tool"
  end

  test do
    system bin/"my-erlang-tool", "--version"
    assert_match "my-erlang-tool", shell_output("#{bin}/my-erlang-tool --help")
  end
end
