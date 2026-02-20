class MyDartTool < Formula
  desc "A Dart CLI tool"
  homepage "https://github.com/example/my-dart-tool"
  url "https://github.com/example/my-dart-tool/archive/refs/tags/v1.0.0.tar.gz"
  sha256 "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
  license "BSD-3-Clause"

  livecheck do
    url :stable
    strategy :github_latest
  end

  depends_on "dart-sdk" => :build

  def install
    system "dart", "pub", "get"
    system "dart", "compile", "exe", "bin/main.dart", "-o", "my-dart-tool"
    bin.install "my-dart-tool"
  end

  test do
    system bin/"my-dart-tool", "--version"
    assert_match "my-dart-tool", shell_output("#{bin}/my-dart-tool --help")
  end
end
