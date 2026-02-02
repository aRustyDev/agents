class MyJuliaTool < Formula
  desc "A Julia CLI tool"
  homepage "https://github.com/example/my-julia-tool"
  url "https://github.com/example/my-julia-tool/archive/refs/tags/v1.0.0.tar.gz"
  sha256 "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
  license "MIT"

  livecheck do
    url :stable
    strategy :github_latest
  end

  depends_on "julia"

  def install
    libexec.install Dir["*"]
    (bin/"my-julia-tool").write <<~SH
      #!/bin/bash
      exec "#{Formula["julia"].opt_bin}/julia" "#{libexec}/src/main.jl" "$@"
    SH
  end

  test do
    system bin/"my-julia-tool", "--help"
    assert_match "my-julia-tool", shell_output("#{bin}/my-julia-tool --help")
  end
end
