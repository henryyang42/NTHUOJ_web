'''
The MIT License (MIT)

Copyright (c) 2014 NTHUOJ team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

from django.db import models
from users.models import User
from team.models import Team
from datetime import datetime

# Create your models here.

class Problem(models.Model):

    pname = models.CharField(max_length=50, default='')
    owner = models.ForeignKey(User)
    description = models.TextField(blank=True)
    input = models.TextField(blank=True)
    output = models.TextField(blank=True)
    sample_in = models.TextField(blank=True)
    sample_out = models.TextField(blank=True)
    visible = models.BooleanField(default=False)
    error_torrence = models.DecimalField(decimal_places=15, max_digits=17, blank=True)
    other_judge_id = models.IntegerField(blank=True)

    LOCAL = 'L'
    SPECIAL = 'S'
    ERROR_TORRENT = 'E'
    PARTIAL = 'P'
    OTHER = 'O'
    JUDGE_TYPE_CHOICE = (
        (LOCAL, 'Local Judge'),
        (SPECIAL, 'Special Judge'),
        (ERROR_TORRENT, 'Error Torrent'),
        (PARTIAL, 'Partial Judge'),
        (OTHER, 'Use Other Judge'),
    )
    judge_source = models.CharField(max_length=1, choices=JUDGE_TYPE_CHOICE, default=LOCAL)

    def __unicode__(self):
        return self.pname


class Testcase(models.Model):

    problem = models.ForeignKey(Problem)
    description = models.TextField(blank=True)
    time_limit = models.IntegerField(default=1)
    memory_limit = models.IntegerField(default=32)

    def __unicode__(self):
        return str(self.id)


class Submission(models.Model):

    problem = models.ForeignKey(Problem)
    user = models.ForeignKey(User)
    team = models.ForeignKey(Team, blank=True)
    submit_time = models.DateTimeField(default=datetime.now)
    error_msg = models.TextField(blank=True)

    WAIT = 'W'
    JUDGING = 'J'
    ACCEPTED = 'AC'
    NOT_ACCEPTED = 'NA'
    COMPILE_ERROR = 'CE'
    RESTRICTED_FUNCTION = 'RF'
    JUDGE_ERROR = 'JE'
    STATUS_CHOICE = (
        (WAIT, 'Being Judged'),
        (JUDGING, 'Judging'),
        (ACCEPTED, 'All Accepted'),
        (NOT_ACCEPTED, 'Not Accepted'),
        (COMPILE_ERROR, 'Compile Error'),
        (RESTRICTED_FUNCTION, 'Restricted Function'),
        (JUDGE_ERROR, 'Judge Error'),
    )
    status = models.CharField(max_length=2, choices=STATUS_CHOICE, default=WAIT)

    C = 'C'
    CPP = 'CP'
    CPP11 = '11'
    LANGUAGE_CHOICE = (
        (C, 'C'),
        (CPP, 'C++'),
        (CPP11, 'C++11'),
    )
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICE, default=C)

    def __unicode__(self):
        return str(self.id)
    

class SubmissionDetail(models.Model):

    tid = models.ForeignKey(Testcase)
    sid = models.ForeignKey(Submission)
    cpu = models.FloatField(default=0)
    memory = models.IntegerField(default=0)

    AC = 'AC'
    WA = 'WA'
    TLE = 'TLE'
    MLE = 'MLE'
    RE = 'RE'
    PE = 'PE'
    VIRDECT_CHOICE = (
        (AC, 'Accepted'),
        (WA, 'Wrong Answer'),
        (TLE, 'Time Limit Exceeded'),
        (MLE, 'Memory Limit Exceeded'),
        (RE, 'Runtime Error'),
        (PE, 'Presentation Error'),
    )
    virdect = models.CharField(max_length=3, default='')

    class Meta:
        unique_together = (('tid', 'sid'),)

    def __unicode__(self):
        return sid + ' to ' + tid

