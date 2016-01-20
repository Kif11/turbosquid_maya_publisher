"""certify"""

import random
import unittest
from maya import cmds as cmds
import checkmate
reload(checkmate)


class NGonsTestCase(unittest.TestCase):
    """1. Detect Ngons? How many? Show/Highlight them."""
    def setUp(self):
        cmds.file(force=True, new =True)
        cmds.workspace('checkMateTests', openWorkspace=True)
        cmds.file("scenes/testNgonsAndOverlappingfaces.mb", open=True)

    def tearDown(self):
        cmds.file(force=True, new =True)
        
    def testngons(self):
        result = checkmate.has_ngons()[2]
        expectedresult = [u'polySurface2.f[146]', u'polySurface2.f[511]', u'polySurface2.f[512]']

        print result
        print expectedresult
        self.assertEqual(result, expectedresult)
                
class IsolatedVerticesTestCase(unittest.TestCase):
    """2. Detect Isolated Vertices? How many? Show/Highlight them.
    """
    def setUp(self):
        cmds.file(force=True, new =True)
        cmds.workspace('checkMateTests', openWorkspace=True)
        cmds.file("scenes/testIsolatedVertices.mb", open=True)    
        
    def tearDown(self):
        cmds.file(force=True, new =True)
        
    def testIsolatedVertices(self):
        """has_isolatedvertices should return True, int, [vertex,] if scene contains isolated vertices"""
        result = checkmate.has_isolatedvertices2()
        expectedresult = (True, 20, [u'pCylinder1.vtx[40]', u'pCylinder1.vtx[41]', u'pCylinder1.vtx[42]', u'pCylinder1.vtx[43]', u'pCylinder1.vtx[44]', u'pCylinder1.vtx[45]', u'pCylinder1.vtx[46]', u'pCylinder1.vtx[47]', u'pCylinder1.vtx[48]', u'pCylinder1.vtx[49]', u'pCylinder1.vtx[50]', u'pCylinder1.vtx[51]', u'pCylinder1.vtx[52]', u'pCylinder1.vtx[53]', u'pCylinder1.vtx[54]', u'pCylinder1.vtx[55]', u'pCylinder1.vtx[56]', u'pCylinder1.vtx[57]', u'pCylinder1.vtx[58]', u'pCylinder1.vtx[59]']) # 
        print result
        print expectedresult
        self.assertEqual(result, expectedresult)

                
class CoincidentVerticesTestCase(unittest.TestCase):
    """3. Detect Coincident (overlapping) Vertices? How many? Show/Highlight 
    them.
    """
    def setUp(self):
        cmds.file(force=True, new =True)
        cmds.workspace('checkMateTests', openWorkspace=True)
        cmds.file("scenes/testOverlappingVertices_FlippedNormals.mb", open=True)
   
    def tearDown(self):
        cmds.file(force=True, new =True)
        
    def testcoincidentvertices(self):
        result = checkmate.has_coincidentvertices2()[1]
        expectedresult = 3809
        self.assertEqual(result, expectedresult)

class OverlappingFacesTestCase(unittest.TestCase):
    """4. Detect Overlapping Faces? How many? Show/Highlight them.
    """
    def setUp(self):
        cmds.file(force=True, new =True)
        cmds.workspace('checkMateTests', openWorkspace=True)
        cmds.file("scenes/testOverlappingVertices_FlippedNormals.mb", open=True)
   
    def tearDown(self):
        cmds.file(force=True, new =True)
        
    def testcoincidentvertices(self):
        result = checkmate.has_laminafaces()
        expectedresult = (True, 2, [u'victorian_chair_obj:ch211.f[2461]', u'victorian_chair_obj:ch211.f[3489]'])
        self.assertEqual(result, expectedresult)


class FlippedNormalsTestCase(unittest.TestCase):
    """5. Detect Flipped Normals? How many? Show/Highlight/Correct them.
    """
    def setUp(self):
        cmds.file(force=True, new =True)
        cmds.workspace('checkMateTests', openWorkspace=True)
        cmds.file("scenes/testOverlappingVertices_FlippedNormals.mb", open=True)
   
    def tearDown(self):
        cmds.file(force=True, new =True)
        
    def testcoincidentvertices(self):
        result = checkmate.has_flippednormals()[0]
        expectedresult = True
        self.assertEqual(result, expectedresult)

