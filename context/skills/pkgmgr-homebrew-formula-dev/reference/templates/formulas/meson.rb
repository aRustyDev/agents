class MyMesonTool < Formula
  desc "A Meson-based CLI tool"
  homepage "https://github.com/example/my-meson-tool"
  url "https://github.com/example/my-meson-tool/archive/refs/tags/v1.0.0.tar.gz"
  sha256 "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
  license "LGPL-2.1-only"

  livecheck do
    url :stable
    strategy :github_latest
  end

  depends_on "meson" => :build

  depends_on "ninja" => :build

  def install
    system "meson", "setup", "build", *std_meson_args
    system "meson", "compile", "-C", "build"
    system "meson", "install", "-C", "build"
  end

  test do
    system bin/"my-meson-tool", "--version"
    assert_match "my-meson-tool", shell_output("#{bin}/my-meson-tool --help")
  end
end
