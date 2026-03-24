class MyKotlinTool < Formula
  desc "A Kotlin CLI tool"
  homepage "https://github.com/example/my-kotlin-tool"
  url "https://github.com/example/my-kotlin-tool/archive/refs/tags/v1.0.0.tar.gz"
  sha256 "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
  license "Apache-2.0"

  livecheck do
    url :stable
    strategy :github_latest
  end

  depends_on "gradle" => :build

  depends_on "openjdk"

  def install
    system "gradle", "installDist"
    libexec.install Dir["build/install/*/lib"]
    libexec.install Dir["build/install/*/bin"]
    (bin/"my-kotlin-tool").write_env_script libexec/"bin/my-kotlin-tool", JAVA_HOME: Formula["openjdk"].opt_prefix
  end

  test do
    system bin/"my-kotlin-tool", "--version"
    assert_match "my-kotlin-tool", shell_output("#{bin}/my-kotlin-tool --help")
  end
end