class MissingUVTestCase(unittest.TestCase):
    """6. Detect missing UV maps? Show associated geometry for missing UVs.
    """
    def setUp(self):
        cmds.file(force=True, new =True)
        cmds.workspace('checkMateTests', openWorkspace=True)
        cmds.file("scenes/testMissingUVmaps.mb", open=True)
   
    def tearDown(self):
        cmds.file(force=True, new =True)
        
    def testcoincidentvertices(self):
        result = checkmate.has_missinguvmaps()[0]
        expectedresult = True
        self.assertEqual(result, expectedresult)

class CoincidenVerticesTestCase(unittest.TestCase):
    """7. Detect overlapping UV faces Show/Highlight them.
    """
    def setUp(self):
        cmds.file(force=True, new =True)
        cmds.workspace('checkMateTests', openWorkspace=True)
        cmds.file("scenes/testCoincidentVertices.ma", open=True)
   
    def tearDown(self):
        cmds.file(force=True, new =True)
        
    def testcoincidentvertices(self):
        result = checkmate.has_coincidentvertices2()
        expectedresult = (True, 2, 1, [u'polySurfaceShape1.vtx[124]', u'polySurfaceShape1.vtx[125]'], [[u'polySurface1']])
        self.assertEqual(result, expectedresult)

class PolyCountTestCase(unittest.TestCase):
    """8. Show proper Poly and Vertex count for entire scene
    """
    def setUp(self):
        cmds.file(force=True, new =True)
        cmds.workspace('checkMateTests', openWorkspace=True)
        cmds.file("scenes/testOverlappingVertices_FlippedNormals.mb", open=True)
   
    def tearDown(self):
        cmds.file(force=True, new =True)
        
    def testwrongpolycount(self):
        result = checkmate.polyvertexcount(faces=10437, vertices=8450)[0]
        expectedresult = False
        self.assertEqual(result, expectedresult)

class FileLinksTestCase(unittest.TestCase):
    """9. File Links - missing texture paths/dlls
    """
    def setUp(self):
        cmds.file(force=True, new =True)
        cmds.workspace('checkMateTests', openWorkspace=True)
        cmds.file("scenes/testFileLinks.mb", open=True)
   
    def tearDown(self):
        cmds.file(force=True, new =True)
        
    def testfilelinks(self):
        """testfile links should return (False, None)"""
        result = checkmate.has_missingfiles()
        expectedresult = (False, 0, {})
        self.assertEqual(result, expectedresult)

class HiddenObjectsTestCase(unittest.TestCase):
    """10.	Hidden objects? Unhide all objects
    """
    def setUp(self):
        cmds.file(force=True, new =True)
        cmds.workspace('checkMateTests', openWorkspace=True)
        cmds.file("scenes/testHiddenObjects.mb", open=True)
   
    def tearDown(self):
        cmds.file(force=True, new =True)

    def testhiddenobjectsemptyscene(self):
        """ testhiddenobjects should return (False, None) on empty scene 
        """
        cmds.file(force=True, new =True)
        result = checkmate.has_hiddenobjects()
        expectedresult = (False, 0, [])
        self.assertEqual(result, expectedresult)

class DefaultNamesTestCase(unittest.TestCase):
    """11.	Show Object Naming (detect default names). 
       Open list window with object names for review.
    """
    def setUp(self):
        cmds.file(force=True, new =True)
        cmds.workspace('checkMateTests', openWorkspace=True)
        cmds.file("scenes/testDefaultNames.mb", open=True)
   
    def tearDown(self):
        cmds.file(force=True, new =True)
        
    def testdefaultnames(self):
        result = checkmate.has_defaultnames()
        expectedresult = (False, 0, {})
        self.assertEqual(result, expectedresult)

