import os
import sys
import time
from traceback import print_exc

import pyNastran
#from pyNastran.op2.op2 import OP2
from pyNastran.f06.f06 import FatalError
from pyNastran.op2.dev_explicit.op2 import OP2
from pyNastran.op2.dev_explicit.op2_vectorized import OP2_Vectorized as OP2V

# we need to check the memory usage
try:
    if os.name == 'nt':  # windows
        import wmi
        windows_flag = True
    elif os.name in ['posix', 'mac']:  # linux/mac
        import resource
        windows_flag = False
except:
    is_mem = False

def parse_table_names_from_F06(f06Name):
    """gets the op2 names from the f06"""
    infile = open(f06Name,'r')
    marker = 'NAME OF DATA BLOCK WRITTEN ON FORTRAN UNIT IS'
    names = []
    for line in infile:
        if marker in line:
            word = line.replace(marker,'').strip().strip('.')
            names.append(word)

    infile.close()
    return names


def get_failed_files(filename):
    infile = open(filename, 'r')
    lines = infile.readlines()
    infile.close()

    files = []
    for line in lines:
        files.append(line.strip())
    return files


def run_lots_of_files(files ,make_geom=True, write_bdf=False, write_f06=True,
                   delete_f06=True, is_vector=False,
                   debug=True, saveCases=True, skipFiles=[],
                   stopOnFailure=False, nStart=0, nStop=1000000000):
    n = ''
    assert make_geom in [True, False]
    assert write_bdf in [True, False]
    assert write_f06 in [True, False]
    iSubcases = []
    failedCases = []
    nFailed = 0
    nTotal  = 0
    nPassed = 0
    t0 = time.time()
    for (i, op2file) in enumerate(files[nStart:nStop], nStart):  # 149
        baseName = os.path.basename(op2file)
        #if baseName not in skipFiles and not baseName.startswith('acms') and i not in nSkip:
        if baseName not in skipFiles and '#' not in op2file:
            print("%"*80)
            print('file=%s\n' % op2file)
            n = '%s ' %(i)
            sys.stderr.write('%sfile=%s\n' %(n, op2file))
            nTotal += 1
            isPassed = run_op2(op2file, make_geom=make_geom, write_bdf=write_bdf,
                               write_f06=write_f06,
                               is_mag_phase=False,
                               is_vector=is_vector,
                               delete_f06=delete_f06,
                               iSubcases=iSubcases, debug=debug,
                               stopOnFailure=stopOnFailure) # True/False
            if not isPassed:
                sys.stderr.write('**file=%s\n' % op2file)
                failedCases.append(op2file)
                nFailed +=1
            else:
                nPassed +=1
            #sys.exit('end of test...test_op2.py')

    if saveCases:
        f = open('failedCases.in','wb')
        for op2file in failedCases:
            f.write('%s\n' % op2file)
        f.close()

    seconds = time.time()-t0
    minutes = seconds/60.
    print("dt = %s seconds = %s minutes" % (seconds, minutes))

    #op2 = OP2('test_tet10_subcase_1.op2')
    #op2.read_op2()

    msg = '-----done with all models %s/%s=%.2f%%  nFailed=%s-----' %(nPassed,nTotal,100.*nPassed/float(nTotal),nTotal-nPassed)
    print(msg)
    sys.exit(msg)


