#!/usr/bin/python2

import sys
import traceback
import lexor
import syntaxor

def run_test_succ(filepath, test_number):
    """
    Run a test that should succeed silently.
    """
    print test_number, 
    try:
        s = syntaxor.Syntaxor(filepath)
        s.check_syntax()
        print "succeeded"
    except syntaxor.SyntaxError as se:
        print "failed"
        print se.message

def run_test_fail(filepath, test_number, line_number):
    """
    Run a test that should fail with an exception.
    """
    try:
        s = syntaxor.Syntaxor(filepath)
        s.check_syntax()
    except syntaxor.SyntaxError as se:
        _, _, tbo = sys.exc_info()
        exc_lineno =  traceback.extract_tb(tbo)[-1:][0][1]
        print test_number,
        if (exc_lineno == line_number):
            print "succeeded"
            #print se.message
        else:
            print "failed at", exc_lineno , "instead of", line_number
            print se.message
            print

if (__name__ == '__main__'):
    run_test_succ("../tests/syntaxor/000cor.java", "000")
    run_test_fail("../tests/syntaxor/001err.java", "001", 36)
    run_test_fail("../tests/syntaxor/002err.java", "002", 52)
    run_test_fail("../tests/syntaxor/003err.java", "003", 56)
    run_test_fail("../tests/syntaxor/004err.java", "004", 69)
    run_test_fail("../tests/syntaxor/005err.java", "005", 73)
    run_test_fail("../tests/syntaxor/006err.java", "006", 96)
    run_test_fail("../tests/syntaxor/007err.java", "007", 132)
    run_test_fail("../tests/syntaxor/008err.java", "008", 155)
    run_test_fail("../tests/syntaxor/009err.java", "009", 176)
    run_test_fail("../tests/syntaxor/010err.java", "010", 185)
    run_test_fail("../tests/syntaxor/011err.java", "011", 199)
    run_test_fail("../tests/syntaxor/012err.java", "012", 207)
#   run_test_fail("../tests/syntaxor/013err.java", "013", 221)
#   run_test_fail("../tests/syntaxor/014err.java", "014", 232)
#   run_test_fail("../tests/syntaxor/015err.java", "015", 247)
#   run_test_fail("../tests/syntaxor/016err.java", "016", 258)
#   run_test_fail("../tests/syntaxor/017err.java", "017", 272)
    run_test_fail("../tests/syntaxor/018err.java", "018", 280)
    run_test_fail("../tests/syntaxor/019err.java", "019", 290)
    run_test_fail("../tests/syntaxor/020err.java", "020", 305)
    run_test_fail("../tests/syntaxor/021err.java", "021", 316)
    run_test_fail("../tests/syntaxor/022err.java", "022", 330)
    run_test_fail("../tests/syntaxor/023err.java", "023", 334)
    run_test_fail("../tests/syntaxor/024err.java", "024", 334) #354
    run_test_fail("../tests/syntaxor/025err.java", "025", 389)
    run_test_fail("../tests/syntaxor/026err.java", "026", 403)
    run_test_fail("../tests/syntaxor/027err.java", "027", 434)
    run_test_fail("../tests/syntaxor/028err.java", "028", 444)
    run_test_fail("../tests/syntaxor/029err.java", "029", 453)
    run_test_fail("../tests/syntaxor/030err.java", "030", 468)
    run_test_fail("../tests/syntaxor/031err.java", "031", 491)
    run_test_fail("../tests/syntaxor/032err.java", "032", 96) #524
    run_test_fail("../tests/syntaxor/033err.java", "033", 542)
    run_test_fail("../tests/syntaxor/034err.java", "034", 546)
    run_test_fail("../tests/syntaxor/035err.java", "035", 570)
    run_test_fail("../tests/syntaxor/036err.java", "036", 574)
    run_test_fail("../tests/syntaxor/037err.java", "037", 601)
    run_test_fail("../tests/syntaxor/038err.java", "038", 605)
    run_test_fail("../tests/syntaxor/039err.java", "039", 692)
    run_test_fail("../tests/syntaxor/040err.java", "040", 692) #707
    run_test_fail("../tests/syntaxor/041err.java", "041", 722)
    run_test_fail("../tests/syntaxor/042err.java", "042", 766) #736
    run_test_fail("../tests/syntaxor/043err.java", "043", 770) #741
    run_test_fail("../tests/syntaxor/044err.java", "044", 746) #748
    run_test_fail("../tests/syntaxor/045err.java", "045", 542) #759
    run_test_fail("../tests/syntaxor/046err.java", "046", 692) #778
    run_test_fail("../tests/syntaxor/047err.java", "047", 746) #782
    run_test_fail("../tests/syntaxor/048err.java", "048", 766) #800
    run_test_fail("../tests/syntaxor/049err.java", "049", 770) #804
    run_test_fail("../tests/syntaxor/050err.java", "050", 788) #837
    run_test_fail("../tests/syntaxor/051err.java", "051", 792) #841
    run_test_fail("../tests/syntaxor/052err.java", "052", 948) #845
    run_test_fail("../tests/syntaxor/053err.java", "053", 746) #862
    run_test_fail("../tests/syntaxor/054err.java", "054", 199) #866
    run_test_fail("../tests/syntaxor/055err.java", "055", 746) #870
#   run_test_fail("../tests/syntaxor/056err.java", "056", 874)
#   run_test_fail("../tests/syntaxor/057err.java", "057", 888)
#   run_test_fail("../tests/syntaxor/058err.java", "058", 892)
#   run_test_fail("../tests/syntaxor/059err.java", "059", 896)
#   run_test_fail("../tests/syntaxor/060err.java", "060", 913)
#   run_test_fail("../tests/syntaxor/061err.java", "061", 917)
#   run_test_fail("../tests/syntaxor/062err.java", "062", 928)
#   run_test_fail("../tests/syntaxor/063err.java", "063", 945)
#   run_test_fail("../tests/syntaxor/064err.java", "064", 949)
