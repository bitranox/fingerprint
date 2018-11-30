fingerprint
=================
Monitoring Registry and File Changes in Windows - forensic analytics for windows registry and files

"fingerprint" records the state of a windows system, in terms of files and registry.
Such fingerprints can be compared to find all changed data.
The data can be narrowed with procmon logfiles, in order to see which process caused the changes.
Procmon Logfiles can be filtered to show only events for changed Files or Registry Entries.
This makes it much more easy to find the cause of system changes.

All fingerprints are stored in csv, Excel compatible format, for convenient filtering, sorting, etc.
You can also use third party tools like "Meld", "FC", "diff" to compare fingerprints.

You can use fingerprint in batchfiles to automatically filter out events of Your interest - its batch friendly

sources are included, but You just might use the fp.exe file created with pyinstaller from `Releases <https://github.com/bitranox/fingerprint/releases>`_

Usage Scenarios
---------------
Monitor honeypots, monitor system changes, find "hidden" registry entries or files, like expiration of demo versions,
analyze virus activities, analyze if Your privacy was compromised. You will be able to find every Spy Program, Worm,
or hack into Your system, unless the program ONLY resides in memory and does not alter anything - but that is very unlikely

Usage
-----
check the `Wiki <https://github.com/bitranox/fingerprint/wiki>`_

Installation
------------
no installation required, just use the fp.exe file from `Releases <https://github.com/bitranox/fingerprint/releases>`_

Requirements
---------------
following Packets will be installed / needed (when using .py files):

click

python-registry

pyinstaller (if You want to create Your own .exe Files)

Acknowledgement
---------------
Inspired by Regshot, InstallWatch Pro, SpyMe Tools, RegDiff, WhatChanged, RegFromApp, Uninstaller Pro and others

Contribute
----------
I would love for you to fork and send me pull request for this project.
Please contribute.

License
-------
This software is licensed under the `MIT license <http://en.wikipedia.org/wiki/MIT_License>`_

See `License file <https://github.com/bitranox/fingerprint/blob/master/LICENSE>`_

SAMPLE SESSION
--------------
Lets make s walk-through by example. Lets assume we have a software with "Trial Period" and the Software stops working after the trial period.

After uninstalling and reinstalling the software, it still shows "Trial Period ended" - so this software is not completely uninstalling, leaving some files or registry entries behind.

all programs are started from the commandline. Use fp.exe [command] --help for showing the help with all commandline parameters.

STEP1: create fingerprint of drive c:\\ on a clean system:
 fp.exe files --fp_dir=c:\\ --f_output=c:\\fp\\fp1.csv

STEP2: create fingerprint after installing, running and uninstalling the software:
 fp.exe files --fp_dir=c:\\ --f_output=c:\\fp\\fp2.csv

STEP3: create diff files. In that files all changes between clean and uninstalled state are stored:
 fp.exe files_diff --fp1=c:\\fp\\fp1.csv --fp2=c:\\fp\\fp2.csv --f_output=c:\\fp\\fp1-fp2.csv

STEP4: reinstall the software
 use procmon to log all system activity and save the log as csv file "c:\\fp\\reinstall_procmon.csv"

Filtering Procmon Logfiles and registry fingerprints will be explained soon, since it is in refractoring stage now.
 If You are inpatient You might use the old Version 1.6 (from releases) .



REMARKS
-------

You might record quite some noise - there is no filter to sort it out at the moment. On the other hand - I would hide exactly in the noise, so I left it

Procmon Logfiles can get quite big - You might set some appropriate filters there (for the processes or programs You examine).


TODO
----

- travis windows
