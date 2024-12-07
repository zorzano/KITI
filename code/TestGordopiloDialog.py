import unittest
import logging
import sys
from GordopiloDialog import GordopiloDialog

logger = logging.getLogger(__name__)
logging.basicConfig(filename='testGordopiloDialog.log', level=logging.INFO)

class TestGordopiloDialog(unittest.TestCase):
    #gp=GordopiloDialog()
    
    def setUp(self):
        print("setUp TestGordopiloDialog")
        self.gp=GordopiloDialog()


    def tearDown(self):
        print("tearDown TestGordopiloDialog")
        self.gp.close()

    def test_01(self):
        self.assertTrue(1==1)
    
    def test_02(self):
        answer=self.gp.answerText("Quectel?")
        print(answer)
        self.assertTrue("Quectel" in answer)
        self.assertTrue("[*]" not in answer)

    def test_03(self):
        answer=self.gp.answerText("Normativa Corporativa?")
        print(answer)
        self.assertTrue("Normativa" in answer)
        self.assertTrue("[*]" not in answer)

if __name__ == '__main__':
    unittest.main()
