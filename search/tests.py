"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from search.utils import parse_query
from django.conf import settings

SEARCH_SETTINGS = settings.SEARCH_SETTINGS

class SearchTest(TestCase):
    def test_parse_query(self):
        """
        Tests query parses.
        """
        # Define test shortcut
        def test(query, t2, p2, l2):
            t1, p1, l1 = parse_query(query)
            # t1, p1 and l1 should be (under sort) be equal to t2, p2 and l2
            self.assertEqual(
                (sorted(t1), sorted(p1), sorted(l1)),
                (sorted(t2), sorted(p2), sorted(l2))
            )

        # Create shortnames for special symbols
        dsymb = SEARCH_SETTINGS['syntax']['DELIM']
        psymb = SEARCH_SETTINGS['syntax']['PERSON']
        tsymb = SEARCH_SETTINGS['syntax']['TAG']
        lsymb = SEARCH_SETTINGS['syntax']['LITERAL']
        esymb = SEARCH_SETTINGS['syntax']['ESCAPE']

        # Test person tokens
        test("%sTerm" % (psymb,),
                [], [("Term", (0,5))], [])
        test("%sTe%srm" % (psymb,tsymb),
                [], [("Te%srm" % (tsymb, ), (0,6))], [])
        test("%sTe%srm" % (psymb,lsymb),
                [], [("Te%srm" % (lsymb, ), (0,6))], [])
        test("%sTerm%s%sTerm2" % (psymb, dsymb, psymb),
                [], [("Term", (0,5)), ("Term2", (6,12))], [])
        test("%sTerm2%s%sTerm" % (psymb, dsymb, psymb),
                [], [("Term", (7,12)), ("Term2", (0,6))], [])
        test(psymb, [], [], [])
        # Test tag tokens
        test("%sTerm" % (tsymb,),
                [("Term",(0,5))], [], [])
        test("%sTe%srm" % (tsymb,psymb),
                [("Te%srm" % (psymb, ), (0,6))], [], [])
        test("%sTe%srm" % (tsymb,lsymb),
                [("Te%srm" % (lsymb, ), (0,6))], [], [])
        test("%sTerm%s%sTerm2" % (tsymb, dsymb, tsymb),
                [("Term", (0,5)), ("Term2", (6,12))], [], [])
        test("%sTerm2%s%sTerm" % (tsymb, dsymb, tsymb),
                [("Term", (7,12)), ("Term2", (0,6))], [], [])
        test(tsymb, [], [], [])
        # Test single literal tokens
        test("Term",
                [], [], [("Term", (0,4))])
        test("Te%srm" % (tsymb, ),
                [], [], [("Te%srm" % (tsymb, ), (0,5))],)
        test("Te%srm" % (psymb, ),
                [], [], [("Te%srm" % (psymb, ), (0,5))],)
        test("Te%srm" % (lsymb, ),
                [], [], [("Te%srm" % (lsymb, ), (0,5))],)
        test("Term%sTerm2" % (dsymb,),
                [], [], [("Term",(0,4)), ("Term2",(5,10))])
        test("Term2%sTerm" % (dsymb,),
                [], [], [("Term",(6,10)), ("Term2",(0,5))])
        # Test long literal tokens
        test("%sTerm%s" % (lsymb, lsymb),
                [], [], [("Term",(0,6))])
        test("%sTerm" % (lsymb,),
                [], [], [("Term",(0,5))])
        test("%sTe%srm%s" % (lsymb,psymb, lsymb),
                [], [], [("Te%srm" % (psymb, ), (0,7))])
        test("%sTe%srm%s" % (lsymb,tsymb, lsymb),
                [], [], [("Te%srm" % (tsymb, ), (0,7))])
        test("%sTerm%s%s%sTerm2%s" % (lsymb, lsymb, dsymb, lsymb, lsymb),
                [], [], [("Term", (0,6)), ("Term2", (7,14))])
        test("%sTerm2%s%s%sTerm%s" % (lsymb, lsymb, dsymb, lsymb, lsymb),
                [], [], [("Term", (8,14)), ("Term2", (0,7))])
        test("%sTerm Term2%s%s%sTerm3%s" % (lsymb, lsymb, dsymb, lsymb, lsymb),
                [], [], [("Term Term2", (0,12)), ("Term3", (13,20))])
        test(lsymb+lsymb, [], [], [])
        # Test mix of persons and tags
        test("%sTerm%s%sTerm2" % (psymb, dsymb, tsymb),
                [("Term2", (6,12))], [("Term", (0,5))], [])
        test("%sTerm%s%sTerm2" % (tsymb, dsymb, psymb),
                [("Term", (0,5))], [("Term2", (6,12))], [])
        # Test mix of persons and single literals
        test("%sTerm%sTerm2" % (psymb, dsymb),
                [], [("Term", (0,5))], [("Term2", (6,11))])
        test("Term%s%sTerm2" % (dsymb, psymb),
                [], [("Term2", (5,11))], [("Term", (0,4))])
        # Test mix of persons and long literals
        test("%sTerm%s%sTerm2 Term3%s" % (psymb, dsymb, lsymb, lsymb),
                [], [("Term", (0,5))], [("Term2 Term3", (6,19))])
        test("%sTerm2 Term3%s%s%sTerm" % (lsymb, lsymb, dsymb, psymb),
                [], [("Term", (14,19))], [("Term2 Term3", (0,13))])
        # Test mix of tags and single literals
        test("%sTerm%sTerm2" % (tsymb, dsymb),
                [("Term", (0,5))], [], [("Term2", (6,11))])
        test("Term%s%sTerm2" % (dsymb, tsymb),
                [("Term2", (5,11))], [], [("Term", (0,4))])
        # Test mix of tags and long literals
        test("%sTerm%s%sTerm2 Term3%s" % (tsymb, dsymb, lsymb, lsymb),
                [("Term", (0,5))], [], [("Term2 Term3", (6,19))])
        test("%sTerm2 Term3%s%s%sTerm" % (lsymb, lsymb, dsymb, tsymb),
                [("Term", (14,19))], [], [("Term2 Term3", (0,13))])
        # Test mix of single literals and long literals
        test("Term%s%sTerm2 Term3%s" % (dsymb, lsymb, lsymb),
                [], [], [("Term", (0,4)), ("Term2 Term3", (5,18))])
        test("%sTerm2 Term3%s%sTerm" % (lsymb, lsymb, dsymb),
                [], [], [("Term2 Term3", (0,13)), ("Term", (14,18))])
        # Test escape of tag symbol
        test("%s%sTerm" % (esymb, tsymb),
                [], [], [("%sTerm" % (tsymb), (1,6))])
        test("%s%sTerm%s" % (esymb, tsymb, dsymb),
                [], [], [("%sTerm" % (tsymb), (1,6))])
        # Test escape of person symbol
        test("%s%sTerm" % (esymb, psymb),
                [], [], [("%sTerm" % (psymb), (1,6))])
        test("%s%sTerm%s" % (esymb, psymb, dsymb),
                [], [], [("%sTerm" % (psymb), (1,6))])
        # Test escape of literal symbol
        test("%s%sTerm" % (esymb, lsymb),
                [], [], [("%sTerm" % (lsymb), (1,6))])
        test("%s%sTerm%s" % (esymb, lsymb, dsymb),
                [], [], [("%sTerm" % (lsymb), (1,6))])
        test("%s%sTerm%sTerm2" % (esymb, lsymb, dsymb),
                [], [], [("%sTerm" % (lsymb), (1,6)), ("Term2", (7,12))])
