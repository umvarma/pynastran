from __future__ import unicode_literals
#import codecs
import io

encoding_list = [ 'ascii', 'big5', 'big5hkscs', 'cp037', 'cp424', 'cp437', 'cp500',
    'cp737', 'cp775', 'cp850', 'cp852', 'cp855', 'cp856', 'cp857', 'cp860', 'cp861',
    'cp862', 'cp863', 'cp864', 'cp865', 'cp866', 'cp869', 'cp874', 'cp875', 'cp932',
    'cp949', 'cp950', 'cp1006', 'cp1026', 'cp1140', 'cp1250', 'cp1251', 'cp1252',
    'cp1253', 'cp1254', 'cp1255', 'cp1256', 'cp1257', 'cp1258', 'euc_jp', 'euc_jis_2004',
    'euc_jisx0213', 'euc_kr', 'gb2312', 'gbk', 'gb18030', 'hz', 'iso2022_jp',
    'iso2022_jp_1', 'iso2022_jp_2', 'iso2022_jp_2004', 'iso2022_jp_3', 'iso2022_jp_ext',
    'iso2022_kr', 'latin_1', 'iso8859_2', 'iso8859_3', 'iso8859_4', 'iso8859_5',
    'iso8859_6', 'iso8859_7', 'iso8859_8', 'iso8859_9', 'iso8859_10', 'iso8859_13',
    'iso8859_14', 'iso8859_15', 'johab', 'koi8_r', 'koi8_u', 'mac_cyrillic',
    'mac_greek', 'mac_iceland', 'mac_latin2', 'mac_roman', 'mac_turkish',
    'ptcp154', 'shift_jis', 'shift_jis_2004', 'shift_jisx0213', 'utf_16',
    'utf_16_be', 'utf_16_le', 'utf_7', 'utf_8' ]

def run(bdf_filename, encoding='utf-8'):
    print('working on %r' % bdf_filename)
    #f2 = codecs.open(bdf_filename, 'w', encoding=encoding, errors='strict')

    try:
        with io.open(bdf_filename, 'r', encoding=encoding, errors='strict') as f:
            for line in f:
                print(line.rstrip())
    except:
        print('----------------------------------------------------------')
        for encodingi in encoding_list:
            try:
                with io.open(bdf_filename, 'r', encoding=encodingi, errors='strict') as f:
                    for line in f:
                        print(line.rstrip())
                        pass
                print('*passed %s' % codeci)
            except:
                #print('*********failed %s' % codeci)
                pass


#run('file.bdf', 'latin-1')
run('file.bdf', 'utf-8')

run('file2.bdf', 'latin-1')