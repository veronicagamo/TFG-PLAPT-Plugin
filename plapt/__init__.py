# **************************************************************************
# *
# * Authors: Verónica Gamo (veronica.gamoparejo@usp.ceu.es)
# *
# * Biocomputing Unit, CNB-CSIC
# *
# * This program is free software; you can redistribute it and/or modify
# * it under the terms of the GNU General Public License as published by
# * the Free Software Foundation; either version 2 of the License, or
# * (at your option) any later version.
# *
# * This program is distributed in the hope that it will be useful,
# * but WITHOUT ANY WARRANTY; without even the implied warranty of
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# * GNU General Public License for more details.
# *
# * You should have received a copy of the GNU General Public License
# * along with this program; if not, write to the Free Software
# * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
# * 02111-1307  USA
# *
# *  All comments concerning this program package may be sent to the
# *  e-mail address 'scipion@cnb.csic.es'
# *
# **************************************************************************

# Scipion em imports
import os, subprocess
from subprocess import run
from scipion.install.funcs import InstallHelper

# Scipion chem imports
import pwchem

# Plugin imports
from .constants import PLUGIN_VERSION, PLAPT_DIC

_version_ = PLUGIN_VERSION
_logo = ""
_references = ['']

class Plugin(pwchem.Plugin):
	@classmethod
	def _defineVariables(cls):
		""" Return and write a variable in the config file. """
		cls._defineEmVar(PLAPT_DIC['home'], '{}-{}'.format(PLAPT_DIC['name'], PLAPT_DIC['version']))

	@classmethod
	def defineBinaries(cls, env):
		""" Install the necessary packages. """
		cls.addPLAPT(env)

	########################### PACKAGE FUNCTIONS ###########################
	@classmethod
	def addPLAPT(cls, env, default=True):
		"""This function installs PLAPT's package."""
		
		# Instantiating install helper
		installer = InstallHelper(PLAPT_DIC['name'], packageHome=cls.getVar(PLAPT_DIC['home']), packageVersion=PLAPT_DIC['version'])

		plapt_env_name = f"{PLAPT_DIC['name']}-{PLAPT_DIC['version']}"
		absolute_download_dir = os.path.abspath(cls.getVar(PLAPT_DIC['home']))
		repo_dir = os.path.join(absolute_download_dir, "WELP-PLAPT")

		# Check if WELP-PLAPT is already cloned
		if not os.path.exists(repo_dir):
			clone_command = f'cd {absolute_download_dir} && git clone https://github.com/trrt-good/WELP-PLAPT.git'
		else:
			clone_command = f'cd {repo_dir} && git pull origin main'  # Update if it exists

		# Installing package
		installer.getCondaEnvCommand(binaryName=PLAPT_DIC['name'], binaryVersion=PLAPT_DIC['version']) \
			.addCommand(clone_command) \
			.addCommand(f'cd {repo_dir} && conda env update --name {plapt_env_name} --file environment.yml') \
			.addPackage(env, dependencies=['conda'], default=default)

	@classmethod
	def runPLAPT(cls, program, args, cwd=None):
		""" Run PLAPT command from a given protocol. """
		absolute_download_dir = os.path.abspath(cls.getVar(PLAPT_DIC['home']))
		repo_dir = os.path.join(absolute_download_dir, "WELP-PLAPT")
		full_program = '%s && cd %s && %s ' % (cls.getEnvActivationCommand(PLAPT_DIC), repo_dir, program)
		print('full_program ', full_program)
		run(full_program + args, env=cls.getEnviron(), cwd=cwd, shell=True)
