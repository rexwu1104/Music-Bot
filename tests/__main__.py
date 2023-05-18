import unittest

from group_test import *
from dl_test import *

def test():
    suite = unittest.TestSuite()
    suite.addTest(GroupTest('equal'))
    suite.addTest(GroupTest('same'))
    suite.addTest(DownloadTest('spotify_download'))
    suite.addTest(DownloadTest("soundcloud_download"))
    
    unittest.TextTestRunner().run(suite)
    
test()