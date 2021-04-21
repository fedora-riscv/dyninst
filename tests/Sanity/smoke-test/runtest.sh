#!/bin/bash
# vim: dict=/usr/share/beakerlib/dictionary.vim cpt=.,w,b,u,t,i,k
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#   runtest.sh of /tools/dyninst/Sanity/smoke-test
#   Description: The test does basic instrumentation on binaries.
#   Author: Michael Petlan <mpetlan@redhat.com>
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

PACKAGE="dyninst"

rlJournalStart
        rlPhaseStartSetup
                rlRun "TMPD=$(mktemp -d)"
                rlRun "cp -r dynamic dynamic-double static $TMPD/"
                rlRun "pushd $TMPD"
                # load the proper environment - set the variables
                #               When using dyninst, we have to have LD_LIBRARY_PATH set to dyninst's directory
                #               and DYNINSTAPI_RT_LIB should keep the path of libdyninstAPI_RT.so.8.0 shared library.
                #               After having this set properly, an application what uses dyninst, can be compiled and run.

                test -e "/usr/lib64" && BITS="64" || BITS=""
                ARCH=`rlGetPrimaryArch`

                rlAssertRpm $PACKAGE
                DYNINST_ROOT="/usr/lib$BITS/dyninst"
                INCLUDE="-I/usr/include/dyninst"
                LINK="-L/usr/lib$BITS/dyninst -L/usr/lib$BITS/dyninst/lib"
                echo $LD_LIBRARY_PATH | grep "$DYNINST_ROOT"
                if [ $? -ne 0 ]; then
                        export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:$DYNINST_ROOT"
                fi

                # the API runtime library path should be available from rpmquery
                if [ `rpmquery -l $PACKAGE.$ARCH | grep API_RT | wc -l` -eq 1 ]; then
                        # if there's only one file, we may accept that
                        DYNINSTAPI_RT_LIB=`rpmquery -l $PACKAGE.$ARCH | grep API_RT`
                else
                        # sometimes there're many links to the API_RT lib, so we have to choose the proper file
                        for rtlib in `rpmquery -l $PACKAGE.$ARCH | grep API_RT`; do
                                test -L $rtlib || DYNINSTAPI_RT_LIB="$rtlib"
                        done
                fi
                export DYNINSTAPI_RT_LIB
                if [[ ! $LD_LIBRARY_PATH =~ .*dyninst.* ]]; then
                        LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$LD_LIBRARY_PATH/dyninst
                fi
                export LD_LIBRARY_PATH

                # compile both static and dynamic test
                for TC in static dynamic dynamic-double; do
                        cd $TC
                        rlRun "make BITS=\"$BITS\" DYNINST_ROOT=\"$DYNINST_ROOT\" INCLUDE=\"$INCLUDE\" LINK=\"$LINK\"" 0 "Compiling $TC dyninst example."
                        cd ..
                done

                # IMPORTANT: We have to make sure, that some SELinux bools are set right (see dyninst docs)
                #
                # We need:
                #       allow_execmod --> on
                #       allow_execstack --> on
                #       deny_ptrace --> off
                #
                # Note: The bool deny_ptrace is not present in RHEL yet.
                #
                SELINUX_STATUS=`sestatus | grep "SELinux status" | awk '{ print $3; }'`
                if [[ "$SELINUX_STATUS" == "enabled" ]]; then
                        rlLog "SELINUX IS ENABLED."
                        SEBOOL_ALLOW_EXECMOD=`getsebool allow_execmod`
                        SEBOOL_ALLOW_EXECSTACK=`getsebool allow_execstack`
                        SEBOOL_DENY_PTRACE=`getsebool deny_ptrace`
                        if [[ "$SEBOOL_ALLOW_EXECMOD" =~ "> off" ]]; then
                                rlLog "SELINUX: We need to set allow_execmod to on."
                                setsebool allow_execmod on
                                SEBOOL_ALLOW_EXECMOD="off"
                        else
                                rlLog "SELINUX: $SEBOOL_ALLOW_EXECMOD -- already OK."
                        fi
                        if [[ "$SEBOOL_ALLOW_EXECSTACK" =~ "> off" ]]; then
                                rlLog "SELINUX: We need to set allow_execstack to on."
                                setsebool allow_execstack on
                                SEBOOL_ALLOW_EXECSTACK="off"
                        else
                                rlLog "SELINUX: $SEBOOL_ALLOW_EXECSTACK -- already OK."
                        fi
                        if [[ "$SEBOOL_DENY_PTRACE" =~ "> on" ]]; then
                                rlLog "SELINUX: We need to set deny_ptrace to off."
                                setsebool deny_ptrace off
                                SEBOOL_DENY_PTRACE="on"
                        else
                                if [ -z "$SEBOOL_DENY_PTRACE" ]; then
                                        rlLog "SELINUX: deny_ptrace does not exist -- OK."
                                else
                                        rlLog "SELINUX: $SEBOOL_DENY_PTRACE -- already OK."
                                fi
                        fi
                else
                        rlLog "SELINUX IS DISABLED. We do not have to change anything."
                fi

                # Checking for lahf instruction support (bz1134843 workaround)
                ARCH=`uname -i`
                if [[ "$ARCH" =~ "86" ]]; then
                        IS_LAHF_SUPPORTED=`cat /proc/cpuinfo | grep lahf`
                        if [ -z "$IS_LAHF_SUPPORTED" ]; then
                                rlLogWarning "The CPU does not support needed LAHF instruction."
                        fi
                fi
        rlPhaseEnd

        rlPhaseStartTest "Testing static instrumentation"
                cd static
                rlRun "./mutator"
                rlAssertExists "mutated"
                RESULT=`./mutated`
                if [[ "$RESULT" == "MUTATION OK." ]]; then
                        rlPass "Instrumentation PASSed."
                else
                        rlFail "Instrumentation FAILed."
                fi
                cd ..
        rlPhaseEnd

        rlPhaseStartTest "Testing dynamic instrumentation"
                cd dynamic
                ./mutatee 10 &
                PID=$!
                # export DYNINST_DEBUG_STARTUP=1
                # export DYNINST_DEBUG_RTLIB=1
                # export DYNINST_DEBUG_CRASH=1
                # export DYNINST_DEBUG_BPATCH=1
                ./mutator $PID
                sleep 50
                RESULT=`cat RESULT.log`
                if [[ "$RESULT" == "MUTATION OK." ]]; then
                        rlPass "Instrumentation PASSed."
                else
                        rlFail "Instrumentation FAILed."
                fi
                cd ..
        rlPhaseEnd

        rlPhaseStartTest "Testing dynamic double instrumentation"
                # This case needs to have the DYNINSTAPI_RT_LIB variable pointing to a regular file
                #       not to symlink. So it has to be hacked a little
                export DYNINSTAPI_RT_LIB=`readlink -fn $DYNINSTAPI_RT_LIB`

                cd dynamic-double
                ./mutatee 10 &
                PID=$!
                # export DYNINST_DEBUG_STARTUP=1
                # export DYNINST_DEBUG_RTLIB=1
                # export DYNINST_DEBUG_CRASH=1
                # export DYNINST_DEBUG_BPATCH=1
                ./mutator $PID
                sleep 50
                RESULT=`cat RESULT.log`
                if [[ "$RESULT" == "MUTATION OK." ]]; then
                        rlPass "Instrumentation PASSed."
                else
                        rlFail "Instrumentation FAILed."
                fi
                cd ..
        rlPhaseEnd

        rlPhaseStartCleanup
                rlRun "popd"
                rlRun "rm -r $TMPD"

                # restore the SELinux bools, if they were changed
                if [[ "$SEBOOL_ALLOW_EXECMOD" == "off" ]]; then
                        rlLog "Restoring SELinux bool allow_execmod to $SEBOOL_ALLOW_EXECMOD."
                        setsebool allow_execmod $SEBOOL_ALLOW_EXECMOD
                fi
                if [[ "$SEBOOL_ALLOW_EXECSTACK" == "off" ]]; then
                        rlLog "Restoring SELinux bool allow_execstack to $SEBOOL_ALLOW_EXECSTACK."
                        setsebool allow_execstack $SEBOOL_ALLOW_EXECSTACK
                fi
                if [[ "$SEBOOL_DENY_PTRACE" == "on" ]]; then
                        rlLog "Restoring SELinux bool deny_ptrace to $SEBOOL_DENY_PTRACE."
                        setsebool deny_ptrace $SEBOOL_DENY_PTRACE
                fi
        rlPhaseEnd
rlJournalPrintText
rlJournalEnd
