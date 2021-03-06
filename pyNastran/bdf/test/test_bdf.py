# pylint: disable=W0612,C0103
from __future__ import (nested_scopes, generators, division, absolute_import,
                        print_function, unicode_literals)
from six import iteritems
import os
import sys
import numpy
from numpy import array
import warnings
warnings.simplefilter('always')

numpy.seterr(all='raise')
import traceback

from pyNastran.op2.op2 import OP2
from pyNastran.utils import print_bad_path
from pyNastran.bdf.bdf import BDF, NastranMatrix
from pyNastran.bdf.bdf_replacer import BDFReplacer
from pyNastran.bdf.test.compare_card_content import compare_card_content

import pyNastran.bdf.test
test_path = pyNastran.bdf.test.__path__[0]
#print "test_path = ",test_path


def run_all_files_in_folder(folder, debug=False, xref=True, check=True,
                            punch=False, cid=None, nastran=''):
    print("folder = %s" % folder)
    filenames = os.listdir(folder)
    run_lots_of_files(filenames, debug=debug, xref=xref, check=check,
                      punch=punch, cid=cid, nastran=nastran)


def run_lots_of_files(filenames, folder='', debug=False, xref=True, check=True,
                      punch=False, cid=None, nastran=''):
    filenames = list(set(filenames))
    filenames.sort()

    #debug = True
    filenames2 = []
    diffCards = []
    for filename in filenames:
        if (filename.endswith('.bdf') or filename.endswith('.dat') or
            filename.endswith('.nas') or filename.endswith('.nas')):
            filenames2.append(filename)

    failedFiles = []
    n = 1
    for filename in filenames2:
        absFilename = os.path.abspath(os.path.join(folder, filename))
        if folder != '':
            print("filename = %s" % absFilename)
        isPassed = False
        try:
            (fem1, fem2, diffCards2) = run_bdf(folder, filename, debug=debug,
                                               xref=xref, check=check, punch=punch,
                                               cid=cid, isFolder=True, dynamic_vars={},
                                               nastran=nastran)
            del fem1
            del fem2
            diffCards += diffCards
            isPassed = True
        except KeyboardInterrupt:
            sys.exit('KeyboardInterrupt...sys.exit()')
        except IOError:
            pass
        #except RuntimeError:  # only temporarily uncomment this when running lots of tests
            #pass
        #except AttributeError:  # only temporarily uncomment this when running lots of tests
            #pass
        #except SyntaxError:  # only temporarily uncomment this when running lots of tests
            #pass
        except SystemExit:
            sys.exit('sys.exit...')
        except:
            traceback.print_exc(file=sys.stdout)
            #raise
        print('-' * 80)

        if isPassed:
            sys.stderr.write('%i %s' % (n, absFilename))
            n += 1
        else:
            sys.stderr.write('*' + absFilename)
            failedFiles.append(absFilename)
        sys.stderr.write('\n')

    print('*' * 80)
    try:
        print("diffCards1 = %s" % list(set(diffCards)))
    except TypeError:
        #print "type(diffCards) =",type(diffCards)
        print("diffCards2 = %s" % diffCards)
    return failedFiles


def memory_usage_psutil():
    # return the memory usage in MB
    try:
        import psutil
    except ImportError:
        return '???'
    process = psutil.Process(os.getpid())
    mem = process.get_memory_info()[0] / float(2 ** 20)
    return mem

def get_double_from_precision(precision):
    if precision == 'single':
        double = False
    elif precision == 'double':
        precision = True
    return double

