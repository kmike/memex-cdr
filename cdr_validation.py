import json
import argparse
import gzip as gz
import datetime

def is_media(doc):
    ''' Checks whether item is media '''
    if 'obj_parent' in doc.keys():
        return True
    else:
        return False

def test_media(doc, _ids, media_fields):
    ''' Checks media fields exist as keys in doc '''    
    parent = doc.get('obj_parent')
    if parent not in _ids:
        return (False, "Missing parent document (field: obj_parent)")
    else:
        return check_required_fields(doc, media_fields)

def test_crawl(doc, crawl_fields):
    return check_required_fields(doc, crawl_fields)

def check_required_fields(doc, crawl_fields):
    ''' Checks crawl fields exist as keys in doc '''
    missing_fields = []
    for field in crawl_fields:
        if field not in doc:
            missing_fields.append(field)
    if missing_fields:
        return (False, "Missing required fields: "+" ".join(missing_fields))
    else:
        return (True, "Passed")

media_fields = ['_id','timestamp','content_type','obj_original_url','obj_parent','obj_stored_url','team','version']
crawl_fields = ['_id','timestamp','content_type','crawler','extracted_metadata','extracted_text','raw_content','team','url','version']

if __name__ == '__main__':

    desc='CDR Validation'
    parser = argparse.ArgumentParser(
        description=desc,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=desc)

    parser.add_argument("--input_file", help="path to the gzip file for testing")    
    parser.add_argument("--result_file", help="path to the gzip file for testing")    
    
    args = parser.parse_args()

    # parsed argument for input/result file
    input_file = args.input_file
    result_file = args.result_file

    # generate input _ids dictionary
    _ids = {}

    # capture start time
    start = datetime.datetime.now()

    # iterate over input file to generate dictionary of _id's
    with gz.open(input_file,'r') as fp:
        for line in fp:
            _id = json.loads(line).get('_id')
            _ids[_id] = ''
        fp.close()
    
    # using _ids dictionary, iterate over input and test fields
    with gz.open(input_file,'r') as fp:
        for line in fp:
            doc = json.loads(line)
            _id = doc.get('_id')
            if is_media(doc):
                result = test_media(doc, _ids, media_fields)
            else:
                result = test_crawl(doc, crawl_fields)
            _ids[_id] = result
    fp.close()
    
    passed = 0
    failed = 0
    
    # write output file
    with open(result_file, 'a') as fp:
        for item in _ids.iteritems():
            if item[1][0]:
                res = 'Passed'
                fp.write(str(item[0]) + ',' + res + '\n')
                passed += 1
            else:
                res = 'Failed'
                reason = item[1][1]
                fp.write(str(item[0]) + ',' + res + ',' + reason + '\n')
                failed +=1
        fp.close()

    end = datetime.datetime.now()
    total_time = end - start
    
    print str(passed) + ' documents passed.'
    print str(failed) + ' documents failed.'
    print 'Took ' + str(total_time)