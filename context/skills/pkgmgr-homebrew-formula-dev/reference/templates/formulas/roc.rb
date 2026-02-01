class MyRocTool < Formula
  desc "A Roc CLI tool"
  homepage "https://github.com/example/my-roc-tool"
  url "https://github.com/example/my-roc-tool/archive/refs/tags/v1.0.0.tar.gz"
  sha256 "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
  license "MIT"

  livecheck do
    url :stable
    strategy :github_latest
  end

  depends_on "roc" => :build

  def install
    system "roc", "build", "--optimize", "main.roc"
    bin.install "my-roc-tool"
  end

  test do
    system bin/"my-roc-tool", "--version"
    assert_match "my-roc-tool", shell_output("#{bin}/my-roc-tool --help")
  end
end
