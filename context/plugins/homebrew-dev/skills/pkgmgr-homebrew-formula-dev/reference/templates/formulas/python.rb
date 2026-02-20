class MyPythonTool < Formula
  desc "A Python-based CLI utility"
  homepage "https://github.com/example/my-python-tool"
  url "https://github.com/example/my-python-tool/archive/refs/tags/v2.0.0.tar.gz"
  sha256 "abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890"
  license "MIT"

  livecheck do
    url :stable
    strategy :pypi
  end

  depends_on "python@3.12" => :build

  resource "certifi" do
    url "https://files.pythonhosted.org/packages/certifi-2024.2.2.tar.gz"
    sha256 "1111111111111111111111111111111111111111111111111111111111111111"
  end

  resource "urllib3" do
    url "https://files.pythonhosted.org/packages/urllib3-2.2.1.tar.gz"
    sha256 "2222222222222222222222222222222222222222222222222222222222222222"
  end

  def install
    virtualenv_install_with_resources
  end

  test do
    system bin/"my-python-tool", "--version"
    assert_match "my-python-tool #{version}", shell_output("#{bin}/my-python-tool --help")
  end
end
