class MyHaskellTool < Formula
  desc "A Haskell CLI tool"
  homepage "https://github.com/example/my-haskell-tool"
  url "https://github.com/example/my-haskell-tool/archive/refs/tags/v1.0.0.tar.gz"
  sha256 "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
  license "BSD-3-Clause"

  livecheck do
    url :stable
    strategy :github_latest
  end

  depends_on "ghc" => :build

  depends_on "cabal-install" => :build

  def install
    system "cabal", "v2-update"
    system "cabal", "v2-install", *std_cabal_v2_args
  end

  test do
    system bin/"my-haskell-tool", "--version"
    assert_match "my-haskell-tool", shell_output("#{bin}/my-haskell-tool --help")
  end
end