def run_bdf(folder, bdfFilename, debug=False, xref=True, check=True, punch=False,
            cid=None, meshForm='combined', isFolder=False, print_stats=False,
            sum_load=False, size=8, precision='single',
            reject=False, nastran='', dynamic_vars={}):
    bdfModel = str(bdfFilename)
    print("bdfModel = %s" % bdfModel)
    if isFolder:
        bdfModel = os.path.join(test_path, folder, bdfFilename)

    assert os.path.exists(bdfModel), '%r doesnt exist' % bdfModel

    if reject:
        fem1 = BDFReplacer(bdfModel + '.rej', debug=debug, log=None)
    else:
        fem1 = BDF(debug=debug, log=None)
    if dynamic_vars:
        fem1.set_dynamic_syntax(dynamic_vars)

    fem1.log.info('starting fem1')
    sys.stdout.flush()
    fem2 = None
    diffCards = []
    try:
        (outModel) = run_fem1(fem1, bdfModel, meshForm, xref, punch, sum_load, size, precision, cid)
        (fem2)     = run_fem2(      bdfModel, outModel, xref, punch, sum_load, size, precision, reject, debug=debug, log=None)
        (diffCards) = compare(fem1, fem2, xref=xref, check=check, print_stats=print_stats)
        nastran = 'nastran scr=yes bat=no old=no '
        if nastran and 0:
            dirname = os.path.dirname(bdfModel)
            basename = os.path.basename(bdfModel).split('.')[0]

            op2_model = os.path.join(dirname, 'out_%s.op2' % basename)

            cwd = os.getcwd()
            bdf_model2 = os.path.join(cwd, 'out_%s.bdf' % basename)
            op2_model2 = os.path.join(cwd, 'out_%s.op2' % basename)
            f06_model2 = os.path.join(cwd, 'out_%s.f06' % basename)
            print(bdf_model2)
            if os.path.exists(bdf_model2):
                os.remove(bdf_model2)

            # make sure we're writing an OP2
            bdf = BDF()
            bdf.read_bdf(outModel)
            if 'POST' in bdf.params:
                post = bdf.params['POST']
                #print('post = %s' % post)
                post.update_values(value1=-1)
                #print('post = %s' % post)
            else:
                card = ['PARAM', 'POST', -1]
                bdf.add_card(card, 'PARAM', is_list=True)
            bdf.write_bdf(bdf_model2)

            #os.rename(outModel, outModel2)
            os.system(nastran + bdf_model2)
            op2 = OP2()
            if not os.path.exists(op2_model2):
                raise RuntimeError('%s failed' % f06_model2)
            op2.read_op2(op2_model2)
            print(op2.get_op2_stats())

    except KeyboardInterrupt:
        sys.exit('KeyboardInterrupt...sys.exit()')
    except IOError:
        pass
    #except AttributeError:  # only temporarily uncomment this when running lots of tests
        #pass
    #except SyntaxError:  # only temporarily uncomment this when running lots of tests
        #pass
    #except AssertionError:  # only temporarily uncomment this when running lots of tests
        #pass
    except SystemExit:
        sys.exit('sys.exit...')
    except:
        #exc_type, exc_value, exc_traceback = sys.exc_info()
        #print "\n"
        traceback.print_exc(file=sys.stdout)
        #print msg
        print("-" * 80)
        raise

    print("-" * 80)
    return (fem1, fem2, diffCards)


def run_fem1(fem1, bdfModel, meshForm, xref, punch, sum_load, size, precision, cid):
    assert os.path.exists(bdfModel), print_bad_path(bdfModel)
    try:
        if '.pch' in bdfModel:
            fem1.read_bdf(bdfModel, xref=False, punch=True)
        else:
            fem1.read_bdf(bdfModel, xref=xref, punch=punch)
    except:
        print("failed reading %r" % bdfModel)
        raise
    #fem1.sumForces()

    double = get_double_from_precision(precision)
    if fem1._auto_reject:
        outModel = bdfModel + '.rej'
    else:
        outModel = bdfModel + '_out'
        if cid is not None and xref:
            fem1.resolveGrids(cid=cid)
        if meshForm == 'combined':
            fem1.write_bdf(outModel, interspersed=False, size=size, is_double=double)
        elif meshForm == 'separate':
            fem1.write_bdf(outModel, interspersed=False, size=size, is_double=double)
        else:
            msg = "meshForm=%r; allowedForms=['combined','separate']" % meshForm
            raise NotImplementedError(msg)
        #fem1.writeAsCTRIA3(outModel)
    return (outModel)


def run_fem2(bdfModel, outModel, xref, punch,
             sum_load, size, precision,
             reject, debug=False, log=None):
    assert os.path.exists(bdfModel), bdfModel
    assert os.path.exists(outModel), outModel

    double = get_double_from_precision(precision)
    if reject:
        fem2 = BDFReplacer(bdfModel + '.rej', debug=debug, log=None)
    else:
        fem2 = BDF(debug=debug, log=None)
    fem2.log.info('starting fem2')
    sys.stdout.flush()
    try:
        fem2.read_bdf(outModel, xref=xref, punch=punch)
    except:
        print("failed reading %r" % outModel)
        raise

    outModel2 = bdfModel + '_out2'

    if sum_load:
        p0 = array([0., 0., 0.])
        subcases = fem2.caseControlDeck.get_subcase_list()
        for isubcase in subcases[1:]:  # drop isubcase = 0
            loadcase_id, options = fem2.caseControlDeck.get_subcase_parameter(isubcase, 'LOAD')
            F, M = fem2.sum_forces_moments(p0, loadcase_id, include_grav=False)
            print('  isubcase=%i F=%s M=%s' % (isubcase, F, M))
    fem2.write_bdf(outModel2, interspersed=False, size=size, is_double=double)
    #fem2.writeAsCTRIA3(outModel2)
    os.remove(outModel2)
    return (fem2)


