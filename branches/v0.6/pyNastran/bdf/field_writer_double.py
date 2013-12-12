import sys

def print_scientific_double(value):
    """
    Prints a value in 16-character scientific double precision.

    Scientific Notation:                   5.0E+1
    Double Precision Scientific Notation:  5.0D+1
    """
    if value < 0:
        format = "%16.9e"
    else:
        format = "%16.10e"

    svalue = format % value
    #left, right = svalue.split('e')
    #field = '%16s' % ('%sd%s' % (left.strip('0'), right))
    field = svalue.replace('e', 'd')

    assert len(field) == 16, ('value=%r field=%r is not 16 characters '
                              'long, its %s' % (value, field, len(field)))
    return field


def print_field_double(value):
    """
    Prints a single 16-character width field

    :param value:   the value to print
    :returns field: an 16-character string
    """
    if isinstance(value, int):
        field = "%16s" % value
    elif isinstance(value, float):
        field = print_scientific_double(value)
    elif value is None:
        field = "                "
    else:
        field = "%16s" % value
    if len(field) != 16:
        msg = 'field=|%s| is not 16 characters long...rawValue=|%s|' % (field, value)
        raise RuntimeError(msg)
    return field


def print_card_double(fields):
    """
    Prints a nastran-style card with 16-character width fields.

    :param fields: all the fields in the BDF card (no blanks)

    .. note:: A large field format follows the  8-16-16-16-16-8 = 80
     format where the first 8 is the card name or blank (continuation).
     The last 8-character field indicates an optional continuation,
     but because it's a left-justified unneccessary field,
     print_card doesnt use it.
    """
    nFieldsMain = len(fields) - 1  # chop off the card name
    nBDFLines = nFieldsMain // 8
    if nFieldsMain % 8 != 0:
        nBDFLines += 1
    nExtraFields = 8 * nBDFLines -  nFieldsMain
    if nExtraFields:
        fields += [None] * nExtraFields

    try:
        out = '%-8s' % (fields[0]+'*')
    except:
        print("ERROR!  fields=%s" % fields)
        sys.stdout.flush()
        raise

    for i in xrange(1, len(fields)):
        field = fields[i]
        try:
            out += print_field_double(field)
        except:
            print("bad fields = %s" % fields)
            raise
        if i % 4 == 0:  # allow 1+4 fields per line
            out = out.rstrip(' ')
            if out[-1] == '\n':  # empty line
                out += '*'
            out += '\n*       '
    out = out.rstrip(' \n*') + '\n'  # removes blank lines at the end of cards
    return out

if __name__ == '__main__':
    field = print_scientific_double(-55.1040257079)
    field = print_scientific_double(-55.1040257078872)
    field = print_scientific_double(-3.76948125497534)
