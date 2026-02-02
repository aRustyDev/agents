class MySwiftTool < Formula
  desc "A Swift CLI tool"
  homepage "https://github.com/example/my-swift-tool"
  url "https://github.com/example/my-swift-tool/archive/refs/tags/v1.0.0.tar.gz"
  sha256 "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
  license "MIT"

  livecheck do
    url :stable
    strategy :github_latest
  end

  def install
    system "swift", "build", "-c", "release"
    bin.install ".build/release/my-swift-tool"
  end

  test do
    system bin/"my-swift-tool", "--version"
    assert_match "my-swift-tool", shell_output("#{bin}/my-swift-tool --help")
  end
end
