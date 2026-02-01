class MyDaemon < Formula
  desc "A background service daemon"
  homepage "https://github.com/example/my-daemon"
  url "https://github.com/example/my-daemon/archive/refs/tags/v1.0.0.tar.gz"
  sha256 "deadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef"
  license "MIT"

  livecheck do
    url :stable
    strategy :github_latest
  end

  depends_on "go" => :build

  def install
    system "go", "build", *std_go_args(ldflags: "-s -w -X main.version=#{version}")
  end

  service do
    run ["#{opt_bin}/my-daemon", "--config", "#{etc}/my-daemon.conf"]
    run_type :immediate
    keep_alive true
    log_path "#{var}/log/my-daemon.log"
    error_log_path "#{var}/log/my-daemon-error.log"
  end

  test do
    system bin/"my-daemon", "--version"
    assert_match "my-daemon version #{version}", shell_output("#{bin}/my-daemon --help")
  end

  def caveats
    <<~EOS
      To start my-daemon now and restart at login:\n  brew services start my-daemon
    EOS
  end
end

