Starting Development
====================

This document describes how to start developing on Pyalysis. Familiarity with
git_, GitHub_, and commonly used Python tools such as virtualenv_, pytest_ and,
tox_ is assumed.

.. _git: http://git-scm.com
.. _GitHub: https://github.com
.. _virtualenv: http://www.virtualenv.org
.. _pytest: http://pytest.org
.. _tox: http://tox.readthedocs.org

To start working on Pyalysis you should fork the Pyalysis repository on Github
and make a local clone of your fork.

Once you have done that you should create a virtualenv, activate it, and
install the necessary tools for development, testing and building the
documentation with::

    $ make dev-env

Once you have done that you can run the tests with ``py.test`` or ``make test``,
some parts of the project such as documentation or package metadata is not
tested with ``py.test`` but with a tox environment.

In order to test the code on all interpreters, test the documentation or
package data, you therefore have to run ``tox``. It's recommended to do this
everytime before you commit.

To build the documentation you can use ``make doc``, to view the HTML version
you can use ``make view-doc``.


Making Changes
--------------

Now that you have created a development environment, you probably want to
actually make a change. In order for your changes to be accepted you should
follow a couple of rules.

If you are fixing a bug, make a branch based on the branch for the latest
supported version, if you are implementing a feature make a branch based on
`master`.

Keep commits small, if the word "and" appears in the summary of a commit
your commit is too large. Write useful commit messages, these_ are good
guidelines, generally keep the summary small and don't be afraid of explaining
the changes in detail.

.. _these: http://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html

Don't merge in the branch you have initially branched from (master or a version
branch) unless something has been added that you need, if that happens explain
why you performed a merge in the commit message.

Whether you work on a feature or a bugfix, add tests and documentation. In the
case of a bug a changelog entry is probably sufficient.

If this is your first contribution to the project, please add yourself to the
list of contributors in :doc:`../notes/authors`.

Once you have made your changes push them to your Github repository and make
a pull request to the branch you initially branched off of. Explain what you
did and what problems it solves.

When you make a pull request summarize what you did, the use case, how it is
useful, and -- if applicable -- why you have chosen the approach you have taken
as opposed to others.

Once you have made your pull request be patient, this is an open source project
and it may take some time until someone is able to review your request. Once
your changes have passed review, they will be merged.
