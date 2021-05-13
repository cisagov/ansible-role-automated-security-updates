"""Module containing the tests for the default scenario."""

# Standard Python Libraries
import os

# Third-Party Libraries
# import pytest
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ["MOLECULE_INVENTORY_FILE"]
).get_hosts("all")


def test_packages(host):
    """Test that the expected packages were installed."""
    distribution = host.system_info.distribution
    if distribution in ["debian", "kali", "ubuntu"]:
        assert host.package("unattended-upgrades").is_installed
    elif distribution in ["fedora"]:
        assert host.package("dnf-automatic").is_installed
    elif distribution in ["amzn"]:
        assert host.package("yum-cron").is_installed
    else:
        # This distribution is unsupported
        assert False, f"Distribution {distribution} is not supported."


def test_service_enabled(host):
    """Test that the automatic upgrade service exists and was enabled."""
    distribution = host.system_info.distribution
    if distribution in ["debian", "kali", "ubuntu"]:
        assert host.service("unattended-upgrades").is_enabled
    elif distribution in ["fedora"]:
        assert host.service("dnf-automatic").is_enabled
    elif distribution in ["amzn"]:
        assert host.service("yum-cron").is_enabled
    else:
        # This distribution is unsupported
        assert False, f"Distribution {distribution} is not supported."


def test_service_configuration(host):
    """Test that the automatic upgrade service is configured as expected."""
    distribution = host.system_info.distribution
    if distribution in ["debian", "kali"]:
        f = host.file("/etc/apt/apt.conf.d/50unattended-upgrades")
        assert f.exists
        assert f.is_file
    elif distribution in ["ubuntu"]:
        f = host.file("/etc/apt/apt.conf.d/50unattended-upgrades")
        assert f.exists
        assert f.is_file
    elif distribution in ["fedora"]:
        f = host.file("/etc/dnf/automatic.conf")
        assert f.exists
        assert f.is_file
        assert f.contains(r"^upgrade_type = security$")
        assert f.contains(r"^download_updates = yes$")
        assert f.contains(r"^apply_updates = yes$")
    elif distribution in ["amzn"]:
        f = host.file("/etc/yum/yum-cron.conf")
        assert f.exists
        assert f.is_file
        assert f.contains(r"^update_cmd = security$")
        assert f.contains(r"^download_updates = yes$")
        assert f.contains(r"^apply_updates = yes$")
    else:
        # This distribution is unsupported
        assert False, f"Distribution {distribution} is not supported."
