class MyNimTool < Formula
  desc "A Nim CLI tool"
  homepage "https://github.com/example/my-nim-tool"
  url "https://github.com/example/my-nim-tool/archive/refs/tags/v1.0.0.tar.gz"
  sha256 "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
  license "MIT"

  livecheck do
    url :stable
    strategy :github_latest
  end

  depends_on "nim" => :build

  def install
    system "nimble", "build", "-y"
    bin.install "my-nim-tool"
  end

  test do
    system bin/"my-nim-tool", "--version"
    assert_match "my-nim-tool", shell_output("#{bin}/my-nim-tool --help")
  end
end