def divide(value1, value2):
    if value1 == value2:  # good for 0/0
        return 1.0
    else:
        try:
            v = value1 / float(value2)
        except ZeroDivisionError:
            v = 0.
    return v


def compare_card_count(fem1, fem2, print_stats=False):
    cards1 = fem1.card_count
    cards2 = fem2.card_count
    for key in cards1:
        if key != key.upper():
            raise RuntimeError('Proper capitalization wasnt determined')
    if print_stats:
        print(fem1.get_bdf_stats())
    else:
        fem1.get_bdf_stats()
    return compute_ints(cards1, cards2, fem1)


def compute_ints(cards1, cards2, fem1):
    cardKeys1 = set(cards1.keys())
    cardKeys2 = set(cards2.keys())
    allKeys = cardKeys1.union(cardKeys2)
    diffKeys1 = list(allKeys.difference(cardKeys1))
    diffKeys2 = list(allKeys.difference(cardKeys2))

    listKeys1 = list(cardKeys1)
    listKeys2 = list(cardKeys2)
    if diffKeys1 or diffKeys2:
        print(' diffKeys1=%s diffKeys2=%s' % (diffKeys1, diffKeys2))

    for key in sorted(allKeys):
        msg = ''
        if key in listKeys1:
            value1 = cards1[key]
        else:
            value1 = 0

        if key in listKeys2:
            value2 = cards2[key]
        else:
            value2 = 0

        diff = abs(value1 - value2)
        star = ' '
        if diff and key not in ['INCLUDE']:
            star = '*'
        if key not in fem1.cards_to_read:
            star = '-'

        factor1 = divide(value1, value2)
        factor2 = divide(value2, value1)
        factorMsg = ''
        if factor1 != factor2:
            factorMsg = 'diff=%s factor1=%g factor2=%g' % (diff, factor1,
                                                          factor2)
        msg += '  %skey=%-7s value1=%-7s value2=%-7s' % (star, key, value1,
                                                       value2) + factorMsg
        msg = msg.rstrip()
        print(msg)
    #return listKeys1 + listKeys2
    return diffKeys1 + diffKeys2


def compute(cards1, cards2):
    cardKeys1 = set(cards1.keys())
    cardKeys2 = set(cards2.keys())
    allKeys = cardKeys1.union(cardKeys2)
    diffKeys1 = list(allKeys.difference(cardKeys1))
    diffKeys2 = list(allKeys.difference(cardKeys2))

    listKeys1 = list(cardKeys1)
    listKeys2 = list(cardKeys2)
    msg = ''
    if diffKeys1 or diffKeys2:
        msg = 'diffKeys1=%s diffKeys2=%s' % (diffKeys1, diffKeys2)

    for key in sorted(allKeys):
        msg = ''
        if key in listKeys1:
            value1 = cards1[key]
        else:
            value2 = 0

        if key in listKeys2:
            value2 = cards2[key]
        else:
            value2 = 0

        if key == 'INCLUDE':
            msg += '    key=%-7s value1=%-7s value2=%-7s' % (key,
                                                             value1, value2)
        else:
            msg += '   *key=%-7s value1=%-7s value2=%-7s' % (key,
                                                             value1, value2)
        msg = msg.rstrip()
        print(msg)


def get_element_stats(fem1, fem2):
    """verifies that the various element methods work"""
    for (key, loads) in sorted(iteritems(fem1.loads)):
        for load in loads:
            try:
                allLoads = load.getLoads()
                if not isinstance(allLoads, list):
                    raise TypeError('allLoads should return a list...%s'
                                    % (type(allLoads)))
            except:
                print("load statistics not available - load.type=%s "
                      "load.sid=%s" % (load.type, load.sid))
                raise

    fem1._verify_bdf()

    mass, cg, I = fem1.mass_properties(reference_point=None, sym_axis=None)
    print("mass =", mass)
    print("cg   =", cg)
    print("I    =", I)

   # for (key, e) in sorted(iteritems(fem1.elements)):
   #     try:
   #         e._verify()
   #         #if isinstance(e, RigidElement):
   #             #pass
   #         #elif isinstance(e, DamperElement):
   #             #b = e.B()
   #         #elif isinstance(e, SpringElement):
   #             #L = e.Length()
   #             #K = e.K()
   #             #pid = e.Pid()
   #         #elif isinstance(e, PointElement):
   #             #m = e.Mass()
   #             #c = e.Centroid()
   #     except Exception as exp:
   #         #print("e=\n",str(e))
   #         print("*stats - e.type=%s eid=%s  element=\n%s"
   #             % (e.type, e.eid, str(exp.args)))
   #     except AssertionError as exp:
   #         print("e=\n",str(e))
   #         #print("*stats - e.type=%s eid=%s  element=\n%s"
   #             #% (e.type, e.eid, str(exp.args)))
   #
   #         #raise


