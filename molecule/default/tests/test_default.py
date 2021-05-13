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
