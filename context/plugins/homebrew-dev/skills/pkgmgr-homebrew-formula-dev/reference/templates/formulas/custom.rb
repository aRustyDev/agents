class MyCustomTool < Formula
  desc "A tool with a custom build process"
  homepage "https://github.com/example/my-custom-tool"
  url "https://github.com/example/my-custom-tool/archive/refs/tags/v1.0.0.tar.gz"
  sha256 "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
  license "MIT"

  livecheck do
    url :stable
    strategy :github_latest
  end

  def install
    system "make"
    bin.install "mybinary"
  end

  test do
    system bin/"my-custom-tool", "--version"
    assert_match "my-custom-tool", shell_output("#{bin}/my-custom-tool --help")
  end
end
