import os, json, re, sys, time

if len(sys.argv) >= 2:
    queryString = ' '.join(sys.argv[1:])
else:
    queryString = 'status:merged'

regex = re.compile(r'(\(|)[bB]ug(:|) ([0-9]{0,})(\)|)')
bugIds = []

def queryGerrit(queryString, bugIds, resumeKey = None):
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
                bugIds.append(m.group(3))
        else:
            print "Uh oh!"
            print data
            sys.exit(0)

    if rowCount == 5000:
        print 'Resuming with ' + lastResumeKey
        #print 'Last Bugzilla search URL was: https://bugzilla.wikimedia.org/buglist.cgi?query_format=advanced&bug_status=UNCONFIRMED&bug_status=NEW&bug_status=ASSIGNED&bug_status=REOPENED&bug_id=' + '&bug_id='.join(bugIds)
        time.sleep(3)
        queryGerrit(queryString, bugIds, resumeKey = lastResumeKey)

queryGerrit(queryString, bugIds)

def chunks(l, n): # http://stackoverflow.com/a/1751478
    return [l[i:i+n] for i in range(0, len(l), n)]

print 'Final Bugzilla search URL(s) were:'
for chunk in chunks(bugIds, 100):
    print 'https://bugzilla.wikimedia.org/buglist.cgi?query_format=advanced&bug_status=UNCONFIRMED&bug_status=NEW&bug_status=ASSIGNED&bug_status=REOPENED&bug_id=' + '&bug_id='.join(chunk)
