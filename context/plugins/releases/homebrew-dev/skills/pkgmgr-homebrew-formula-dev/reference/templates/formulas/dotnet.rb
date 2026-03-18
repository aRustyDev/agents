class MyDotnetTool < Formula
  desc "A .NET CLI tool"
  homepage "https://github.com/example/my-dotnet-tool"
  url "https://github.com/example/my-dotnet-tool/archive/refs/tags/v1.0.0.tar.gz"
  sha256 "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
  license "MIT"

  livecheck do
    url :stable
    strategy :github_latest
  end

  depends_on "dotnet"

  def install
    system "dotnet", "publish", "-c", "Release", "-o", "#{libexec}"
    (bin/"my-dotnet-tool").write_env_script libexec/"my-dotnet-tool", DOTNET_ROOT: Formula["dotnet"].opt_libexec
  end

  test do
    system bin/"my-dotnet-tool", "--version"
    assert_match "my-dotnet-tool", shell_output("#{bin}/my-dotnet-tool --help")
  end
end
