class MyMakeTool < Formula
  desc "A tool built with Make"
  homepage "https://github.com/example/my-make-tool"
  url "https://github.com/example/my-make-tool/archive/refs/tags/v1.0.0.tar.gz"
  sha256 "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
  license "MIT"

  livecheck do
    url :stable
    strategy :github_latest
  end

  def install
    system "make", "PREFIX=#{prefix}"
    system "make", "install", "PREFIX=#{prefix}"
  end

  test do
    system bin/"my-make-tool", "--version"
    assert_match "my-make-tool", shell_output("#{bin}/my-make-tool --help")
  end
end
