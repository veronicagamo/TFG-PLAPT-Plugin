import os
import json
from urllib.request import urlopen

from pyworkflow.protocol.params import PointerParam, StringParam, BooleanParam
from pwem.protocols import EMProtocol
from pwchem.objects import SetOfSmallMolecules, SmallMolecule
from pwem.objects import Sequence
from plapt import Plugin
from pwchem.utils import *
from pwchem.constants import RDKIT_DIC
import pyworkflow.object as pwobj

class ProtChemPLAPT(EMProtocol):
    """ Protocol for ligand-target interaction analysis using PLAPT with support for one sequence and small molecules. """

    _label = 'PLAPT Analysis'

    def __init__(self, **kwargs):
        EMProtocol.__init__(self, **kwargs)

    def _defineParams(self, form):
        form.addSection(label='Input')

        form.addParam('inputSet', PointerParam, pointerClass="SetOfSmallMolecules",
                      label='Set of ligands:', allowsNull=False,
                      help='Select the set of small molecules (ligands) for analysis.')

        form.addParam('inputSequence', PointerParam, pointerClass="Sequence",
                            label='Single sequence:', allowsNull=False,
                            help='Select a single protein sequence for analysis.')

    def _insertAllSteps(self):
        self._insertFunctionStep('runPlaptAnalysis')

    def runPlaptAnalysis(self):
        ligand_smiles_list = []
        inputMoleculeSet = self.inputSet.get()

        for mol in inputMoleculeSet:
            smi = self.getSMI(mol.getFileName(), 1)
            if smi:
                ligand_smiles_list.append((smi, mol))

        if not ligand_smiles_list:
            raise RuntimeError("No valid SMILES found! Check your input.")

        # Only a single sequence is allowed
        protein_input = self.inputSequence.get().getSequence()
        if not protein_input:
            raise RuntimeError("No valid protein sequence found! Check your input.")

        resultsPath = os.path.abspath(self._getExtraPath("results.json"))
        smiles_str = " ".join([f'"{smi}"' for smi, _ in ligand_smiles_list])

        args = f'-p "{protein_input}" -m {smiles_str} -o {resultsPath}'
        Plugin.runPLAPT(f"python3 plapt_cli.py ", args)

        inputMoleculeSet = self.inputSet.get()
        updatedMoleculeSet = inputMoleculeSet.createCopy(self._getPath(), copyInfo=True)

        with open(resultsPath) as f:
            plapt_results = json.load(f)

        if isinstance(plapt_results, list):
            # Asignar cada molécula con los datos en orden del JSON
            for mol, result in zip(inputMoleculeSet, plapt_results):
                # setattr(mol, 'target_protein', pwobj.String(protein_input)
                setattr(mol, 'pKd_PLAPT', pwobj.Float(result.get('neg_log10_affinity_M')))
                setattr(mol, 'Affinity_uM_PLAPT', pwobj.Float(result.get('affinity_uM')))
                updatedMoleculeSet.append(mol.clone())

        self._defineOutputs(updatedMoleculeSet=updatedMoleculeSet)


    def getSMI(self, mol, nt):
        fnSmall = os.path.abspath(mol)
        fnRoot, ext = os.path.splitext(os.path.basename(fnSmall))

        if ext == '.smi':
            return self.parseSMI(fnSmall)

        outDir = os.path.abspath(self._getExtraPath())
        fnOut = os.path.abspath(self._getExtraPath(fnRoot + '.smi'))
        args = f'-i "{fnSmall}" -of smi -o {fnOut} --outputDir {outDir} -nt {nt}'
        Plugin.runScript(self, 'rdkit_IO.py', args, env=RDKIT_DIC, cwd=outDir)    

        return self.parseSMI(fnOut)
    
    def parseSMI(self, smiFile):
        smi = None
        with open(smiFile) as f:
            for line in f:
                smi = line.split()[0].strip()
                if not smi.lower() == 'smiles':
                    break
        return smi
