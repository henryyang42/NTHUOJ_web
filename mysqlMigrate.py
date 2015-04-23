# -*- coding: utf-8 -*-
"""
execfile('mysqlMigrate.py')
"""
import MySQLdb
import sys, datetime
import HTMLParser, bs4
from users.models import *
from status.models import *
from contest.models import *
from group.models import *
from problem.models import *

DEBUG = 0

def html2pure(html):
    text = ''
    soup = bs4.BeautifulSoup(html)
    ps = soup.find_all('p')
    for p in ps:
        text += str(p.get_text().encode('utf8'))

    ps = soup.find_all('pre')
    for p in ps:
        text += str(p.get_text().encode('utf8'))
    if text:
        return text
    return html

def purify(problem):
    problem.pname = HTMLParser.HTMLParser().unescape(problem.pname)
    problem.description = HTMLParser.HTMLParser().unescape(problem.description)
    problem.input = HTMLParser.HTMLParser().unescape(problem.input)
    problem.output = HTMLParser.HTMLParser().unescape(problem.output)
    problem.sample_in = HTMLParser.HTMLParser().unescape(problem.sample_in)
    problem.sample_out = HTMLParser.HTMLParser().unescape(problem.sample_out)
    problem.sample_in = html2pure(problem.sample_in)
    problem.sample_out = html2pure(problem.sample_out)
    problem.save()


def get_user(username):
    user = None
    try:
        user = User.objects.get(username=username)
    except:
        user = User.objects.get(username='boss')

    return user


def get_problem(pid):
    problem = Problem()
    try:
        problem = Problem.objects.get(id=pid)
    except:
        problem = Problem()

    return problem


def drawProgressBar(label, current, max_len, fail=0):
    barLen = 20
    current += 1
    percent = float(current) / max_len
    sys.stdout.write("\r")
    progress = ""
    for i in range(barLen):
        if i < int(barLen * percent):
            progress += "="
        else:
            progress += " "
    sys.stdout.write("%s: [ %s ] (%d/%d) %.2f%%  (%d failure)" % (label, progress, current, max_len, percent * 100, fail))
    sys.stdout.flush()


def migrate_users(cur):
    """
|-----------------------------------------------------------------------------------------|
| Field          | Type              | Null | Key  | Default            | EXTRA           |
|-----------------------------------------------------------------------------------------|
| id             | varchar(16)       | NO   | PRI  |                    |                 |
| password       | char(41)          | YES  |      |                    |                 |
| real_name      | varchar(16)       | YES  |      |                    |                 |
| email          | varchar(64)       | NO   |      |                    |                 |
| user_level     | int(11)           | NO   |      |                    |                 |
| nickname       | varchar(50)       | YES  |      |                    |                 |
|-----------------------------------------------------------------------------------------|
    """

    cur.execute("SELECT * FROM users")
    data = cur.fetchall()
    data_len = len(data)

    data_len = len(data)
    fail = 0

    for i, d in enumerate(data):
        drawProgressBar('users', i, data_len, fail)
        try:
            user = User.objects.create(
                    username=d[0],
                    password=d[1],
                    email=d[3],
                )
        except:
            fail += 1

    print
    print 'Migrate users finished'


def migrate_coowner(cur):
    """
|-----------------------------------------------------------------------------------------|
| Field          | Type              | Null | Key  | Default            | EXTRA           |
|-----------------------------------------------------------------------------------------|
| id             | varchar(30)       | NO   | PRI  |                    |                 |
|-----------------------------------------------------------------------------------------|
    """

    cur.execute("SELECT * FROM coowner")
    data = cur.fetchall()
    if DEBUG:
        data = data[:100]
    data_len = len(data)
    fail = 0

    for i, d in enumerate(data):
        drawProgressBar('coowner', i, data_len, fail)
        user = User.objects.get(username=d[0])
        user.user_level = User.SUB_JUDGE
        user.save()

    print
    print 'Migrate coowner finished'


