fingerprint
=================

Monitoring Registry and File Changes in Windows - forensic analytics for windows registry and files.

I wrote this software because those I found in the wild are either too slow, undocumented, or expansive.

"fingerprint" records the state of the system, by saving all filenames, file sizes, creation, access and modify dates in a csv file. 
All registry keys and values are stored in a second file. Different Fingerprints can be compared and filtered with procmon logfiles to analyze what and when the system was changed.

All fingerprints are stored in csv, Excel compatible format, for convenient filtering, sorting, etc.

sources are included, but You just might use the .exe files created with pyinstaller from `Releases <https://github.com/bitranox/fingerprint/releases>`_

Installation
------------

no installation required, just use the .exe files from `Releases <https://github.com/bitranox/fingerprint/releases>`_

Requirements
---------------

following Packets will be installed / needed (when using .py files): 

python-registry

Acknowledgement
---------------
Inspired by Regshot, InstallWatch Pro, SpyMe Tools, RegDiff, WhatChanged, RegFromApp and others

Contribute
----------

I would love for you to fork and send me pull request for this project.
Please contribute.


License
-------

This software is licensed under the `MIT license <http://en.wikipedia.org/wiki/MIT_License>`_

See `License file <https://github.com/bitranox/fingerprint/blob/master/LICENSE>`_


SAMPLE SESSION
-


Lets make s walk-through by example. Lets assume we have a software with "Trial Period" and the Software stops working after the trial period. 

After uninstalling and reinstalling the software, it still shows "Trial Period ended" - so this software is not completely uninstalling, leaving some files or registry entries behind.

all programs are started from the commandline. Use <command> -h for showing the help with all commandline parameters.

- STEP1 - create fingerprint on a clean system. 
  use "fingerprint.exe" with elevated rights (run as administrator) to create a fingerprint named "before-install".
- STEP2 - create fingerprint after installing named "after-install"
- STEP3 - create fingerprint after running the software (before expiration), named "run-ok",
  use procmon to log all system activity and save the log as csv file "procmon-run-ok.csv"
- STEP4 - create fingerprint after running the software (after expiration), named "run-expired", 
  use procmon to create "procmon-run-expired.csv"
- STEP5 - create fingerprint after uninstalling the software, named "uninstall"
- STEP6 - create fingerprint after re-installing the software, named "reinstall", 
  use procmon to create "procmon-reinstall.csv"
- STEP7 - create fingerprint after run the software until expiration message named "reinstall-expired",
  use procmon to create "procmon-reinstall-expired.csv"
- STEP8 - compare Snapshots and Filter Procmon Logs
use "fingerprint-diff.exe" to analyze the changes between different steps.

In this particular case, create a diff between "before-install" and "uninstall" - the diff files will now state all system changes between the clean machine and the state after uninstalling the software.

- STEP9 - Filter the differences with "fingerprint-filter.exe"

Now filter the differences with the procmon logfile "procmon-reinstall-expired.csv" - so You will identify which of the remaining files or registry keys were accessed.
 
