class MyOcamlTool < Formula
  desc "An OCaml CLI tool"
  homepage "https://github.com/example/my-ocaml-tool"
  url "https://github.com/example/my-ocaml-tool/archive/refs/tags/v1.0.0.tar.gz"
  sha256 "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
  license "ISC"

  livecheck do
    url :stable
    strategy :github_latest
  end

  depends_on "ocaml" => :build

  depends_on "dune" => :build

  def install
    system "dune", "build"
    bin.install "_build/default/bin/my-ocaml-tool.exe" => "my-ocaml-tool"
  end

  test do
    system bin/"my-ocaml-tool", "--version"
    assert_match "my-ocaml-tool", shell_output("#{bin}/my-ocaml-tool --help")
  end
end