def migrate_judge(cur):
    """
|-----------------------------------------------------------------------------------------|
| Field          | Type              | Null | Key  | Default            | EXTRA           |
|-----------------------------------------------------------------------------------------|
| id             | varchar(30)       | NO   | PRI  |                    |                 |
|-----------------------------------------------------------------------------------------|
    """

    cur.execute("SELECT * FROM judge")
    data = cur.fetchall()
    if DEBUG:
        data = data[:100]
    data_len = len(data)
    fail = 0

    for i, d in enumerate(data):
        drawProgressBar('judge', i, data_len, fail)
        user = User.objects.get(username=d[0])
        user.user_level = User.JUDGE
        user.save()

    print
    print 'Migrate judge finished'


def migrate_admin(cur):
    """
|-----------------------------------------------------------------------------------------|
| Field          | Type              | Null | Key  | Default            | EXTRA           |
|-----------------------------------------------------------------------------------------|
| id             | varchar(16)       | NO   | PRI  |                    |                 |
|-----------------------------------------------------------------------------------------|
    """

    cur.execute("SELECT * FROM admin")
    data = cur.fetchall()
    if DEBUG:
        data = data[:100]
    data_len = len(data)
    fail = 0

    for i, d in enumerate(data):
        drawProgressBar('admin', i, data_len, fail)
        user = User.objects.get(username=d[0])
        user.user_level = User.ADMIN
        user.save()

    print
    print 'Migrate admin finished'

"""User and it's userlevel are defined above"""


def migrate_problems(cur):
    """
|-----------------------------------------------------------------------------------------|
| Field          | Type              | Null | Key  | Default            | EXTRA           |
|-----------------------------------------------------------------------------------------|
| pid            | int(11)           | NO   | PRI  | 0                  |                 |
| pname          | varchar(64)       | YES  |      |                    |                 |
| cid            | int(11)           | YES  |      |                    |                 |
| memory_limit   | int(11)           | YES  |      |                    |                 |
| time_limit     | int(11)           | YES  |      |                    |                 |
| description    | text              | YES  |      |                    |                 |
| input          | text              | YES  |      |                    |                 |
| output         | text              | YES  |      |                    |                 |
| sample_input   | text              | YES  |      |                    |                 |
| sample_output  | text              | YES  |      |                    |                 |
| problemsetter  | varchar(32)       | YES  |      |                    |                 |
| anonymous      | char(8)           | YES  |      | 0                  |                 |
| special_judge  | char(4)           | NO   |      |                    |                 |
| gid            | int(11)           | YES  | MUL  |                    |                 |
| tid            | int(11)           | NO   |      | 0                  |                 |
| parent_pid     | int(11)           | NO   |      | 0                  |                 |
| visible        | varchar(10)       | NO   |      | unchecked          |                 |
|-----------------------------------------------------------------------------------------|
    """

    cur.execute("SELECT * FROM problems")
    data = cur.fetchall()
    if DEBUG:
        data = data[:100]
    data_len = len(data)
    fail = 0

    for i, d in enumerate(data):
        drawProgressBar('problems', i, data_len, fail)
        pname = d[1]
        description = d[5]
        input = d[5]
        output= d[6]
        sample_in = d[8]
        sample_out = d[9]
        if not pname:
            pname = ''
        if not description:
            description = ''
        if not input:
            input = ''
        if not input:
            input = ''
        if not output:
            output = ''
        if not sample_in:
            sample_in = ''
        if not sample_out:
            sample_out = ''
        if len(pname) > 50:
            pname = pname[0:50]

        try:
            judge_source = Problem.LOCAL if d[14]==0 else Problem.OTHER
            judge_type = Problem.NORMAL
            if d[14]==1:
                judge_type = Problem.ICPC_JUDGE
            elif d[14] == 2:
                judge_type = Problem.POJ_JUDGE
            elif d[14] ==3:
                judge_type = Problem.UVA_JUDGE
            problem = Problem.objects.create(
                    id=d[0],
                    pname=pname,
                    owner=get_user(d[10]),
                    description=description,
                    input=input,
                    output=output,
                    sample_in=sample_in,
                    sample_out=sample_out,
                    visible=(d[16] == 'checked'),
                    judge_source=judge_source,
                    judge_type=judge_type
                )
        except:
            fail += 1



    print
    print 'Migrate problems finished with %d failure' % fail


