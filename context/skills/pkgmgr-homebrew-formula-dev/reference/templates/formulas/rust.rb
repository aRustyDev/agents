class RustAnalyzer < Formula
  desc "Experimental Rust compiler front-end for IDEs"
  homepage "https://rust-analyzer.github.io"
  url "https://github.com/rust-lang/rust-analyzer/archive/refs/tags/v0.3.1.tar.gz"
  sha256 "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2"
  license "Apache-2.0"

  livecheck do
    url :stable
    strategy :github_latest
  end

  depends_on "rust" => :build
  uses_from_macos "zlib"

  def install
    system "cargo", "install", *std_cargo_args, "--features", "lsp", "--features", "jemalloc"
  end

  test do
    system bin/"rust-analyzer", "--help"
    assert_match "rust-analyzer", shell_output("#{bin}/rust-analyzer --help")
  end
end
