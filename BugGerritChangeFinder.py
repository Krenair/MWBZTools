import os, json, re, sys, time

if len(sys.argv) >= 2:
    queryString = ' '.join(sys.argv[1:])
else:
    queryString = 'status:merged'

regex = re.compile(r'(\(|)[bB]ug(:|) ([0-9]{0,})(\)|)')

def queryGerrit(queryString, resumeKey = None):
    cmd = 'ssh -p 29418 gerrit.wikimedia.org gerrit query --commit-message --format json ' + queryString
    rowCount = 0

    if resumeKey != None:
        cmd += ' resume_sortkey:' + resumeKey

    for line in os.popen(cmd).read().splitlines():
        data = json.loads(line)
        if 'rowCount' in data:
            print str(data['rowCount']) + ' rows in ' + str(data['runTimeMilliseconds']) + 'ms'
            rowCount = data['rowCount']
        elif 'sortKey' in data and 'commitMessage' in data:
            lastResumeKey = data['sortKey']
            m = regex.match(data['commitMessage'])
            if m and m.group(3) != '':
                print m.group(3), data['url']
        else:
            print "Uh oh!"
            print data
            sys.exit(0)

    if rowCount == 5000:
        print 'Resuming with ' + lastResumeKey
        time.sleep(3)
        queryGerrit(queryString, resumeKey = lastResumeKey)

queryGerrit(queryString)


