class MyScalaTool < Formula
  desc "A Scala CLI tool"
  homepage "https://github.com/example/my-scala-tool"
  url "https://github.com/example/my-scala-tool/archive/refs/tags/v1.0.0.tar.gz"
  sha256 "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
  license "Apache-2.0"

  livecheck do
    url :stable
    strategy :github_latest
  end

  depends_on "sbt" => :build

  depends_on "openjdk"

  def install
    system "sbt", "assembly"
    libexec.install Dir["target/**/*.jar"]
    bin.write_jar_script Dir[libexec/"*.jar"].first, "my-scala-tool"
  end

  test do
    system bin/"my-scala-tool", "--version"
    assert_match "my-scala-tool", shell_output("#{bin}/my-scala-tool --help")
  end
end
