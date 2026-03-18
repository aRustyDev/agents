class MyJavaTool < Formula
  desc "A Java CLI tool"
  homepage "https://github.com/example/my-java-tool"
  url "https://github.com/example/my-java-tool/archive/refs/tags/v1.0.0.tar.gz"
  sha256 "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
  license "Apache-2.0"

  livecheck do
    url :stable
    strategy :github_latest
  end

  depends_on "maven" => :build

  depends_on "openjdk"

  def install
    system "mvn", "package", "-DskipTests"
    libexec.install "target/my-java-tool.jar"
    bin.write_jar_script libexec/"my-java-tool.jar", "my-java-tool"
  end

  test do
    system bin/"my-java-tool", "--version"
    assert_match "my-java-tool", shell_output("#{bin}/my-java-tool --help")
  end
end