def migrate_testcases(cur):
    """
|-----------------------------------------------------------------------------------------|
| Field          | Type              | Null | Key  | Default            | EXTRA           |
|-----------------------------------------------------------------------------------------|
| tid            | int(11)           | NO   | PRI  |                    | auto_increment  |
| pid            | int(11)           | NO   | MUL  |                    |                 |
| timeLimit      | int(11)           | NO   |      |                    |                 |
| memoryLimit    | int(11)           | NO   |      |                    |                 |
|-----------------------------------------------------------------------------------------|
    """

    cur.execute("SELECT * FROM testcases")
    data = cur.fetchall()
    if DEBUG:
        data = data[:100]
    data_len = len(data)
    fail = 0

    for i, d in enumerate(data):
        drawProgressBar('testcases', i, data_len, fail)
        if not Problem.objects.filter(id=d[1]):
            fail += 1
            continue
        try:
            testcase = Testcase.objects.create(
                id=d[0],
                problem=Problem.objects.get(id=d[1]),
                time_limit=d[2],
                memory_limit=d[3]
            )
        except:
            fail += 1

    print
    print 'Migrate testcases finished with %d failure' % fail

""" problems info are define above """


def migrate_contest(cur):
    """
|-----------------------------------------------------------------------------------------|
| Field          | Type              | Null | Key  | Default            | EXTRA           |
|-----------------------------------------------------------------------------------------|
| cid            | int(11)           | NO   | PRI  |                    | auto_increment  |
| start_time     | datetime          | YES  | MUL  |                    |                 |
| end_time       | datetime          | YES  | MUL  |                    |                 |
| cname          | varchar(64)       | YES  |      |                    |                 |
| freeze         | int(11)           | NO   |      | 0                  |                 |
| result         | enum('yes','no')  | NO   |      | yes                |                 |
| owner          | varchar(16)       | NO   | MUL  |                    |                 |
|-----------------------------------------------------------------------------------------|
    """

    cur.execute("SELECT * FROM contest")
    data = cur.fetchall()
    if DEBUG:
        data = data[:100]
    data_len = len(data)
    fail = 0

    for i, d in enumerate(data):
        drawProgressBar('contest', i, data_len, fail)
        cname=d[3]
        if not cname:
            cname = ''
        if len(cname) > 50:
            cname = cname[0:50]

        contest = Contest.objects.create(
                id=d[0],
                cname=cname,
                owner=get_user(d[6]),
                freeze_time=d[4]
            )
        if d[1]:
            contest.start_time = d[1]
        if d[2]:
            contest.end_time = d[2]
        contest.save()

    print
    print 'Migrate contest finished with %d failure' % fail


def migrate_contest_coowner(cur):
    """
|-----------------------------------------------------------------------------------------|
| Field          | Type              | Null | Key  | Default            | EXTRA           |
|-----------------------------------------------------------------------------------------|
| id             | varchar(30)       | YES  |      |                    |                 |
| cid            | int(13)           | YES  |      |                    |                 |
|-----------------------------------------------------------------------------------------|
    """

    cur.execute("SELECT * FROM contest_coowner")
    data = cur.fetchall()
    if DEBUG:
        data = data[:100]
    data_len = len(data)
    fail = 0

    for i, d in enumerate(data):
        drawProgressBar('contest_coowner', i, data_len, fail)

        try:
            contest = Contest.objects.get(id=d[1])
            contest.coowner.add(get_user(d[0]))
        except:
            fail += 1

    print
    print 'Migrate contest_coowner finished with %d failure' % fail


