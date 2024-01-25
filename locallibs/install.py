# encoding: utf-8
#
# Copyright 2018 Greg Neagle.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Functions to pip install extra modules in our framework"""

from __future__ import print_function

import itertools
import os
import subprocess
import sys


def ensure_pip(framework_path, version):
    """Ensure pip is installed in our Python framework"""
    python_path = os.path.join(
        framework_path, "Versions", version, "bin/python" + version
    )
    if not os.path.exists(python_path):
        print("No python at %s" % python_path, file=sys.stderr)
        return
    cmd = [python_path, "-s", "-m", "ensurepip"]
    print("Ensuring pip is installed...")
    subprocess.check_call(cmd)


def install(pkgname, framework_path, version):
    """Use pip to install a Python pkg into framework_path"""
    python_path = os.path.join(
        framework_path, "Versions", version, "bin/python" + version
    )
    if not os.path.exists(python_path):
        print("No python at %s" % python_path, file=sys.stderr)
        return
    cmd = [python_path, "-s", "-m", "pip", "install", pkgname]
    print("Installing %s..." % pkgname)
    subprocess.check_call(cmd)


def upgrade_pip_install(framework_path, version):
    """Use pip to upgrade pip"""
    python_path = os.path.join(
        framework_path, "Versions", version, "bin/python" + version
    )
    if not os.path.exists(python_path):
        print("No python at %s" % python_path, file=sys.stderr)
        return
    cmd = [python_path, "-s", "-m", "pip", "install", "--upgrade", "pip"]
    print("Upgrading pip installation...")
    subprocess.check_call(cmd)


def install_requirements(
        requirements_file, framework_path, version, pip_platform, no_binary, only_binary):
    """Use pip to install a Python pkg into framework_path"""

    def multi_value_option(option, values, separator=None):
        """Helper function supply the same option with multiple value

        Args:
            option (str): the option name (e.g. --<option>)
            values (list): a list of values that should be passed to the option
            separator (str): if the option is separated by a value (e.g. "=") and 
                each option value combo should be returned as a single string

        Returns:
            list: a flattened list of the option and values
        """
        if separator:
            return list(itertools.chain.from_iterable(
                [[option + separator + value] for value in values]
            ))
        return list(itertools.chain.from_iterable([[option, value] for value in values]))

    python_path = os.path.join(
        framework_path, "Versions", version, "bin/python" + version
    )
    headers_path = os.path.abspath(os.path.join(
        framework_path, "Versions", version, "include/python" + version
    ))
    site_packages_path = os.path.join(
        framework_path, "Versions", version, "lib/python" + version
        + "/site-packages"
    )
    if not os.path.exists(python_path):
        print("No python at %s" % python_path, file=sys.stderr)
        return
    cmd = [python_path, "-s", "-m", "pip", "install", "-r", requirements_file]

    if pip_platform:
        cmd.extend(multi_value_option("--platform", pip_platform))
        cmd.append("--target=%s" % site_packages_path)

    if no_binary:
        cmd.extend(multi_value_option("--no-binary", no_binary, "="))

    elif only_binary:
        cmd.extend(multi_value_option("--only-binary", only_binary, "="))

    pip_env = os.environ
    pip_env["CPPFLAGS"] = "-I%s" % headers_path
    print("Installing modules from %s..." % requirements_file)
    subprocess.check_call(cmd, env=pip_env)


def install_extras(
    framework_path,
    version="2.7",
    requirements_file=None,
    upgrade_pip=False,
    without_pip=False,
    pip_platform=None,
    no_binary=None,
    only_binary=None
):
    """install all extra pkgs into Python framework path"""
    print()
    python_guard_path = (
        os.path.expanduser("~/Library/Python/%s/lib/python/site-packages") % version
    )
    if os.path.exists(python_guard_path):
        print("*********************************************************")
        print("*** Python user files exist that conflict with the    ***")
        print("*** version of relocatable python you are trying to   ***")
        print("*** create. This can result in extra python modules   ***")
        print("*** not being installed properly or out of date.      ***")
        print("*** Please remove these files or create this package  ***")
        print("*** under a fresh user account.                       ***")
        print("*** The files are located at:                         ***")
        print("*** %s ***" % python_guard_path)
        print("*********************************************************")
        print()

    if not without_pip:
        ensure_pip(framework_path, version)
        install("wheel", framework_path, version)
        if upgrade_pip:
            upgrade_pip_install(framework_path, version)
        if requirements_file:
            print()
            install_requirements(
                requirements_file, framework_path, version, pip_platform, no_binary, only_binary)
    else:
        print("Skipping all requirements, packages, etc due to without-pip specified")