def run_op2(op2FileName, make_geom=False, write_bdf=False, write_f06=True,
            is_mag_phase=False, is_vector=False, delete_f06=False,
            iSubcases=[], debug=False, stopOnFailure=True):
    assert '.op2' in op2FileName.lower(), 'op2FileName=%s is not an OP2' % op2FileName
    isPassed = False
    if isinstance(iSubcases, basestring):
        if '_' in iSubcases:
            iSubcases = [int(i) for i in iSubcases.split('_')]
        else:
            iSubcases = [int(iSubcases)]
    print('iSubcases =', iSubcases)

    #debug = True
    try:
        if is_vector:
            op2 = OP2V(make_geom=make_geom, debug=debug)
        else:
            op2 = OP2(make_geom=make_geom, debug=debug)

        op2.set_subcases(iSubcases)

        #op2.read_bdf(op2.bdfFileName,includeDir=None,xref=False)
        #op2.write_bdf_as_patran()
        op2.read_op2(op2FileName)
        print("---stats for %s---" % op2FileName)
        #op2.get_op2_stats()
        print(op2.get_op2_stats())
        if write_bdf:
            op2.write_bdf('fem.bdf.out', interspersed=True)
        #tableNamesF06 = parse_table_names_from_F06(op2.f06FileName)
        #tableNamesOP2 = op2.getTableNamesFromOP2()
        if write_f06:
            (model, ext) = os.path.splitext(op2FileName)
            op2.write_f06(model+'.test_op2.f06', is_mag_phase=is_mag_phase)
            if delete_f06:
                try:
                    os.remove(model+'.test_op2.f06')
                except:
                    pass

        #print "subcases = ",op2.subcases

        #assert tableNamesF06==tableNamesOP2,'tableNamesF06=%s tableNamesOP2=%s' %(tableNamesF06,tableNamesOP2)
        #op2.caseControlDeck.sol = op2.sol
        #print op2.caseControlDeck.get_op2_data()
        #print op2.caseControlDeck.get_op2_data()
        isPassed = True
    except KeyboardInterrupt:
        sys.stdout.flush()
        print_exc(file=sys.stdout)
        sys.stderr.write('**file=%s\n' % op2FileName)
        sys.exit('keyboard stop...')
    #except RuntimeError: # the op2 is bad, not my fault
    #    isPassed = True
    #    if stopOnFailure:
    #        raise
    #    else:
    #        isPassed = True

    except IOError: # missing file
        if stopOnFailure:
            raise
    except FatalError:
        if stopOnFailure:
            raise
        isPassed = True
    #except AssertionError:
    #    isPassed = True
    #except RuntimeError: #invalid analysis code
    #    isPassed = True
    except SystemExit:
        #print_exc(file=sys.stdout)
        #sys.exit('stopping on sys.exit')
        raise
    #except NameError:  # variable isnt defined
    #    if stopOnFailure:
    #        raise
    #    else:
    #        isPassed = True
    #except IndexError: # bad bdf
    #    isPassed = True
    except SyntaxError: #Param Parse
        if stopOnFailure:
            raise
        isPassed = True
    except:
        #print e
        if stopOnFailure:
            raise
        else:
            print_exc(file=sys.stdout)
            isPassed = False

    return isPassed


def main():
    from docopt import docopt
    ver = str(pyNastran.__version__)

    msg  = "Usage:\n"
    msg += "test_op2 [-q] [-g] [-w] [-f] [-z] [-t] [-s <sub>] OP2_FILENAME\n"
    msg += "  test_op2 -h | --help\n"
    msg += "  test_op2 -v | --version\n"
    msg += "\n"
    msg += "Tests to see if an OP2 will work with pyNastran %s.\n" % ver
    msg += "\n"
    msg += "Positional Arguments:\n"
    msg += "  OP2_FILENAME         Path to OP2 file\n"
    msg += "\n"
    msg += "Options:\n"
    msg += "  -q, --quiet          Suppresses debug messages (default=False)\n"
    msg += "  -g, --geometry       Reads the OP2 for geometry, which can be written out (default=False)\n"
    msg += "  -w, --write_bdf      Writes the bdf to fem.bdf.out (default=False)\n"
    msg += "  -f, --write_f06      Writes the f06 to fem.f06.out (default=True)\n"
    msg += "  -z, --is_mag_phase   F06 Writer writes Magnitude/Phase instead of\n"
    msg += "                       Real/Imaginary (still stores Real/Imag); (default=False)\n"
    msg += "  -s <sub>, --subcase  Specify a single subcase to parse\n"
    msg += "  -t, --vector         Vectorizes the results (default=False)\n"
    msg += "  -h, --help           Show this help message and exit\n"
    msg += "  -v, --version        Show program's version number and exit\n"

    if len(sys.argv) == 1:
        sys.exit(msg)

    data = docopt(msg, version=ver)
    #print("data", data)

    for key, value in sorted(data.iteritems()):
        print("%-12s = %r" % (key.strip('--'), value))

    if os.path.exists('skippedCards.out'):
        os.remove('skippedCards.out')

    import time
    t0 = time.time()
    run_op2(data['OP2_FILENAME'],
            make_geom     = data['--geometry'],
            write_bdf     = data['--write_bdf'],
            write_f06     = data['--write_f06'],
            is_mag_phase  = data['--is_mag_phase'],
            is_vector     = data['--vector'],
            iSubcases     = data['--subcase'],
            debug         = not(data['--quiet']))
    print("dt = %f" %(time.time() - t0))

if __name__=='__main__':  # op2
    main()