class SceneBoundingBoxTestCase(unittest.TestCase):
    """12.	Measure scene bounding box (set units to metric first, 
    then measure in centimeters)
    """
    def setUp(self):
        cmds.file(force=True, new =True)
        cmds.workspace('checkMateTests', openWorkspace=True)
        cmds.file("scenes/testSceneBoundingBox.mb", open=True)
   
    def tearDown(self):
        cmds.file(force=True, new =True)
        
    def testsceneboundingbox(self):
        """testsceneboundingbox should return (units, 
            bbMinX, bbMinY, bbMinZ, 
            bbMaxX, bbMaxY, bbMaxZ, 
            centerX, centerY, centerZ, 
            width, height, depth)"""
        result = checkmate.sceneboundingbox()
        expectedresult = (u'cm', -11.358497820667679, -9.3890409501887184, -1.0000004768371582, 1.5000001192092896, 5.6526868135085016, 11.112967834304836, -4.9292488507291949, -1.8681770683401084, 5.056483678733839, 12.858497939876969, 15.041727763697221, 12.112968311141994) 
        self.assertEqual(result, expectedresult)

    def testsceneboundingboxunits(self):
        """testsceneboundingbox should fail on scenes that are not using cm as linear units"""
        cmds.file("scenes/testSceneBoundingBoxUnitsFeet.mb", open=True)
        # second argument should be a callable object, not the result from invoking that callable objec
        self.assertRaises(checkmate.InvalidLinearUnits, checkmate.sceneboundingbox)
        
    def testsceneboundingboxnogeometry(self):
        """testsceneboundingbox should fail on empty scenes"""
        cmds.file(force=True, new=True)
        # second argument should be a callable object, not the result from invoking that callable objec
        self.assertRaises(checkmate.NoGeometryError, checkmate.sceneboundingbox)
        

class RenderTestCase(unittest.TestCase):
    """13.	Trigger/Generate a Render
    """
    def setUp(self):
        cmds.file(force=True, new =True)
        cmds.workspace('checkMateTests', openWorkspace=True)
        cmds.file("scenes/testRender.mb", open=True)
   
    def tearDown(self):
        cmds.file(force=True, new =True)
        
    def testwrongpolycount(self):
        result = checkmate.render_snapshots()
        expectedresult = '/Users/michiel/Documents/maya/projects/reports/testRender'
        self.assertEqual(result, expectedresult)


class CenteredAtOriginTestCase(unittest.TestCase):
    """14.	Determine if object centered at Origin?
    """
    def setUp(self):
        cmds.file(force=True, new =True)
        cmds.workspace('checkMateTests', openWorkspace=True)
        cmds.file("scenes/testCenteredAtOrigin.mb", open=True)
   
    def tearDown(self):
        cmds.file(force=True, new =True)
        
    def testcenteredatorigin(self):
        result = checkmate.is_centeredatorigin()
        expectedresult = (False, 0, [])
        self.assertEqual(result, expectedresult)


class NonZeroTransformsTestCase(unittest.TestCase):
    """15.	Does the object(s) have transforms applied? 
    If so, have a way to inform the inspector of them and 
    option to zero these out on a per object basis.
    """
    def setUp(self):
        cmds.file(force=True, new =True)
        cmds.workspace('checkMateTests', openWorkspace=True)
        cmds.file("scenes/testNonZeroTransforms.mb", open=True)
   
    def tearDown(self):
        cmds.file(force=True, new =True)
        
    def testwrongpolycount(self):
        result = checkmate.has_nonzerotransforms()
        expectedresult =  (False, 0, [])
        self.assertEqual(result, expectedresult)
        
class MichielIsGek(unittest.TestCase):
    """ Check that the unittest itself works
    """
    def setUp(self):
        pass   
    def tearDown(self):
        pass
    def test1(self):
    	self.assertEqual('foo', 'foo')
