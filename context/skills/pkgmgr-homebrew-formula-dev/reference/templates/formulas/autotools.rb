class MyAutotoolsTool < Formula
  desc "An autotools-based CLI tool"
  homepage "https://github.com/example/my-autotools-tool"
  url "https://github.com/example/my-autotools-tool/archive/refs/tags/v1.0.0.tar.gz"
  sha256 "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
  license "GPL-3.0-only"

  livecheck do
    url :stable
    strategy :github_latest
  end

  def install
    system "./configure", *std_configure_args
    system "make", "install"
  end

  test do
    system bin/"my-autotools-tool", "--version"
    assert_match "my-autotools-tool", shell_output("#{bin}/my-autotools-tool --help")
  end
end
