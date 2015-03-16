#!/usr/bin/env python

"""
Test pycacheback
"""

import os
import shutil
import random
import copy
from pycacheback import pyCacheBack
import unittest


class TestpyCacheBack(unittest.TestCase):
    def testSimple(self):
        """A simple 'smoke test' for the extended dictionary."""

        # make an extended dictionary and define a key/value pair
        a = pyCacheBack()
        a[1] = 'one'

        # make sure we can retrieve the pre-defined key/value pair
        msg = "a[1] != 'one'!"
        self.assertEqual(a[1], 'one', msg)

        # make sure that accessing non-existant key raises KeyError
        self.assertRaises(KeyError, a.__getitem__, 2)

        # make sure the len() function works correctly
        msg = 'len(a) should be 1, got %d!' % len(a)
        self.assertEqual(len(a), 1, msg)

    def testDict(self):
        """Test the basic dictionary methods that should still work."""

        # make an extended dictionary and define some key/value pairs
        a = pyCacheBack()
        a[1] = 'one'
        a[2] = '2'
        a[3] = 3
        a['4'] = 'four'

        # check other dictionary methods
        msg = 'len(a) should be 4, got %d!' % len(a)
        self.assertEqual(len(a), 4, msg)

        msg = "'1 in a' was False, should be True!"
        self.assertTrue(1 in a, msg)

        msg = "'\'4\' in a' was False, should be True!"
        self.assertTrue('4' in a, msg)

        b = a.copy()
        msg = "a.copy() doesn't return a true copy'"
        self.assertEqual(a, b, msg)

        msg = "a.get(1) should return 'one', got %s" % a.get(1)
        self.assertEqual(a.get(1), 'one', msg)

        msg = ("a.get(10, 'NONE') should return 'NONE', got %s"
               % str(a.get(10, 'NONE')))
        self.assertEqual(a.get(10, 'NONE'), 'NONE', msg)

        msg = "a.has_key(2) should return True, got %s" % str(a.has_key(2))
        self.assertTrue(a.has_key(2), msg)

        msg = ("a.has_key(10) should return False, got %s"
               % str(a.has_key(10)))
        self.assertFalse(a.has_key(10), msg)

        msg = ("a.items() should return [(1, 'one'), (2, '2'), (3, 3), "
               "('4', 'four')], got %s" % str(a.items()))
        self.assertEqual([(1, 'one'), (2, '2'), (3, 3), ('4', 'four')],
                         a.items(), msg)

        msg = "a.keys() should return [1, 2, 3, '4'], got %s" % str(a.keys())
        self.assertEqual([1, 2, 3, '4'], a.keys(), msg)

        msg = "a.keys() should return [1, 2, 3, '4'], got %s" % str(a.keys())
        self.assertEqual([1, 2, 3, '4'], a.keys(), msg)

        msg = ("a.values() should return ['one', '2', 3, 'four'], got %s"
               % str(a.values()))
        self.assertEqual(['one', '2', 3, 'four'], a.values(), msg)

        result = a.setdefault(10, 'TEN')
        msg = "a.setdefault(10, 'TEN') doesn't return 'TEN'?"
        self.assertEqual(result, 'TEN', msg)
        msg = "a.setdefault() doesn't set the default?"
        self.assertEqual(a[10], 'TEN', msg)

        result = a.pop(10)
        msg = "a.pop(10) should return 'TEN' but got %s?" % result
        self.assertEqual(result, 'TEN', msg)

        result = a.pop(10, 'not found')
        msg = ("a.pop(10, 'not found') should return 'not found' but got %s?"
               % result)
        self.assertEqual(result, 'not found', msg)

        #msg = "a.pop(10) should raise KeyError exception, but didn't?"
        self.assertRaises(KeyError, a.pop, 10)

        msg = "a.update(b) should set 'TEN' key but didn't"
        b = {'TEN': 10}
        a.update(b)
        self.assertEqual(a['TEN'], 10, msg)

        a.clear()
        msg = 'After clear(), len(a) should be 0, got %d!' % len(a)
        self.assertEqual(len(a), 0, msg)

        b = {'TEN': 10}
        a.update(b)
        msg = "a.keys() should return ['TEN'], got %s" % str(a.keys())
        self.assertEqual(a.keys(), ['TEN'], msg)

    def testLRU(self):
        """Test the LRU mechanism."""

        # make an extended dictionary, maxLRU is 2 for testing
        a = pyCacheBack(max_lru=2)

        # the LRU list should be empty when we start
        msg = ("Initial LRU list should be empty, but it's %s"
               % str(a._lru_list))
        self.assertEqual(a._lru_list, [], msg)

        # make sure the len() function works correctly
        msg = "len(a) should be 0, got %d!" % len(a)
        self.assertEqual(len(a), 0, msg)

        # add a key/value pair, recheck LRU and length
        a['test'] = 'test value'
        msg = ("LRU list should be %s, but it's %s"
               % (str(['test']), str(a._lru_list)))
        self.assertEqual(a._lru_list, ['test'], msg)

        msg = "len(a) should be 1, got %d!" % len(a)
        self.assertEqual(len(a), 1, msg)

        # add another key/value pair, recheck LRU
        a['test2'] = 'another test value'
        msg = ("LRU list should be %s, but it's %s"
               % (str(['test2', 'test']), str(a._lru_list)))
        self.assertEqual(a._lru_list, ['test2', 'test'], msg)

        # access first key/value pair, check LRU changed
        b = a['test']
        msg = ("LRU list should be %s, but it's %s"
               % (str(['test', 'test2']), str(a._lru_list)))
        self.assertEqual(a._lru_list, ['test', 'test2'], msg)

        # make sure the len() function works correctly
        msg = "len(a) should be 2, got %d!" % len(a)
        self.assertEqual(len(a), 2, msg)

        # add third key/value pair, check LRU changed
        a['test3'] = 100
        msg = ("LRU list should be %s, but it's %s"
               % (str(['test3', 'test']), str(a._lru_list)))
        self.assertEqual(a._lru_list, ['test3', 'test'], msg)

        # make sure the len() function works correctly (still 2)
        msg = "len(a) should be 2, got %d!" % len(a)
        self.assertEqual(len(a), 2, msg)

        # delete first key/value pair, check LRU changed
        del a['test']
        msg = ("LRU list should be %s, but it's %s"
               % (str(['test3']), str(a._lru_list)))
        self.assertEqual(a._lru_list, ['test3'], msg)

        # make sure the len() function works correctly
        msg = "len(a) should be 1, got %d!" % len(a)
        self.assertEqual(len(a), 1, msg)

    def testBacking(self):
        """Test the backing mechanism.  Keys will be (x, y) form."""

        # create the test directory
        test_dir = './_#test_dir#_'
        shutil.rmtree(test_dir, ignore_errors=True)
        os.mkdir(test_dir)

        # override the backing functions in pyCacheBack
        class my_cache(pyCacheBack):
            def _put_to_back(self, key, value):
                (x, y) = key
                dir_path = os.path.join(test_dir, str(x))
                try:
                    os.mkdir(dir_path)
                except OSError:
                    pass
                file_path = os.path.join(dir_path, str(y))
                with open(file_path, 'wb') as f:
                    f.write(str(value))

            def _get_from_back(self, key):
                (x, y) = key
                file_path = os.path.join(test_dir, str(x), str(y))
                try:
                    with open(file_path, 'rb') as f:
                        value = f.read()
                except IOError:
                    raise KeyError, str(key)
                return value

        # define utility testing function
        def check_file(self, file_path, expected_contents):
            if not os.path.isfile(file_path):
                self.fail("File %s doesn't exist!?" % file_path)
            with open(file_path, 'rb') as f:
                file_contents = f.read()
            if file_contents != expected_contents:
                self.fail("Expected file contents %s, got %s"
                          % (expected_contents, file_contents))

        # OK, test it
        a = my_cache(max_lru=2)
        a[(1,1)] = 'one and one'
        a[(1,2)] = 'one and two'
        a[(1,1)] = 'one and one, second value'  # redefine (1,1) value

        # test if backing files are as expected
        check_file(self, os.path.join(test_dir, '1', '1'), a[(1,1)])
        check_file(self, os.path.join(test_dir, '1', '2'), a[(1,2)])

        # add third key, flushing (1,2), check backing file still there
        a[(1,3)] = 'one, three'
        check_file(self, os.path.join(test_dir, '1', '2'), a[(1,2)])

        # check that we can still get (1,2) data from backing store
        msg = "a[(1,2)] != 'one and two'!"
        self.assertEqual(a[(1,2)], 'one and two', msg)

        # delete a key, ensure gone & check backing file still there
        del a[(1,3)]
        check_file(self, os.path.join(test_dir, '1', '3'),
                   'one, three')

        # clean up
        shutil.rmtree(test_dir)

    def testIter(self):
        kv_list = [(1, 'one'), (2, 2), (3, 3.0)]
        a = pyCacheBack(kv_list, max_lru=10)
        for i, x in enumerate(iter(a)):
            msg = "'%d'th key should be %d, got %s" % (i+1, kv_list[i][0], x)
            self.assertEqual(kv_list[i][0], x, msg)

    def testCopy(self):
        kv_list = [(1, 'one'), (2, 2), (3, 3.0)]
        a = pyCacheBack(kv_list, max_lru=10)
        b = a.copy()
        msg = 'Length of copied dict should be %d, got %d' % (len(a), len(b))
        self.assertEqual(len(b), len(a), msg)
        # change element of 'a', see if 'b' gets it
        orig = b[2]
        a[2] = 'test'
        _ = a[3]
        msg = "copy: b[2] should be %s, got %s" % (orig, str(b[2]))
        self.assertEqual(b[2], orig, msg)

    def testClear(self):
        kv_list = [(1, 'one'), (2, 2), (3, 3.0)]
        a = pyCacheBack(kv_list, max_lru=10)
        msg = 'Length before should be %d, got %d' % (len(kv_list), len(a))
        self.assertEqual(len(a), len(kv_list), msg)
        a.clear()
        msg = 'Length after should be 0, got %d' % len(a)
        self.assertEqual(len(a), 0, msg)
        # check LRU list is empty
        msg = ".clear() didn't empty ._lru_list, it's '%s'" % str(a._lru_list)
        self.assertEqual([], a._lru_list, msg)

    def testGet(self):
        kv_list = [(1, 'one'), (2, 2), (3, 3.0)]
        a = pyCacheBack(kv_list, max_lru=10)
        msg = (".get(1) should return '%s', got '%s'"
               % (str(kv_list[1][0]), str(a.get(1))))
        self.assertEqual(a.get(1), 'one', msg)

    def testHasKey(self):
        kv_list = [(1, 'one'), (2, 2), (3, 3.0)]
        a = pyCacheBack(kv_list, max_lru=10)
        msg = ".has_key(1) should return True, got '%s'" % str(a.has_key(1))
        self.assertEqual(a.has_key(1), True, msg)
        msg = (".has_key(100) should return False, got '%s'"
               % str(a.has_key(100)))
        self.assertEqual(a.has_key(100), False, msg)

        self.assertEqual(1 in a, True, msg)

    def testItems(self):
        kv_list = [(1, 'one'), (2, 2), (3, 3.0)]
        a = pyCacheBack(kv_list, max_lru=10)
        expected = str(kv_list)
        msg = (".items() should return '%s', got '%s'"
               % (expected, str(a.items())))
        self.assertEqual(expected, str(a.items()), msg)

    def testItems(self):
        kv_list = [(1, 'one'), (2, 2), (3, 3.0)]
        a = pyCacheBack(kv_list, max_lru=10)
        for i, x in enumerate(a.iteritems()):
            msg = (".iteritems() item %d should be '%s', got '%s'"
                   % (i, str(kv_list[i]), str(x)))
            self.assertEqual(kv_list[i], x, msg)

    def testItervalues(self):
        kv_list = [(1, 'one'), (2, 2), (3, 3.0)]
        a = pyCacheBack(kv_list, max_lru=10)
        for i, x in enumerate(a.itervalues()):
            msg = (".itervalues() item %d should be '%s', got '%s'"
                   % (i, str(kv_list[i][1]), str(x)))
            self.assertEqual(kv_list[i][1], x, msg)

    def testItervalues(self):
        kv_list = [(1, 'one'), (2, 2), (3, 3.0)]
        a = pyCacheBack(kv_list, max_lru=10)
        k_list = [x[0] for x in kv_list]
        msg = ".keys() should be '%s', got '%s'" % (str(k_list), str(a.keys()))
        self.assertEqual(k_list, a.keys(), msg)

    def testPop(self):
        kv_list = [(1, 'one'), (2, 2), (3, 3.0)]
        a = pyCacheBack(kv_list, max_lru=10)
        random.shuffle(kv_list)
        for (k, v) in kv_list:
            _ = a[k]
        expected_lru_len = len(a._lru_list)
        for (k, v) in kv_list:
            value = a.pop(k, None)
            msg = (".pop(%s) should return '%s', got '%s'"
                   % (str(k), str(v), str(value)))
            self.assertEqual(v, value, msg)
            expected_lru_len = expected_lru_len - 1
            msg = (".pop(%s) should leave dict with len(LRU)=%d, got %d"
                   % (str(k), expected_lru_len, len(a._lru_list)))
            self.assertEqual(len(a._lru_list), expected_lru_len, msg)

    def testPopitem(self):
        kv_list = [(1, 'one'), (2, 2), (3, 3.0)]
        a = pyCacheBack(kv_list, max_lru=10)
        # get a big LRU list
        shuffle_kv_list = copy.deepcopy(kv_list)
        random.shuffle(shuffle_kv_list)
        for (k, v) in shuffle_kv_list:
            _ = a[k]
        a_len = len(a)
        lru_len = len(a._lru_list)
        for i in range(a_len):
            (k, v) = a.popitem()
            msg = (".popitem() returned '%s', shouldn't be in dict?"
                   % str((k, v)))
            self.assertIn((k, v), kv_list, msg)
        msg = ".popitem() all done, len should be 0, got %d" % len(a)
        self.assertEqual(len(a), 0, msg)
        msg = (".popitem() all done, ._lru_list should be [], got '%s'"
               % str(a._lru_list))
        self.assertEqual(a._lru_list, [], msg)

    def testSetdefault(self):
        kv_list = [(1, 'one'), (2, 2), (3, 3.0)]
        a = pyCacheBack(kv_list, max_lru=10)
        ret_val = a.setdefault(100, True)
        msg = ".setdefault(100, True) should return True, got %s" % str(ret_val)
        self.assertEqual(ret_val, True, msg)

    def testUpdate(self):
        kv_list = [(1, 'one'), (2, 2), (3, 3.0)]
        a = pyCacheBack(kv_list, max_lru=10)
        kv_update = [(4, '****'), (5, 'V')]
        a.update(kv_update)
        expected_len = len(kv_list) + len(kv_update)
        msg = (".update() should create length %d, got length %d"
               % (expected_len, len(a)))
        self.assertEqual(expected_len, len(a), msg)
        # check actual contents
        full_list = kv_list + kv_update
        b = pyCacheBack(full_list, max_lru=10)
        msg = ".update() didn't work, got dict '%s'" % str(a)
        self.assertEqual(b, a, msg)

    def testValues(self):
        kv_list = [(1, 'one'), (2, 2), (3, 3.0)]
        a = pyCacheBack(kv_list, max_lru=10)
        expected_values = [kv[1] for kv in kv_list]
        msg = (".values should return '%s', got '%s'"
               % (str(expected_values), str(a.values())))
        self.assertEqual(expected_values, a.values(), msg)


unittest.main()