def migrate_pid_cid(cur):
    """
|-----------------------------------------------------------------------------------------|
| Field          | Type              | Null | Key  | Default            | EXTRA           |
|-----------------------------------------------------------------------------------------|
| pid            | int(11)           | NO   |      |                    |                 |
| cid            | int(11)           | NO   |      |                    |                 |
|-----------------------------------------------------------------------------------------|
    """

    cur.execute("SELECT * FROM pid_cid")
    data = cur.fetchall()
    if DEBUG:
        data = data[:100]
    data_len = len(data)
    fail = 0

    for i, d in enumerate(data):
        drawProgressBar('pid_cid', i, data_len, fail)
        contest = Contest.objects.filter(id=d[1])
        if not Problem.objects.filter(id=d[0]):
            fail += 1
            continue
        if contest:
            contest = contest[0]
            problem = Problem.objects.get(id=d[0])
            contest.problem.add(problem)
    print
    print 'Migrate pid_cid finished with %d failure' % fail


def migrate_clarification(cur):
    """
|-----------------------------------------------------------------------------------------|
| Field          | Type              | Null | Key  | Default            | EXTRA           |
|-----------------------------------------------------------------------------------------|
| clid           | int(11) unsigned  | NO   | PRI  |                    | auto_increment  |
| uid            | varchar(12)       | NO   |      |                    |                 |
| pid            | int(11) unsigned  | NO   |      |                    |                 |
| cid            | int(11) unsigned  | NO   |      |                    |                 |
| msg            | longtext          | NO   |      |                    |                 |
| time           | timestamp         | NO   |      | CURRENT_TIMESTAMP  |                 |
| solved         | tinyint(1)        | NO   |      | 0                  |                 |
| reply          | text              | YES  |      |                    |                 |
| title          | varchar(100)      | NO   |      |                    |                 |
|-----------------------------------------------------------------------------------------|
    """

    cur.execute("SELECT * FROM clarification")
    data = cur.fetchall()
    if DEBUG:
        data = data[:100]
    data_len = len(data)
    fail = 0

    for i, d in enumerate(data):
        drawProgressBar('clarification', i, data_len, fail)
        contest = None
        problem = None
        reply = d[7]
        content = d[8]+d[4]
        try:
            problem = Problem.objects.get(id=d[2])
            contest = Contest.objects.get(id=d[3])
        except:
            fail += 1
            continue
        if not reply:
            reply = ''
        if len(content) > 500:
            content = content[0:500]
        c = Clarification.objects.create(
                id=d[0],
                problem=problem,
                contest=contest,
                content=content,
                reply=reply,
                asker=get_user(d[1]),
                ask_time=d[5]
            )
    print
    print 'Migrate clarification finished with %d failure' % fail

""" contest things are defined above """

