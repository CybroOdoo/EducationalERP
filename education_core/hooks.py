# -*- coding: utf-8 -*-
###############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2026-TODAY Cybrosys Technologies(
#    <https://www.cybrosys.com>).
#    Author: Cybrosys Techno Solutions(<https://www.cybrosys.com>)
#
#    This program is under the terms of the Odoo Proprietary License v1.0 (
#    OPL-1)
#    It is forbidden to publish, distribute, sublicense, or sell copies of the
#    Software or modified copies of the Software.
#
#    THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NON INFRINGEMENT. IN NO EVENT SHALL
#    THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,DAMAGES OR OTHER
#    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,ARISING
#    FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#    DEALINGS IN THE SOFTWARE.
#
###############################################################################
import logging
import subprocess
import sys

_logger = logging.getLogger(__name__)


def pre_init_hook(env):
    """Pre-initialization hook to ensure external dependency 'phonenumbers'
    is installed.
    """
    try:
        import phonenumbers
    except ImportError:
        _logger.info("Installing missing Python dependency 'phonenumbers'...")
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "phonenumbers"]
            )
            _logger.info("Successfully installed 'phonenumbers'.")
        except Exception as e:
            _logger.error(
                "Failed to auto-install 'phonenumbers' via pip: %s", str(e)
            )
            raise RuntimeError(
                "The 'phonenumbers' Python library is required. "
                "Please install it manually using: pip install phonenumbers"
            ) from e


def post_init_hook(env):
    """Generate the date-relative demo data of the three institutions.

    Runs after the XML demo data; does nothing when the module is
    installed without demo data.
    """
    from .demo.education_demo_data import load_demo_data
    load_demo_data(env)