#    def test2(self):
#        self.assertNotEqual('foo', 'bar')
#    def test3(self):
#        self.assertAlmostEqual(1.23456789, 1.2345666, 3)
#    def test4(self):
#        self.assertNotAlmostEqual(1.23456789, 1.2345666, 7)
#    def test5(self):
#        self.assertGreater(63456, 99)
#    def test6(self):
#        self.assertGreaterEqual(99, 99)
#    def test7(self):
#        self.assertLess(98, 99)
#    def test8(self):
#        self.assertLessEqual(12, 12)
#    def test9(self):
#        self.assertMultiLineEqual(self, first, second, msg=None)
#    def test10(self):
#        self.assertRegexpMatches('Group1', 'Group.*', msg='Fuck, Yeah!')
#    def test11(self):
#        self.assertNotRegexpMatches('Groups1', 'Group.*', msg='Shit!')
#    def test12(self):
#        self.assertIn('x', ['x', 'y', 'z'], msg=None)
#    def test13(self):
#        self.assertNotIn('a', ['x', 'y', 'z'], msg=None)
#    def test14(self):
#        self.assertItemsEqual([1,2,3], [2,1,3])
#    def test15(self):
#        self.assertSetEqual(set1, set2, msg=None)
#    def test16(self):
#        self.assertDictEqual({'a':1, 'b':2}, {'a':1, 'b':2}, msg=None)
#    def test17(self):
#        self.assertDictContainsSubset({'a':1, 'b':2}, {'a':1, 'b':2, 'c':3}, msg=None)
#    def test18(self):
#        self.assertListEqual([1,2,3], [1,2,3])
#    def test19(self):
#        self.assertTupleEqual((1,2,3), (1,2,3))
#    def test20(self):
#        self.assertSequenceEqual((1,2,3), (1,2,3), msg=None, seq_type=None)
#    def test21(self):
#        self.assertRaises(TypeError, random.shuffle, (1,2,3))
#    def test22(self):
#        self.assertRaisesRegexp(ValueError, 'invalid literal for.*XYZ$', int, 'XYZ')
#    def test23(self):
#        self.assertIsNone(None)
#    def test24(self):
#        self.assertIsNotNone(True)
#    def test25(self):
#        self.assertIs(True, True)
#    def test26(self):
#        self.assertIsNot(True, False)
#    def test27(self):
#        self.assertIsInstance()
#    def test28(self):
#        self.assertNotIsInstance()
#    def test29(self):
#        self.assertFalse(False)
#    def test30(self):
#        self.assertTrue(True)
################################################################################

def testCheckMate():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    loader.sortTestMethodsUsing = None
    suite.addTests(loader.loadTestsFromTestCase(NGonsTestCase))
    suite.addTests(loader.loadTestsFromTestCase(IsolatedVerticesTestCase))
    suite.addTests(loader.loadTestsFromTestCase(CoincidentVerticesTestCase))
    suite.addTests(loader.loadTestsFromTestCase(OverlappingFacesTestCase))
    suite.addTests(loader.loadTestsFromTestCase(FlippedNormalsTestCase))
    suite.addTests(loader.loadTestsFromTestCase(MissingUVTestCase))
    suite.addTests(loader.loadTestsFromTestCase(CoincidenVerticesTestCase))
    suite.addTests(loader.loadTestsFromTestCase(PolyCountTestCase))
    suite.addTests(loader.loadTestsFromTestCase(FileLinksTestCase))
    suite.addTests(loader.loadTestsFromTestCase(HiddenObjectsTestCase))
    suite.addTests(loader.loadTestsFromTestCase(DefaultNamesTestCase))
    suite.addTests(loader.loadTestsFromTestCase(SceneBoundingBoxTestCase))
    suite.addTests(loader.loadTestsFromTestCase(RenderTestCase))
    suite.addTests(loader.loadTestsFromTestCase(CenteredAtOriginTestCase))
    suite.addTests(loader.loadTestsFromTestCase(NonZeroTransformsTestCase))
    #suite.addTests(loader.loadTestsFromTestCase(CheckMateTestCase))
    suite.addTests(loader.loadTestsFromTestCase(MichielIsGek))
    unittest.TextTestRunner(verbosity=2).run(suite)
    
    
    # suite = unittest.TestLoader().loadTestsFromTestCase(CoincidentVerticesTestCase)
    # unittest.TextTestRunner(verbosity=2).run(suite)
    ################################################################################
    #def checkmatesuite():
    #    suite =  unittest.TestSuite()
    #    # suite.addTest(TestSequenceFunctions('test_shuffle')) 
    #    suite.addTest(CoincidentVerticesTestCase('testcoincidentvertices')) 
    #    return suite
        
    #unittest.TextTestRunner(verbosity=2).run(suite)
