Advanced usage
==============

Get release process status
--------------------------

At any time, the ``project-release --status`` command can be used to get an
overview of the current status of the release process.

Create a custom commit
----------------------

After the merge, if a custom commit is needed before the bump commit, the
``project-release --edit`` command can be used. The procedure will stop to let
the user perform the custom commit. Use the ``project-release --continue``
command to terminate the procedure.

Handle merge conflicts
----------------------

If the git merge is not successful, the initial ``project-release`` command will
stop, asking the user to resolve any conflicts.

Once the work is done (committed or staged), the ``project-release --continue``
command can be used to continue the release process.

At any time, the ``project-release --abort`` command can be used to interrupt
the release process.
