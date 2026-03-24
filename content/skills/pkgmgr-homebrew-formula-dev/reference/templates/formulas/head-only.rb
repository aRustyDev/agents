class BleedingEdge < Formula
  desc "A tool that only builds from HEAD"
  homepage "https://github.com/example/bleeding-edge"
  license "GPL-3.0-only"
  head "https://github.com/example/bleeding-edge.git", branch: "main"

  depends_on "go" => :build

  def install
    system "go", "build", *std_go_args(ldflags: "-s -w")
  end

  test do
    system bin/"bleeding-edge", "--help"
    assert_match "bleeding-edge", shell_output("#{bin}/bleeding-edge --help")
  end
end