def migrate_submissions(cur):
    """
|-----------------------------------------------------------------------------------------|
| Field          | Type              | Null | Key  | Default            | EXTRA           |
|-----------------------------------------------------------------------------------------|
| sid            | int(11)           | NO   | PRI  |                    | auto_increment  |
| date           | datetime          | YES  |      |                    |                 |
| uid            | varchar(16)       | YES  | MUL  |                    |                 |
| pid            | int(11)           | NO   | MUL  |                    |                 |
| status         | varchar(30)       | YES  |      |                    |                 |
| cpu            | decimal(6,3)      | YES  |      |                    |                 |
| memory         | int(11)           | YES  |      |                    |                 |
| source         | char(10)          | NO   |      |                    |                 |
| err_msg        | blob              | YES  |      |                    |                 |
| SSID           | int(11)           | NO   |      | 0                  |                 |
|-----------------------------------------------------------------------------------------|
    """

    cur.execute("SELECT * FROM submissions")
    data = cur.fetchall()
    if DEBUG:
        data = data[:100]
    data_len = len(data)
    fail = 0

    for i, d in enumerate(data):
        drawProgressBar('submissions', i, data_len, fail)
        problem = None
        try:
            problem = Problem.objects.get(id=d[3])
        except:
            fail += 1
            continue
        user = get_user(d[2])
        submit_time = d[1]
        error_msg = d[8]
        status = d[4]
        language = d[7].upper()

        if not submit_time:
            submit_time = datetime.datetime.now()
        if not error_msg:
            err_msg = ''
        if not status:
            status = '0/1'
        try:
            if eval(status):
                status = Submission.ACCEPTED
            else:
                status = Submission.NOT_ACCEPTED
        except:
            status = Submission.JUDGE_ERROR

        submission = Submission.objects.create(
            id=d[0],
            user=user,
            submit_time=submit_time,
            problem=problem,
            error_msg=err_msg,
            status=status,
            language=language
        )

    print
    print 'Migrate submissions finished with %d failure' % fail


def migrate_submission_result_detail(cur):
    """
|-----------------------------------------------------------------------------------------|
| Field          | Type              | Null | Key  | Default            | EXTRA           |
|-----------------------------------------------------------------------------------------|
| sid            | int(11)           | NO   | MUL  |                    |                 |
| pid            | int(11)           | NO   | MUL  |                    |                 |
| tid            | int(11)           | NO   |      |                    |                 |
| verdict        | varchar(30)       | NO   |      |                    |                 |
| runTime        | float             | NO   |      |                    |                 |
| memoryAmt      | int(11)           | NO   |      |                    |                 |
| errMsg         | text              | NO   |      |                    |                 |
|-----------------------------------------------------------------------------------------|
    """

    cur.execute("SELECT * FROM submission_result_detail")
    data = cur.fetchall()
    if DEBUG:
        data = data[:100]
    data_len = len(data)
    fail = 0

    for i, d in enumerate(data):
        drawProgressBar('submission_result_detail', i, data_len, fail)
        tid = None
        sid = None
        cpu = d[4]
        memory = d[5]
        verdict = d[3]
        errmsg = d[6]
        g = 0
        for V in SubmissionDetail.VERDICT_CHOICE:
            abbr = V[0]
            full = V[1].upper()
            if verdict.upper() == full:
                verdict = abbr
                g = 1
                break
        if not g:
            verdict = SubmissionDetail.WA
        try:
            tid = Testcase.objects.get(id=d[2])
            sid = Submission.objects.get(id=d[0])
            SubmissionDetail.objects.create(
                tid=tid,
                sid=sid,
                cpu=cpu,
                memory=memory,
                verdict=verdict
            )

            if errmsg:
                sid.err_msg = errmsg
                print errmsg
                sid.save()
        except:
            fail += 1
    print
    print 'Migrate submission_result_detail finished with %d failure' % fail

""" submission things are defined above """

def migrate_mapping(cur):
    """
|-----------------------------------------------------------------------------------------|
| Field          | Type              | Null | Key  | Default            | EXTRA           |
|-----------------------------------------------------------------------------------------|
| pid            | int(11)           | NO   | PRI  |                    |                 |
| realid         | char(16)          | NO   |      |                    |                 |
|-----------------------------------------------------------------------------------------|
    """

    cur.execute("SELECT * FROM mapping")
    data = cur.fetchall()
    if DEBUG:
        data = data[:100]
    data_len = len(data)
    fail = 0

    for i, d in enumerate(data):
        drawProgressBar('mapping', i, data_len, fail)
        try:
            problem = Problem.objects.get(id=d[0])
            problem.other_judge_id = d[1]
            problem.save()
        except:
            fail += 1
    print
    print 'Migrate mapping finished'


