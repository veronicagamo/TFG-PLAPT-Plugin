.. |organization| replace:: scipion-chem
.. |repository| replace:: scipion-chem-plapt

========================================
PLAPT Scipion Plugin
========================================
**Documentation under development, sorry for the inconvenience**

Scipion framework plugin for ligand–protein affinity prediction using the PLAPT deep learning model.

========================================
Install this plugin
========================================
You will need to use `Scipion3 <https://scipion-em.github.io/docs/docs/scipion-modes/how-to-install.html>`_ to run these protocols.

PLAPT and its dependencies are installed automatically by the plugin.

- **Install the stable version**

    Through the plugin manager GUI by launching Scipion and following **Others** >> **Plugin Manager**

    or

.. parsed-literal::

    scipion3 installp -p \ |repository|\ 

- **Developer's version**

    1. Download repository:

    .. parsed-literal::

        git clone https://github.com/\ |organization|\ /\ |repository|\ .git

    2. Install:

    .. parsed-literal::

        scipion3 installp -p /path/to/\ |repository|\  --devel

========================================
Protocols
========================================
This plugin contains the following protocols:

- **PLAPT Analysis**: Predict ligand–protein affinity based on a single sequence and a set of small molecules.

========================================
Packages & environments
========================================
Packages installed by this plugin can be located in ``/path/to/scipion/software/em/``.

The following packages will be created:

- plapt-``version``

Where ``version`` is the current version of the PLAPT package.

Also, the following conda environments will be created:

- plapt-``version``

As of today, Scipion does not automatically uninstall the conda environments created during plugin installation, so you may need to remove these manually if uninstalling the plugin.

========================================
External software
========================================
This plugin integrates the following software:
  
.. _plapt: https://github.com/DIFACQUIM/plapt
.. |plapt| replace:: **PLAPT** 

- |plapt|_: Deep learning model for protein–ligand binding affinity prediction from sequence and SMILES.

========================================
Changelog
========================================
All recent version changes can be found `here <https://github.com/scipion-chem/scipion-chem-plapt/blob/devel/CHANGES.rst>`_.

