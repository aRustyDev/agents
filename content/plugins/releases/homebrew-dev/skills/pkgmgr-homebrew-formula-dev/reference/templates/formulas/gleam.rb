class MyGleamTool < Formula
  desc "A Gleam CLI tool"
  homepage "https://github.com/example/my-gleam-tool"
  url "https://github.com/example/my-gleam-tool/archive/refs/tags/v1.0.0.tar.gz"
  sha256 "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
  license "Apache-2.0"

  livecheck do
    url :stable
    strategy :github_latest
  end

  depends_on "gleam" => :build

  depends_on "erlang"

  def install
    system "gleam", "export", "erlang-shipment"
    libexec.install Dir["build/erlang-shipment/*"]
    bin.write_env_script libexec/"entrypoint.sh", PATH: "#{Formula["erlang"].opt_bin}:$PATH"
  end

  test do
    system bin/"my-gleam-tool", "--version"
    assert_match "my-gleam-tool", shell_output("#{bin}/my-gleam-tool --help")
  end
end
