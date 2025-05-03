from pyworkflow.tests import BaseTest, DataSet, setupTestProject
from pwchem.protocols import ProtChemImportSmallMolecules
from pwchem.protocols import ProtChemPLAPT
from pwem.protocols import ProtImportSequence
from pwchem.utils import assertHandle

class TestPLAPT(BaseTest):
    @classmethod
    def setUpClass(cls):
        setupTestProject(cls)
        cls.dsLig = DataSet.getDataSet("smallMolecules")
        cls.dsSeq = DataSet.getDataSet("model_building_tutorial")

        cls._runImportSmallMols()
        cls._waitOutput(cls.protImportSmallMols, 'outputSmallMolecules', sleepTime=5)

        cls._runImportSequence()
        cls._waitOutput(cls.protImportSequence, 'outputSequence', sleepTime=5)

    @classmethod
    def _runImportSmallMols(cls):
        cls.protImportSmallMols = cls.newProtocol(
            ProtChemImportSmallMolecules,
            filesPath=cls.dsLig.getFile('sdf')
        )
        cls.proj.launchProtocol(cls.protImportSmallMols, wait=False)

    @classmethod
    def _runImportSequence(cls):
        cls.protImportSequence = cls.newProtocol(
            ProtImportSequence,
            inputSeqData=1,
            seqFile=cls.dsSeq.getFile('sequence/RIPK1.fasta')
        )
        cls.proj.launchProtocol(cls.protImportSequence, wait=False)

    def test_run_plapt(self):
        protPLAPT = self.newProtocol(
            ProtChemPLAPT,
            inputSet=self.protImportSmallMols.outputSmallMolecules,
            inputSequence=self.protImportSequence.outputSequence
        )

        self.launchProtocol(protPLAPT)
        self._waitOutput(protPLAPT, 'updatedMoleculeSet', sleepTime=10)
        
        updatedSet = getattr(protPLAPT, 'updatedMoleculeSet', None)
        assertHandle(self.assertIsNotNone, updatedSet, cwd=protPLAPT.getWorkingDir())

        for mol in updatedSet:
            self.assertTrue(hasattr(mol, 'pKd_PLAPT'))
            self.assertTrue(hasattr(mol, 'Affinity_uM_PLAPT'))