def migrate_icpc_sid(cur):
    """
|-----------------------------------------------------------------------------------------|
| Field          | Type              | Null | Key  | Default            | EXTRA           |
|-----------------------------------------------------------------------------------------|
| ssid           | int(11)           | NO   |      |                    |                 |
| icpc_sid       | bigint(20)        | NO   |      |                    |                 |
|-----------------------------------------------------------------------------------------|
    """

    cur.execute("SELECT * FROM icpc_sid")
    data = cur.fetchone()
    if DEBUG:
        data = data[:100]
    data_len = len(data)
    fail = 0

    for i, d in enumerate(data):
        drawProgressBar('icpc_sid', i, data_len, fail)
        try:
            submission = Submission.objects.get(id=d[0])
            submission.other_judge_sid = d[1]
            submission.save()
        except:
            fail += 1

    print
    print 'Migrate icpc_sid finished'




def migrate_uva_sid(cur):
    """
|-----------------------------------------------------------------------------------------|
| Field          | Type              | Null | Key  | Default            | EXTRA           |
|-----------------------------------------------------------------------------------------|
| ssid           | int(11)           | NO   | PRI  |                    |                 |
| uva_sid        | bigint(20)        | NO   | MUL  |                    |                 |
|-----------------------------------------------------------------------------------------|
    """

    cur.execute("SELECT * FROM uva_sid")
    data = cur.fetchall()
    if DEBUG:
        data = data[:100]
    data_len = len(data)
    fail = 0

    for i, d in enumerate(data):
        drawProgressBar('uva_sid', i, data_len, fail)
        try:
            submission = Submission.objects.get(id=d[0])
            submission.other_judge_sid = d[1]
            submission.save()
        except:
            fail += 1

    print
    print 'Migrate uva_sid finished'


def problem_html_cleanup():
    problems = Problem.objects.all()
    p_len = problems.count()
    fail = 0

    for i in range(p_len):
        p = problems[i]
        drawProgressBar('purify_problem', i, p_len, fail)
        try:
            purify(p)
        except:
            fail += 1
            print 'Purify %s GG' % str(p)

def problem_passrate():
    problems = Problem.objects.all()
    p_len = problems.count()
    fail = 0

    for i in range(p_len):
        p = problems[i]
        drawProgressBar('purify_problem', i, p_len, fail)
        try:
            p.total_submission = Submission.objects.filter(problem=p).count()
            p.ac_count = Submission.objects.filter(problem=p, status=Submission.ACCEPTED).count()
            p.save()
        except:
            fail += 1
            print 'Problem_passrate %s GG' % str(p)



migrate_dependency = [
    migrate_users,
    migrate_coowner,
    migrate_judge,
    migrate_admin,
    migrate_problems,
    migrate_testcases,
    migrate_contest,
    migrate_contest_coowner,
    migrate_pid_cid,
    migrate_clarification,
    migrate_submissions,
    migrate_submission_result_detail,
    migrate_mapping,
    migrate_icpc_sid,
    migrate_uva_sid
]

funcs = [problem_html_cleanup, problem_passrate]


con = None
DEBUG = int(raw_input('DEBUG(1:on, 0:off):'))
sql_user = raw_input('sql user: ')
sql_pwd = raw_input('sql pwd:  ')
sql_db = raw_input('sql db:   ')

try:
    con = MySQLdb.connect('localhost', sql_user, sql_pwd, sql_db)
    # prepare a cursor object using cursor() method
    cur = con.cursor()

    # execute SQL query using execute() method.
    cur.execute("SELECT VERSION()")
    ver = cur.fetchone()
    print "Database version : %s " % ver

    for f in migrate_dependency:
        f(cur)
    for f in funcs:
        f()


except MySQLdb.Error, e:
    print "Error %d: %s" % (e.args[0],e.args[1])
    sys.exit(1)

finally:
    if con:
        con.close()

print '\n\nMirgration finished!\nMirgration finished!\nMirgration finished!'
