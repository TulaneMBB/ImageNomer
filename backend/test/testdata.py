import unittest
import sys

sys.path.append('..')

import data

class TestData(unittest.TestCase):
    def test_demo2df_easy(self):
        var = dict(a=1, b=2, c=10, d=-1, e=2)
        var_cat = dict(a='M', b='F', c='M', d='F', e='M')
        demo = dict(age=var, sex=var_cat)
        df = data.demo2df(demo)
        self.assertTrue(df.at['a','sex'] == 'M')
        self.assertTrue(df.at['b','age'] == 2)

    def test_demo2df_medium(self):
        demo = data.get_demo('anton', 'test')
        df = data.demo2df(demo)
        self.assertTrue(df.at['000','age'] == 148)
        self.assertTrue(df.at['008','sex'] == 'M')
        self.assertTrue(df.at['005','wrat'] == 113)

    '''
    def test_make_group_easy(self):
        demo = data.get_demo('anton', 'test')
        df = data.demo2df(demo)
        print(data.make_group(df, 'sex', 'F'))
        print(data.make_group(df, 'age', (0, 160)))
    '''

    def test_make_group_query_easy(self):
        demo = data.get_demo('anton', 'test')
        df = data.demo2df(demo)
        print(df)
        print(data.make_group_query(df, 'sex == "F"'))
        print(data.make_group_query(df, 'age > 160 and age < 200'))

if __name__ == '__main__':
    unittest.main()
