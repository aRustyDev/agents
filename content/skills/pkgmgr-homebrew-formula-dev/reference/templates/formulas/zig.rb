class MyZigTool < Formula
  desc "A Zig CLI tool"
  homepage "https://github.com/example/my-zig-tool"
  url "https://github.com/example/my-zig-tool/archive/refs/tags/v1.0.0.tar.gz"
  sha256 "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
  license "MIT"

  livecheck do
    url :stable
    strategy :github_latest
  end

  depends_on "zig" => :build

  def install
    system "zig", "build", "-Doptimize=ReleaseSafe"
    bin.install ".zig-out/bin/my-zig-tool"
  end

  test do
    system bin/"my-zig-tool", "--version"
    assert_match "my-zig-tool", shell_output("#{bin}/my-zig-tool --help")
  end
end
