"""Module containing the tests for the default scenario."""

# Standard Python Libraries
import configparser
import os

# Third-Party Libraries
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ["MOLECULE_INVENTORY_FILE"]
).get_hosts("all")


def test_packages(host):
    """Test that the expected packages were installed."""
    distribution = host.system_info.distribution
    if distribution in ["debian", "kali", "ubuntu"]:
        assert host.package("unattended-upgrades").is_installed
    elif distribution in ["amzn"]:
        assert host.package("dnf-automatic").is_installed
    elif distribution in ["fedora"]:
        assert host.package("dnf5-plugin-automatic").is_installed
    else:
        # This distribution is unsupported
        assert False, f"Distribution {distribution} is not supported."


def test_service_enabled(host):
    """Test that the automatic upgrade service exists and was enabled."""
    distribution = host.system_info.distribution
    if distribution in ["debian", "kali", "ubuntu"]:
        assert host.service("unattended-upgrades").is_enabled
    elif distribution in ["amzn"]:
        assert host.service("dnf-automatic.timer").is_enabled
    elif distribution in ["fedora"]:
        assert host.service("dnf5-automatic.timer").is_enabled
    else:
        # This distribution is unsupported
        assert False, f"Distribution {distribution} is not supported."


def test_service_configuration(host):
    """Test that the automatic upgrade service is configured as expected."""
    distribution = host.system_info.distribution
    if distribution in ["debian", "kali"]:
        filename = "/etc/apt/apt.conf.d/50unattended-upgrades"
        f = host.file(filename)
        assert f.exists
        assert f.is_file

        begin_regex = r"/^Unattended-Upgrade::Origins-Pattern/"
        end_regex = r"/^};$/"
        comment_regex = r"/^\s*\/\/.*$/d"
        awk_command = f"BEGIN {{p = 0}}; {begin_regex} {{p = 1; next}}; {end_regex} {{p = 0; next}}; p {{print}}"
        # The awk script extracts the contents of the Origins-Pattern
        # clause.  The sed command removes all comments.  The grep
        # outputs the remaining lines that contain the word security.
        # There should be one such line.
        full_command = f"test \"$(awk '{awk_command}' {filename} | sed '{comment_regex}' | grep --invert-match --ignore-case --fixed-strings security | wc --lines) -eq 1\""
        assert host.run(full_command).succeeded
    elif distribution in ["ubuntu"]:
        filename = "/etc/apt/apt.conf.d/50unattended-upgrades"
        f = host.file(filename)
        assert f.exists
        assert f.is_file

        begin_regex = r"/^Unattended-Upgrade::Allowed-Origins/"
        end_regex = r"/^};$/"
        comment_regex = r"/^\s*\/\/.*$/d"
        awk_command = f"BEGIN {{p = 0}}; {begin_regex} {{p = 1; next}}; {end_regex} {{p = 0; next}}; p {{print}}"
        # The awk script extracts the contents of the Origins-Pattern
        # clause.  The sed command removes all comments.  The grep
        # outputs the remaining lines that contain the word security.
        # There should be three such lines.
        full_command = f"test \"$(awk '{awk_command}' {filename} | sed '{comment_regex}' | grep --invert-match --ignore-case --fixed-strings security | wc --lines) -eq 3\""
        assert host.run(full_command).succeeded
    elif distribution in ["amzn", "fedora"]:
        filename = "/etc/dnf/automatic.conf"
        f = host.file(filename)
        assert f.exists
        assert f.is_file
        config = configparser.ConfigParser()
        config.read_string(f.content_string, filename)
        assert "commands" in config.sections()
        assert "upgrade_type" in config["commands"]
        assert config["commands"]["upgrade_type"] == "security"
        assert "download_updates" in config["commands"]
        assert config["commands"]["download_updates"]
        assert "apply_updates" in config["commands"]
        assert config["commands"]["apply_updates"]
    else:
        # This distribution is unsupported
        assert False, f"Distribution {distribution} is not supported."
