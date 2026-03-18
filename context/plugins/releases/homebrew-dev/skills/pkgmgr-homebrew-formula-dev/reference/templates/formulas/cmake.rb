class MyCmakeTool < Formula
  desc "A CMake-based CLI tool"
  homepage "https://github.com/example/my-cmake-tool"
  url "https://github.com/example/my-cmake-tool/archive/refs/tags/v1.0.0.tar.gz"
  sha256 "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
  license "BSD-3-Clause"

  livecheck do
    url :stable
    strategy :github_latest
  end

  depends_on "cmake" => :build

  def install
    args = std_cmake_args
    system "cmake", "-S", ".", "-B", "build", *args
    system "cmake", "--build", "build"
    system "cmake", "--install", "build"
  end

  test do
    system bin/"my-cmake-tool", "--version"
    assert_match "my-cmake-tool", shell_output("#{bin}/my-cmake-tool --help")
  end
end
