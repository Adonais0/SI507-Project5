import unittest
from SI507project5_code import *

class Test_Tumblr_API(unittest.TestCase):
    def setUp(self):
        self.cache_diction = json.loads(open('cache_contents.json').read())
        self.creds_diction = json.loads(open('creds_contents.json').read())
        self.alldesignprocess = open("alldesignprocess.csv")
        self.uxdesignresource = open("uxdesignresource.csv")
        self.uxdesignprocess = open('uxdesignprocess-blog.csv')

    def test_cache_success(self):
        self.assertTrue(self.cache_diction)
        self.assertTrue(self.creds_diction)
        self.assertIsInstance(self.cache_diction,dict)
        self.assertIsInstance(self.creds_diction,dict)

    def test_files_exist(self):
        self.assertTrue(self.alldesignprocess.read())
        self.assertTrue(self.uxdesignprocess.read())
        self.assertTrue(self.uxdesignresource.read())

    def test_get_from_cache(self):
        self.assertTrue(get_from_cache('HTTPS://API.TUMBLR.COM/V2/BLOG/UXDESIGNRESOURCE.TUMBLR.COM/POSTS?LIMIT_20_OFFSET_3',CACHE_DICTION))
        self.assertIsInstance(get_from_cache('HTTPS://API.TUMBLR.COM/V2/BLOG/UXDESIGNRESOURCE.TUMBLR.COM/POSTS?LIMIT_20_OFFSET_3',CACHE_DICTION),list)
        self.assertTrue(get_from_cache('TUMBLR',self.creds_diction))

    def test_get_token(self):
        self.assertTrue(get_tokens())

    def test_get_token_from_service(self):
        self.assertTrue('Tumblr')

    def tearDown(self):
        self.alldesignprocess.close()
        self.uxdesignresource.close()
        self.uxdesignprocess.close()















if __name__ == "__main__":
    unittest.main(verbosity=2)
