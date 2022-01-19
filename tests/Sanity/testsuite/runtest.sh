#!/bin/bash
# vim: dict=/usr/share/beakerlib/dictionary.vim cpt=.,w,b,u,t,i,k
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#   runtest.sh of /tools/dyninst/Sanity/testsuite
#   Description: Basic functionality covering testsuite
#   Author: Michael Petlan <mpetlan@redhat.com>
#           Martin Cermak <mcermak@redhat.com>
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#   Copyright (c) 2013 Red Hat, Inc. All rights reserved.
#
#   This copyrighted material is made available to anyone wishing
#   to use, modify, copy, or redistribute it subject to the terms
#   and conditions of the GNU General Public License version 2.
#
#   This program is distributed in the hope that it will be
#   useful, but WITHOUT ANY WARRANTY; without even the implied
#   warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#   PURPOSE. See the GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public
#   License along with this program; if not, write to the Free
#   Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
#   Boston, MA 02110-1301, USA.
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Include Beaker environment
. /usr/share/beakerlib/beakerlib.sh || exit 1

PACKAGE=${PACKAGE:-dyninst}
TESTDIR=${TESTDIR:-/usr/lib64/dyninst/testsuite}

# Tests known to fail
SKIPLIST=test_thread_2,pc_thread,pc_tls,test_reloc,test_thread_3,\
test_thread_5,test_thread_6,test_thread_8


rlJournalStart
        rlPhaseStartSetup
            rlRun "rpm -q $PACKAGE $PACKAGE-testsuite"

            DYNINSTAPI_RT_LIB=$(rpm -ql $PACKAGE | fgrep libdyninstAPI_RT.so | sort | tail -1)

            LD_LIBRARY_PATH="$LD_LIBRARY_PATH:$TESTDIR"
            LD_LIBRARY_PATH="$LD_LIBRARY_PATH:$(dirname $DYNINSTAPI_RT_LIB)"
            LD_LIBRARY_PATH=${LD_LIBRARY_PATH#:}

            export DYNINSTAPI_RT_LIB
            export LD_LIBRARY_PATH

            rlRun "setsebool allow_execmod on"
            rlRun "setsebool allow_execstack on"
            rlRun "setsebool deny_ptrace off"

            rlRun "pushd $TESTDIR"
        rlPhaseEnd

        rlPhaseStartTest
            rlRun "./runTests -v++ -allmode -allcompilers -allopt -exclude $SKIPLIST"
        rlPhaseEnd

        rlPhaseStartCleanup
            rlRun "popd"
        rlPhaseEnd
rlJournalPrintText
rlJournalEnd
