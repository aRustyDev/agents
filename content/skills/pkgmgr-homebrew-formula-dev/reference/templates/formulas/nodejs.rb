class MyNodeTool < Formula
  desc "A Node.js CLI tool"
  homepage "https://github.com/example/my-node-tool"
  url "https://registry.npmjs.org/my-node-tool/-/my-node-tool-1.0.0.tgz"
  sha256 "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
  license "MIT"

  livecheck do
    url :stable
    strategy :npm
  end

  depends_on "node"

  def install
    system "npm", "install", *std_npm_args
    bin.install_symlink Dir["#{libexec}/bin/*"]
  end

  test do
    system bin/"my-node-tool", "--version"
    assert_match "my-node-tool", shell_output("#{bin}/my-node-tool --help")
  end
end