def get_matrix_stats(fem1, fem2):
    for (key, dmig) in sorted(iteritems(fem1.dmigs)):
        try:
            if isinstance(dmig, NastranMatrix):
                dmig.getMatrix()
            else:
                print("statistics not available - "
                      "matrix.type=%s matrix.name=%s" % (dmig.type, dmig.name))
        except:
            print("*stats - matrix.type=%s name=%s  matrix=\n%s"
                % (dmig.type, dmig.name, str(dmig)))
            raise


def compare(fem1, fem2, xref=True, check=True, print_stats=True):
    diffCards = compare_card_count(fem1, fem2, print_stats=print_stats)
    if xref and check:
        get_element_stats(fem1, fem2)
        get_matrix_stats(fem1, fem2)
    compare_card_content(fem1, fem2)
    #compare_params(fem1,fem2)
    #print_points(fem1,fem2)
    return diffCards


def compare_params(fem1, fem2):
    compute(fem1.params, fem2.params)


def print_points(fem1, fem2):
    for (nid, n1) in sorted(iteritems(fem1.nodes)):
        print("%s   xyz=%s  n1=%s  n2=%s" % (nid, n1.xyz, n1.Position(True),
                                            fem2.Node(nid).Position()))
        break
    coord = fem1.Coord(5)
    print(coord)
    #print coord.Stats()


def main():
    from docopt import docopt
    msg  = "Usage:\n"
    msg += "  test_bdf [-q] [-x] [-p] [-c] [-L] BDF_FILENAME\n" #
    msg += "  test_bdf [-q] [-x] [-p] [-c] [-L] [-d] BDF_FILENAME\n" #
    msg += "  test_bdf [-q] [-x] [-p] [-c] [-L] [-l] BDF_FILENAME\n" #
    msg += "  test_bdf [-q] [-p] [-r] BDF_FILENAME\n" #
    #msg += "  test_bdf [-q] [-p] [-o [<VAR=VAL>]...] BDF_FILENAME\n" #
    msg += '  test_bdf -h | --help\n'
    msg += '  test_bdf -v | --version\n'
    msg += '\n'

    msg += "Positional Arguments:\n"
    msg += "  BDF_FILENAME   path to BDF/DAT/NAS file\n"
    msg += '\n'

    msg += 'Options:\n'
    msg += '  -q, --quiet    prints debug messages (default=False)\n'
    msg += '  -x, --xref     disables cross-referencing and checks of the BDF.\n'
    msg += '                  (default=False -> on)\n'
    msg += '  -p, --punch    disables reading the executive and case control decks in the BDF\n'
    msg += '                 (default=False -> reads entire deck)\n'
    msg += '  -c, --check    disables BDF checks.  Checks run the methods on \n'
    msg += '                 every element/property to test them.  May fails if a \n'
    msg += '                 card is fully not supported (default=False)\n'
    msg += '  -l, --large    writes the BDF in large field, single precision format (default=False)\n'
    msg += '  -d, --double   writes the BDF in large field, double precision format (default=False)\n'
    msg += '  -L, --loads    sums the forces/moments on the model for the different subcases (default=False)\n'
    msg += '  -r, --reject   rejects all cards with the appropriate values applied (default=False)\n'
    #msg += '  -o <VAR_VAL>, --openmdao <VAR_VAL>   rejects all cards with the appropriate values applied;\n'
    #msg += '                 Uses the OpenMDAO %var syntax to replace it with value.\n'
    #msg += '                 So test_bdf -r var1=val1 var2=val2\n'

    msg += '  -h, --help     show this help message and exit\n'
    msg += "  -v, --version  show program's version number and exit\n"

    if len(sys.argv) == 1:
        sys.exit(msg)

    ver = str(pyNastran.__version__)
    data = docopt(msg, version=ver)

    for key, value in sorted(iteritems(data)):
        print("%-12s = %r" % (key.strip('--'), value))

    import time
    t0 = time.time()

    if data['--large']:
        size = 16
        if data['--double']:
            precision = 'double'
        else:
            precision = 'single'
    else:
        size = 8
        precision = 'single'

    run_bdf('.', data['BDF_FILENAME'],
                 debug=not(data['--quiet']),
                 xref =not(data['--xref' ]),
                 check=not(data['--check']),
                 punch=data['--punch'],
                 reject=data['--reject'],
                 size=size,
                 precision=precision,
                 sum_load=data['--loads']
    )
    print("total time:  %.2f sec" % (time.time() - t0))


if __name__ == '__main__':  # pragma: no cover
    main()
